"""Print the next video to post: first slug in queue.txt not yet in posted.txt (empty if none)."""
import os, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def read(name):
    p = os.path.join(root, name)
    return [l.strip() for l in open(p) if l.strip() and not l.startswith("#")] if os.path.exists(p) else []

posted = {l.split()[0] for l in read("posted.txt")}
for slug in read("queue.txt"):
    if slug not in posted:
        if not os.path.exists(os.path.join(root, "videos", slug, "spec.py")):
            sys.exit(f"queue.txt lists {slug} but videos/{slug}/spec.py is missing")
        print(slug); break
