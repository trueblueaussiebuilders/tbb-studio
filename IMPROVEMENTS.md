# Improvements log

Each maintenance run ships one tested improvement (two if both are small) and logs it here.
Rules: older specs must keep building; evolve the look in steps; never touch the schedule, account, secrets or voice.

## What's working

- 2026-11-18: no reach / watch-time data yet. The new insights workflow runs, but the token has no insights
  permission (see Backlog #1). Likes only so far: 008 steel portal frame 30, 003 brick veneer 9, 005 Super-T bridge 9,
  004 timber wall frame 7, 009 suspended slab 6, 006 load-bearing wall 3, 001/002/007 0. Too early to call a pattern;
  structural steel and "it's held up by timber" style surprise hooks are early leaders.

## Changelog

### 2026-11-18: Instant hook (scroll-stopping first frame)
- **What:** frame 0 used to be an empty blueprint (header typed on from nothing, hook text faded in from 0.4s,
  3D model started at 0.2s). Now the header, the first hook line and the 3D ground slab are on screen at t=0;
  the next lines land by ~0.5s and the orange punchline pops in (slight scale-down) at ~0.6-0.85s; hook_sub at 1.0s.
- **Why:** Reels autoplay starts on frame 0 and viewers decide in the first second. A blank first frame is a
  scroll-past. Before/after checked on 010, 011, 012 at t = 0, 0.4, 0.9, 1.6.
- **First video:** 010-box-culvert (posts 2026-11-18), and every video after it. No spec changes needed.
- **Files:** engine/blueprint.py (draw_frame header + hook block).

### 2026-11-18: Daily insights workflow
- **What:** `.github/workflows/insights.yml` (daily 21:17 UTC + manual) runs `publish/insights.py`, which reads the
  media IDs in posted.txt, pulls each Reel's views, reach, likes, comments, shares, saves, total interactions,
  average and total watch time, and commits `insights.csv` (with each video's category, title and hook) to main.
  Unsupported metrics are skipped and listed in the `unsupported` column; a missing permission gives a warning
  with exact fix steps instead of failing.
- **Why:** so future runs can learn which hooks, categories and features actually work.
- **Status:** runs green. Basic fields (permalink, likes, comments) are filled; insights metrics are blocked until the
  token gets the insights permission (Backlog #1).
- **Files:** .github/workflows/insights.yml, publish/insights.py.

## Backlog (ranked)

1. **Enable insights permission (Mathew, 5 min in Meta).** The token is a Facebook-login token (starts "EA") and the
   API says `(#10) Application does not have permission`. Add `instagram_manage_insights` to the Meta app, generate a
   new Page token for the account with it ticked, and update the IG_ACCESS_TOKEN secret. Impact: unlocks every
   data-driven decision below.
2. **Music bed ducked under the voice + soft "tick" on each label reveal.** Videos are voice-only. A quiet,
   royalty-free generated bed (synthesised in numpy, no licensing risk) adds energy and retention. Impact: high.
3. **3D "x-ray" cutaway in the middle of the video.** The 3D model only appears in the hook and result; a 2-3s
   3D orbit at step 4 or 5 with the current part highlighted orange (render(highlight=...) already exists) would add
   a pattern interrupt mid-video. Impact: high on average watch time.
4. **Auto layout check (`tools/check.py`).** Render frames at every label's full-on time and flag label plates that
   overlap each other, text in the bottom 20% / right edge, or a 3D model that clips the frame. Impact: fewer
   manual fixes, safer automation.
5. **End-card call to action that varies:** "Save this for your next build" / "Which step surprised you?" /
   a one-question quiz. Impact: saves and comments (both weigh heavily in Reels ranking).
6. **On-screen number in the hook** (e.g. "90% OF THIS ROAD IS ROCK") where a safe, general figure exists. Impact: medium.
7. **Use the empty top band during steps** (400-640px is often blank in wide, shallow sections): a small live
   mini-map of the 3D model with the current step highlighted. Impact: medium.
8. **Publish retry with a fresh container** for transient Instagram errors (no failures seen yet). Impact: reliability.
9. **"Wrong vs right" / "Spot the defect" format** as a second series. Impact: shares; needs insights first.

## Tried and dropped

(none yet)
