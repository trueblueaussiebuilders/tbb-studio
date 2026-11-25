"""Pull each posted Reel's metrics from the Instagram Graph API into insights.csv.

  python publish/insights.py --out insights.csv

Reads the media IDs in posted.txt (lines starting with # are ignored), asks the API for every
Reels metric in METRICS, skips any metric the API no longer supports (without failing), and
writes one row per video with the video's category / title / hook from its spec for analysis.

Env: IG_ACCESS_TOKEN, IG_USER_ID (same as publishing).
Needs the insights permission on the token: instagram_business_manage_insights (Instagram login)
or instagram_manage_insights (Facebook login).
"""
import argparse, csv, json, os, re, sys, time, urllib.parse, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import instagram as ig

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Reels insights metrics, in CSV column order. Times come back in milliseconds.
METRICS = ["views", "reach", "likes", "comments", "shares", "saved", "total_interactions",
           "ig_reels_avg_watch_time", "ig_reels_video_view_total_time"]
COLUMNS = ["slug", "category", "title", "hook", "posted", "media_id", "permalink", "fetched_utc",
           "views", "reach", "likes", "comments", "shares", "saved", "total_interactions",
           "avg_watch_s", "total_watch_s", "unsupported", "question"]
def permission_hint():
    if ig.token().startswith("EA"):     # Facebook-login token (what this account uses)
        return ("The Instagram token has no insights permission. In the Meta app (developers.facebook.com -> your app), "
                "add the permission 'instagram_manage_insights' (keep instagram_basic, instagram_content_publish, "
                "pages_show_list, pages_read_engagement), generate a new token for the Facebook Page linked to "
                "@trueblueaussiebuilders with that permission ticked, and paste it into the IG_ACCESS_TOKEN repo secret.")
    return ("The Instagram token has no insights permission. In the Meta app (developers.facebook.com -> your app -> "
            "Instagram -> API setup with Instagram login), add the permission 'instagram_business_manage_insights', "
            "then click 'Generate token' for @trueblueaussiebuilders again and paste it into the IG_ACCESS_TOKEN repo secret.")


class ApiError(Exception):
    def __init__(self, code, body):
        self.code, self.body = code, body
        try: self.err = json.loads(body).get("error", {})
        except ValueError: self.err = {}
        super().__init__(f"HTTP {code}: {body[:300]}")

    @property
    def permission(self):
        msg = self.err.get("message", "").lower()
        return self.err.get("code") in (10, 200) or "permission" in msg


def get(path, params):
    params = dict(params, access_token=ig.token())
    url = f"{ig.host()}/{ig.VER}/{path}?" + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace").replace(ig.token(), "***")
            if e.code >= 500 and attempt < 2: time.sleep(5 * (attempt + 1)); continue
            raise ApiError(e.code, body)
        except urllib.error.URLError as e:
            if attempt < 2: time.sleep(5 * (attempt + 1)); continue
            raise ApiError(0, f"network error: {e.reason}")


def posted():
    rows = []
    for line in open(os.path.join(ROOT, "posted.txt")):
        if not line.strip() or line.startswith("#"): continue
        parts = line.split()
        if len(parts) >= 3: rows.append((parts[0], parts[1], parts[2]))
    return rows


def spec_info(slug):
    p = os.path.join(ROOT, "videos", slug, "spec.py")
    src = open(p).read() if os.path.exists(p) else ""
    def field(name):
        m = re.search(rf'"{name}":\s*"([^"]*)"', src); return m.group(1) if m else ""
    m = re.search(r'"hook":\s*\[([^\]]*)\]', src)
    hook = " / ".join(re.findall(r'"([^"]*)"', m.group(1))) if m else ""
    return field("category"), field("title"), hook, field("question")


def metrics(mid, unsupported):
    """Ask for all metrics at once; if the API rejects one, fall back to one-by-one and skip the bad ones."""
    want = [m for m in METRICS if m not in unsupported]
    out = {}
    try:
        res = get(f"{mid}/insights", {"metric": ",".join(want)})
        for d in res.get("data", []):
            v = d.get("values", [{}])[0].get("value") if d.get("values") else d.get("total_value", {}).get("value")
            out[d["name"]] = v
        return out
    except ApiError as e:
        if e.permission: raise
    for m in want:
        try:
            res = get(f"{mid}/insights", {"metric": m})
            for d in res.get("data", []):
                out[d["name"]] = d.get("values", [{}])[0].get("value")
        except ApiError as e:
            if e.permission: raise
            unsupported.add(m)
            print(f"  skipping metric {m}: {e.err.get('message', e)}"[:200])
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(ROOT, "insights.csv"))
    a = ap.parse_args()
    now = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    unsupported, rows, no_perm, failed = set(), [], False, 0
    for slug, date, mid in posted():
        cat, title, hook, question = spec_info(slug)
        row = {"slug": slug, "category": cat, "title": title, "hook": hook, "question": question, "posted": date, "media_id": mid,
               "fetched_utc": now}
        try:
            info = get(mid, {"fields": "permalink,like_count,comments_count"})
            row["permalink"] = info.get("permalink", "")
            row["likes"], row["comments"] = info.get("like_count", ""), info.get("comments_count", "")
        except ApiError as e:
            print(f"{slug}: media lookup failed: {e}"[:300]); failed += 1
            rows.append(row); continue
        if not no_perm:
            try:
                m = metrics(mid, unsupported)
                for k in ("views", "reach", "likes", "comments", "shares", "saved", "total_interactions"):
                    if m.get(k) is not None: row[k] = m[k]
                if m.get("ig_reels_avg_watch_time") is not None: row["avg_watch_s"] = round(m["ig_reels_avg_watch_time"] / 1000, 2)
                if m.get("ig_reels_video_view_total_time") is not None:
                    row["total_watch_s"] = round(m["ig_reels_video_view_total_time"] / 1000, 1)
            except ApiError as e:
                no_perm = True
                print(f"insights not permitted: {e}"[:300])
        row["unsupported"] = " ".join(sorted(unsupported))
        rows.append(row)
        print(f"{slug}: views={row.get('views', '-')} reach={row.get('reach', '-')} likes={row.get('likes', '-')} "
              f"shares={row.get('shares', '-')} saved={row.get('saved', '-')} avg_watch_s={row.get('avg_watch_s', '-')}")
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS); w.writeheader()
        for r in rows: w.writerow({k: r.get(k, "") for k in COLUMNS})
    print(f"wrote {len(rows)} rows to {a.out}")
    if no_perm:
        print(f"::warning::{permission_hint()}")
        summ = os.environ.get("GITHUB_STEP_SUMMARY")
        if summ: open(summ, "a").write(f"**Insights blocked:** {permission_hint()}\n")
    if rows and failed == len(rows):
        sys.exit("Every media lookup failed. Check the IG_ACCESS_TOKEN secret (run the maintenance workflow).")


if __name__ == "__main__":
    main()
