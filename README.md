# True Blue Builds studio

Automated blueprint-style construction Reels for [@truebluebuilds](https://instagram.com/truebluebuilds).

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
