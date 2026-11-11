"""Publish a Reel via the Instagram API with Instagram Login.

  python publish/instagram.py post --video-url URL --caption-file FILE   -> prints media id
  python publish/instagram.py refresh --out FILE                          -> writes refreshed token to FILE
  python publish/instagram.py check                                        -> confirms token + account

Env: IG_ACCESS_TOKEN, IG_USER_ID
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request, urllib.error

def host():
    """Instagram-login tokens (IG...) use graph.instagram.com; Facebook/unified-login tokens (EA...) use graph.facebook.com."""
    if os.environ.get("IG_HOST"): return os.environ["IG_HOST"]
    return "https://graph.facebook.com" if token().startswith("EA") else "https://graph.instagram.com"
VER = os.environ.get("IG_GRAPH_VERSION", "v26.0")


def token():
    # tolerate stray whitespace / quotes from copy-paste into GitHub secrets
    return os.environ.get("IG_ACCESS_TOKEN", "").strip().strip('"').strip("'").strip()


def diagnose():
    t = token(); uid = os.environ.get("IG_USER_ID", "").strip()
    kind = {"IG": "Instagram-login token", "EA": "Facebook/unified-login token"}.get(t[:2], "unrecognised")
    print(f"token: starts '{t[:2]}', length {len(t)}, looks like {kind}; contains spaces: {' ' in t}")
    print(f"user id: length {len(uid)}, all digits: {uid.isdigit()}")


def call(method, path, params, versioned=True):
    params = dict(params, access_token=token())
    url = f"{host()}/{VER}/{path}" if versioned else f"{host()}/{path}"
    data = None
    if method in ("GET", "DELETE"):
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method), timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        body = body.replace(token(), "***") if token() else body
        sys.exit(f"Instagram API error {e.code} on {path}: {body}")


def post(video_url, caption, cover_url=None):
    uid = os.environ["IG_USER_ID"].strip()
    params = {"media_type": "REELS", "video_url": video_url, "caption": caption, "share_to_feed": "true"}
    if cover_url: params["cover_url"] = cover_url
    c = call("POST", f"{uid}/media", params)
    cid = c["id"]; print("container", cid)
    for _ in range(60):                       # up to ~10 min for Instagram to fetch + process the video
        st = call("GET", cid, {"fields": "status_code,status"})
        code = st.get("status_code"); print("status", code)
        if code == "FINISHED": break
        if code in ("ERROR", "EXPIRED"): sys.exit(f"container failed: {st}")
        time.sleep(10)
    else:
        sys.exit("timed out waiting for Instagram to process the video")
    pub = call("POST", f"{uid}/media_publish", {"creation_id": cid})
    mid = pub["id"]
    info = call("GET", mid, {"fields": "permalink"})
    print("published", mid, info.get("permalink", ""))
    return mid


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("post"); p.add_argument("--video-url", required=True); p.add_argument("--caption-file", required=True)
    p.add_argument("--id-file"); p.add_argument("--cover-url")
    r = sub.add_parser("refresh"); r.add_argument("--out", required=True)
    sub.add_parser("check")
    d = sub.add_parser("delete"); d.add_argument("media_ids", nargs="+")
    a = ap.parse_args()
    if a.cmd == "post":
        mid = post(a.video_url, open(a.caption_file).read().strip(), a.cover_url)
        if a.id_file: open(a.id_file, "w").write(mid)
    elif a.cmd == "refresh":
        if token().startswith("EA"):
            print("Facebook/unified-login token: no self-refresh endpoint; check expiry in the 'check' output.")
            return
        res = call("GET", "refresh_access_token", {"grant_type": "ig_refresh_token"}, versioned=False)
        open(a.out, "w").write(res["access_token"])
        print("token refreshed, expires in", res.get("expires_in"), "s")
    elif a.cmd == "delete":
        for mid in a.media_ids:
            print(mid, call("DELETE", mid.strip(), {}))
    elif a.cmd == "check":
        diagnose()
        uid = os.environ["IG_USER_ID"].strip()
        if token().startswith("EA"):
            try:
                d = call("GET", "debug_token", {"input_token": token()}).get("data", {})
                exp = d.get("expires_at", 0)
                print(f"token type: {d.get('type')}, valid: {d.get('is_valid')}, expires: "
                      f"{'never' if exp == 0 else time.strftime('%Y-%m-%d', time.gmtime(exp))}, scopes: {d.get('scopes')}")
            except SystemExit as e:
                print("(couldn't inspect token)", str(e)[:200])
            me = call("GET", uid, {"fields": "username,name"})
            print("connected:", me.get("username"), "user_id", uid)
        else:
            me = call("GET", "me", {"fields": "user_id,username,account_type"})
            print("connected:", me.get("username"), me.get("account_type"), "user_id", me.get("user_id"))
        lim = call("GET", f"{os.environ['IG_USER_ID'].strip()}/content_publishing_limit", {"fields": "quota_usage,config"})
        print("publishing limit:", lim)


if __name__ == "__main__":
    main()
