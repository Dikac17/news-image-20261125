#!/usr/bin/env python3
"""THE WORLD — 25 November 2026. One-image newspaper summary of the day's world news.

Deterministic: draws everything with PIL from fixed data, no network, no random
numbers, no timestamps. Two runs produce byte-identical PNG output.

Run:  python3 main.py        (writes /output/entry.png, 1024x1024, <= 1 MiB)
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "/output/entry.png"

INK = (17, 17, 17)
PAPER = (248, 244, 234)
FAINT = (90, 84, 74)
RED = (164, 30, 34)
SKY = (43, 58, 74)
SKY2 = (58, 74, 94)
ORANGE = (217, 123, 41)
GOLD = (201, 162, 39)
LIGHT = (232, 226, 212)
RULE = (17, 17, 17)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    """Greedy word wrap by pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, f, max_w, leading, fill=INK):
    """Draw wrapped paragraph; returns y after last line."""
    for line in wrap(d, text, f, max_w):
        d.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def fit_line(d, text, path, size, max_w):
    """Largest font size <= `size` whose rendered width fits max_w."""
    s = size
    while s > 18:
        f = font(path, s)
        if d.textlength(text, font=f) <= max_w:
            return f
        s -= 1
    return font(path, 18)


def kicker(d, x, y, text, color=RED):
    f = font(SANS_B, 15)
    d.rectangle([x, y + 2, x + 8, y + 16], fill=color)
    d.text((x + 14, y), text.upper(), font=f, fill=color)
    return y + 22


def rule(d, x0, y, x1, w=2):
    d.line([(x0, y), (x1, y)], fill=RULE, width=w)


def draw_tower_scene(d, x, y, w, h):
    """Riyadh skyline at dusk: Kingdom Centre tower, missile streaks, smoke."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    for sx, sy, r in [(18, 14, 2), (52, 30, 1), (96, 10, 2), (150, 26, 1),
                      (210, 12, 2), (260, 34, 1), (310, 16, 2), (350, 28, 1)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(230, 225, 200))
    base = y + h - 26
    for bx, bw, bh in [(0, 34, 52), (40, 26, 70), (72, 30, 44), (300, 36, 58),
                       (340, 24, 40)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(30, 40, 52))
        for wy in range(base - bh + 8, base - 6, 12):
            d.rectangle([x + bx + 6, wy, x + bx + 10, wy + 5], fill=(232, 190, 90))
    tx, tw = x + 118, 96
    d.polygon([(tx, base), (tx, y + 42), (tx + tw, y + 42), (tx + tw, base)],
              fill=(16, 22, 30))
    d.polygon([(tx + 6, base), (tx + 6, y + 52), (tx + tw - 6, y + 52),
               (tx + tw - 6, base)], fill=(24, 32, 44))
    ax0, ax1, ay = tx + 22, tx + tw - 22, y + 46
    d.polygon([(ax0, ay + 34), (ax0, ay + 2), (ax1, ay + 2), (ax1, ay + 34),
               (ax1 - 8, ay + 34), (ax1 - 8, ay + 16), (ax0 + 8, ay + 16),
               (ax0 + 8, ay + 34)], fill=SKY)
    for wy in range(y + 62, base - 8, 14):
        d.rectangle([tx + 12, wy, tx + 18, wy + 7], fill=(232, 190, 90))
        d.rectangle([tx + tw - 18, wy, tx + tw - 12, wy + 7], fill=(232, 190, 90))
    d.line([(x + 250, y + 30), (x + 196, y + 78)], fill=ORANGE, width=3)
    d.line([(x + 330, y + 18), (x + 288, y + 66)], fill=(240, 200, 120), width=2)
    cx, cy = x + 196, y + 82
    for r, col in [(26, ORANGE), (18, (240, 160, 60)), (10, (250, 220, 130))]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    for sx, sy, r in [(150, 108, 16), (176, 96, 20), (206, 106, 14)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(120, 116, 108))
    d.rectangle([x, base, x + w, y + h], fill=(20, 18, 16))
    d.text((x + 10, y + h - 22), "RIYADH AT DUSK: THE KINGDOM CENTRE TOWER",
           font=font(SANS_B, 11), fill=(220, 214, 196))


def draw_bars(d, x, y, w, h):
    """14 bars: the 14 economies facing new US tariffs."""
    d.rectangle([x, y, x + w, y + h], fill=LIGHT)
    n = 14
    bw = (w - 16) // n
    vals = [0.42, 0.55, 0.38, 0.72, 0.61, 0.48, 0.80, 0.35, 0.58, 0.66,
            0.44, 0.52, 0.76, 0.40]
    for i, v in enumerate(vals):
        bx = x + 8 + i * bw
        bh = int((h - 34) * v)
        col = RED if i in (3, 6, 12) else INK
        d.rectangle([bx + 1, y + h - 22 - bh, bx + bw - 2, y + h - 22], fill=col)
    d.text((x + 8, y + h - 18), "14 ECONOMIES  •  US TARIFF PROBE",
           font=font(SANS_B, 11), fill=INK)


def draw_rocket(d, x, y, w, h):
    """Shenzhou-24 launch: rocket, flame, moon, stars, Tiangong arc. Fills panel."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 34))
    # moon, top left
    d.ellipse([x + 14, y + 8, x + 52, y + 46], fill=(232, 228, 210))
    d.ellipse([x + 24, y + 18, x + 32, y + 26], fill=(205, 200, 182))
    d.ellipse([x + 36, y + 28, x + 42, y + 34], fill=(205, 200, 182))
    for sx, sy, r in [(80, 14, 2), (120, 30, 1), (200, 12, 2), (250, 26, 1),
                      (290, 16, 2), (70, 52, 1), (290, 54, 1), (230, 48, 2)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(235, 230, 210))
    # rocket, scaled to fill the panel height (design space 40 wide x 190 tall)
    s = h / 190.0
    cx = x + w // 2
    top = y + 2
    ry = lambda v: top + v * s
    rx = lambda v: cx + v * s
    d.polygon([(rx(-9), ry(128)), (cx, ry(186)), (rx(9), ry(128))], fill=ORANGE)
    d.polygon([(rx(-5), ry(128)), (cx, ry(168)), (rx(5), ry(128))], fill=(250, 220, 130))
    d.rounded_rectangle([rx(-11), ry(34), rx(11), ry(130)], radius=3,
                        fill=(240, 238, 230))
    d.polygon([(rx(-11), ry(34)), (cx, ry(8)), (rx(11), ry(34))], fill=RED)
    d.rectangle([rx(-11), ry(78), rx(11), ry(92)], fill=RED)
    d.polygon([(rx(-11), ry(104)), (rx(-23), ry(132)), (rx(-11), ry(132))], fill=RED)
    d.polygon([(rx(11), ry(104)), (rx(23), ry(132)), (rx(11), ry(132))], fill=RED)
    d.ellipse([rx(-5), ry(46), rx(5), ry(62)], outline=INK, width=2)
    # Tiangong station, right side
    d.arc([x + w - 92, y + 10, x + w - 12, y + 50], start=200, end=340,
          fill=GOLD, width=3)
    d.rectangle([x + w - 58, y + 22, x + w - 30, y + 30], fill=GOLD)
    d.rectangle([x + w - 44, y + 30, x + w - 36, y + 44], fill=GOLD)


def draw_gavel(d, x, y, w, h):
    """Courtroom gavel + GUILTY stamp for the Huawei verdict. Wide-short panel:
    big stamp on the left, gavel on the right."""
    d.rectangle([x, y, x + w, y + h], fill=LIGHT)
    # GUILTY stamp, left
    d.rectangle([x + 10, y + 14, x + 138, y + 56], outline=RED, width=3)
    d.text((x + 20, y + 20), "GUILTY", font=font(SANS_B, 28), fill=RED)
    # gavel, right: handle diagonal, head horizontal, sound block below
    gx, gy = x + 210, y + 30
    d.line([(gx - 42, gy + 34), (gx + 42, gy - 6)], fill=(110, 74, 38), width=9)
    d.rounded_rectangle([gx - 30, gy - 22, gx + 34, gy + 2], radius=6, fill=(70, 46, 24))
    d.ellipse([gx - 8, gy - 14, gx + 12, gy + 2], fill=(90, 60, 30))
    d.rounded_rectangle([gx - 34, gy + 34, gx + 38, gy + 48], radius=4, fill=(90, 60, 30))
    for dx in (-18, 0, 18):
        d.line([(gx + dx, gy + 18), (gx + dx, gy + 28)], fill=RED, width=3)


def draw_no_fly(d, x, y, w, h):
    """No-fly zone: jet silhouette inside a dashed exclusion circle."""
    d.rectangle([x, y, x + w, y + h], fill=SKY2)
    cx, cy = x + w // 2, y + h // 2 + 14
    for a in range(0, 360, 12):
        d.arc([cx - 44, cy - 44, cx + 44, cy + 44], start=a, end=a + 7,
              fill=(240, 220, 150), width=3)
    jx, jy = cx, cy - 2
    s = 0.62  # scale jet to the small panel
    jet = [(jx, jy - 58 * s), (jx + 10 * s, jy - 30 * s), (jx + 52 * s, jy - 6 * s),
           (jx + 52 * s, jy + 2 * s), (jx + 12 * s, jy + 6 * s),
           (jx + 8 * s, jy + 34 * s), (jx, jy + 22 * s), (jx - 8 * s, jy + 34 * s),
           (jx - 12 * s, jy + 6 * s), (jx - 52 * s, jy + 2 * s),
           (jx - 52 * s, jy - 6 * s), (jx - 10 * s, jy - 30 * s)]
    d.polygon(jet, fill=(235, 232, 222))
    d.text((x + 8, y + 8), "NO-FLY ZONE", font=font(SANS_B, 15), fill=(255, 255, 255))


def draw_fire(d, x, y, w, h):
    """Burning fuel tanker on the Cairo ring road."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 20, 18))
    d.rectangle([x, y + h - 30, x + w, y + h - 18], fill=(60, 58, 54))
    for i in range(2):
        d.rectangle([x + 10 + i * 70, y + h - 26, x + 34 + i * 70, y + h - 22],
                    fill=(220, 200, 90))
    tx, ty = x + 8, y + h - 62
    d.rounded_rectangle([tx, ty + 4, tx + 96, ty + 28], radius=9, fill=(200, 198, 190))
    d.polygon([(tx + 98, ty + 6), (tx + 122, ty + 6), (tx + 128, ty + 28),
               (tx + 98, ty + 28)], fill=(180, 40, 30))
    d.rectangle([tx + 104, ty + 10, tx + 116, ty + 18], fill=(220, 225, 235))
    for wx in (tx + 20, tx + 60, tx + 112):
        d.ellipse([wx - 9, ty + 24, wx + 9, ty + 42], fill=(10, 10, 10))
    fx = tx + 30
    d.polygon([(fx, ty - 4), (fx + 14, ty - 36), (fx + 28, ty - 4)], fill=ORANGE)
    d.polygon([(fx + 40, ty - 4), (fx + 52, ty - 28), (fx + 64, ty - 4)], fill=ORANGE)
    d.polygon([(fx + 16, ty - 4), (fx + 26, ty - 24), (fx + 36, ty - 4)],
              fill=(250, 220, 130))
    d.text((x + 8, y + 8), "≥30 KILLED", font=font(SANS_B, 17), fill=(255, 120, 90))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 26  # margin
    R = W - M

    # ---------- masthead: 20..150 ----------
    rule(d, M, 20, R, 3)
    d.text((W // 2, 28), "THE WORLD", font=font(SERIF_B, 84),
           fill=INK, anchor="ma")
    d.text((W // 2, 122), "WEDNESDAY, 25 NOVEMBER 2026  •  WORLD NEWS IN ONE IMAGE  •  PRICE: ONE READ",
           font=font(SANS_B, 15), fill=INK, anchor="ma")
    rule(d, M, 148, R, 2)

    # ---------- lead story: 160..468 ----------
    y = 160
    y = kicker(d, M, y, "Middle East — Lead Story")
    for line in ["GULF IN FLAMES:", "HOUTHIS HIT RIYADH;",
                "IRAN CLAIMS 2 US DRONES DOWN"]:
        d.text((M, y), line, font=fit_line(d, line, SERIF_B, 38, 560), fill=INK)
        y += 44
    y += 6
    deck = ("Houthi missiles struck Riyadh's tallest tower, wounding 11 people, "
            "two of them Indian nationals. The Houthis also claimed a strike on "
            "Saudi Arabia's biggest oil refinery, and the Saudi-led coalition "
            "answered by bombing Hodeidah port. Iran said its air defences shot "
            "down two US drones — an MQ-9 and a 'Lucas' suicide drone — over the "
            "Strait of Hormuz, as Washington told its citizens to leave Iran.")
    y = para(d, M, y, deck, font(SERIF, 16), 560, 21)
    draw_tower_scene(d, 612, 190, 386, 262)
    rule(d, M, 476, R, 2)

    # ---------- row 2: three columns, 488..712 ----------
    y0 = 488
    col_w, gap = 312, 12
    xs = [M, M + col_w + gap, M + 2 * (col_w + gap)]
    # Tariffs
    x = xs[0]
    kicker(d, x, y0, "Trade")
    d.text((x, y0 + 24), "US PLANS TARIFFS", font=font(SERIF_B, 24), fill=INK)
    d.text((x, y0 + 53), "ON 14 ECONOMIES", font=font(SERIF_B, 24), fill=INK)
    para(d, x, y0 + 88, "Trump's team is set to unveil a probe into global "
         "factory overcapacity, with new tariffs proposed for 14 major economies.",
         font(SERIF, 15), col_w, 19)
    draw_bars(d, x, y0 + 148, col_w, 76)
    # Shenzhou-24
    x = xs[1]
    kicker(d, x, y0, "Space")
    d.text((x, y0 + 24), "SHENZHOU-24 LIFTS", font=font(SERIF_B, 24), fill=INK)
    d.text((x, y0 + 53), "OFF WITH PAKISTAN'S", font=font(SERIF_B, 24), fill=INK)
    para(d, x, y0 + 88, "China launched two taikonauts and Muhammad Zeeshan "
         "Ali — the first foreign crew member aboard the Tiangong station.",
         font(SERIF, 15), col_w, 19)
    draw_rocket(d, x, y0 + 148, col_w, 76)
    # Huawei
    x = xs[2]
    kicker(d, x, y0, "Tech")
    d.text((x, y0 + 24), "HUAWEI FOUND", font=font(SERIF_B, 24), fill=INK)
    d.text((x, y0 + 53), "GUILTY IN US COURT", font=font(SERIF_B, 24), fill=INK)
    para(d, x, y0 + 88, "The Chinese telecom giant was convicted in a major "
         "US criminal trial over its business with Iran — a landmark in the "
         "US–China tech war.", font(SERIF, 15), col_w, 19)
    draw_gavel(d, x, y0 + 148, col_w, 76)
    rule(d, M, 722, R, 2)

    # ---------- row 3: two halves, 734..868 ----------
    y0 = 734
    # Poland (left half): visual left, text right
    draw_no_fly(d, M, y0, 140, 124)
    tx = M + 152
    kicker(d, tx, y0, "Europe")
    d.text((tx, y0 + 24), "POLAND TO SET UP", font=font(SERIF_B, 22), fill=INK)
    d.text((tx, y0 + 50), "NO-FLY ZONE", font=font(SERIF_B, 22), fill=INK)
    para(d, tx, y0 + 80, "Warsaw will declare a no-fly zone near Ukraine after "
         "airspace violations blamed on Russia. Kyiv needs €115bn for 2027.",
         font(SERIF, 14), 322, 18)
    # Cairo (right half)
    x2 = 520
    draw_fire(d, x2, y0, 140, 124)
    tx = x2 + 152
    kicker(d, tx, y0, "Egypt")
    d.text((tx, y0 + 24), "CAIRO TANKER FIRE", font=font(SERIF_B, 22), fill=INK)
    d.text((tx, y0 + 50), "KILLS AT LEAST 30", font=font(SERIF_B, 22), fill=INK)
    para(d, tx, y0 + 80, "A fuel tanker overturned and burst into flames on the "
         "Imbaba ring road near Cairo; at least 30 people were killed.",
         font(SERIF, 14), 322, 18)
    rule(d, M, 878, R, 2)

    # ---------- also today: 890..990 ----------
    y0 = 890
    d.text((M, y0), "ALSO TODAY", font=font(SANS_B, 14), fill=RED)
    items = [
        "Netanyahu: Israeli judge urges prosecutors to drop the main bribery case.",
        "Nvidia: Jensen Huang apologises to staff in his first speech back as CEO.",
        "Bangladesh raises garment wages 36% to 17,000 taka after weeks of protests.",
        "Sudan: RSF drone strike kills 19 in Blue Nile; Israel kills a senior Hamas official in Gaza.",
        "Indonesia: rescuers search for miners trapped in a flooded gold mine.",
    ]
    yy = y0 + 22
    for it in items:
        d.text((M + 12, yy), "•", font=font(SERIF, 13), fill=RED)
        yy = para(d, M + 28, yy, it, font(SERIF, 13), R - M - 28, 16)
    rule(d, M, yy + 4, R, 2)
    d.text((W // 2, yy + 12), "THE WORLD  •  25 NOVEMBER 2026  •  Stories verified 25 Nov 2026 — Reuters, BusinessWorld, 10things.news, Open Chronicle",
           font=font(SANS, 11), fill=FAINT, anchor="ma")

    os.makedirs("/output", exist_ok=True)
    img.save(OUT, format="PNG")
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
