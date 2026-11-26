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

- 2026-11-22: still likes only (insights permission not enabled). 012 road pavement 24, 008 steel portal frame 30,
  004 timber wall frame 21, 013 post-tensioned slab 15 after half a day (second-best first day), 003 and 005 9,
  009 6, 011 4, 006 3, 010 1, 001/002/007 0. The two newest posts, with the music bed, short hook and instant hook
  (012, 013) are the two best first days on the channel; older videos took days to reach that. Could also be
  account growth, so keep comparing once views exist. Structure reveals + one clear surprise claim keep working,
  so 016 noise wall leads on "hidden piles".

- 2026-11-23: still likes only (insights permission not enabled). 008 steel portal frame 30, 013 post-tensioned slab
  29 (in 1.5 days), 012 road pavement 24, 004 timber wall frame 23, 014 curtain wall 23 (under a day), 003 10,
  005 9, 009 6, 011 4, 006 3, 010 1, 001/002/007 0. The four newest posts (012-014, every one with the music bed,
  short and instant hook, part-built first frame) are all in the top five and reached 20+ likes within a day, which
  no video before 012 did. Pattern across 3 videos now, not one: keep the current hook format. 013 also got the
  most comments (2). Commercial (014) did well with a "holds nothing up" surprise claim, so the claim matters more
  than the category. 017 shower waterproofing follows it: "the tiles aren't the waterproofing".

- 2026-11-24: still likes only (insights permission not enabled). 008 steel portal frame 30, 013 post-tensioned slab
  30, 014 curtain wall 29, 012 road pavement 24, 004 timber wall frame 23, 015 roof trusses 16 after ~12 hours,
  003 10, 005 9, 009 6, 011 4, 006 3, 010 1, 001/002/007 0. All five posts since 012 (music bed, short + instant
  hook, part-built first frame) are in the top six; 015 is tracking like 014 did on day one. Comments are still
  rare (2 on 013, 1 on 006), so a caption question is worth testing (Backlog #4). 018 concrete driveway follows
  the surprise-claim hook pattern on a relatable home topic: "those cracks in your driveway were planned".

- 2026-11-25: still likes only (insights permission not enabled). 013 post-tensioned slab 31, 008 steel portal frame
  30, 014 curtain wall 29, 012 road pavement 24, 004 timber wall frame 23, 015 roof trusses 18, 003 10, 005 9, 009 6,
  011 4, 016 noise wall 4 after ~13 hours, 006 3, 010 1, 001/002/007 0. 016 is the first post since 012 to start
  slowly (015 had 16 at the same age). It is also the third infrastructure video, and all three are at the bottom
  (005 9, 010 1, 016 4), so infrastructure is now the weakest category across three posts, not one. Next
  infrastructure pick should lead with the most relatable angle (a road or bridge people drive on daily) and a
  surprise claim. Comments are still 3 in total across 16 posts, so the caption question (shipped today) is the test.

- 2026-11-26: still likes only (insights permission not enabled). 013 post-tensioned slab 31, 008 steel portal frame
  30, 014 curtain wall 29, 012 road pavement 24, 017 shower waterproofing 23 after ~12 hours, 004 timber wall frame 23,
  015 roof trusses 18, 003 10, 005 9, 016 noise wall 7, 009 6, 011 4, 006 3, 010 1, 001/002/007 0. 017 is by far the
  best reno post (the other two have 3 and 4) and matched 014's first day, so a strong surprise claim lifted a weak
  category again (as 012 did for civil): across 012, 014, 017 the claim matters more than the category. 016 has
  stalled at 7, so infrastructure stays the weakest category (three of three at the bottom). 017 got 0 comments
  despite the caption question, but that's one post; keep judging over 5 (Backlog #4). 020 office partition follows
  the pattern with "this office wall has a gap at the top".

## Changelog

### 2026-11-26: End card keeps the 3D model and hands it back to the hook (seamless loop)
- **What:** the end card used to dim everything to near-black and put "FOLLOW FOR MORE" in the middle of the frame,
  on top of the faded model. Now the finished 3D model stays on screen at full brightness: it carries straight on
  from the result's last frame (same place, angle and size, so there's no cut or double image), glides down to the
  hook's position over 0.6s and turns back to the hook's starting angle by the last frame. "FOLLOW FOR MORE"
  (rising in), the orange rule and the handle now sit above it, where the hook text was. Reels loop straight back
  to frame 0, which shows the same model half built in the same spot and angle under the hook text, so the loop
  reads as the build starting again instead of a jump from a dark card. `end_model_on()` / `end_motion()` /
  `END_TEXT_Y` in engine/blueprint.py; opt out per spec with `META["end_model"] = False`. Specs with a witty
  `signoff` (001-003) keep the old text-only card by default, since their sign-off lines need the middle. The
  result's underlying 3D render is skipped once the end card takes over, so it costs no extra render time.
- **Why:** review of 018/019 as a phone viewer: the last ~3s were the dullest of the video (a near-empty dark frame),
  right at the loop point where Reels counts replays, and "FOLLOW FOR MORE" was drawn over the fading model.
  Backlog #6.
- **Checked:** tools/check.py --queue clean (018, 019, 020); before/after end frames of 019 (old: dark card, text over
  a ghosted model; new: bright model under clean text, continuous through the cut at the end of the result) and 020
  (last frame matches frame 0's framing); 008 (no sign-off) gets the new card, 001 (sign-off) is unchanged; old
  specs 001, 011, 013 report only their existing mid-video issues; full local build of 018 (next to post): 67.0s,
  audio and video lengths match, -16.1 LUFS, true peak -1.2 dBFS, last frame lines up with frame 0.
- **First video:** 018-concrete-driveway (posts 2026-11-26) and every video with a 3D model after it. No spec changes.
- **Files:** engine/blueprint.py, README.md.

### 2026-11-26 (content): 020 office partition + "board" 3D material
- Wall elevation (floor track, deflection head track, studs cut short and dashed behind the deep leg, noggings, a
  cable through the stud holes, acoustic batts, two plasterboard sheets as a cut-away, suspended ceiling) beside a
  magnified "HEAD DETAIL" box (slab, deep-leg track, the stud stopping short with a GAP dimension, boards stopping
  short, screws only below the legs, flexible sealant). The result sags the slab (labelled "movement exaggerated")
  and the gap closes in the detail while the wall stays put. New `kind="board"` (light fill) in engine/three_d.py.
  Note: the 3D edge depth test lets edges ~50mm behind a face show through, so thin linings like plasterboard read
  slightly see-through; fine for the x-ray look.

### 2026-11-25: Caption question + build-replay sound
- **What:** (1) new optional spec field `META["question"]`: one short, easy-to-answer question. `bp.caption(spec)`
  (used by engine/build.py for `<slug>.caption.txt` and `--caption-only`) puts it right after the caption's first
  line, so it shows in the feed preview before "... more". Specs without it get their CAPTION unchanged.
  publish/insights.py adds a `question` column to insights.csv so comment counts can be compared with and without.
  Added to the three queued videos: 017 "Did you know the tiles aren't the waterproofing? Yes or no in the
  comments.", 018 "Go and look: do the cracks in your driveway sit in the joints? Tell us below.", 019 "Have you
  ever parked under one of these without knowing? Tell us below."
  (2) engine/audio.py: a soft woody "tock" as each build order lands in the result's 3D replay, rising through a
  C major pentatonic scale as the model completes (at most ~8 per second; always one on the last part). Positions
  come from `replay_window()` so they stay in sync with the picture. Opt out with `META["replay_sfx"] = False`.
- **Why:** comments are the one engagement number we can measure now (3 across 16 posts) and Reels ranking weighs
  them; an easy yes/no question in the visible part of the caption is the standard fix (Backlog #2). The replay
  was the only big on-screen change with no sound; ticks make the timelapse feel physical (Backlog #5).
- **Checked:** captions of 017-019 show the question as the second paragraph, older specs (001, 008, 011) unchanged;
  tick times match the replay (017: lands 56.36-57.84s inside the 56.06-57.75s replay), tick peak 0.63 vs whoosh
  0.83 and thump 1.13 so the effects' overall level is unchanged; full local build of 017 (next to post): 61.8s,
  audio and video lengths match, -16.2 LUFS, true peak -1.2 dBFS; replay frames unchanged; tools/check.py --queue
  clean (017, 018, 019); old specs 001, 008, 011 still build; insights.py `spec_info` returns the new column.
  (3) small fix: the 3D model cache is now stored on the spec module instead of keyed by `id(spec)`, which a
  script looping over videos could reuse (found while testing the ticks: 019 briefly got 016's model).
- **First video:** 017-shower-waterproofing (posts 2026-11-25) for both.
- **Files:** engine/blueprint.py, engine/build.py, engine/audio.py, publish/insights.py, README.md,
  videos/017, 018, 019 specs.

### 2026-11-25 (content): 019 transfer beam
- Elevation along a transfer beam: ghost of the beam and the columns above in step 1, props, deep formwork with a
  DEEP dimension, two layers of bottom bars, ligatures closer near the supports, starter bars, a poker vibrator
  riding the pour front, then the upper columns and floors above; the result traces the load path (down the upper
  columns, sideways through the beam, down the wide columns) over "OPEN SPACE BELOW". 3D: two transfer frames,
  props and forms left out so the finished model shows the columns stopping on the beams.

### 2026-11-24: 3D build replay in the result + perspective-correct 3D depth
- **What:** (1) when the 3D model takes over in the result, it now rebuilds from the ground up in build order,
  each order dropping in one after another over about 2 seconds (30% of the result, 1.4-2.2s), then keeps orbiting
  finished. The section label swaps to "3D  //  START TO FINISH" (it used to keep saying "SECTION ..." over the
  3D shot). `replay_window()` / `replay_appear()` in engine/blueprint.py; opt out per spec with
  `META["replay"] = False`. (2) engine/three_d.py now interpolates depth perspective-correctly (1/z) in the
  z-buffer: big faces used to read too far away mid-face, so parts behind them showed through. Visible fixes:
  017's membrane no longer z-fights through the floor tiles, 015's trusses no longer show through the roof sheets,
  018's mesh stays hidden inside the slab.
- **Why:** review of 016/017 as a phone viewer: the result was the calmest part of the video (a slow orbit of a
  model the viewer had already seen in the hook). A fast start-to-finish rebuild is a timelapse recap of every
  step, a final pattern interrupt, and it ends the loop on the build-up the hook starts from.
- **Checked:** tools/check.py --queue clean (016, 017, 018); before/after result frames of 016 with real timings
  (old: static finished orbit; new: piles, posts, panels row by row, finished) and replay frames of 013, 017,
  018; old specs 001, 008, 011, 013 still build; full local build of 016 (next to post): 61.7s, audio and video
  lengths match, -16.1 LUFS, peak -1.1 dBFS. Before/after covers of 015 and 017 for the depth fix.
- **First video:** 016-noise-wall (posts 2026-11-24) and every video with a 3D model after it. No spec changes.
- **Files:** engine/blueprint.py, engine/three_d.py.

### 2026-11-24 (content): 018 concrete driveway
- Driveway plan inset lined up with the section (the saw cuts drop in on both at the same x), a plate compactor
  pass per base layer, a saw blade cutting each joint, and the result shows the slab shrinking and cracking right
  under the cuts. 3D: garage + driveway, x-ray after the mesh step with the slab still a ghost.

### 2026-11-23: Slow camera drift on the drawing + bigger step text
- **What:** (1) the 2D section now drifts all through the steps: a slow push-in (to 4.5%) over each odd step and a
  pull-back over each even one, centred on the drawing area, back to 1.0 by the result. It's continuous (each step
  starts at the zoom the last one ended on), so there's no jump at the cuts, and the zoomed drawing is clipped inside
  the frame border, under the section label and above the progress ticks. `section_zoom()` / `_section()` in
  engine/blueprint.py; opt out or tune per spec with `META["drift"] = 0` (or e.g. 0.03).
  (2) step body text 32px -> 36px (about 11.5pt -> 13pt on a phone), line pitch 46 -> 50, wrap width 880 -> 890;
  the panel moves up 7px and the title/body gap tightens so three lines still end above the bottom 20%.
- **Why:** review of 015-017 as a phone viewer: between the line-draw animations the drawing sat perfectly still for
  2-4s at a time; a slow push/pull keeps something moving on every frame (a standard retention trick). The body text
  was the smallest text on screen apart from the footnote (Backlog #10).
- **Checked:** tools/check.py --queue clean (015, 016, 017) with the new engine; before/after frames of 015, 016,
  017 at max zoom and at step text (drawing visibly larger by the end of odd steps, hatch edges clipped cleanly at the
  border, body text clearly bigger, no new overlaps or text in the bottom 20%); old specs 001, 011, 013 still build;
  full local builds of 015 (next to post) and 017 with the voice.
- **First video:** 015-roof-trusses (posts 2026-11-23) and every video after it. No spec changes needed.
- **Files:** engine/blueprint.py.

### 2026-11-23 (content): "membrane" 3D material
- `kind="membrane"` (strong blue fill) in engine/three_d.py, so a waterproofing membrane reads at a glance.
  First used by 017-shower-waterproofing, which also has a plan inset (falls, waterstop, membrane, tiles) like 015.

### 2026-11-22: Bigger shared leader labels (24px -> 28px, one engine helper)
- **What:** new `label()` (and `gone()`) in engine/blueprint.py: the leader + typed label on a dark plate that every
  spec since 007 copied locally, now at `LABEL_SIZE = 28` (was 24) with the plate scaling to match. Optional
  `size=` per label. The queued specs (014, 015, 016) dropped their local copies and use it; 001-013 keep their
  own 24px version and build unchanged.
- **Why:** on a phone (1080px video shown ~390pt wide) the 24px labels were about 9pt, the smallest key text on
  screen, and they carry most of what each drawing means. Backlog #2.
- **Checked:** tools/check.py --queue clean after one fix (016 "CONCRETE PILE" grew into the pile, now "CONCRETE");
  before/after phone-size frames of 014, 015, 016 (labels clearly easier to read, no new overlaps); old specs
  001, 006, 011, 013 still build; full build of 014 (next to post).
- **Rule for new specs:** don't define `label()` in the spec; use the engine one. Left-anchored labels at x=110
  now take about 17px per character, so keep them short where the drawing starts near x=300.
- **First video:** 014-curtain-wall (posts 2026-11-22).
- **Files:** engine/blueprint.py, videos/014, 015, 016 specs.

### 2026-11-22 (content): x-ray ground + "precast" 3D material
- 016-noise-wall draws the ground as a thin plate with the piles hanging below it, so the hidden part is the hero
  of the 3D shots. New `kind="precast"` (lighter fill) in engine/three_d.py makes wall panels read as solid.

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
2. **Use the empty top band in every video:** turn the plan insets (015, 017, 018) and the detail boxes (015's bubble,
   020's HEAD DETAIL) into engine helpers (`inset()` frame + caption cycling, `detail_box()`). Impact: medium, more to
   look at during the 2D steps, and less copy-paste in specs.
3. **Faster 3D rendering in the post build:** 015's render took ~9 min on the runner (2 cores); cache the static
   parts' layer between frames or render the 3D at a lower supersample when it's moving fast. Impact: reliability
   (posts land closer to 7:30pm, more headroom).
4. **Judge the caption question after ~5 posts** (017-021): compare comments per post with the 16 before it (3 in
   total; 017 got 0). If no lift, try putting the question as the very first caption line instead. Impact: comments.
5. **On-screen number in the hook** (e.g. "90% OF THIS ROAD IS ROCK") where a safe, general figure exists. Impact: medium.
6. **Infrastructure hooks:** all three infrastructure posts are at the bottom. Next one should be the most relatable
   (a bridge or road people use daily) with a surprise claim, or try a "you drive over this every day" framing.
   Impact: lifts the weakest slot in the rotation.
7. **Save / comment prompt on the end card.** Needs Mathew's OK first: the current content rule is that the end card
   says only "Follow for more". Impact: saves and comments.
8. **Publish retry with a fresh container** for transient Instagram errors (no failures seen yet). Impact: reliability.
9. **"Wrong vs right" / "Spot the defect" format** as a second series. Impact: shares; needs insights first.
10. **Music variety:** a few bed variants (key/tempo per category) so the channel doesn't repeat one loop forever.
    Impact: low-medium; wait for watch-time data to confirm the bed helps.
11. **Run tools/check.py in CI** (preview/post workflows, warning-only at first). Impact: reliability.
12. **Shared `arrow()` / `fill_poly()` helpers** in the engine (every recent spec copies them). Impact: low.
13. **Drift focus on the active part** (optional per-step focus point). Impact: low-medium.
14. **Cache pip wheels in post.yml** (`setup-python` `cache: pip`). Impact: low.
15. **3D materials that read at a glance:** insulation and linings look alike in the blue palette; a hatched or
    dotted face fill for batts would help (020). Impact: low.

## Tried and dropped

(none yet)
