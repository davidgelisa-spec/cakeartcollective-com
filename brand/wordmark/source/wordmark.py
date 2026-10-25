"""Cake Art Collective wordmark — Orange-Avenue-inspired high-contrast serif.

Letters are drawn individually (not from a font) and placed by hand.
Usage: python wordmark.py OUTDIR
"""
import math
import os
import sys

from pathops import Path
from fontTools.pens.svgPathPen import SVGPathPen

from build_font import (poly, rect, circle, union, diff, inter, tr, xform, lerp, arc,
                        bez, spline, join, stroke, ring, serif)

H = 700        # cap height
X = 440        # x-height
ASC = 712      # ascender
STEM_C = 100   # cap thick stroke
STEM_L = 86    # lowercase thick stroke
HAIR = 11
KC = 2.3       # contrast exponent: higher keeps hairlines longer, swells later
SER = (11, 42, 34)
SER_L = (10, 34, 28)
SQ = 2.1       # superellipse squareness of bowls (2 = ellipse)

TEAL = "#2F6B62"


def cstroke(pts, wmax, k=KC, hmin=HAIR):
    return stroke(pts, wmax, hmin, k=k)


def teardrop(pts, wmax, r, ramp=0.3, k=KC):
    """Stroke whose last `ramp` fraction swells into a round teardrop terminal."""
    def w(t, tx, ty):
        base = HAIR + (wmax - HAIR) * abs(ty) ** k
        if t > 1 - ramp:
            u = (t - (1 - ramp)) / ramp
            base = base + (2 * r * 0.92 - base) * u ** 2.2
        return base
    ex, ey = pts[-1]
    return [stroke(pts, None, None, wfun=w), circle(ex, ey, r)]


def taper(pts, wmax, tip=HAIR, ramp=0.25, k=KC):
    """Stroke that fines down to a sharp hairline at its end."""
    def w(t, tx, ty):
        base = HAIR + (wmax - HAIR) * abs(ty) ** k
        if t > 1 - ramp:
            u = (t - (1 - ramp)) / ramp
            base = base + (tip * 0.6 - base) * u
        return max(base, 3)
    return stroke(pts, None, None, wfun=w)


def stem(x, y0, y1, w, top=None, bot=None, ser=SER):
    out = [rect(x - w / 2, y0, x + w / 2, y1)]
    if top:
        out += serif(x, w, y1, top=True, L=top[0], R=top[1], ser=ser)
    if bot:
        out += serif(x, w, y0, L=bot[0], R=bot[1], ser=ser)
    return out


# ------------------------------------------------------------------ letters

def C():
    cx, cy, rx, ry = 372, 350, 322, 356
    pts = arc(cx, cy, rx, ry, 52, 312, sq=SQ, n=90)
    _, outer = ring(cx, cy, rx, ry, STEM_C + 8, HAIR, sq=SQ, k=KC)
    out = [cstroke(pts, STEM_C + 8)]
    # top terminal: vertical beak, slightly cupped
    ex, ey = pts[0]
    beak = poly([(ex - 50, ey + 70), (ex + 14, ey + 70), (ex + 14, ey - 168), (ex - 4, ey - 168), (ex - 30, ey - 40)])
    out.append(inter(beak, outer))
    # bottom terminal: short vertical spur
    ex, ey = pts[-1]
    out.append(inter(poly([(ex - 30, ey - 60), (ex + 14, ey - 60), (ex + 14, ey + 92), (ex - 2, ey + 92)]), outer))
    return out


def A():
    wl, wr = 22, 104
    xl, xr, top = 0, 690, H + 14
    apx = (xl + xr) / 2 + 6
    left = poly([(xl, 0), (xl + wl, 0), (apx + 4, top), (apx - wl + 4, top)])
    right = poly([(xr - wr, 0), (xr, 0), (apx + 10, top), (apx + 10 - wr, top)])
    out = [inter(union([left, right]), rect(-500, -1, 1500, top - 4))]
    out.append(rect(130, 222, 560, 233))
    out += serif(xl + wl / 2, wl, 0, ser=(11, 44, 20))
    out += serif(xr - wr / 2, wr, 0, ser=(11, 44, 30))
    return out


def a():
    sx = 338
    out = [rect(sx - STEM_L / 2, 0, sx + STEM_L / 2, 292)]
    hook = arc(222, 292, 116, 150, 0, 152, sq=SQ, n=50)
    out += teardrop(hook, 62, 37, ramp=0.3)
    bowl = arc(196, 134, 150, 134, 64, 334, sq=SQ, n=70)
    out.append(cstroke(bowl, STEM_L - 2))
    out.append(stroke(lerp(bowl[0], (sx, 262), 6), None, None, wfun=lambda t, tx, ty: HAIR + 3))
    # small spur at the foot of the stem
    out.append(poly([(sx - STEM_L / 2, 0), (sx + STEM_L / 2 + 34, 0), (sx + STEM_L / 2 + 34, 9), (sx + STEM_L / 2, 52)]))
    return out


def k():
    out = stem(46, 0, ASC, STEM_L + 2, top=(True, False), bot=(True, True), ser=SER_L)
    out.append(poly([(80, 150), (100, 150), (344, X), (324, X)]))
    out += serif(334, 20, X, top=True, ser=(10, 34, 12))
    out.append(poly([(318, 0), (414, 0), (223, 319), (167, 254)]))
    out += serif(366, 96, 0, ser=(10, 36, 22))
    return out


def e():
    cx, cy, rx, ry = 236, 222, 206, 226
    pts = arc(cx, cy, rx, ry, 10, 334, sq=SQ, n=90)
    out = [taper(pts, STEM_L + 10, ramp=0.14)]
    y = cy + ry * math.sin(math.radians(10)) ** (2 / SQ)
    out.append(rect(cx - rx, y - 6, cx + rx + 18, y + 6))
    return out


def o():
    r, _ = ring(222, 222, 206, 226, STEM_L + 12, HAIR, sq=SQ, k=KC)
    return [r]


def l():
    return stem(46, 0, ASC, STEM_L, top=(True, False), bot=(True, True), ser=SER_L)


def i():
    return stem(46, 0, X, STEM_L, top=(True, False), bot=(True, True), ser=SER_L) + [circle(48, 584, 46)]


def v():
    xl, xr = 0, 480
    apx = (xl + xr) / 2 - 4
    a_ = poly([(xl, X), (xl + 94, X), (apx + 20, -8), (apx - 74, -8)])
    b_ = poly([(xr - 21, X), (xr, X), (apx + 20, -8), (apx, -8)])
    out = [inter(union([a_, b_]), rect(-500, -2, 1500, X + 1))]
    out += serif(47, 94, X, top=True, ser=(10, 36, 22))
    out += serif(xr - 10.5, 21, X, top=True, ser=(10, 32, 10))
    return out


def c_body():
    cx, cy, rx, ry = 220, 222, 200, 226
    pts = arc(cx, cy, rx, ry, 44, 318, sq=SQ, n=80)
    return [taper(pts[::-1], STEM_L + 10, ramp=0.0)], pts


def r_body():
    out = stem(46, 0, X, STEM_L, top=(True, False), bot=(True, True), ser=(10, 40, 28))
    pts = arc(170, 312, 126, X - 312 - 4, 168, 30, sq=SQ, n=40)
    out.append(cstroke(pts, STEM_L - 10))
    return out, pts


def pen_w(wmax, hmin=HAIR, k=1.6):
    """Pointed-pen contrast: only downstrokes swell."""
    return lambda ty: hmin + (wmax - hmin) * max(0.0, -ty) ** k


def loop_t(start, tx, via):
    """Cursive loop: hairline upstroke from `start` crossing the t stem,
    over the top, then a swelling downstroke that becomes the t stem."""
    ctrl = [start] + via + [(tx + 10, 520), (tx + 80, 610), (tx + 104, 700), (tx + 70, 772),
                            (tx + 10, 778), (tx - 26, 728), (tx - 14, 640), (tx, 560), (tx, 500)]
    pts = spline(ctrl, n=14)

    def w(t, tx_, ty):
        if t < 0.55:
            return HAIR + 2
        # downstroke swells progressively, reaching full stem weight as it joins the t
        u = min(1.0, max(0.0, (t - 0.74) / 0.22))
        wm = 26 + (STEM_L - 26) * u ** 1.3
        return HAIR + (wm - HAIR) * max(0.0, -ty) ** 1.4
    out = [stroke(pts, None, None, wfun=w)]
    out.append(rect(tx - STEM_L / 2, 130, tx + STEM_L / 2, 505))
    tail = join(lerp((tx, 136), (tx, 128), 2), arc(tx + 112, 128, 112, 134, 180, 335, sq=SQ, n=40))
    tw = pen_w(STEM_L, k=1.2)
    out.append(stroke(tail, None, None, wfun=lambda t, tx_, ty: max(HAIR - 2, tw(ty)) if t > 0.05 else STEM_L))
    out.append(rect(tx - STEM_L / 2 - 64, X - HAIR, tx + STEM_L / 2 + 150, X))
    return out


def ct():
    cx, cy, rx, ry = 220, 222, 200, 226
    pts = arc(cx, cy, rx, ry, 318, 72, sq=SQ, n=80)   # bottom terminal -> top terminal
    body = [taper(pts[::-1], STEM_L + 10, ramp=0.12)]
    ex, ey = pts[-1]
    tx = 470
    return body + loop_t((ex, ey), tx, [(ex + 70, ey - 6), (tx - 46, 462)])


def rt():
    out = stem(46, 0, X, STEM_L, top=(True, False), bot=(True, True), ser=(10, 40, 28))
    tx = 330
    out += loop_t((60, 330), tx, [(100, 402), (172, 444), (tx - 40, 470)])
    return out


def t():
    tx = 92
    top = 600
    out = [rect(tx - STEM_L / 2, 130, tx + STEM_L / 2, top)]
    # angled cut across the top of the stem
    out[0] = diff(out[0], poly([(tx - STEM_L / 2 - 1, top + 1), (tx + STEM_L / 2 + 1, top + 1), (tx - STEM_L / 2 - 1, top - 70)]))
    tail = join(lerp((tx, 136), (tx, 128), 2), arc(tx + 112, 128, 112, 134, 180, 335, sq=SQ, n=40))
    tw = pen_w(STEM_L, k=1.2)
    out.append(stroke(tail, None, None, wfun=lambda t_, tx_, ty: max(HAIR - 2, tw(ty)) if t_ > 0.05 else STEM_L))
    out.append(rect(tx - STEM_L / 2 - 60, X - HAIR, tx + STEM_L / 2 + 140, X))
    return out


def c():
    cx, cy, rx, ry = 220, 222, 200, 226
    pts = arc(cx, cy, rx, ry, 318, 90, sq=SQ, n=80)    # bottom terminal -> top
    out = [taper(pts[::-1], STEM_L + 10, ramp=0.12)]
    hook = arc(cx, cy, rx, ry, 100, 26, sq=SQ, n=40)
    out += teardrop(hook, 40, 40, ramp=0.55)
    return out


def r():
    out = stem(46, 0, X, STEM_L, top=(True, False), bot=(True, True), ser=(10, 40, 28))
    pts = arc(170, 312, 128, X - 312 - 4, 168, 2, sq=SQ, n=50)
    out += teardrop(pts, 30, 36, ramp=0.4)
    return out


# ------------------------------------------------------------------ layout

def word(parts):
    """parts: list of (builder, gap_before). Places each letter after the previous one's right edge."""
    shapes, x = [], 0
    for fn, gap in parts:
        if fn is None:
            x += gap
            continue
        g = union(fn())
        xmin, _, xmax, _ = g.bounds
        g = tr(g, x + gap - xmin)
        shapes.append(g)
        x = x + gap + (xmax - xmin)
    return union(shapes)


LAYOUT = [
    (C, 0), (a, 46), (k, 34), (e, 14),
    (None, 210),
    (A, 0), (r, 34), (t, 6),
    (None, 210),
    (C, 0), (o, 28), (l, 42), (l, 60), (e, 34), (c, 26), (t, 8), (i, 30), (v, 20), (e, 14),
]


def to_svg(p, color, pad=40):
    xmin, ymin, xmax, ymax = p.bounds
    pen = SVGPathPen(None)
    xform(p, (1, 0, 0, -1, -xmin + pad, ymax + pad)).draw(pen)
    w, h = xmax - xmin + 2 * pad, ymax - ymin + 2 * pad
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">'
            f'<title>Cake Art Collective</title><path fill="{color}" d="{pen.getCommands()}"/></svg>')


def to_png(p, path, color, height=400, pad=40, bg=None):
    from PIL import Image, ImageDraw, ImageChops
    from fontTools.pens.recordingPen import RecordingPen
    ss = 4
    xmin, ymin, xmax, ymax = p.bounds
    sc = (height - 2 * pad) / (ymax - ymin) * ss
    W = int((xmax - xmin) * sc + 2 * pad * ss)
    Hh = height * ss
    rec = RecordingPen()
    p.draw(rec)
    mask = Image.new("1", (W, Hh), 0)
    cur = []

    def flush():
        if len(cur) > 2:
            m = Image.new("1", (W, Hh), 0)
            ImageDraw.Draw(m).polygon([((x - xmin) * sc + pad * ss, (ymax - y) * sc + pad * ss) for x, y in cur], fill=1)
            nonlocal_mask[0] = ImageChops.logical_xor(nonlocal_mask[0], m)
    nonlocal_mask = [mask]
    for op, args in rec.value:
        if op == "moveTo":
            cur = [args[0]]
        elif op == "lineTo":
            cur.append(args[0])
        elif op == "curveTo":
            p0 = cur[-1]
            a1, a2, a3 = args
            for j in range(1, 13):
                t = j / 12
                u = 1 - t
                cur.append((u**3 * p0[0] + 3 * u * u * t * a1[0] + 3 * u * t * t * a2[0] + t**3 * a3[0],
                            u**3 * p0[1] + 3 * u * u * t * a1[1] + 3 * u * t * t * a2[1] + t**3 * a3[1]))
        elif op in ("closePath", "endPath"):
            flush()
            cur = []
    alpha = nonlocal_mask[0].convert("L").resize((W // ss, Hh // ss), Image.LANCZOS)
    rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
    img = Image.new("RGBA", alpha.size, rgb + (0,))
    img.putalpha(alpha)
    if bg:
        base = Image.new("RGBA", alpha.size, bg)
        base.alpha_composite(img)
        img = base
    img.save(path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "wm"
    os.makedirs(out, exist_ok=True)
    p = word(LAYOUT)
    for name, col in (("teal", TEAL), ("black", "#1A1A1A"), ("white", "#FFFFFF")):
        with open(os.path.join(out, f"cake-art-collective-wordmark-{name}.svg"), "w") as f:
            f.write(to_svg(p, col))
        to_png(p, os.path.join(out, f"cake-art-collective-wordmark-{name}.png"), col, height=600)
    to_png(p, os.path.join(out, "preview.png"), TEAL, height=300, bg=(255, 255, 255, 255))
    print("done")
