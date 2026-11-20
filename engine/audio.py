"""Music bed + sound effects, synthesised in numpy (no samples, no licensing risk).

mix(voice_track, tim, spec) returns the final narration track with:
  * a soft music bed: warm additive pad chords (vi-IV-I-V), a plucked arpeggio, and from step 1 a soft kick
    on every beat. It's ducked under the voice (about -20 dB when speaking) and fades out over the end card.
  * light sound effects on what the viewer sees change: a thump when the hook punchline pops in, a soft
    whoosh at each new step, a shimmer when the 3D x-ray interlude opens, a two-note chime on the end card.

Opt out per video with META["music"] = False (or META["sfx"] = False for effects only).
Everything is deterministic, so a rebuild sounds the same.
"""
import numpy as np

BPM = 96
BEAT = 60.0 / BPM
BAR = 4 * BEAT
# vi - IV - I - V in C major (MIDI notes): bass, then three chord tones
CHORDS = [(45, 57, 60, 64), (41, 53, 57, 60), (48, 55, 60, 64), (43, 55, 59, 62)]

BED_DB_OPEN = -14.0      # bed level relative to the voice's speaking RMS, between lines
BED_DB_DUCK = -21.0      # ... and while the voice is speaking
SFX_DB = -12.0           # effects relative to the voice RMS


def _hz(m): return 440.0 * 2 ** ((m - 69) / 12.0)


def _db(x): return 10 ** (x / 20.0)


def _env(n, sr, attack, release):
    """Linear attack, hold, linear release over n samples."""
    e = np.ones(n, np.float32)
    a, r = min(int(attack * sr), n // 2), min(int(release * sr), n // 2)
    if a: e[:a] = np.linspace(0, 1, a, dtype=np.float32)
    if r: e[n - r:] = np.linspace(1, 0, r, dtype=np.float32)
    return e


def _add(buf, i0, x):
    if i0 >= len(buf): return
    i0 = max(0, i0)
    x = x[:len(buf) - i0]
    buf[i0:i0 + len(x)] += x


def _pad_note(f, dur, sr):
    """Soft pad voice: a few sine partials, two slightly detuned copies for width."""
    n = int(dur * sr); t = np.arange(n, dtype=np.float32) / sr
    out = np.zeros(n, np.float32)
    for det in (-0.003, 0.003):
        for k, amp in ((1, 1.0), (2, 0.35), (3, 0.12), (4, 0.05)):
            fk = f * k * (1 + det)
            if fk > sr * 0.45: break
            out += amp * np.sin(2 * np.pi * fk * t + k * 0.7)
    return out * _env(n, sr, 0.5, 0.8) * 0.5


def _pluck(f, sr, dur=0.55):
    n = int(dur * sr); t = np.arange(n, dtype=np.float32) / sr
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.08)
    return (x * np.exp(-t / 0.16) * _env(n, sr, 0.004, 0.05)).astype(np.float32)


def _kick(sr, dur=0.3):
    n = int(dur * sr); t = np.arange(n, dtype=np.float32) / sr
    f = 58 + 80 * np.exp(-t / 0.03)
    ph = 2 * np.pi * np.cumsum(f) / sr
    return (np.sin(ph) * np.exp(-t / 0.09) * _env(n, sr, 0.002, 0.03)).astype(np.float32)


def _noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n).astype(np.float32)


def _smooth(x, sr, secs):
    """Moving average (centred) via cumsum: vectorised low-pass for envelopes and noise colour."""
    w = max(1, int(secs * sr))
    c = np.cumsum(np.concatenate([np.zeros(w, np.float32), x, np.zeros(w, np.float32)]))
    y = (c[w:] - c[:-w]) / w
    return y[w // 2: w // 2 + len(x)].astype(np.float32)


def _whoosh(sr, dur=0.45, seed=1):
    n = int(dur * sr); t = np.arange(n, dtype=np.float32) / sr
    x = _noise(n, seed)
    x = x - _smooth(x, sr, 0.0008)                      # high-pass-ish: airy, not rumbly
    x = _smooth(x, sr, 0.00012)                         # take the harsh top off
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return (x * e * 0.6).astype(np.float32)


def _thump(sr):
    n = int(0.35 * sr); t = np.arange(n, dtype=np.float32) / sr
    f = 65 + 90 * np.exp(-t / 0.025)
    body = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t / 0.11)
    click = _noise(n, 7) * np.exp(-t / 0.006) * 0.25
    return ((body + click) * _env(n, sr, 0.001, 0.04)).astype(np.float32)


def _shimmer(sr, dur=1.0):
    n = int(dur * sr); t = np.arange(n, dtype=np.float32) / sr
    out = np.zeros(n, np.float32)
    for k, m in enumerate((72, 76, 79, 84)):            # C major arpeggio up, fast
        st = int(k * 0.07 * sr)
        tt = t[:n - st]
        out[st:] += np.sin(2 * np.pi * _hz(m) * tt) * np.exp(-tt / 0.35) * 0.5
    return out * _env(n, sr, 0.005, 0.2)


def _chime(sr):
    n = int(1.6 * sr); t = np.arange(n, dtype=np.float32) / sr
    out = np.zeros(n, np.float32)
    for st, m in ((0.0, 76), (0.18, 84)):
        s = int(st * sr); tt = t[:n - s]
        out[s:] += (np.sin(2 * np.pi * _hz(m) * tt) + 0.2 * np.sin(2 * np.pi * _hz(m) * 3 * tt) * np.exp(-tt / 0.1)) \
            * np.exp(-tt / 0.5)
    return out * _env(n, sr, 0.003, 0.3) * 0.6


def _rms(x):
    return float(np.sqrt(np.mean(x.astype(np.float64) ** 2))) if len(x) else 0.0


def bed(n, sr, tim):
    """Music bed for a track of n samples. Energy steps up when the build starts (step 1)."""
    total = n / sr
    s1 = tim["hook"]
    end0 = total - tim["end"]
    pad = np.zeros(n, np.float32); arp = np.zeros(n, np.float32); kick = np.zeros(n, np.float32)
    bars = int(np.ceil(total / BAR)) + 1
    for b in range(bars):
        t0 = b * BAR
        ch = CHORDS[b % len(CHORDS)]
        for m in ch[1:]:
            _add(pad, int(t0 * sr), _pad_note(_hz(m), BAR + 0.6, sr) * 0.33)
        _add(pad, int(t0 * sr), _pad_note(_hz(ch[0]), BAR + 0.6, sr) * 0.45)         # bass
        pattern = (ch[1], ch[2], ch[3], ch[2] + 12, ch[3], ch[2], ch[1] + 12, ch[3])
        for k, m in enumerate(pattern):                                              # 8th-note pluck arpeggio
            tk = t0 + k * BEAT / 2
            if tk >= total: break
            _add(arp, int(tk * sr), _pluck(_hz(m + 12), sr) * (0.5 if k % 2 else 0.7))
        for k in range(4):                                                           # kick on every beat from step 1
            tk = t0 + k * BEAT
            if s1 - 0.05 <= tk < end0:
                _add(kick, int(tk * sr), _kick(sr) * (1.0 if k % 2 == 0 else 0.7))
    t = np.arange(n, dtype=np.float32) / sr
    arp_gain = np.clip((t - 0.2) / 1.0, 0, 1) * 0.55                               # arp comes in under the hook
    out = pad * 0.9 + arp * arp_gain + kick * 0.9
    fade = np.clip((total - t) / max(tim["end"], 1.0), 0, 1) ** 1.5                 # fade over the end card
    fade *= np.clip(t / 0.08, 0, 1)
    return (out * fade).astype(np.float32)


def sfx(n, sr, tim, spec):
    """Effects on what changes on screen. Positions match engine/blueprint.py's animation timing."""
    from engine import blueprint as bp
    out = np.zeros(n, np.float32)
    M = spec.META
    last = len(M["hook"]) - 1
    _add(out, int((0.15 + (last - 1) * 0.3 + 0.15) * sr), _thump(sr) * 0.9)          # hook punchline pop
    tl = bp.Timeline(tim)
    for i in range(1, tl.n + 1):                                                       # new step
        _add(out, int((tl.step_start(i) - 0.3) * sr), _whoosh(sr, seed=i) * 0.55)     # peaks on the cut
    _add(out, int((tl.res0 - 0.4) * sr), _whoosh(sr, 0.6, seed=99) * 0.65)          # the result
    if hasattr(spec, "model3d"):
        w = bp.xray_window(spec, tl)
        if w: _add(out, int(w[0] * sr), _shimmer(sr) * 0.5)                           # x-ray interlude opens
    _add(out, int((tl.end0 + 0.45) * sr), _chime(sr) * 0.7)                            # end card
    return out


def duck_gain(voice, sr):
    """0 where the voice is silent, 1 where it's speaking; fast attack, slow release, with lookahead."""
    env = np.sqrt(_smooth(voice.astype(np.float32) ** 2, sr, 0.05))
    thr = max(_rms(voice) * 0.25, 1e-4)
    on = np.clip(env / thr, 0, 1)
    on = np.maximum(on, np.concatenate([on[int(0.08 * sr):], np.zeros(int(0.08 * sr), np.float32)]))  # lookahead
    return _smooth(on, sr, 0.25)


def mix(voice, sr, tim, spec):
    """voice: float32 narration track. Returns voice + ducked bed + sfx, peak-safe."""
    M = getattr(spec, "META", {})
    if M.get("music", True) is False and M.get("sfx", True) is False:
        return voice
    n = len(voice)
    active = voice[np.abs(voice) > 0.01]
    vr = _rms(active) if len(active) else 0.1
    out = voice.astype(np.float32).copy()
    if M.get("music", True) is not False:
        b = bed(n, sr, tim)
        b *= vr / max(_rms(b), 1e-6)                                          # bed RMS == voice RMS ...
        d = duck_gain(voice, sr)
        g = _db(BED_DB_OPEN) + (_db(BED_DB_DUCK) - _db(BED_DB_OPEN)) * d     # ... then ducked to these levels
        out += b * g
    if M.get("sfx", True) is not False:
        s = sfx(n, sr, tim, spec)
        out += s * (vr / max(np.max(np.abs(s)), 1e-6)) * _db(SFX_DB) * 3.0   # effect peaks ~ -2.5 dB re voice RMS x3
    peak = np.max(np.abs(out))
    if peak > 0.98: out *= 0.98 / peak
    return out.astype(np.float32)
