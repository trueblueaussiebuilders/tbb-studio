"""Publish a Reel via the Instagram API with Instagram Login.

  python publish/instagram.py post --video-url URL --caption-file FILE   -> prints media id
  python publish/instagram.py refresh --out FILE                          -> writes refreshed token to FILE
  python publish/instagram.py check                                        -> confirms token + account

Env: IG_ACCESS_TOKEN, IG_USER_ID
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request, urllib.error

HOST = os.environ.get("IG_HOST", "https://graph.instagram.com")
VER = os.environ.get("IG_GRAPH_VERSION", "v26.0")


def call(method, path, params, versioned=True):
    params = dict(params, access_token=os.environ["IG_ACCESS_TOKEN"])
    url = f"{HOST}/{VER}/{path}" if versioned else f"{HOST}/{path}"
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method), timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        body = body.replace(os.environ["IG_ACCESS_TOKEN"], "***")
        sys.exit(f"Instagram API error {e.code} on {path}: {body}")


def post(video_url, caption):
    uid = os.environ["IG_USER_ID"]
    c = call("POST", f"{uid}/media", {"media_type": "REELS", "video_url": video_url, "caption": caption, "share_to_feed": "true"})
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
    p.add_argument("--id-file")
    r = sub.add_parser("refresh"); r.add_argument("--out", required=True)
    sub.add_parser("check")
    a = ap.parse_args()
    if a.cmd == "post":
        mid = post(a.video_url, open(a.caption_file).read().strip())
        if a.id_file: open(a.id_file, "w").write(mid)
    elif a.cmd == "refresh":
        res = call("GET", "refresh_access_token", {"grant_type": "ig_refresh_token"}, versioned=False)
        open(a.out, "w").write(res["access_token"])
        print("token refreshed, expires in", res.get("expires_in"), "s")
    elif a.cmd == "check":
        me = call("GET", "me", {"fields": "user_id,username,account_type"})
        print("connected:", me.get("username"), me.get("account_type"), "user_id", me.get("user_id"))
        lim = call("GET", f"{os.environ['IG_USER_ID']}/content_publishing_limit", {"fields": "quota_usage,config"})
        print("publishing limit:", lim)


if __name__ == "__main__":
    main()
