"""Collective Display — a high-contrast display serif generated from code.

Every glyph is built from stroked centrelines (width follows stroke angle:
vertical = thick, horizontal = hairline) plus rectangles, wedges and balls,
merged with skia-pathops and written out as CFF OpenType + WOFF2.

Usage:  python build_font.py OUTDIR
"""
import math
import sys
import os

import pathops
from pathops import Path, PathOp
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

FAMILY = "Collective Display"
STYLE = "Regular"
PSNAME = "CollectiveDisplay-Regular"
VERSION = "1.000"

UPM = 1000
H = 700        # cap height
X = 440        # x-height
ASC = 740      # ascender
DSC = -220     # descender
DIG = 680      # figure height

S = 90         # cap thick stem
HC = 12        # cap hairline
SL = 80        # lowercase stem
HL = 11        # lowercase hairline
K = 1.7        # contrast curve exponent

# serifs: (thickness, extension, bracket)
SER_C = (12, 40, 26)
SER_L = (11, 32, 22)


# ---------------------------------------------------------------- geometry

def poly(pts):
    p = Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    return p


def rect(x0, y0, x1, y1):
    return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def circle(cx, cy, r, ry=None):
    ry = ry or r
    k = 0.5523
    p = Path()
    p.moveTo(cx + r, cy)
    p.cubicTo(cx + r, cy + k * ry, cx + k * r, cy + ry, cx, cy + ry)
    p.cubicTo(cx - k * r, cy + ry, cx - r, cy + k * ry, cx - r, cy)
    p.cubicTo(cx - r, cy - k * ry, cx - k * r, cy - ry, cx, cy - ry)
    p.cubicTo(cx + k * r, cy - ry, cx + r, cy - k * ry, cx + r, cy)
    p.close()
    return p


def union(shapes):
    b = pathops.OpBuilder(fix_winding=True, keep_starting_points=False)
    for s in shapes:
        b.add(s, PathOp.UNION)
    return b.resolve()


def diff(a, b):
    return pathops.op(a, b, PathOp.DIFFERENCE, fix_winding=True)


def inter(a, b):
    return pathops.op(a, b, PathOp.INTERSECTION, fix_winding=True)


def xform(p, m):
    q = Path()
    p.draw(TransformPen(q.getPen(), m))
    return q


def tr(p, dx, dy=0):
    return xform(p, (1, 0, 0, 1, dx, dy))


def lerp(a, b, n=8):
    return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)]


def arc(cx, cy, rx, ry, a0, a1, sq=2.25, n=None):
    """Superellipse arc, angles in degrees (a1 < a0 runs clockwise)."""
    n = n or max(8, int(abs(a1 - a0) / 4))
    e = 2.0 / sq
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        c, s = math.cos(a), math.sin(a)
        pts.append((cx + rx * math.copysign(abs(c) ** e, c),
                    cy + ry * math.copysign(abs(s) ** e, s)))
    return pts


def bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
    return out


def spline(ctrl, n=12):
    """Catmull-Rom through control points, densely sampled."""
    out = []
    m = len(ctrl)
    for i in range(m - 1):
        p0 = ctrl[max(i - 1, 0)]
        p1, p2 = ctrl[i], ctrl[i + 1]
        p3 = ctrl[min(i + 2, m - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        seg = bez(p1, c1, c2, p2, n)
        out.extend(seg if i == 0 else seg[1:])
    return out


def join(*lists):
    out = []
    for l in lists:
        for p in l:
            if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 0.5:
                out.append(p)
    return out


def _smooth_run(path, pts):
    """Append a smooth Catmull-Rom curve through pts (path already at pts[0])."""
    m = len(pts)
    for i in range(m - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, m - 1)]
        path.cubicTo(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6,
                     p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6,
                     p2[0], p2[1])


def _smooth_closed(pts):
    p = Path()
    m = len(pts)
    p.moveTo(*pts[0])
    for i in range(m):
        p0, p1, p2, p3 = pts[(i - 1) % m], pts[i], pts[(i + 1) % m], pts[(i + 2) % m]
        p.cubicTo(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6,
                  p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6,
                  p2[0], p2[1])
    p.close()
    return p


def _offsets(pts, wmax, hmin, k, wfun, closed):
    n = len(pts)
    L, R = [], []
    for i in range(n):
        if closed:
            a, b = pts[(i - 1) % n], pts[(i + 1) % n]
        else:
            a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        tx, ty = dx / d, dy / d
        t = i / (n - 1)
        if wfun:
            w = wfun(t, tx, ty)
        else:
            wm = wmax(t) if callable(wmax) else wmax
            w = hmin + (wm - hmin) * abs(ty) ** k
        nx, ny = -ty, tx
        L.append((pts[i][0] + nx * w / 2, pts[i][1] + ny * w / 2))
        R.append((pts[i][0] - nx * w / 2, pts[i][1] - ny * w / 2))
    return L, R


def stroke(pts, wmax, hmin, k=K, wfun=None):
    """Open contrast stroke along a dense centreline."""
    L, R = _offsets(pts, wmax, hmin, k, wfun, False)
    p = Path()
    p.moveTo(*L[0])
    _smooth_run(p, L)
    p.lineTo(*R[-1])
    _smooth_run(p, R[::-1])
    p.close()
    return pathops.simplify(p, fix_winding=True)


def ring(cx, cy, rx, ry, wmax, hmin, sq=2.25, k=K):
    """Closed contrast ring. Returns (ring, outer_fill)."""
    pts = arc(cx, cy, rx, ry, 0, 360, sq, n=120)[:-1]
    L, R = _offsets(pts, wmax, hmin, k, None, True)
    a, b = _smooth_closed(L), _smooth_closed(R)
    outer, inner = (a, b) if abs(a.area) > abs(b.area) else (b, a)
    return diff(outer, inner), outer


def diag(xb, xt, yb, yt, w):
    """Straight stroke with horizontal ends; xb/xt are LEFT edge x at bottom/top."""
    return poly([(xb, yb), (xb + w, yb), (xt + w, yt), (xt, yt)])


def serif(xc, w, y, top=False, L=True, R=True, ser=SER_C, ext=None, br=None):
    t, e, b = ser
    e = e if ext is None else ext
    b = b if br is None else br
    x0 = xc - w / 2 - (e if L else 0)
    x1 = xc + w / 2 + (e if R else 0)
    s = 1 if not top else -1
    shapes = [rect(x0, y, x1, y + s * t)]
    yb = y + s * t
    for side, on in ((-1, L), (1, R)):
        if not on or b <= 0:
            continue
        ex = xc + side * w / 2
        curve = bez((ex, yb + s * b), (ex, yb + s * b * 0.45), (ex + side * b * 0.45, yb), (ex + side * b, yb), 8)
        shapes.append(poly([(ex - side * 0.5, yb - s * 0.5)] + curve))
    return shapes


def wedge(x, y, down=True, w=30, tip=10, ln=125, flip=False):
    """Beak serif hanging from a bar end. x is the outer edge; flip puts it on the left."""
    s = -1 if down else 1
    if flip:
        return poly([(x, y), (x + w, y), (x + tip, y + s * ln), (x, y + s * ln)])
    return poly([(x - w, y), (x, y), (x, y + s * ln), (x - tip, y + s * ln)])


def ball(x, y, r):
    return circle(x, y, r)


def end(pts):
    return pts[-1]


# ------------------------------------------------------------------ glyphs

GLYPHS = {}   # name -> (unicode or None, builder, lsb, rsb)


def glyph(name, uni=None, lsb=40, rsb=40):
    def deco(f):
        GLYPHS[name] = (uni, f, lsb, rsb)
        return f
    return deco


def cstem(x, y0=0, y1=H, w=S, top=(True, True), bot=(True, True), ser=SER_C):
    out = [rect(x - w / 2, y0, x + w / 2, y1)]
    if any(top):
        out += serif(x, w, y1, top=True, L=top[0], R=top[1], ser=ser)
    if any(bot):
        out += serif(x, w, y0, L=bot[0], R=bot[1], ser=ser)
    return out


def lstem(x, y0=0, y1=X, **kw):
    kw.setdefault("w", SL)
    kw.setdefault("ser", SER_L)
    return cstem(x, y0, y1, **kw)


NONE = (False, False)
LEFT = (True, False)
RIGHT = (False, True)


# ---- capitals

def _apex(xl, xr, y0, y1, wl, wr, up=True, clip=6):
    """Two diagonals meeting at a point; up=True for A, False for V."""
    mx = (xl + xr) / 2
    if up:
        a = diag(xl, mx - wl / 2, y0, y1 + 10, wl)
        b = diag(xr - wr, mx - wr / 2, y0, y1 + 10, wr)
        a = poly([(xl, y0), (xl + wl, y0), (mx + wl * 0.0, y1 + 10), (mx - wl, y1 + 10)])
        b = poly([(xr - wr, y0), (xr, y0), (mx + 2, y1 + 10), (mx + 2 - wr, y1 + 10)])
        return [inter(union([a, b]), rect(-2000, y0 - 1, 4000, y1 + clip))]
    a = poly([(xl, y1), (xl + wl, y1), (mx + 2, y0 - 10), (mx + 2 - wl, y0 - 10)])
    b = poly([(xr - wr, y1), (xr, y1), (mx + wr, y0 - 10), (mx, y0 - 10)])
    return [inter(union([a, b]), rect(-2000, y0 - clip, 4000, y1 + 1))]


@glyph("A", 0x41)
def g_A():
    wl, wr = 24, 98
    out = _apex(0, 640, 0, H, wl, wr, up=True)
    out.append(rect(110, 218, 520, 230))
    out += serif(wl / 2, wl, 0, br=12)
    out += serif(640 - wr / 2, wr, 0, br=16)
    return out


@glyph("B", 0x42)
def g_B():
    out = cstem(45, top=LEFT, bot=LEFT)
    top = join(lerp((45, H - 6), (250, H - 6)), arc(250, 522, 200, 172, 90, -90), lerp((250, 350), (45, 350)))
    bot = join(lerp((45, 356), (265, 356)), arc(265, 181, 245, 175, 90, -90), lerp((265, 6), (45, 6)))
    out += [stroke(top, S - 6, HC), stroke(bot, S, HC)]
    return out


@glyph("C", 0x43)
def g_C():
    cx, cy, rx, ry = 340, 350, 295, 354
    pts = arc(cx, cy, rx, ry, 46, 314)
    _, outer = ring(cx, cy, rx, ry, S + 6, HC)
    out = [stroke(pts, S + 6, HC)]
    ex, ey = pts[0]
    out.append(inter(rect(ex - 44, ey - 150, ex + 12, ey + 80), outer))
    ex, ey = pts[-1]
    out.append(inter(rect(ex - 40, ey - 60, ex + 12, ey + 70), outer))
    return out


@glyph("D", 0x44)
def g_D():
    out = cstem(45, top=LEFT, bot=LEFT)
    pts = join(lerp((45, H - 6), (270, H - 6)), arc(270, 350, 365, 344, 90, -90, sq=2.4), lerp((270, 6), (45, 6)))
    out.append(stroke(pts, S + 4, HC))
    return out


def _bar_e(y0, x1, beak, ln=125):
    out = [rect(20, y0, x1, y0 + HC)]
    if beak == "down":
        out.append(wedge(x1, y0 + HC, down=True, ln=ln))
    elif beak == "up":
        out.append(wedge(x1, y0, down=False, ln=ln + 20))
    elif beak == "mid":
        out.append(poly([(x1 - 13, y0 - 46), (x1, y0 - 52), (x1, y0 + HC + 52), (x1 - 13, y0 + HC + 46)]))
    return out


@glyph("E", 0x45)
def g_E():
    out = cstem(45, top=LEFT, bot=LEFT)
    out += _bar_e(H - HC, 470, "down")
    out += _bar_e(344, 400, "mid")
    out += _bar_e(0, 505, "up")
    return out


@glyph("F", 0x46)
def g_F():
    out = cstem(45, top=LEFT, bot=(True, True))
    out += _bar_e(H - HC, 470, "down")
    out += _bar_e(334, 400, "mid")
    return out


@glyph("G", 0x47)
def g_G():
    cx, cy, rx, ry = 345, 350, 300, 354
    pts = arc(cx, cy, rx, ry, 46, 340)
    _, outer = ring(cx, cy, rx, ry, S + 6, HC)
    out = [stroke(pts, S + 6, HC)]
    ex, ey = pts[0]
    out.append(inter(rect(ex - 44, ey - 150, ex + 12, ey + 80), outer))
    sx = cx + rx - 6
    out.append(inter(rect(sx - 46, 40, sx + 44, 300), outer))
    out.append(rect(sx - 150, 288, sx + 60, 300))
    return out


@glyph("H", 0x48)
def g_H():
    return cstem(45) + cstem(600) + [rect(45, 350, 600, 362)]


@glyph("I", 0x49)
def g_I():
    return cstem(45)


@glyph("J", 0x4A)
def g_J():
    out = cstem(230, 170, H, bot=NONE)
    pts = join(lerp((230, 175), (230, 170), 2), arc(95, 170, 135, 176, 0, -150))
    out.append(stroke(pts, S, HC))
    ex, ey = pts[-1]
    out.append(ball(ex + 10, ey + 24, 44))
    return out


@glyph("K", 0x4B)
def g_K():
    out = cstem(45)
    out.append(diag(70, 466, 250, H, 24))
    out += serif(478, 24, H, top=True, br=10)
    out.append(diag(160, 434, 395, 0, 96))
    out += serif(482, 96, 0, br=14)
    return out


@glyph("L", 0x4C)
def g_L():
    out = cstem(45, bot=LEFT)
    out += _bar_e(0, 470, "up")
    return out


@glyph("M", 0x4D)
def g_M():
    out = cstem(40, w=22, top=LEFT)
    out.append(diag(29, 368, H, 0, 92)[0] if False else poly([(29, H), (121, H), (460, 0), (368, 0)]))
    out.append(poly([(428, 0), (450, 0), (735, H), (713, H)]))
    out += cstem(735 - 45, top=RIGHT)
    return out


@glyph("N", 0x4E)
def g_N():
    out = cstem(40, w=22, top=LEFT)
    out.append(poly([(29, H), (123, H), (621, -10), (527, -10)]))
    out += cstem(610, -10, H, w=22, bot=NONE)
    return out


@glyph("O", 0x4F)
def g_O():
    r, _ = ring(355, 350, 310, 354, S + 8, HC)
    return [r]


@glyph("P", 0x50)
def g_P():
    out = cstem(45, top=LEFT)
    pts = join(lerp((45, H - 6), (255, H - 6)), arc(255, 500, 245, 194, 90, -90), lerp((255, 306), (45, 306)))
    out.append(stroke(pts, S, HC))
    return out


@glyph("Q", 0x51)
def g_Q():
    r, _ = ring(355, 350, 310, 354, S + 8, HC)
    tail = spline([(330, 20), (420, -50), (560, -110), (700, -125)])
    t = stroke(tail, None, None, wfun=lambda t, tx, ty: 16 + 70 * math.sin(math.pi * min(1, t * 1.15)) ** 1.2 * (1 - t * 0.5))
    return [r, t]


@glyph("R", 0x52)
def g_R():
    out = cstem(45, top=LEFT)
    pts = join(lerp((45, H - 6), (255, H - 6)), arc(255, 515, 240, 179, 90, -90), lerp((255, 336), (45, 336)))
    out.append(stroke(pts, S, HC))
    out.append(diag(470, 230, 0, 342, 98))
    out += serif(519, 98, 0, L=False, br=14)
    return out


def _S(cx, top_c, top_r, bot_c, bot_r, wm, hm, beak):
    (tcy, trx, try_) = top_c[0], top_r[0], top_r[1]
    (bcy, brx, bry) = bot_c[0], bot_r[0], bot_r[1]
    top = arc(cx, tcy, trx, try_, 28, 198)
    bot = arc(cx + 6, bcy, brx, bry, 22, -154)
    a, b = top[-1], bot[0]
    ta = math.radians(198)
    tb = math.radians(22)
    s = 1.25
    t0 = (trx * math.sin(ta) * -1 * -1, -try_ * math.cos(ta) * -1)
    # direction leaving the top arc (ccw) and entering the bottom arc (cw)
    t0 = (-trx * math.sin(ta), try_ * math.cos(ta))
    t1 = (brx * math.sin(tb), -bry * math.cos(tb))
    spine = bez(a, (a[0] + t0[0] * s / 3 * 2, a[1] + t0[1] * s / 3 * 2),
                (b[0] - t1[0] * s / 3 * 2, b[1] - t1[1] * s / 3 * 2), b, 30)
    pts = join(top, spine, bot)
    out = [stroke(pts, wm, hm)]
    ex, ey = pts[0]
    out.append(poly([(ex - beak[0], ey + 30), (ex + 6, ey + 30), (ex + 6, ey - beak[1]), (ex - 6, ey - beak[1])]))
    ex, ey = pts[-1]
    out.append(poly([(ex - 6, ey - 30), (ex + beak[0], ey - 30), (ex + 6, ey + beak[1]), (ex - 6, ey + beak[1])]))
    return out


@glyph("S", 0x53)
def g_S():
    return _S(290, (529,), (210, 171), (180,), (232, 186), S + 4, HC, (40, 130))


@glyph("T", 0x54)
def g_T():
    out = [rect(0, H - HC, 580, H), wedge(0, H - HC, flip=True), wedge(580, H - HC)]
    out += cstem(290, top=NONE)
    return out


@glyph("U", 0x55)
def g_U():
    pts = join(lerp((45, H), (45, 245)), arc(320, 245, 275, 251, 180, 360), lerp((595, 245), (595, H)))

    def wm(t):
        if t < 0.55:
            return S
        u = min(1, (t - 0.55) / 0.2)
        return S + (24 - S) * (u * u * (3 - 2 * u))
    out = [stroke(pts, wm, HC)]
    out += serif(45, S, H, top=True)
    out += serif(595, 24, H, top=True, br=12)
    return out


@glyph("V", 0x56)
def g_V():
    out = _apex(0, 640, 0, H, 98, 24, up=False)
    out += serif(49, 98, H, top=True, br=16)
    out += serif(628, 24, H, top=True, br=12)
    return out


@glyph("W", 0x57)
def g_W():
    out = _apex(0, 540, 0, H, 96, 22, up=False) + _apex(360, 900, 0, H, 96, 22, up=False)
    out += serif(48, 96, H, top=True, br=16)
    out += serif(408, 96, H, top=True, br=16, L=False)
    out += serif(889, 22, H, top=True, br=12)
    return out


@glyph("X", 0x58)
def g_X():
    out = [diag(500, 10, 0, H, 98), diag(70, 566, 0, H, 24)]
    out += serif(59, 98, H, top=True, br=14) + serif(549, 98, 0, br=14)
    out += serif(578, 24, H, top=True, br=10) + serif(82, 24, 0, br=10)
    return out


@glyph("Y", 0x59)
def g_Y():
    out = [poly([(10, H), (108, H), (377, 330), (283, 330)]),
           poly([(626, H), (650, H), (377, 330), (330, 330)])]
    out += cstem(330, 0, 350, top=NONE)
    out += serif(59, 98, H, top=True, br=14) + serif(638, 24, H, top=True, br=10)
    return out


@glyph("Z", 0x5A)
def g_Z():
    out = [rect(40, H - HC, 560, H), rect(20, 0, 580, HC)]
    out.append(poly([(20, 0), (118, 0), (564, H), (466, H)]))
    out.append(wedge(40, H - HC, flip=True))
    out.append(wedge(580, HC, down=False, ln=140))
    return out


# ---- lowercase

def o_ring(cx=240, cy=220, rx=195, ry=219, wm=SL + 6):
    return ring(cx, cy, rx, ry, wm, HL)


@glyph("a", 0x61, lsb=34, rsb=30)
def g_a():
    out = [rect(380 - SL / 2, 0, 380 + SL / 2, 300)]
    hook = arc(245, 300, 135, 140, 0, 150)
    out.append(stroke(hook, SL, HL))
    ex, ey = hook[-1]
    out.append(ball(ex + 22, ey - 12, 42))
    bowl = arc(205, 132, 150, 132, 78, 338)
    out.append(stroke(bowl, SL - 4, HL))
    out.append(stroke(lerp(bowl[0], (345, 255), 6), None, None, wfun=lambda t, tx, ty: HL + 4))
    out.append(poly([(340, 0), (420, 0), (440, 0), (440, 10), (420, 40)]))
    return out


@glyph("b", 0x62, lsb=30)
def g_b():
    r, _ = o_ring(280)
    return lstem(40, 0, ASC, top=LEFT, bot=NONE) + [r]


@glyph("c", 0x63, lsb=34, rsb=26)
def g_c():
    return _c()


def _c(ballend=True):
    pts = arc(230, 220, 190, 219, 42, 318)
    out = [stroke(pts, SL + 6, HL)]
    if ballend:
        ex, ey = pts[0]
        out.append(ball(ex - 24, ey - 30, 43))
    return out, pts[0]


GLYPHS["c"] = (0x63, lambda: _c()[0], 34, 26)


@glyph("d", 0x64, lsb=34, rsb=30)
def g_d():
    r, _ = o_ring(235)
    return [r] + lstem(432, 0, ASC, top=LEFT, bot=RIGHT)


@glyph("e", 0x65, lsb=34, rsb=30)
def g_e():
    cx, cy, rx, ry = 235, 220, 195, 219
    pts = arc(cx, cy, rx, ry, 14, 330)
    out = [stroke(pts, SL + 6, HL)]
    y = cy + ry * math.sin(math.radians(14)) ** (2 / 2.25)
    out.append(rect(cx - rx, y - 6, cx + rx + SL / 2 - 4, y + 6))
    return out


@glyph("f", 0x66, lsb=24, rsb=0)
def g_f():
    out = lstem(110, 0, 560, top=NONE, bot=(True, True))
    hook = join(lerp((110, 552), (110, 560), 2), arc(235, 560, 125, 172, 180, 35))
    out.append(stroke(hook, SL, HL))
    ex, ey = hook[-1]
    out.append(ball(ex - 6, ey - 34, 42))
    out.append(rect(20, X - HL, 270, X))
    return out


@glyph("g", 0x67, lsb=34, rsb=30)
def g_g():
    r, _ = o_ring(235, 230, 190, 212)
    stem = join(lerp((430, X), (430, -80)), arc(255, -80, 175, 132, 0, -160))
    out = [r, stroke(stem, SL, HL)]
    ex, ey = stem[-1]
    out.append(ball(ex + 14, ey + 26, 42))
    out += serif(430, SL, X, top=True, L=False, R=True, ser=SER_L)
    return out


def shoulder(x0, x1, y_join=300, wm=SL):
    cx = (x0 + x1) / 2
    rx = (x1 - x0) / 2
    pts = join(arc(cx, y_join, rx, X - y_join - 4, 165, 0), lerp((x1, y_join), (x1, 0)))
    return stroke(pts, wm, HL)


@glyph("h", 0x68, lsb=30)
def g_h():
    return lstem(40, 0, ASC, top=LEFT) + [shoulder(40, 425)] + serif(425, SL, 0, ser=SER_L)


@glyph("i", 0x69, lsb=30)
def g_i():
    return lstem(40, top=LEFT) + [ball(42, 610, 46)]


@glyph("j", 0x6A, lsb=-20, rsb=30)
def g_j():
    out = lstem(120, -100, X, top=LEFT, bot=NONE)
    hook = join(lerp((120, -95), (120, -100), 2), arc(0, -100, 120, 112, 0, -160))
    out.append(stroke(hook, SL, HL))
    ex, ey = hook[-1]
    out.append(ball(ex + 8, ey + 22, 40))
    out.append(ball(122, 610, 46))
    return out


@glyph("k", 0x6B, lsb=30, rsb=24)
def g_k():
    out = lstem(40, 0, ASC, top=LEFT)
    out.append(diag(62, 310, 140, X, 22))
    out += serif(321, 22, X, top=True, ser=SER_L, br=8)
    out.append(diag(140, 316, 260, 0, 90))
    out += serif(361, 90, 0, ser=SER_L, br=12)
    return out


@glyph("l", 0x6C, lsb=30)
def g_l():
    return lstem(40, 0, ASC, top=LEFT)


@glyph("m", 0x6D, lsb=30)
def g_m():
    out = lstem(40, top=LEFT) + [shoulder(40, 370), shoulder(370, 700)]
    out += serif(370, SL, 0, ser=SER_L) + serif(700, SL, 0, ser=SER_L)
    return out


@glyph("n", 0x6E, lsb=30)
def g_n():
    return lstem(40, top=LEFT) + [shoulder(40, 425)] + serif(425, SL, 0, ser=SER_L)


@glyph("o", 0x6F, lsb=34, rsb=34)
def g_o():
    return [o_ring()[0]]


@glyph("p", 0x70, lsb=30)
def g_p():
    r, _ = o_ring(280)
    return lstem(40, DSC, X, top=LEFT) + [r]


@glyph("q", 0x71, lsb=34, rsb=30)
def g_q():
    r, _ = o_ring(235)
    return [r] + lstem(432, DSC, X, top=RIGHT)


def _r_parts(ballend=True):
    out = lstem(40, top=LEFT, bot=(True, True))
    pts = arc(170, 300, 132, X - 304, 165, 25)
    out.append(stroke(pts, SL - 6, HL))
    if ballend:
        ex, ey = pts[-1]
        out.append(ball(ex - 6, ey - 30, 40))
    return out, pts[-1]


GLYPHS["r"] = (0x72, lambda: _r_parts()[0], 30, 16)


def _s_parts():
    return _S(200, (333,), (148, 107), (113,), (163, 119), SL + 2, HL, (32, 100))


GLYPHS["s"] = (0x73, _s_parts, 34, 34)


def _t_parts(cross=True, top=True):
    x = 90
    out = [rect(x - SL / 2, 120, x + SL / 2, 590 if top else X)]
    if top:
        out[0] = diff(out[0], poly([(x - SL / 2 - 1, 591), (x + SL / 2 + 1, 591), (x - SL / 2 - 1, 520)]))
    tail = join(lerp((x, 125), (x, 120), 2), arc(x + 125, 120, 125, 126, 180, 335))
    out.append(stroke(tail, SL, HL))
    if cross:
        out.append(rect(25, X - HL, 255, X))
    return out


GLYPHS["t"] = (0x74, _t_parts, 14, 14)


@glyph("u", 0x75, lsb=30)
def g_u():
    pts = join(lerp((40, X), (40, 190)), arc(232, 190, 192, 196, 180, 340))

    def wm(t):
        if t < 0.6:
            return SL
        u = min(1, (t - 0.6) / 0.25)
        return SL + (20 - SL) * u
    out = [stroke(pts, wm, HL)]
    out += serif(40, SL, X, top=True, ser=SER_L)
    out += lstem(425, top=LEFT, bot=RIGHT)
    return out


@glyph("v", 0x76, lsb=26, rsb=26)
def g_v():
    out = _apex(0, 470, 0, X, 88, 22, up=False)
    out += serif(44, 88, X, top=True, ser=SER_L, br=12)
    out += serif(459, 22, X, top=True, ser=SER_L, br=8)
    return out


@glyph("w", 0x77, lsb=26, rsb=26)
def g_w():
    out = _apex(0, 410, 0, X, 86, 20, up=False) + _apex(290, 700, 0, X, 86, 20, up=False)
    out += serif(43, 86, X, top=True, ser=SER_L, br=12)
    out += serif(333, 86, X, top=True, ser=SER_L, br=12, L=False)
    out += serif(690, 20, X, top=True, ser=SER_L, br=8)
    return out


@glyph("x", 0x78, lsb=26, rsb=26)
def g_x():
    out = [diag(370, 10, 0, X, 88), diag(66, 418, 0, X, 22)]
    out += serif(54, 88, X, top=True, ser=SER_L, br=10) + serif(414, 88, 0, ser=SER_L, br=10)
    out += serif(429, 22, X, top=True, ser=SER_L, br=8) + serif(77, 22, 0, ser=SER_L, br=8)
    return out


@glyph("y", 0x79, lsb=26, rsb=26)
def g_y():
    out = [poly([(0, X), (88, X), (262, 0), (174, 0)])]
    out.append(poly([(444, X), (470, X), (162, -190), (136, -190)]))
    out.append(ball(128, -178, 40))
    out += serif(44, 88, X, top=True, ser=SER_L, br=12)
    out += serif(459, 22, X, top=True, ser=SER_L, br=8)
    return out


@glyph("z", 0x7A, lsb=30, rsb=30)
def g_z():
    out = [rect(30, X - HL, 400, X), rect(20, 0, 420, HL)]
    out.append(poly([(20, 0), (106, 0), (410, X), (324, X)]))
    out.append(wedge(30, X - HL, flip=True, ln=95, w=26))
    out.append(wedge(420, HL, down=False, ln=105, w=26))
    return out


# ---- ligatures (loop joins)

def _loop_into_t(start, tx, ctrl):
    """Hairline loop rising from `start`, curling over and dropping into the t stem at tx."""
    pts = spline([start] + ctrl + [(tx, 600), (tx, 545)], n=16)

    def w(t, tx_, ty):
        base = HL + (34 - HL) * abs(ty) ** 1.5
        if t > 0.86:
            u = (t - 0.86) / 0.14
            base = base + (SL - base) * u * u * abs(ty)
        return base
    return stroke(pts, None, None, wfun=w)


def _lig(parts_a, adv_a, parts_b, dx_b):
    return parts_a + [tr(p, adv_a + dx_b) for p in parts_b]


def _t_body(dx):
    return [tr(p, dx) for p in _t_parts(top=False)] + [tr(rect(90 - SL / 2, X - 2, 90 + SL / 2, 570), dx)]


@glyph("c_t", lsb=34, rsb=20)
def g_ct():
    c, (ex, ey) = _c(ballend=False)
    dx = 400
    tx = dx + 90
    loop = _loop_into_t((ex, ey), tx, [(tx - 85, ey + 110), (tx - 12, 600), (tx + 78, 720), (tx + 50, 826), (tx - 40, 822), (tx - 74, 734), (tx - 22, 646)])
    return c + _t_body(dx) + [loop]


@glyph("r_t", lsb=30, rsb=20)
def g_rt():
    r, (ex, ey) = _r_parts(ballend=False)
    dx = 300
    tx = dx + 90
    loop = _loop_into_t((ex, ey), tx, [(tx - 85, ey + 110), (tx - 12, 600), (tx + 78, 720), (tx + 50, 826), (tx - 40, 822), (tx - 74, 734), (tx - 22, 646)])
    return r + _t_body(dx) + [loop]


@glyph("s_t", lsb=34, rsb=20)
def g_st():
    s = _s_parts()
    # top terminal of the s sits at roughly the 28 degree point of the top bowl
    a = math.radians(28)
    ex = 200 + 148 * math.cos(a) ** (2 / 2.25)
    ey = 333 + 107 * math.sin(a) ** (2 / 2.25)
    s = s[:1] + s[2:]       # drop the top beak; the loop replaces it
    dx = 390
    tx = dx + 90
    loop = _loop_into_t((ex, ey), tx, [(tx - 85, ey + 110), (tx - 12, 600), (tx + 78, 720), (tx + 50, 826), (tx - 40, 822), (tx - 74, 734), (tx - 22, 646)])
    return s + _t_body(dx) + [loop]


@glyph("l_l", lsb=30, rsb=40)
def g_ll():
    gap = 200
    out = lstem(40, 0, 640, top=NONE) + lstem(40 + gap, 0, 640, top=NONE)
    arch = spline([(40, 600), (40, 690), (78, 778), (140, 806), (202, 778), (240, 690), (240, 600)], n=14)

    def w(t, tx, ty):
        edge = max(0.0, 1 - min(t, 1 - t) / 0.22)
        thick = 30 + (SL - 30) * edge * edge
        return HL + (thick - HL) * abs(ty) ** 1.5
    out.append(stroke(arch, None, None, wfun=w))
    flick = spline([(180, 795), (255, 826), (335, 815), (372, 772)], n=12)
    out.append(stroke(flick, None, None, wfun=lambda t, tx, ty: HL + 8 * math.sin(math.pi * t)))
    out.append(ball(362, 764, 26))
    return out


# ---- figures

@glyph("zero", 0x30)
def g_zero():
    return [ring(270, DIG / 2, 220, DIG / 2 + 4, 88, HC)[0]]


@glyph("one", 0x31, lsb=60, rsb=60)
def g_one():
    out = cstem(220, 0, DIG, w=86, top=NONE, bot=(True, True), ser=(12, 80, 26))
    out.append(poly([(177, DIG), (220, DIG), (60, 560), (50, 572)]))
    return out


@glyph("two", 0x32)
def g_two():
    top = arc(270, 490, 195, 186, 162, -38)
    a = top[-1]
    pts = join(top, spline([a, (330, 270), (160, 110), (70, 8)], n=16))
    out = [stroke(pts, 90, HC)]
    sx, sy = top[0]
    out.append(ball(sx + 32, sy - 10, 46))
    out.append(rect(56, 0, 490, HC))
    out.append(wedge(490, HC, down=False, ln=125))
    return out


@glyph("three", 0x33)
def g_three():
    top = join(arc(255, 515, 175, 165, 158, -90), lerp((255, 350), (185, 350), 4))
    bot = join(lerp((185, 356), (255, 356), 4), arc(255, 182, 210, 180, 90, -158))
    out = [stroke(top, 84, HC), stroke(bot, 92, HC)]
    sx, sy = top[0]
    out.append(ball(sx + 30, sy - 12, 42))
    ex, ey = bot[-1]
    out.append(ball(ex + 30, ey + 14, 46))
    return out


@glyph("four", 0x34)
def g_four():
    out = cstem(410, 0, DIG, w=88, top=NONE, ser=(12, 50, 22))
    out.append(poly([(352, DIG), (380, DIG), (40, 196), (12, 196)]))
    out.append(rect(12, 186, 540, 198))
    return out


@glyph("five", 0x35)
def g_five():
    out = [rect(120, DIG - HC, 450, DIG), wedge(450, DIG - HC, ln=90), rect(110, 395, 132, DIG)]
    bowl = join(spline([(121, 405), (190, 425), (270, 432)], n=8), arc(270, 225, 215, 207, 90, -152))
    out.append(stroke(bowl, 92, HC))
    ex, ey = bowl[-1]
    out.append(ball(ex + 30, ey + 14, 46))
    return out


def _six():
    r, _ = ring(280, 215, 205, 219, 90, HC)
    rise = spline([(78, 220), (92, 420), (190, 610), (330, 680), (420, 660)], n=14)
    out = [r, stroke(rise, 88, HC)]
    out.append(ball(406, 636, 44))
    return out


GLYPHS["six"] = (0x36, _six, 40, 40)


@glyph("seven", 0x37)
def g_seven():
    out = [rect(40, DIG - HC, 500, DIG), wedge(40, DIG - HC, flip=True, ln=110)]
    pts = spline([(496, DIG - 6), (430, 520), (300, 260), (230, 0)], n=16)
    out.append(stroke(pts, 96, HC))
    return out


@glyph("eight", 0x38)
def g_eight():
    a, _ = ring(270, 520, 168, 160, 84, HC)
    b, _ = ring(270, 185, 200, 189, 92, HC)
    return [a, b]


@glyph("nine", 0x39)
def g_nine():
    return [xform(p, (-1, 0, 0, -1, 560, DIG)) for p in _six()]


# ---- punctuation & symbols

DOT = 46


@glyph("period", 0x2E, lsb=50, rsb=50)
def g_period():
    return [ball(0, DOT, DOT)]


def _comma_shape(x, y):
    tail = spline([(x + 34, y - 6), (x + 34, y - 70), (x - 20, y - 150)], n=12)
    return [ball(x, y, DOT), stroke(tail, None, None, wfun=lambda t, tx, ty: 44 * (1 - t) + 8)]


@glyph("comma", 0x2C, lsb=50, rsb=50)
def g_comma():
    return _comma_shape(0, DOT)


@glyph("colon", 0x3A, lsb=50, rsb=50)
def g_colon():
    return [ball(0, DOT, DOT), ball(0, X - DOT, DOT)]


@glyph("semicolon", 0x3B, lsb=50, rsb=50)
def g_semicolon():
    return _comma_shape(0, DOT) + [ball(0, X - DOT, DOT)]


@glyph("exclam", 0x21, lsb=60, rsb=60)
def g_exclam():
    return [poly([(0, H), (84, H), (50, 190), (34, 190)]), ball(42, DOT, DOT)]


@glyph("question", 0x3F)
def g_question():
    hook = join(arc(230, 520, 170, 180, 160, -70), spline([(288, 352), (230, 300), (225, 190)], n=10))
    out = [stroke(hook, 84, HC)]
    sx, sy = hook[0]
    out.append(ball(sx + 30, sy - 10, 42))
    out.append(ball(226, DOT, DOT))
    return out


def _tear(x, y, up=True):
    shapes = _comma_shape(x, y)
    if not up:
        shapes = [xform(p, (-1, 0, 0, -1, 2 * x, 2 * y - 40)) for p in shapes]
    return shapes


@glyph("quoteright", 0x2019, lsb=50, rsb=50)
def g_quoteright():
    return _tear(0, 650)


@glyph("quoteleft", 0x2018, lsb=50, rsb=50)
def g_quoteleft():
    return _tear(0, 650, up=False)


@glyph("quotedblright", 0x201D, lsb=50, rsb=50)
def g_qdr():
    return _tear(0, 650) + _tear(130, 650)


@glyph("quotedblleft", 0x201C, lsb=50, rsb=50)
def g_qdl():
    return _tear(0, 650, up=False) + _tear(130, 650, up=False)


@glyph("quotesingle", 0x27, lsb=60, rsb=60)
def g_quotesingle():
    return [poly([(0, H + 20), (60, H + 20), (36, 470), (24, 470)])]


@glyph("quotedbl", 0x22, lsb=60, rsb=60)
def g_quotedbl():
    return [poly([(0, H + 20), (60, H + 20), (36, 470), (24, 470)]),
            poly([(120, H + 20), (180, H + 20), (156, 470), (144, 470)])]


@glyph("hyphen", 0x2D, lsb=40, rsb=40)
def g_hyphen():
    return [rect(0, 232, 240, 262)]


@glyph("endash", 0x2013, lsb=0, rsb=0)
def g_endash():
    return [rect(0, 236, 500, 258)]


@glyph("emdash", 0x2014, lsb=0, rsb=0)
def g_emdash():
    return [rect(0, 236, 1000, 258)]


@glyph("parenleft", 0x28, lsb=60, rsb=30)
def g_parenleft():
    return [stroke(arc(330, 270, 290, 500, 122, 238, sq=2), 70, HC)]


@glyph("parenright", 0x29, lsb=30, rsb=60)
def g_parenright():
    return [xform(p, (-1, 0, 0, 1, 0, 0)) for p in g_parenleft()]


@glyph("slash", 0x2F, lsb=10, rsb=10)
def g_slash():
    return [diag(0, 330, -80, 760, 24)]


@glyph("plus", 0x2B)
def g_plus():
    return [rect(0, 285, 460, 299), rect(216, 62, 244, 522)]


@glyph("equal", 0x3D)
def g_equal():
    return [rect(0, 350, 460, 362), rect(0, 220, 460, 232)]


@glyph("asterisk", 0x2A)
def g_asterisk():
    out = []
    for ang in (90, 18, 162, 234, 306):
        a = math.radians(ang)
        tip = (150 + 140 * math.cos(a), 560 + 140 * math.sin(a))
        out.append(stroke(spline([(150, 560), tip], n=6), None, None, wfun=lambda t, tx, ty: 10 + 30 * t * (1 - t) * 4 * (0.6 + 0.4 * t)))
    return out


@glyph("percent", 0x25)
def g_percent():
    a, _ = ring(140, 540, 100, 150, 54, 10)
    b, _ = ring(560, 160, 100, 150, 54, 10)
    return [a, b, diag(100, 576, 0, H, 22)]


@glyph("ampersand", 0x26)
def g_ampersand():
    pts = spline([(640, 0), (500, 110), (300, 330), (180, 470), (185, 615), (275, 692), (370, 625),
                  (345, 500), (215, 400), (90, 270), (80, 115), (200, 4), (370, 22), (480, 150), (540, 300)], n=10)
    return [stroke(pts, 92, HC)]


@glyph("sterling", 0xA3)
def g_sterling():
    pts = spline([(430, 600), (350, 690), (250, 665), (210, 520), (230, 300), (190, 110), (90, 6)], n=12)
    out = [stroke(pts, 90, HC)]
    sx, sy = pts[0]
    out.append(ball(sx - 18, sy - 18, 42))
    out.append(rect(60, 0, 480, HC))
    out.append(wedge(480, HC, down=False, ln=120))
    out.append(rect(80, 330, 380, 342))
    return out


@glyph("dollar", 0x24)
def g_dollar():
    return _S(260, (540,), (195, 160), (180,), (215, 178), 88, HC, (36, 120)) + [rect(262, -70, 274, 780)]


@glyph("numbersign", 0x23)
def g_numbersign():
    return [diag(120, 220, 0, H, 22), diag(320, 420, 0, H, 22),
            rect(40, 440, 520, 452), rect(20, 240, 500, 252)]


GLYPH_SPACE = 240


# ------------------------------------------------------------------- build

KERN = """
pos A [V W Y] -70; pos A T -60; pos A [v w y] -40; pos A [quoteright quotedblright] -60;
pos [V W] A -70; pos Y A -80; pos T A -60;
pos T [a c e o s c_t s_t] -80; pos T [r u v w y z r_t] -60; pos T [period comma] -80;
pos [V W] [a e o c] -50; pos Y [a e o c] -70; pos [V W Y] [period comma] -80;
pos L [T V W Y] -70; pos L [quoteright quotedblright] -80;
pos P A -50; pos P [period comma] -100; pos F [a e o] -30; pos F [period comma] -80;
pos R [T V W Y] -20; pos [r v w y] [period comma] -50;
pos [quoteleft quotedblleft] A -60;
"""

FEA = """
languagesystem DFLT dflt;
languagesystem latn dflt;
feature liga {
    sub c t by c_t;
    sub r t by r_t;
    sub s t by s_t;
    sub l l by l_l;
} liga;
feature kern {
%s
} kern;
""" % KERN


def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    paths, metrics, cmap = {}, {}, {}
    order = [".notdef", "space"]

    nd = diff(rect(50, 0, 450, H), rect(90, 40, 410, H - 40))
    paths[".notdef"] = nd
    metrics[".notdef"] = (500, 50)
    paths["space"] = Path()
    metrics["space"] = (GLYPH_SPACE, 0)
    cmap[0x20] = "space"
    cmap[0xA0] = "space"

    for name, (uni, fn, lsb, rsb) in GLYPHS.items():
        p = union(fn())
        xmin, ymin, xmax, ymax = p.bounds
        p = tr(p, lsb - xmin)
        adv = round(xmax - xmin + lsb + rsb)
        paths[name] = p
        metrics[name] = (adv, round(lsb))
        order.append(name)
        if uni:
            cmap[uni] = name

    charstrings = {}
    ymax_all, ymin_all = 0, 0
    for name in order:
        pen = T2CharStringPen(metrics[name][0], None)
        paths[name].draw(pen)
        charstrings[name] = pen.getCharString()
        if name != "space":
            b = paths[name].bounds
            ymax_all = max(ymax_all, b[3])
            ymin_all = min(ymin_all, b[1])

    fb = FontBuilder(UPM, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupCFF(PSNAME, {"FullName": f"{FAMILY} {STYLE}"}, charstrings, {})
    # CFF lsb must match the outline's xMin
    hmtx = {}
    for name in order:
        adv = metrics[name][0]
        b = paths[name].bounds if name != "space" else (0, 0, 0, 0)
        hmtx[name] = (adv, round(b[0]))
    fb.setupHorizontalMetrics(hmtx)
    fb.setupHorizontalHeader(ascent=ASC + 60, descent=DSC - 30)
    fb.setupNameTable({
        "familyName": FAMILY,
        "styleName": STYLE,
        "uniqueFontIdentifier": f"{PSNAME};{VERSION}",
        "fullName": f"{FAMILY} {STYLE}",
        "psName": PSNAME,
        "version": f"Version {VERSION}",
        "description": "High-contrast display serif with loop ligatures, made for Cake Art Collective.",
    })
    fb.setupOS2(sTypoAscender=ASC + 60, sTypoDescender=DSC - 30, sTypoLineGap=150,
                usWinAscent=int(max(ymax_all, ASC + 60)) + 10, usWinDescent=int(-min(ymin_all, DSC - 30)) + 10,
                sxHeight=X, sCapHeight=H, achVendID="NONE", fsType=0, usWeightClass=400)
    fb.setupPost()
    addOpenTypeFeaturesFromString(fb.font, FEA)

    otf = os.path.join(outdir, f"{PSNAME}.otf")
    fb.save(otf)
    fb.font.flavor = "woff2"
    fb.font.save(os.path.join(outdir, f"{PSNAME}.woff2"))
    fb.font.flavor = None
    return otf, paths, metrics


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    otf, _, _ = build(out)
    print("wrote", otf)
