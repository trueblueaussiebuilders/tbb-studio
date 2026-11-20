# Improvements log

Each maintenance run ships one tested improvement (two if both are small) and logs it here.
Rules: older specs must keep building; evolve the look in steps; never touch the schedule, account, secrets or voice.

## What's working

- 2026-11-18: no reach / watch-time data yet. The new insights workflow runs, but the token has no insights
  permission (see Backlog #1). Likes only so far: 008 steel portal frame 30, 003 brick veneer 9, 005 Super-T bridge 9,
  004 timber wall frame 7, 009 suspended slab 6, 006 load-bearing wall 3, 001/002/007 0. Too early to call a pattern;
  structural steel and "it's held up by timber" style surprise hooks are early leaders.

- 2026-11-19: still no views / watch time (insights permission not yet enabled). Likes as of 2026-11-18: 008 steel
  portal frame 30, 004 timber wall frame 21 (posted a day later than most, so still climbing), 003 and 005 9 each.
  Structural/framing "skeleton" topics lead on likes; keep alternating them in. Not enough data to judge hooks.

- 2026-11-20: still likes only (insights permission not enabled yet). 008 steel portal frame 30, 004 timber wall
  frame 21, 003 brick veneer 9, 005 Super-T bridge 9, 009 suspended slab 6, 006 load-bearing wall 3 (+1 comment),
  011 re-stumping 3 (1 day old), 001/002/007/010 0. Pattern holding over 10 posts: framing/structural "skeleton"
  topics (008, 004, 003) get the most likes; civil/earthworks (007, 010) the least. Keep structure-reveal topics
  and "what's hidden inside" hooks coming; give civil videos a stronger surprise hook.

## Changelog

### 2026-11-20: Music bed + sound effects
- **What:** new `engine/audio.py`, called from `engine/build.py` right after the voiceover. Every video now gets a
  numpy-synthesised music bed (soft pad chords vi-IV-I-V at 96 BPM, a quiet plucked arpeggio from 0.2s, and a soft
  kick on every beat once step 1 starts), ducked under the voice (about 19-20 dB below the voice while it speaks,
  about 14 dB below in the pauses) and faded out over the end card. Plus light effects on what changes on screen:
  a low thump when the orange hook punchline pops in, a soft whoosh peaking on each step cut and on the result,
  a rising shimmer when the 3D x-ray opens, and a two-note chime on "Follow for more". No samples, so no licensing
  risk, and it's deterministic. Opt out per spec with `META["music"] = False` / `META["sfx"] = False`.
- **Why:** videos were voice-only with dead silence between sentences. A bed adds energy and continuity, and sound
  on reveals reinforces the pattern interrupts. Backlog #2.
- **Checked:** full build of 012: duration 72.2s (matches the timeline, no drift), peak -1.2 dBFS, no clipping,
  -16 LUFS integrated (same as voice-only); waveform before/after shows the gaps filled at a low level with the
  voice still dominant. Older specs (001, 006, 011) mix fine. Visuals unchanged.
- **First video:** 012-road-pavement (posts 2026-11-20) and every video after it. No spec changes needed.
- **Tune later:** levels are `BED_DB_OPEN` / `BED_DB_DUCK` / `SFX_DB` at the top of engine/audio.py. Once watch-time
  data exists, compare average watch time before/after 012.
- **Files:** engine/audio.py (new), engine/build.py.

### 2026-11-20 (content): "glass" 3D material
- `kind="glass"` parts get a lighter blue fill in engine/three_d.py. First used by 014-curtain-wall.

### 2026-11-19: Mid-video 3D "x-ray" interlude
- **What:** new optional spec field `META["xray"] = {"after_step": k, "upto": N, "hot": [orders], "scale": 1.0}`.
  For the last ~2.6s of step k the 2D section cross-fades to the 3D model, orbiting ~45 degrees: parts with
  build order <= `upto` are solid, the parts this step is about (`hot`) have orange edges, and everything not built
  yet is drawn as faint blue "ghost" edges, hidden behind solid parts. The section label swaps to
  "3D // BUILT SO FAR", then the drawing fades back for the next step. Skipped automatically if the step is too
  short (< 3.2s). Specs without the field build exactly as before.
- **Why:** the 3D model only appeared in the hook and the result, so the middle 40-50s were all 2D linework. A
  moving 3D view about halfway through is a pattern interrupt and shows how the part being built fits the whole.
- **First video:** 011-re-stumping (posts 2026-11-19, x-ray at the end of "New stumps": the new stumps in orange,
  the bearers, joists and wall frame above as ghosts). Also set on 012 (kerb and channel) and 013 (tendons + anchors
  before the pour).
- **How to use in new specs:** pick a step where the 3D model has something to show (usually step 4-6), print the
  model's part orders, set `upto` to the last order built by the end of that step and `hot` to that step's orders.
- **Files:** engine/blueprint.py (xray_window, draw_frame), engine/three_d.py (render ghost=), videos/011-013 specs.


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
2. **Shorter hook narration (target under 4.5s).** The hook scene runs as long as its voice line: 6.3s on 011,
   7.2s on 012 and 7.3s on 013 (014 was written short: 5.5s), so step 1 doesn't start until ~7s. Trim the hook line to the punchline plus
   "Here's how", and/or start the step-1 drawing under the end of the hook. Impact: high on 3s hold rate.
3. **Auto layout check (`tools/check.py`).** Render frames at every label's full-on time and flag label plates that
   overlap each other, text in the bottom 20% / right edge, or a 3D model that clips the frame. Impact: fewer
   manual fixes, safer automation.
4. **End-card call to action that varies:** "Save this for your next build" / "Which step surprised you?" /
   a one-question quiz. Impact: saves and comments (both weigh heavily in Reels ranking).
5. **On-screen number in the hook** (e.g. "90% OF THIS ROAD IS ROCK") where a safe, general figure exists. Impact: medium.
6. **Use the empty top band during steps** (400-640px is often blank in wide, shallow sections): a small live
   mini-map of the 3D model with the current step highlighted. Impact: medium.
7. **Publish retry with a fresh container** for transient Instagram errors (no failures seen yet). Impact: reliability.
8. **"Wrong vs right" / "Spot the defect" format** as a second series. Impact: shares; needs insights first.
9. **Faster post build.** On 2026-11-19 `tools/install.sh` (apt-get) took 6 of the 11 build minutes. Cache the apt
   packages or skip apt when ffmpeg/cairo are already on the runner. Impact: reliability (less time for a flaky step).
10. **Music variety:** a few bed variants (key/tempo per category) so the channel doesn't repeat one loop forever,
   and a short riser into the 3D result. Impact: low-medium; wait for watch-time data to confirm the bed helps.

## Tried and dropped

(none yet)
