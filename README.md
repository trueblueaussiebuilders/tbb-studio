# True Blue Aussie Builders studio

Automated blueprint-style construction Reels for [@trueblueaussiebuilders](https://instagram.com/trueblueaussiebuilders).

## How it runs

| Who | When | What |
|---|---|---|
| Claude | Monthly | Writes the next batch of videos (`videos/<slug>/spec.py`), adds them to `queue.txt`, opens a PR |
| GitHub (preview.yml) | On every PR | Renders the new videos with the production voice, comments a download link |
| You | Monthly | Watch previews, merge the PR (= approval) |
| GitHub (post.yml) | Tue + Fri 7:30pm Melbourne | Renders the next queued video, hosts it on GitHub Pages, posts it as a Reel, logs it in `posted.txt` |
| GitHub (maintenance.yml) | Weekly | Checks the Instagram connection and refreshes the 60-day token |

## One-time setup

1. **Repo settings → Pages → Source: GitHub Actions.**
2. **Repo settings → Secrets and variables → Actions → New repository secret:**

   | Secret | Where it comes from |
   |---|---|
   | `IG_ACCESS_TOKEN` | Meta developer app → Instagram → API setup with Instagram login → Generate access tokens |
   | `IG_USER_ID` | Same screen, shown next to the account |
   | `ELEVENLABS_API_KEY` | ElevenLabs → profile → API keys |
   | `ELEVENLABS_VOICE_ID` | ElevenLabs → your chosen voice → copy voice ID |
   | `GH_PAT` (optional) | GitHub → Settings → Developer settings → Fine-grained token, this repo only, permission *Secrets: read and write*. Lets the weekly job refresh the Instagram token. Without it, regenerate the token in Meta before day 60. |

3. **Test:** Actions → *Token refresh + connection check* → Run workflow. It should print `connected: truebluebuilds BUSINESS`.
4. **Dry run:** Actions → *Post next video* → Run workflow (dry run ticked). It builds and hosts the video without posting.
5. **Go live:** run it once with dry run unticked, or just wait for Tuesday/Friday.

## Adding a video

```
videos/002-tilt-up-panel/spec.py    # META (on-screen text), NARRATION (voice lines), CAPTION, draw_section()
```
Optional: `model3d()` (3D model for the hook, result and cover; the hook starts it half built, change with
`META["hook_start"] = 0.3` etc.) and `META["xray"] = {"after_step": 4, "upto": 12, "hot": [5, 6]}`
(a 3D "built so far" interlude at the end of that step; see IMPROVEMENTS.md).
In the result, the 3D model rebuilds start to finish in build order (about 2s) before orbiting finished;
turn that off per video with `META["replay"] = False`.
The end card keeps the finished model on screen and moves it back to the hook's position and angle so the Reel loops
smoothly into frame 0 ("FOLLOW FOR MORE" sits above it); turn that off with `META["end_model"] = False`.
Every video gets a synthesised music bed ducked under the voice plus light sound effects (`engine/audio.py`);
turn them off per video with `META["music"] = False` / `META["sfx"] = False` (the build replay's rising "tock" per part
with `META["replay_sfx"] = False`).
`META["question"]`: one short, easy-to-answer question; the caption puts it right after the first line (visible before
"... more") to invite comments. Build the caption with `python -m engine.build videos/<slug> --caption-only`.
Keep `NARRATION["hook"]` to one or two short sentences (about 12 words, no "Here's how": `hook_sub` says it on screen)
so the hook scene stays under 4.5s. Check the layout automatically before committing:
```
python tools/check.py videos/002-tilt-up-panel      # or --queue for everything not yet posted; --out DIR saves problem frames
```
The 2D drawing has a camera: on each step it glides onto that step's work (the orange linework and labels) and
pushes in up to 1.2x, as long as every label on screen during the step stays in view; steps whose work fills the
drawing get the old slow drift (in on odd steps, out on even ones). Draw the newest step's lines and labels in
`tl.col(step, t)` (orange) so the camera can find them. `META["focus"] = False` keeps only the drift,
`META["focus"] = {6: (x, y, 1.15)}` frames a step by hand, `META["drift"] = 0` turns the camera off. Keep key linework
and labels at least ~25px inside the drawing area. Step bodies show at
36px: keep them under ~80 characters so they stay at two lines.
Leader labels: call the engine's `label(ctx, p, col, tip, elbow, txt, anchor, a)` (28px on a dark plate) rather than
copying one into the spec; `gone(t, t0)` fades a label out once it's no longer relevant.
Then add `002-tilt-up-panel` to `queue.txt`. Shared look, panels, timing and end card live in `engine/blueprint.py`.

Local build (no keys needed, uses the free Kokoro voice):
```
pip install -r requirements.txt          # needs ffmpeg + cairo
python -m engine.build videos/001-waffle-pod-slab --out out
python -m engine.build videos/001-waffle-pod-slab --out out --frames 10 25   # PNG stills only
```

## Rules for content
- Typical Australian details only. Every caption says the engineer's design governs.
- No employer project names, drawings or photos.
- Keep key text out of the bottom ~20% and right edge of the frame (Reels UI covers it).
