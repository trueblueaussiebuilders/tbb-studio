"""Voiceover: ElevenLabs when ELEVENLABS_API_KEY + ELEVENLABS_VOICE_ID are set, otherwise Kokoro (free, local)."""
import json, os, subprocess, urllib.request
import numpy as np

SR = 24000
KOKORO_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
KOKORO_DIR = os.environ.get("KOKORO_DIR", os.path.expanduser("~/.cache/kokoro"))


def _decode(data: bytes) -> np.ndarray:
    """Any audio bytes -> mono float32 at SR, via ffmpeg."""
    out = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-f", "f32le", "-ac", "1", "-ar", str(SR), "pipe:1"],
                         input=data, capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32).copy()


def _elevenlabs(lines):
    key, voice = os.environ["ELEVENLABS_API_KEY"], os.environ["ELEVENLABS_VOICE_ID"]
    model = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")
    out, prev = [], None
    for i, line in enumerate(lines):
        body = {"text": line, "model_id": model,
                "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True}}
        # neighbouring text keeps intonation consistent across separately generated lines
        if prev: body["previous_text"] = prev
        if i + 1 < len(lines): body["next_text"] = lines[i + 1]
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
            data=json.dumps(body).encode(), method="POST",
            headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
        with urllib.request.urlopen(req, timeout=120) as r:
            out.append(_decode(r.read()))
        prev = line
    return out


def _kokoro(lines):
    from kokoro_onnx import Kokoro
    os.makedirs(KOKORO_DIR, exist_ok=True)
    for f in ("kokoro-v1.0.onnx", "voices-v1.0.bin"):
        p = os.path.join(KOKORO_DIR, f)
        if not os.path.exists(p):
            print("downloading", f); urllib.request.urlretrieve(KOKORO_URL + f, p)
    k = Kokoro(os.path.join(KOKORO_DIR, "kokoro-v1.0.onnx"), os.path.join(KOKORO_DIR, "voices-v1.0.bin"))
    voice = os.environ.get("KOKORO_VOICE", "am_michael")
    return [k.create(line, voice=voice, speed=1.05, lang="en-us")[0].astype(np.float32) for line in lines]


def engine_name():
    return "elevenlabs" if os.environ.get("ELEVENLABS_API_KEY") and os.environ.get("ELEVENLABS_VOICE_ID") else "kokoro"


def synth(lines):
    return _elevenlabs(lines) if engine_name() == "elevenlabs" else _kokoro(lines)


def _trim(a, thresh=0.01):
    """Strip leading/trailing silence so timings are tight regardless of engine."""
    idx = np.where(np.abs(a) > thresh)[0]
    if len(idx) == 0: return a
    return a[max(0, idx[0] - int(0.03 * SR)): idx[-1] + int(0.08 * SR)]


LEAD = 0.15   # voice starts this long after each scene starts


def narrate(narration):
    """Returns (timings dict, narration track as float32 array)."""
    keys = ["hook"] + [f"step{i}" for i in range(len(narration["steps"]))] + ["result", "end"]
    lines = [narration["hook"]] + narration["steps"] + [narration["result"], narration["end"]]
    clips = dict(zip(keys, [_trim(a) for a in synth(lines)]))
    L = lambda a: len(a) / SR
    tim = {"hook": round(max(2.8, LEAD + L(clips["hook"]) + 0.3), 2),
           "steps": [round(max(3.0, LEAD + L(clips[f"step{i}"]) + 0.3), 2) for i in range(len(narration["steps"]))],
           "result": round(max(3.2, LEAD + L(clips["result"]) + 0.9), 2),
           "end": round(max(2.8, LEAD + L(clips["end"]) + 0.8), 2)}
    durs = [tim["hook"]] + tim["steps"] + [tim["result"], tim["end"]]
    total = sum(durs)
    track = np.zeros(int((total + 0.5) * SR), dtype=np.float32)
    t = 0.0
    for d, k in zip(durs, keys):
        i = int((t + LEAD) * SR); a = clips[k]; track[i:i + len(a)] += a; t += d
    return tim, track[:int(total * SR)]
