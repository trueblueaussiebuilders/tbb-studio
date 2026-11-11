"""Build one video: voiceover -> timings -> scenes -> mp4 (+ caption).

  python -m engine.build videos/001-waffle-pod-slab --out out
  python -m engine.build videos/001-waffle-pod-slab --frames 10 25.5   # PNG test frames only
"""
import argparse, importlib.util, json, multiprocessing as mp, os, subprocess, sys, tempfile
import numpy as np, soundfile as sf
from engine import blueprint as bp
from engine import voice

SPEC = TL = None


def load_spec(folder):
    path = os.path.join(folder, "spec.py")
    s = importlib.util.spec_from_file_location("video_spec", path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def _render_scene(args):
    idx, outdir = args
    t0, t1 = TL.scenes[idx]
    f0, f1 = round(t0 * bp.FPS), round(t1 * bp.FPS)
    tmp, final = f"{outdir}/scene_{idx:02d}.tmp.mp4", f"{outdir}/scene_{idx:02d}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", f"{bp.W}x{bp.H}",
           "-r", str(bp.FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        s = bp.draw_frame(SPEC, TL, f / bp.FPS); s.flush(); p.stdin.write(bytes(s.get_data()))
    p.stdin.close()
    if p.wait() != 0: raise RuntimeError(f"scene {idx} failed")
    os.replace(tmp, final)
    return final


def write_cover(outdir, slug):
    png = os.path.join(outdir, f"{slug}.cover.png")
    bp.draw_cover(SPEC, TL).write_to_png(png)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", png, "-q:v", "2", png[:-4] + ".jpg"], check=True)
    os.remove(png)


def main():
    global SPEC, TL
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--out", default="out")
    ap.add_argument("--frames", nargs="*", type=float)
    ap.add_argument("--caption-only", action="store_true")
    a = ap.parse_args()
    SPEC = load_spec(a.folder)
    slug = os.path.basename(os.path.normpath(a.folder))
    os.makedirs(a.out, exist_ok=True)
    if a.caption_only:
        print(SPEC.CAPTION); return

    tim_path = os.path.join(a.out, f"{slug}.timings.json")
    if a.frames is not None:   # quick look without voice: reuse timings if present
        tim = json.load(open(tim_path)) if os.path.exists(tim_path) else \
            {"hook": 3.5, "steps": [4.0] * len(SPEC.META["steps"]), "result": 6.0, "end": 4.0}
        TL = bp.Timeline(tim)
        for t in a.frames:
            bp.draw_frame(SPEC, TL, t).write_to_png(os.path.join(a.out, f"{slug}_t{t}.png"))
        bp.draw_cover(SPEC, TL).write_to_png(os.path.join(a.out, f"{slug}_cover.png"))
        return

    print(f"[{slug}] voice: {voice.engine_name()}")
    tim, track = voice.narrate(SPEC.NARRATION)
    json.dump(tim, open(tim_path, "w"))
    TL = bp.Timeline(tim)
    print(f"[{slug}] duration {TL.duration:.1f}s, {len(TL.scenes)} scenes")

    with tempfile.TemporaryDirectory() as tmp:
        sf.write(f"{tmp}/voice.wav", track, voice.SR)
        with mp.get_context("fork").Pool(os.cpu_count() or 2) as pool:
            files = pool.map(_render_scene, [(i, tmp) for i in range(len(TL.scenes))])
        with open(f"{tmp}/list.txt", "w") as f:
            f.writelines(f"file '{x}'\n" for x in files)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt",
                        "-c", "copy", f"{tmp}/video.mp4"], check=True)
        final = os.path.join(a.out, f"{slug}.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{tmp}/video.mp4", "-i", f"{tmp}/voice.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-af", "highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "128k",
                        "-shortest", "-movflags", "+faststart", final + ".tmp.mp4"], check=True)
        os.replace(final + ".tmp.mp4", final)
    open(os.path.join(a.out, f"{slug}.caption.txt"), "w").write(SPEC.CAPTION)
    write_cover(a.out, slug)
    print(f"[{slug}] -> {final}")


if __name__ == "__main__":
    main()
