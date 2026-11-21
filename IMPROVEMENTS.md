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

- 2026-11-21: still likes only (insights permission not enabled). 008 steel portal frame 30, 004 timber wall frame 21,
  012 road pavement 19 after less than a day (best first day so far, and a civil topic, the category that had done
  worst; it was the first video with the music bed and the shorter hook, but one video can't prove that), 003 and 005
  9, 009 6, 011 4, 006 3, 010 1. Pattern still: structure/"skeleton" reveals lead; a strong surprise hook ("the black
  stuff is the thin bit") can lift a civil topic. Next residential pick follows that: 015 roof trusses.

## Changelog

### 2026-11-21: Part-built first frame (the hook's 3D model starts half built)
- **What:** in the hook, the 3D model now starts with the first half of its build order already in place at t=0
  (it used to be an empty ground slab), and the rest still drops in over the hook, finishing a bit earlier.
  Optional spec field `META["hook_start"]` (0..0.95, default 0.5) sets how much is built on frame 0.
- **Why:** Reels autoplay and the feed start on frame 0. In every 3D video that frame showed a bare blue plane under
  the first hook line, which says nothing. Now frame 0 is a recognisable structure: a house frame with trusses going
  on (015), a column grid with the tendon deck (013), floors with the first curtain wall row (014), portal frames (008).
- **Checked:** before/after frame 0 and 1s for 008, 013, 014, 015; tools/check.py --queue clean (013, 014, 015);
  full local build of 013 (duration and audio unchanged). Older specs need no change.
- **First video:** 013-post-tensioned-slab (posts 2026-11-21) and every video after it.
- **Files:** engine/blueprint.py (hook block in draw_frame).

### 2026-11-21: Faster, time-limited install step (post run 17.5 min -> about 7)
- **What:** tools/install.sh skips system packages already on the runner, never pulls apt Recommends, tries the
  runner's existing package lists before `apt-get update` (only runs it if the install fails), and puts a time limit
  on each apt call with one clean retry. Prints how long each part took.
- **Why:** the Install step had grown from 38s (11-18) to 6 min (11-19) to 12 min (11-20), almost all of it apt, which
  made the post itself late and left a stalled mirror able to hang the job. Backlog #7.
- **Checked:** dry run of post.yml (run 44848047335): only ffmpeg and libcairo2-dev were missing, installed from the
  existing lists in 16s, whole Install step 32s, build/host/publish green.
- **Files:** tools/install.sh (also used by preview.yml and voice-test.yml).

### 2026-11-21 (content): roof-plan inset + detail bubble
- 015-roof-trusses fills the empty top band with a small "ROOF PLAN" inset that builds along with the steps (trusses
  one by one, straps, battens, sheets) plus a magnified detail bubble for the tie-down. Both are spec-local for now;
  see Backlog #3 to move them into the engine.

### 2026-11-20: Automatic layout check (`tools/check.py`)
- **What:** `python tools/check.py --queue` (or video folders) renders every 0.25s of each video plus the cover with
  the engine instrumented (text, leader/line drawing and 3D are probed, fades through cairo groups are tracked) and
  reports: overlapping labels, a line or another label's leader drawn over a label, text off the left/right edge,
  key text in the bottom 20%, 3D model off the frame / into the header / bottom 20% / the cover title strip (errors);
  3D model small or covering text, hook over 4.5s, video over 75s (warnings). Overlaps must last 0.5s+ so normal
  cross-fades pass. `--out DIR` saves the frame of each problem with a red box. Exit code 1 on any error.
  Uses real timings if a fresh `<slug>.timings.json` is in build/ or out/, `--voice` for exact ones, otherwise an
  estimate from the narration word counts. About 30s per video on 2 cores.
- **Proved on:** a broken copy of 014 (the BRACKET leader through CAST-IN CHANNEL from my first draft, a label pushed
  off the right edge, an oversized 3D model): all caught. Real catch on the queue: in 013 the TOP BARS leader ran
  through the DEAD END label (t~33-38s); fixed by moving DEAD END down a row. 008, 011, 012, 014 clean.
- **How to use:** run it on every new video before committing (replaces most of the manual PNG review; still look
  at the cover and a contact sheet for taste).
- **Files:** tools/check.py (new), videos/013 spec (label row).

### 2026-11-20: Shorter hooks (step 1 starts by ~4s instead of ~7s)
- **What:** engine/voice.py reads the hook tighter than the steps: 0.22s between hook sentences (was 0.4) and a 0.3s
  pause before step 1 (was 0.5). The voice itself and voice.json are unchanged. Hook narration on the queued videos
  is cut to the claim + punchline; the spoken "Here's how a ... is built" is dropped because the on-screen
  hook_sub already says it. Measured with the Kokoro voice: 012 7.24s -> 3.82s, 013 ~7.3s -> 4.09s,
  014 5.46s -> 3.95s.
- **Why:** step 1 (the first visual change after the hook) didn't start until ~7s; viewers decide in 3s.
- **Rule for new specs:** NARRATION["hook"] is one or two short sentences, about 12 words, no "Here's how".
  tools/check.py warns when the hook scene is over 4.5s.
- **First video:** 012-road-pavement (posts 2026-11-20).
- **Files:** engine/voice.py, videos/012, 013, 014 specs.

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
2. **Bigger, shared leader labels.** Labels are 24px (about 9pt on a phone) and every spec copies its own `label()`.
   Move one into engine/blueprint.py at ~28-30px with a phone-safe plate, switch the queued specs to it, and let
   tools/check.py catch the new overlaps. Impact: readability on phones, less copy-paste in specs.
3. **Use the empty top band in every video:** turn 015's roof-plan inset and detail bubble into engine helpers
   (`inset()`, `detail_bubble()`), or a small live 3D mini-map with the current step highlighted. Impact: medium,
   more to look at during the 2D steps.
4. **On-screen number in the hook** (e.g. "90% OF THIS ROAD IS ROCK") where a safe, general figure exists. Impact: medium.
5. **Save / comment prompt.** End-card versions ("Save this for your next build", "Which step surprised you?") need
   Mathew's OK first: the current content rule is that the end card says only "Follow for more". Meanwhile a question
   as the caption's first line can test the same idea. Impact: saves and comments (weigh heavily in Reels ranking).
6. **Publish retry with a fresh container** for transient Instagram errors (no failures seen yet). Impact: reliability.
7. **"Wrong vs right" / "Spot the defect" format** as a second series. Impact: shares; needs insights first.
8. **Music variety:** a few bed variants (key/tempo per category) so the channel doesn't repeat one loop forever,
   and a short riser into the 3D result. Impact: low-medium; wait for watch-time data to confirm the bed helps.
9. **Run tools/check.py in CI** (preview/post workflows, warning-only at first) so a layout regression from an
   engine change is caught even when no one renders frames. Impact: reliability.
10. **Cache pip wheels in post.yml** (`setup-python` `cache: pip`): pycairo builds from source each run (~10s).
    Impact: low.

## Tried and dropped

(none yet)
