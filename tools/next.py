"""Print the next video to post (empty if none).

Daily rotation: reno -> civil -> structural -> commercial -> residential -> infrastructure -> reno ...
Picks the first queued, unposted video in the category after the last one posted.
If that category has nothing ready, it moves on to the next category, so a day is never skipped
just because one category is empty.
"""
import os, re, sys

ROTATION = ["reno", "civil", "structural", "commercial", "residential", "infrastructure"]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read(name):
    p = os.path.join(root, name)
    return [l.strip() for l in open(p) if l.strip() and not l.startswith("#")] if os.path.exists(p) else []

def category(slug):
    p = os.path.join(root, "videos", slug, "spec.py")
    if not os.path.exists(p): sys.exit(f"queue.txt lists {slug} but videos/{slug}/spec.py is missing")
    m = re.search(r'"category":\s*"([a-z]+)"', open(p).read())
    return m.group(1) if m else "residential"

posted = [l.split()[0] for l in read("posted.txt")]
ready = [s for s in read("queue.txt") if s not in set(posted)]
if not ready: sys.exit(0)
last = category(posted[-1]) if posted else ROTATION[-1]
start = (ROTATION.index(last) + 1) % len(ROTATION) if last in ROTATION else 0
for k in range(len(ROTATION)):
    want = ROTATION[(start + k) % len(ROTATION)]
    for slug in ready:
        if category(slug) == want:
            print(slug); sys.exit(0)
print(ready[0])
