"""Oryantasyon videosunu üretir: sahne görselleri (Pillow) + Türkçe seslendirme (edge-tts) + ffmpeg.

Kullanım:  python video/build_video.py
Çıktı:     video/out/oryantasyon.mp4  (+ oryantasyon.srt)
"""
import asyncio
import os
import re
import subprocess
import sys

import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from scenes import SCENES

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")
TMP = os.path.join(OUT, "tmp")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
VOICE = "tr-TR-EmelNeural"
W, H = 1280, 720
PAD = 0.9  # sahne sonu sessizlik (sn)

NAVY, TEAL, GOLD, WHITE, GREY = (11, 28, 51), (0, 168, 150), (255, 190, 60), (245, 248, 252), (150, 170, 195)


def font(size, bold=False):
    for name in (("segoeuib.ttf" if bold else "segoeui.ttf"), ("arialbd.ttf" if bold else "arial.ttf")):
        p = os.path.join("C:/Windows/Fonts", name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise SystemExit("Uygun yazı tipi bulunamadı")


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


def render(idx, scene, total):
    module, title, bullets, _ = scene
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 8], fill=TEAL)
    d.text((60, 36), module, font=font(24, True), fill=TEAL)
    d.text((W - 60, 36), "ECE KALİBRASYON", font=font(24, True), fill=GREY, anchor="ra")

    y = 90
    for ln in wrap(d, title, font(52, True), W - 120):
        d.text((60, y), ln, font=font(52, True), fill=WHITE)
        y += 66
    d.rectangle([60, y + 6, 180, y + 10], fill=GOLD)
    y += 46

    bf = font(34)
    for b in bullets:
        lines = wrap(d, b, bf, W - 190)
        d.ellipse([64, y + 14, 80, y + 30], fill=TEAL)
        for ln in lines:
            d.text((104, y), ln, font=bf, fill=WHITE)
            y += 46
        y += 14

    # ilerleme çubuğu ve avatar
    d.rectangle([0, H - 14, W, H], fill=(25, 45, 75))
    d.rectangle([0, H - 14, int(W * (idx + 1) / total), H], fill=TEAL)
    d.ellipse([W - 130, H - 130, W - 50, H - 50], fill=TEAL)
    d.text((W - 90, H - 90), "M", font=font(44, True), fill=NAVY, anchor="mm")
    d.text((W - 90, H - 40), "Metroli", font=font(20), fill=GREY, anchor="mm")
    d.text((60, H - 50), f"{idx + 1} / {total}", font=font(20), fill=GREY)
    path = os.path.join(TMP, f"s{idx:02d}.png")
    img.save(path)
    return path


def duration(path):
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


def ts(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"


async def synth(i, text):
    path = os.path.join(TMP, f"s{i:02d}.mp3")
    await edge_tts.Communicate(text, VOICE, rate="-5%").save(path)
    return path


def main():
    os.makedirs(TMP, exist_ok=True)
    total = len(SCENES)
    clips, srt, t0 = [], [], 0.0
    for i, sc in enumerate(SCENES):
        png = render(i, sc, total)
        mp3 = asyncio.run(synth(i, sc[3]))
        dur = duration(mp3)
        clip = os.path.join(TMP, f"c{i:02d}.mp4")
        subprocess.run([
            FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-framerate", "25", "-i", png, "-i", mp3,
            "-af", f"apad=pad_dur={PAD}", "-t", f"{dur + PAD:.3f}",
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "44100", "-b:a", "160k", clip,
        ], check=True)
        clips.append(clip)
        # altyazı: cümleleri karakter oranına göre dağıt
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", sc[3]) if s.strip()]
        n = sum(len(s) for s in sents)
        t = t0
        for s in sents:
            seg = dur * len(s) / n
            srt.append((t, t + seg, s))
            t += seg
        t0 += dur + PAD
        print(f"[{i + 1}/{total}] {sc[1]}  ({dur:.1f} sn)")

    lst = os.path.join(TMP, "list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        f.writelines(f"file '{c.replace(os.sep, '/')}'\n" for c in clips)
    srt_path = os.path.join(OUT, "oryantasyon.srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        for n, (a, b, s) in enumerate(srt, 1):
            f.write(f"{n}\n{ts(a)} --> {ts(b)}\n{s}\n\n")
    final = os.path.join(OUT, "oryantasyon.mp4")
    subprocess.run([
        FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", srt_path,
        "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text", "-metadata:s:s:0", "language=tur", final,
    ], check=True)
    print(f"\nTamam: {final}  (toplam {t0 / 60:.1f} dk)")


if __name__ == "__main__":
    main()
