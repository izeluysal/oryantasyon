"""Tek seferlik araç: her eğitim ekranı için sesli, animasyonlu slayt videosu (mp4) ve poster (jpg) üretir.

Kullanım (Pillow ve imageio-ffmpeg kurulu bir Python ile; uygulama bağımlılığı değildir):
    python test/build_training_videos.py [--only 3,5]

Girdi: test/legacy_program/content.js (ekran içeriği), static/audio/*.mp3 (seslendirme).
Çıktı: static/video/sNN.mp4, sNN.jpg ve static/video/oryantasyon.mp4 (tüm ekranların birleşimi).
Maddeler seslendirme boyunca sırayla belirir; altyazı cümleler değiştikçe güncellenir.
"""
import json
import os
import re
import subprocess
import sys

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(ROOT, "static", "audio")
VIDEO_DIR = os.path.join(ROOT, "static", "video")
TMP_DIR = os.path.join(ROOT, "test", "legacy_video", "out", "frames")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ICON_FONT = os.path.join(ROOT, "static", "vendor", "bootstrap-icons", "fonts", "bootstrap-icons.woff")
W, H = 1280, 720
TAIL = 1.0

TOP, BOTTOM = (8, 25, 48), (6, 70, 82)
TEAL, GOLD, WHITE, MUTED = (0, 190, 170), (255, 196, 64), (246, 249, 252), (160, 185, 205)
CARD = (255, 255, 255)

# Ekran sırasına göre ikon (Bootstrap Icons adı) ve yerleşim ("cards" ya da "flow").
ICONS = ["patch-check", "shield-check", "award", "shield-lock", "sliders", "diagram-3", "rulers", "bar-chart",
         "file-earmark-text", "check2-square", "buildings", "signpost-split", "truck", "tools", "people",
         "chat-dots", "chat-left-text", "calendar-check", "cone-striped", "clipboard-check",
         "exclamation-triangle", "mortarboard", "book", "trophy"]
FLOW_SCREENS = {5, 11, 21, 19}


def load_font(path, size):
    """Yazı tipini yükler."""
    return ImageFont.truetype(path, size)


def text_font(size, bold=False):
    """Türkçe karakterli Segoe UI (yoksa Arial) yazı tipi."""
    for name in (("segoeuib.ttf" if bold else "segoeui.ttf"), ("arialbd.ttf" if bold else "arial.ttf")):
        path = os.path.join("C:/Windows/Fonts", name)
        if os.path.exists(path):
            return load_font(path, size)
    raise SystemExit("Yazı tipi bulunamadı")


def icon_codes():
    """Bootstrap Icons CSS'inden ikon adı -> karakter kodu eşlemesi."""
    css_path = os.path.join(ROOT, "static", "vendor", "bootstrap-icons", "bootstrap-icons.css")
    with open(css_path, encoding="utf-8") as css_file:
        css = css_file.read()
    pattern = re.compile(r'\.bi-([a-z0-9-]+)::before\{content:"\\([0-9a-f]+)"')
    return {name: int(code, 16) for name, code in pattern.findall(css)}


def gradient():
    """Dikey degrade arka plan."""
    image = Image.new("RGB", (W, H), TOP)
    draw = ImageDraw.Draw(image)
    for y in range(H):
        ratio = y / H
        draw.line([(0, y), (W, y)], fill=tuple(int(TOP[i] + (BOTTOM[i] - TOP[i]) * ratio) for i in range(3)))
    return image


def wrap(draw, text, font, width):
    """Metni verilen piksel genişliğine göre satırlara böler."""
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    return lines + [current]


def draw_icon(draw, codes, name, center, size, color):
    """Ortalanmış Bootstrap Icons simgesi çizer."""
    font = load_font(ICON_FONT, size)
    draw.text(center, chr(codes.get(name, codes["circle"])), font=font, fill=color, anchor="mm")


def render(scene, index, total, visible, sentence, codes, base):
    """Tek kareyi çizer: başlık, görünen maddeler ve altyazı."""
    module, title, bullets, _ = scene
    image = base.copy()
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle([0, 0, W, 8], fill=TEAL)
    draw.text((60, 30), module, font=text_font(22, True), fill=TEAL)
    draw.text((W - 60, 30), "ECE KALİBRASYON · ORYANTASYON", font=text_font(20, True), fill=MUTED, anchor="ra")

    # Sol panel: büyük ikon ve Metroli
    draw.rounded_rectangle([60, 130, 330, 400], radius=36, fill=(255, 255, 255, 28), outline=(255, 255, 255, 70), width=2)
    draw_icon(draw, codes, ICONS[index % len(ICONS)], (195, 265), 150, GOLD)
    draw.ellipse([60, 425, 130, 495], fill=TEAL)
    draw.text((95, 460), "M", font=text_font(40, True), fill=TOP, anchor="mm")
    draw.text((145, 460), "Metroli", font=text_font(26, True), fill=WHITE, anchor="lm")

    # Başlık
    x0 = 380
    y = 105
    for line in wrap(draw, title, text_font(44, True), W - x0 - 60)[:2]:
        draw.text((x0, y), line, font=text_font(44, True), fill=WHITE)
        y += 54
    draw.rectangle([x0, y + 8, x0 + 90, y + 12], fill=GOLD)
    y += 28

    # Maddeler: en fazla dört kart; "flow" yerleşiminde aralarında ok vardır.
    flow = index in FLOW_SCREENS
    available = 560 - y
    gap = 30 if flow else 14
    card_h = min(104, (available - gap * (len(bullets) - 1)) // max(len(bullets), 1))
    body_font = text_font(27)
    for number, bullet in enumerate(bullets[:visible]):
        top = y + number * (card_h + gap)
        draw.rounded_rectangle([x0, top, W - 60, top + card_h], radius=18, fill=(255, 255, 255, 235))
        draw.ellipse([x0 + 16, top + card_h // 2 - 22, x0 + 60, top + card_h // 2 + 22], fill=TEAL)
        draw.text((x0 + 38, top + card_h // 2), str(number + 1), font=text_font(26, True), fill=WHITE, anchor="mm")
        lines = wrap(draw, bullet, body_font, W - x0 - 60 - 90)
        line_h = 34
        text_top = top + (card_h - line_h * len(lines[:2])) // 2
        for position, line in enumerate(lines[:2]):
            draw.text((x0 + 80, text_top + position * line_h), line, font=body_font, fill=TOP)
        if flow and number < len(bullets) - 1 and number + 1 < visible + 1:
            draw_icon(draw, codes, "arrow-down", (x0 + 38, top + card_h + gap // 2), 24, GOLD)

    # Altyazı çubuğu
    cap_font = text_font(25)
    lines = wrap(draw, sentence, cap_font, W - 160) if sentence else []
    if lines:
        bar_h = 22 + 33 * len(lines)
        draw.rectangle([0, H - bar_h - 20, W, H], fill=(0, 0, 0, 170))
        for position, line in enumerate(lines):
            draw.text((W // 2, H - bar_h - 8 + 33 * position + 16), line, font=cap_font, fill=WHITE, anchor="mm")
    # İlerleme çubuğu
    draw.rectangle([0, H - 8, W, H], fill=(255, 255, 255, 40))
    draw.rectangle([0, H - 8, int(W * (index + 1) / total), H], fill=TEAL)
    return image.convert("RGB")


def duration_of(path):
    """Ses dosyasının süresini saniye olarak döndürür."""
    result = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True, encoding="utf-8", errors="replace")
    match = re.search(r"Duration: (\d+):(\d+):([\d.]+)", result.stderr)
    return int(match[1]) * 3600 + int(match[2]) * 60 + float(match[3])


def timeline(scene, duration):
    """Zaman çizelgesi: (başlangıç, görünen madde sayısı, cümle) aralıkları üretir."""
    voice = scene[3]
    bullets = scene[2][:4]
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", voice) if s.strip()]
    total_chars = sum(len(s) for s in sentences)
    sentence_starts, cursor = [], 0.0
    for sentence in sentences:
        sentence_starts.append(cursor)
        cursor += duration * len(sentence) / total_chars
    bullet_starts = [0.5 + i * (duration * 0.75 / max(len(bullets), 1)) for i in range(len(bullets))]
    points = sorted(set([0.0] + sentence_starts + bullet_starts))
    result = []
    for start in points:
        visible = sum(1 for b in bullet_starts if b <= start + 1e-6)
        current = max(i for i, s in enumerate(sentence_starts) if s <= start + 1e-6)
        result.append((start, visible, sentences[current]))
    return result


def build_scene(scene, index, total, codes, base):
    """Bir ekranın videosunu ve posterini üretir."""
    audio = os.path.join(AUDIO_DIR, "s{:02d}.mp3".format(index))
    duration = duration_of(audio)
    events = timeline(scene, duration)
    os.makedirs(TMP_DIR, exist_ok=True)
    listing = []
    last_frame = None
    for number, (start, visible, sentence) in enumerate(events):
        end = events[number + 1][0] if number + 1 < len(events) else duration + TAIL
        frame = render(scene, index, total, visible, sentence, codes, base)
        path = os.path.join(TMP_DIR, "s{:02d}_{:03d}.png".format(index, number))
        frame.save(path)
        listing.append("file '{}'\nduration {:.3f}".format(path.replace("\\", "/"), max(end - start, 0.04)))
        last_frame = frame
    listing.append("file '{}'".format(path.replace("\\", "/")))
    list_path = os.path.join(TMP_DIR, "s{:02d}.txt".format(index))
    with open(list_path, "w", encoding="utf-8") as list_file:
        list_file.write("\n".join(listing) + "\n")
    output = os.path.join(VIDEO_DIR, "s{:02d}.mp4".format(index))
    subprocess.run([
        FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", list_path, "-i", audio,
        "-vf", "fps=25,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "64k", "-ac", "1", "-af", "apad=pad_dur={}".format(TAIL), "-t", "{:.3f}".format(duration + TAIL),
        "-movflags", "+faststart", output], check=True)
    # Poster: tüm maddelerin göründüğü, altyazısız kare.
    render(scene, index, total, len(scene[2][:4]), "", codes, base).save(
        os.path.join(VIDEO_DIR, "s{:02d}.jpg".format(index)), quality=82)
    for name in os.listdir(TMP_DIR):
        if name.startswith("s{:02d}".format(index)):
            os.remove(os.path.join(TMP_DIR, name))
    return output, duration + TAIL


def main():
    """Tüm (veya --only ile seçilen) ekranların videosunu üretir ve birleşik videoyu hazırlar."""
    sys.path.insert(0, os.path.join(ROOT, "test", "legacy_video"))
    from scenes import SCENES

    only = None
    if "--only" in sys.argv:
        only = {int(n) for n in sys.argv[sys.argv.index("--only") + 1].split(",")}
    os.makedirs(VIDEO_DIR, exist_ok=True)
    codes = icon_codes()
    base = gradient()
    outputs, total_seconds = [], 0.0
    for index, scene in enumerate(SCENES):
        if only is None or index in only:
            output, seconds = build_scene(scene, index, len(SCENES), codes, base)
            print("{:2d} {:5.1f} sn  {}".format(index, seconds, scene[1].encode("ascii", "replace").decode()))
        else:
            output, seconds = os.path.join(VIDEO_DIR, "s{:02d}.mp4".format(index)), 0.0
        outputs.append(output)
        total_seconds += seconds
    if only is None:
        list_path = os.path.join(TMP_DIR, "all.txt")
        with open(list_path, "w", encoding="utf-8") as list_file:
            list_file.write("".join("file '{}'\n".format(p.replace("\\", "/")) for p in outputs))
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy",
                        "-movflags", "+faststart", os.path.join(VIDEO_DIR, "oryantasyon.mp4")], check=True)
        print("toplam: {:.1f} dk".format(total_seconds / 60))


if __name__ == "__main__":
    main()
