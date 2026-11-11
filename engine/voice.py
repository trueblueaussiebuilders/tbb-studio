"""Voiceover: ElevenLabs when ELEVENLABS_API_KEY + ELEVENLABS_VOICE_ID are set, otherwise Kokoro (free, local)."""
import json, os, subprocess, urllib.request, urllib.error
import numpy as np

SR = 24000
KOKORO_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
KOKORO_DIR = os.environ.get("KOKORO_DIR", os.path.expanduser("~/.cache/kokoro"))


def _decode(data: bytes) -> np.ndarray:
    """Any audio bytes -> mono float32 at SR, via ffmpeg."""
    out = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-f", "f32le", "-ac", "1", "-ar", str(SR), "pipe:1"],
                         input=data, capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32).copy()


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _voice_candidates():
    cfg = json.load(open(os.path.join(ROOT, "voice.json")))
    env = os.environ.get("ELEVENLABS_VOICE_ID", "").strip()
    cands = cfg["elevenlabs_voices"]
    if env and " " not in env and len(env) >= 15:     # a real-looking override wins; placeholder text is ignored
        cands = [{"name": "secret override", "id": env}] + cands
    return cands, cfg.get("model", "eleven_multilingual_v2")


def _tts(key, voice_id, model, line, prev=None, nxt=None):
    body = {"text": line, "model_id": model,
            "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True}}
    if prev: body["previous_text"] = prev      # neighbouring text keeps intonation consistent across lines
    if nxt: body["next_text"] = nxt
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
        data=json.dumps(body).encode(), method="POST",
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return _decode(r.read())


def _elevenlabs(lines):
    key = os.environ["ELEVENLABS_API_KEY"].strip().strip('"').strip("'")
    if " " in key or len(key) < 20:
        raise SystemExit(f"ELEVENLABS_API_KEY secret doesn't look like a real key (length {len(key)}). Paste the key itself.")
    cands, model = _voice_candidates()
    errors = []
    for v in cands:                      # pick the first voice this account can use
        try:
            first = _tts(key, v["id"], model, lines[0], nxt=lines[1] if len(lines) > 1 else None)
            print(f"ElevenLabs voice: {v['name']} ({v['id']})")
            break
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:200]
            errors.append(f"{v['name']}: HTTP {e.code} {msg}")
            if e.code == 401: break      # bad key, no point trying other voices
    else:
        raise SystemExit("No ElevenLabs voice worked:\n  " + "\n  ".join(errors) +
                         "\n(402 'payment_required' means the free plan can't use Voice Library voices via the API.)")
    if errors and "HTTP 401" in errors[-1]:
        raise SystemExit("ElevenLabs rejected the API key (401):\n  " + errors[-1])
    out = [first]
    for i in range(1, len(lines)):
        out.append(_tts(key, v["id"], model, lines[i], prev=lines[i - 1], nxt=lines[i + 1] if i + 1 < len(lines) else None))
    return out


def _kokoro(lines):
    from kokoro_onnx import Kokoro
    os.makedirs(KOKORO_DIR, exist_ok=True)
    for f in ("kokoro-v1.0.onnx", "voices-v1.0.bin"):
        p = os.path.join(KOKORO_DIR, f)
        if not os.path.exists(p):
            print("downloading", f); urllib.request.urlretrieve(KOKORO_URL + f, p)
    k = Kokoro(os.path.join(KOKORO_DIR, "kokoro-v1.0.onnx"), os.path.join(KOKORO_DIR, "voices-v1.0.bin"))
    voice = os.environ.get("KOKORO_VOICE") or _cfg().get("kokoro_voice", "am_michael")
    return [k.create(line, voice=voice, speed=1.05, lang="en-us")[0].astype(np.float32) for line in lines]


def _cfg():
    return json.load(open(os.path.join(ROOT, "voice.json")))


def engine_name():
    """voice.json decides. ElevenLabs is only used when chosen there and a key is set."""
    eng = os.environ.get("VOICE_ENGINE") or _cfg().get("engine", "kokoro")
    if eng == "elevenlabs" and not os.environ.get("ELEVENLABS_API_KEY", "").strip():
        return "kokoro"
    return eng


def _reference_wav():
    """Decrypt the voice reference sample (kept encrypted because the repo is public)."""
    key = os.environ.get("VOICE_KEY", "").strip()
    if not key:
        raise SystemExit("VOICE_KEY secret is missing, so the voice sample can't be unlocked.")
    enc = os.path.join(ROOT, _cfg()["chatterbox"]["reference"])
    out = os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "voice_ref.wav")
    r = subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-iter", "200000", "-in", enc, "-out", out,
                        "-pass", "env:VOICE_KEY"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit("Couldn't decrypt the voice sample. Check the VOICE_KEY secret matches exactly.")
    return out


def _chatterbox(lines):
    import torch
    from chatterbox.tts import ChatterboxTTS
    cfg = _cfg()["chatterbox"]
    torch.set_num_threads(os.cpu_count() or 4)
    model = ChatterboxTTS.from_pretrained(device="cpu")
    if os.environ.get("CHATTERBOX_BUILTIN"):
        print("chatterbox: using the model's built-in voice (test mode)")
    else:
        model.prepare_conditionals(_reference_wav(), exaggeration=cfg["exaggeration"])
    out = []
    for i, line in enumerate(lines):
        torch.manual_seed(cfg.get("seed", 7) + i)
        wav = model.generate(line, exaggeration=cfg["exaggeration"], cfg_weight=cfg["cfg_weight"],
                             temperature=cfg["temperature"])
        a = wav.squeeze(0).detach().cpu().numpy().astype(np.float32)
        if model.sr != SR:   # resample via ffmpeg to the engine's rate
            raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", str(model.sr), "-ac", "1", "-i", "pipe:0",
                                  "-f", "f32le", "-ar", str(SR), "-ac", "1", "pipe:1"], input=a.tobytes(), capture_output=True, check=True).stdout
            a = np.frombuffer(raw, dtype=np.float32).copy()
        print(f"  line {i + 1}/{len(lines)} done")
        out.append(a)
    return out


def synth(lines):
    return {"elevenlabs": _elevenlabs, "chatterbox": _chatterbox}.get(engine_name(), _kokoro)(lines)


def _trim(a, thresh=0.01):
    """Strip leading/trailing silence so timings are tight regardless of engine."""
    idx = np.where(np.abs(a) > thresh)[0]
    if len(idx) == 0: return a
    return a[max(0, idx[0] - int(0.03 * SR)): idx[-1] + int(0.08 * SR)]


LEAD = 0.15   # voice starts this long after each scene starts


def _tempo(a, factor):
    if abs(factor - 1.0) < 1e-3: return a
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "pipe:0",
                          "-af", f"atempo={factor}", "-f", "f32le", "-ar", str(SR), "-ac", "1", "pipe:1"],
                         input=a.astype(np.float32).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def narrate(narration):
    """Returns (timings dict, narration track as float32 array)."""
    keys = ["hook"] + [f"step{i}" for i in range(len(narration["steps"]))] + ["result", "end"]
    lines = [narration["hook"]] + narration["steps"] + [narration["result"], narration["end"]]
    ecfg = _cfg().get(engine_name(), {}) if isinstance(_cfg().get(engine_name()), dict) else {}
    tempo, gap = ecfg.get("tempo", 1.0), ecfg.get("line_gap", 0.3)
    clips = dict(zip(keys, [_tempo(_trim(a), tempo) for a in synth(lines)]))
    L = lambda a: len(a) / SR
    tim = {"hook": round(max(2.8, LEAD + L(clips["hook"]) + gap), 2),
           "steps": [round(max(3.0, LEAD + L(clips[f"step{i}"]) + gap), 2) for i in range(len(narration["steps"]))],
           "result": round(max(3.2, LEAD + L(clips["result"]) + 0.9), 2),
           "end": round(max(2.8, LEAD + L(clips["end"]) + 0.8), 2)}
    durs = [tim["hook"]] + tim["steps"] + [tim["result"], tim["end"]]
    total = sum(durs)
    track = np.zeros(int((total + 0.5) * SR), dtype=np.float32)
    t = 0.0
    for d, k in zip(durs, keys):
        i = int((t + LEAD) * SR); a = clips[k]; track[i:i + len(a)] += a; t += d
    return tim, track[:int(total * SR)]
