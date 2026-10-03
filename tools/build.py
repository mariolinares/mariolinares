#!/usr/bin/env python3
"""Draw the GitHub profile panels from design/tokens.json.

    python tools/build.py              writes assets/<panel>-dark.svg and assets/<panel>-light.svg
    python tools/build.py --ds DIR     also writes the design-system previews under DIR/components

The same drawing code feeds both outputs: README panels get hex colours and subset fonts
embedded as base64 (GitHub shows SVG through <img>, which loads nothing external); the
design-system previews get var(--token) colours and the fonts the preview frame preloads.
"""

from __future__ import annotations

import argparse
import base64
import html
import io
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

import content as C

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "design"
ASSETS = ROOT / "assets"
TOKENS = json.loads((DESIGN / "tokens.json").read_text())

W = 880
PAD = 40
RIGHT = W - PAD
FAMILY_KEY = {"Instrument Serif": "display", "Instrument Sans": "sans", "DM Mono": "mono"}
THEMES = [t["id"] for t in TOKENS["color"]["themes"]]
COLORS = {t["name"]: t["value"] for t in TOKENS["color"]["tokens"]}
WARNINGS: list[str] = []


def n(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def px(v) -> float:
    return float(v) if isinstance(v, (int, float)) else float(str(v).removesuffix("px"))


class Face:
    def __init__(self, family: str, path: Path):
        self.family, self.path = family, path
        font = TTFont(path)
        self.upm = font["head"].unitsPerEm
        self.cmap = font.getBestCmap()
        self.adv = font["hmtx"].metrics

    def width(self, s: str, size: float) -> float:
        total = 0
        for ch in s:
            glyph = self.cmap.get(ord(ch))
            if glyph is None:
                WARNINGS.append(f"{self.family} has no glyph for {ch!r}")
                total += self.upm * 0.5
            else:
                total += self.adv[glyph][0]
        return total * size / self.upm


FACES: dict[tuple, Face] = {}
for f in TOKENS["type"]["fonts"]:
    key = (FAMILY_KEY[f["family"]], int(f["weight"]), f.get("style", "normal"))
    FACES[key] = Face(f["family"], DESIGN / f["file"])


class Style:
    def __init__(self, name: str, family: str, spec: dict):
        self.name, self.fam = name, family
        self.size = px(spec["fontSize"])
        self.weight = int(spec.get("fontWeight", 400))
        self.italic = spec.get("fontStyle") == "italic"
        ls = spec.get("letterSpacing", 0)
        self.ls = float(ls[:-2]) * self.size if isinstance(ls, str) and ls.endswith("em") else px(ls)
        self.key = (family, self.weight, "italic" if self.italic else "normal")
        self.face = FACES[self.key]

    def width(self, s: str) -> float:
        return self.face.width(s, self.size) + self.ls * max(len(s) - 1, 0)


STYLES: dict[str, Style] = {}
for group in TOKENS["type"]["groups"]:
    for spec in group["styles"]:
        STYLES[spec["name"]] = Style(spec["name"], spec.get("family", group["family"]), spec)


def wrap(text: str, style: str, width: float) -> list[str]:
    st, lines, cur = STYLES[style], [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and st.width(trial) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + ([cur] if cur else [])


# ── marks ───────────────────────────────────────────────────────────────────────

LOGOS = DESIGN / "logos"


def svg_path(file: Path) -> tuple[str, tuple[float, float, float, float]]:
    """The single path of a Simple Icons file and its bounds."""
    d = re.search(r'<path d="([^"]+)"', file.read_text()).group(1)
    pen = BoundsPen(None)
    parse_path(d, pen)
    return d, pen.bounds


TECH = {f.stem: svg_path(f) for f in sorted((LOGOS / "tech").glob("*.svg"))}


def client_mark(stem: str):
    """('png', base64, aspect) for a CV mask, ('svg', d, bounds) for a vector, None for set type."""
    png, svg = LOGOS / "clients" / f"{stem}.png", LOGOS / "clients" / f"{stem}.svg"
    if png.exists():
        from struct import unpack

        raw = png.read_bytes()
        w, h = unpack(">II", raw[16:24])
        return ("png", base64.b64encode(raw).decode(), w / h)
    if svg.exists():
        d, b = svg_path(svg)
        return ("svg", d, b)
    return None


# ── canvas ──────────────────────────────────────────────────────────────────────


class Canvas:
    def __init__(self, w: float, h: float, alt: str):
        self.w, self.h, self.alt = w, h, alt
        self.body: list[str] = []
        self.used: dict[tuple, set] = defaultdict(set)
        self.css: list[str] = []

    def el(self, s: str) -> None:
        self.body.append(s)

    def rect(self, x, y, w, h, cls, rx=0):
        self.el(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(rx)}" class="{cls}"/>')

    def line(self, x1, y1, x2, y2, cls):
        self.el(f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" class="{cls}"/>')

    def circle(self, cx, cy, r, cls):
        self.el(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" class="{cls}"/>')

    def path(self, d, cls, extra=""):
        self.el(f'<path d="{d}" class="{cls}"{extra}/>')

    def glyph(self, x, y, size, slug, cls="f-ink-muted"):
        """A Simple Icons mark in a size×size box (its own 24-unit square)."""
        d, _ = TECH[slug]
        self.el(
            f'<svg x="{n(x)}" y="{n(y)}" width="{n(size)}" height="{n(size)}" viewBox="0 0 24 24">'
            f'<path d="{d}" class="{cls}"/></svg>'
        )

    def tinted(self, x, y, w, h, png_b64, cls, key):
        """A single-ink PNG mask, painted with a colour token."""
        mid = f"m-{key}"
        self.el(
            f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}">'
            f'<image href="data:image/png;base64,{png_b64}" x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"/>'
            f'</mask><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" class="{cls}" mask="url(#{mid})"/>'
        )

    def text(self, x, y, s, style, cls="f-ink", anchor="start") -> float:
        st = STYLES[style]
        self.used[st.key] |= set(s)
        a = "" if anchor == "start" else f' text-anchor="{anchor}"'
        self.el(f'<text x="{n(x)}" y="{n(y)}" class="t-{style} {cls}"{a}>{escape(s)}</text>')
        return st.width(s)


def color(name: str, theme: str) -> str:
    v = COLORS[name]
    return v if isinstance(v, str) else v.get(theme, v[THEMES[0]])


def font_face(key: tuple, chars: set) -> str:
    face = FACES[key]
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    opts.name_IDs = ["*"]
    opts.hinting = False
    font = TTFont(face.path)
    sub = subset.Subsetter(opts)
    sub.populate(text="".join(sorted(chars | {" "})))
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    return (
        f"@font-face{{font-family:'{face.family}';font-weight:{key[1]};font-style:{key[2]};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    )


def render(cv: Canvas, mode: str, theme: str | None = None) -> str:
    css: list[str] = []
    if mode == "file":
        css += [font_face(k, v) for k, v in sorted(cv.used.items())]
    for name in COLORS:
        v = f"var(--{name})" if mode == "var" else color(name, theme)
        css.append(f".f-{name}{{fill:{v}}}.s-{name}{{stroke:{v}}}")
    families = TOKENS["type"]["families"]
    for st in STYLES.values():
        fam = f"var(--font-{st.fam})" if mode == "var" else families[st.fam]
        italic = ";font-style:italic" if st.italic else ""
        css.append(
            f".t-{st.name}{{font-family:{fam};font-size:{n(st.size)}px;font-weight:{st.weight};"
            f"letter-spacing:{n(st.ls)}px{italic}}}"
        )
    css.append(".nf{fill:none}.w1{stroke-width:1}.w2{stroke-width:2}.cap{stroke-linecap:round}")
    css += cv.css
    size = f'width="{n(cv.w)}" height="{n(cv.h)}"'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n(cv.w)} {n(cv.h)}" {size} role="img">'
        f"<title>{escape(cv.alt)}</title><style>{''.join(css)}</style>{''.join(cv.body)}</svg>"
    )


# ── parts ───────────────────────────────────────────────────────────────────────


def frame(cv: Canvas) -> None:
    cv.rect(0.5, 0.5, cv.w - 1, cv.h - 1, "f-panel s-line w1", rx=16)


def ruler(cv: Canvas, y: float, x0: float = PAD, x1: float = RIGHT) -> None:
    """A hairline with cota ticks every 40px; a long tick every 200px."""
    cv.line(x0, y, x1, y, "s-line w1")
    for i, x in enumerate(range(int(x0), int(x1) + 1, 40)):
        cv.line(x, y, x, y + (8 if i % 5 == 0 else 4), "s-ink-faint w1")


def port(cv: Canvas, x, y, live=False) -> None:
    cv.circle(x, y, 3, f"f-panel {'s-signal' if live else 's-line-strong'} w1")


def icon_for(label: str) -> str | None:
    slug = C.TECH_ICONS.get(label)
    return slug if slug in TECH else None


def chip_width(label: str) -> float:
    return STYLES["chip"].width(label) + 20 + (20 if icon_for(label) else 0)


def chip(cv: Canvas, x, y, label, tone="default") -> float:
    w = chip_width(label)
    fill, stroke, ink = {
        "default": ("f-panel", "s-line-strong", "f-ink"),
        "accent": ("f-accent-wash", "s-accent", "f-accent"),
    }[tone]
    cv.rect(x + 0.5, y + 0.5, w - 1, 25, f"{fill} {stroke} w1", rx=4)
    slug, tx = icon_for(label), x + 10
    if slug:
        cv.glyph(x + 9, y + 6, 14, slug, "f-ink-muted" if tone == "default" else "f-accent")
        tx += 20
    cv.text(tx, y + 17.5, label, "chip", ink)
    return w


def chip_rows(labels, width) -> list[list[str]]:
    """Fewest rows that fit, then balanced so no chip is left alone on the last row."""

    def greedy(limit):
        rows, cur, used = [], [], 0.0
        for label in labels:
            w = chip_width(label)
            if cur and used + w > limit:
                rows.append(cur)
                cur, used = [], 0.0
            cur.append(label)
            used += w + 8
        return rows + ([cur] if cur else [])

    rows = greedy(width)
    if len(rows) > 1:
        target = (sum(chip_width(label) + 8 for label in labels) - 8) / len(rows)
        while target < width:
            balanced = greedy(target)
            if len(balanced) == len(rows):
                return balanced
            target += 4
    return rows


def chips(cv: Canvas, x, y, labels, width, tone="default") -> float:
    rows = chip_rows(labels, width)
    for r, row in enumerate(rows):
        cx = x
        for label in row:
            cx += chip(cv, cx, y + r * 34, label, tone) + 8
    return len(rows) * 34 - 8


def section_header(cv: Canvas, index: str, title: str, note: str, y: float = 0) -> float:
    cv.text(PAD, y + 52, f"{index} —", "label", "f-ink-muted")
    cv.text(PAD - 2, y + 100, title, "display-l", "f-ink")
    cv.text(RIGHT, y + 100, note, "label", "f-ink-muted", "end")
    ruler(cv, y + 124)
    return y + 124


# ── panels ──────────────────────────────────────────────────────────────────────


def hero() -> Canvas:
    H = C.HERO
    remotes = H["remotes"]
    alt = (
        f"{' '.join(H['name'])}. {H['lead']} Uso diario: {', '.join(H['daily_names'])}. "
        f"Mapa de un shell federado que carga remotos: {', '.join(r['name'] for r in remotes)}."
    )
    cv = Canvas(W, 460, alt)
    frame(cv)
    cv.text(PAD, 52, H["label_left"], "label", "f-ink-muted")
    cv.text(RIGHT, 52, H["label_right"], "label", "f-ink-muted", "end")
    ruler(cv, 68)

    # the name, the lead and the stack, left of x = 440
    xl = STYLES["display-xl"]
    step = xl.size * 0.92
    base = 68 + 24 + xl.size * 0.74
    for i, line in enumerate(H["name"]):
        cv.text(PAD - 5, base + i * step, line, "display-xl", "f-ink")
    y = base + step + 50
    for i, line in enumerate(wrap(H["lead"], "lead", 410)):
        cv.text(PAD, y + i * 30, line, "lead", "f-ink-muted")
    ry = cv.h - PAD - 20
    cv.text(PAD, ry - 14, H["daily_label"], "label", "f-ink-muted")
    for i, slug in enumerate(H["daily"]):
        cv.glyph(PAD + i * 36, ry, 20, slug, "f-ink")

    # the map: dot grid, host, routes, remotes, packets
    mx0, mx1 = 488, RIGHT
    for gx in range(mx0, mx1 + 1, 48):
        for gy in range(112, 433, 48):
            cv.circle(gx, gy, 1.2, "f-ink-faint")
    rw, rh, rstep = 128, 40, 56
    top = 110
    rx = mx1 - rw
    hw, hh = 112, 132
    mid = top + (len(remotes) - 1) * rstep / 2 + rh / 2
    hx, hy = mx0 + 8, mid - hh / 2

    routes = []
    for i, r in enumerate(remotes):
        ry = top + i * rstep + rh / 2
        py = hy + 22 + i * (hh - 44) / (len(remotes) - 1)
        x0, x1 = hx + hw, rx
        cx = (x0 + x1) / 2
        d = f"M{n(x0)},{n(py)} C{n(cx)},{n(py)} {n(cx)},{n(ry)} {n(x1)},{n(ry)}"
        back = f"M{n(x1)},{n(ry)} C{n(cx)},{n(ry)} {n(cx)},{n(py)} {n(x0)},{n(py)}"
        routes.append((r, d, back, py, ry))
    for r, d, _, _, _ in sorted(routes, key=lambda t: bool(t[0].get("live"))):
        cv.path(d, "nf " + ("s-signal w2" if r.get("live") else "s-line-strong w1"))

    cv.rect(hx, hy, hw, hh, "f-signal-wash s-signal w1", rx=8)
    cv.text(hx + 16, hy + 30, H["host"]["label"], "label", "f-signal")
    cv.circle(hx + hw - 18, hy + 26, 4, "f-signal")
    cv.circle(hx + hw - 18, hy + 26, 4, "f-signal pulse")
    cv.text(hx + 14, hy + 82, H["host"]["title"], "display-m", "f-ink")
    cv.text(hx + 16, hy + hh - 20, H["host"]["sub"], "chip", "f-ink-muted")

    for i, (r, _, back, py, ry) in enumerate(routes):
        live = bool(r.get("live"))
        y0 = top + i * rstep
        cv.rect(rx, y0, rw, rh, f"f-panel-raised {'s-signal' if live else 's-line-strong'} w1", rx=8)
        cv.text(rx + 16, y0 + 25, r["id"], "label", "f-ink-muted")
        cv.text(rx + 44, y0 + 26, r["name"], "body", "f-ink")
        port(cv, hx + hw, py, live)
        port(cv, rx, ry, live)
        cv.path(back, f"nf s-accent cap pk pk{i}", ' pathLength="100"')

    delays = [0, 1.3, 2.6, 3.9, 5.2, 6.5]
    cv.css.append(
        ".pk{stroke-width:6;stroke-dasharray:0.01 400;stroke-dashoffset:0;opacity:0}"
        ".pulse{transform-box:fill-box;transform-origin:center;opacity:0}"
        "@media (prefers-reduced-motion:no-preference){"
        ".pk{animation:pk 7.8s cubic-bezier(.5,0,.3,1) infinite}"
        + "".join(f".pk{i}{{animation-delay:{d}s}}" for i, d in enumerate(delays))
        + ".pulse{animation:pulse 2.6s ease-out infinite}}"
        "@keyframes pk{0%{stroke-dashoffset:0;opacity:0}4%{opacity:1}26%{opacity:1}"
        "30%{stroke-dashoffset:-100;opacity:0}100%{stroke-dashoffset:-100;opacity:0}}"
        "@keyframes pulse{0%{transform:scale(1);opacity:.7}100%{transform:scale(3.2);opacity:0}}"
    )
    return cv


CARD_W = (RIGHT - PAD - 32) / 2
CARD_IN = CARD_W - 48


def card_height(card: dict) -> float:
    title = wrap(card["title"], "display-m", CARD_IN)
    body = wrap(card["body"], "body", CARD_IN)
    rows = chip_rows(card["chips"], CARD_IN)
    return 56 + len(title) * 34 + 16 + len(body) * 24 + 20 + len(rows) * 34 + 18 + 76


def module_card(cv: Canvas, x: float, y: float, card: dict, h: float) -> None:
    live = bool(card.get("live"))
    cv.rect(x + 0.5, y + 0.5, CARD_W - 1, h - 1, "f-panel-raised s-line w1", rx=8)
    cv.text(x + 24, y + 34, card["id"], "label", "f-ink-muted")
    sw = STYLES["label"].width(card["status"])
    cv.text(x + CARD_W - 24, y + 34, card["status"], "label", "f-ink-muted", "end")
    dot = "f-accent" if card["status"] == "EN PRODUCCIÓN" else "f-panel-raised s-line-strong w1"
    cv.circle(x + CARD_W - 24 - sw - 12, y + 30, 3.5, dot)
    port(cv, x, y + 30, live)

    ty = y + 56 + 22
    for i, line in enumerate(wrap(card["title"], "display-m", CARD_IN)):
        cv.text(x + 23, ty + i * 34, line, "display-m", "f-ink")
    by = ty + (len(wrap(card["title"], "display-m", CARD_IN)) - 1) * 34 + 34
    body = wrap(card["body"], "body", CARD_IN)
    for i, line in enumerate(body):
        cv.text(x + 24, by + i * 24, line, "body", "f-ink-muted")
    cy = by + (len(body) - 1) * 24 + 22
    chips(cv, x + 24, cy, card["chips"], CARD_IN)

    my = y + h - 76
    cv.line(x + 24, my, x + CARD_W - 24, my, "s-line w1")
    slot = CARD_IN / len(card["metrics"])
    for i, (value, label) in enumerate(card["metrics"]):
        mx = x + 24 + i * slot
        cv.text(mx, my + 38, value, "metric", "f-ink")
        cv.text(mx, my + 58, label, "label", "f-ink-muted")
        if STYLES["label"].width(label) > slot - 8:
            WARNINGS.append(f"metric label too wide: {label}")


ACRONYMS = {"ts": "TS", "prs": "PRs", "adr": "ADR", "nx": "Nx", "angular": "Angular"}


def spoken(label: str) -> str:
    """A mono label as it reads in alt text: lower case, acronyms kept."""
    return " ".join(ACRONYMS.get(w, w) for w in label.lower().split())


def modules() -> Canvas:
    M = C.MODULES
    cards = M["cards"]
    rows = [cards[i:i + 2] for i in range(0, len(cards), 2)]
    heights = [max(card_height(c) for c in row) for row in rows]
    also_rows = (len(M["also"]) + 1) // 2
    h = 124 + 32 + sum(heights) + 32 * (len(rows) - 1) + 40 + 24 + also_rows * 28 + 40
    alt = f"{M['title']}. " + " ".join(
        f"{c['title']} ({c['status'].lower()}): {c['body']} Tecnologías: {', '.join(c['chips'])}. "
        + ", ".join(f"{v} {spoken(l)}" for v, l in c["metrics"]) + "."
        for c in cards
    ) + f" También: {'; '.join(M['also'])}. Código privado, demo bajo petición."
    cv = Canvas(W, h, alt)
    frame(cv)
    y = section_header(cv, M["index"], M["title"], M["note"]) + 32
    for row, rh in zip(rows, heights):
        for j, card in enumerate(row):
            module_card(cv, PAD + j * (CARD_W + 32), y, card, rh)
        y += rh + 32
    y += 8
    cv.text(PAD, y, M["also_label"], "label", "f-ink-muted")
    y += 24
    for i, item in enumerate(M["also"]):
        col, row = i % 2, i // 2
        x = PAD + col * (CARD_W + 32)
        port(cv, x + 3, y + row * 28 - 5)
        cv.text(x + 18, y + row * 28, item, "body", "f-ink")
    return cv


def principles() -> Canvas:
    P = C.PRINCIPLES
    cell_w = (RIGHT - PAD) / 2
    inner = cell_w - 56
    heights = [32 + 40 + len(wrap(b, "body", inner)) * 24 + 8 for _, _, b in P["items"]]
    row_h = [max(heights[0], heights[1]), max(heights[2], heights[3])]
    h = 124 + 24 + row_h[0] + 32 + row_h[1] + 32
    alt = f"{P['title']}. " + " ".join(f"{t}: {b}" for _, t, b in P["items"])
    cv = Canvas(W, h, alt)
    frame(cv)
    y0 = section_header(cv, P["index"], P["title"], P["note"]) + 24
    mid_x, mid_y = PAD + cell_w, y0 + row_h[0] + 16
    cv.line(mid_x, y0, mid_x, h - 32, "s-line w1")
    cv.line(PAD, mid_y, RIGHT, mid_y, "s-line w1")
    cv.circle(mid_x, mid_y, 4, "f-signal")
    for i, (idx, title, body) in enumerate(P["items"]):
        col, row = i % 2, i // 2
        x = PAD + col * cell_w + (0 if col == 0 else 32)
        y = y0 + (0 if row == 0 else row_h[0] + 32)
        cv.text(x, y + 22, idx, "label", "f-ink-muted")
        cv.text(x - 1, y + 62, title, "display-m", "f-ink")
        for k, line in enumerate(wrap(body, "body", inner)):
            cv.text(x, y + 92 + k * 24, line, "body", "f-ink-muted")
    return cv


def layers() -> Canvas:
    L = C.LAYERS
    lx, lw = PAD + 48, RIGHT - PAD - 48
    name_w = 172
    chip_w = lw - name_w - 40
    heights = [max(80, 24 + len(chip_rows(c, chip_w)) * 34 + 14) for _, _, c in L["layers"]]
    h = 124 + 32 + sum(heights) + 12 * (len(heights) - 1) + 40
    alt = f"{L['title']}, de la petición al despliegue. " + " ".join(
        f"{name}: {', '.join(c)}." for _, name, c in L["layers"]
    )
    cv = Canvas(W, h, alt)
    frame(cv)
    y = section_header(cv, L["index"], L["title"], L["note"]) + 32
    spine = PAD + 16
    first_mid = y + heights[0] / 2
    last_mid = y + sum(heights) + 12 * (len(heights) - 1) - heights[-1] / 2
    cv.line(spine, first_mid, spine, last_mid, "s-signal w2")
    for (lid, name, techs), lh in zip(L["layers"], heights):
        cv.rect(lx + 0.5, y + 0.5, lw - 1, lh - 1, "f-panel-raised s-line w1", rx=8)
        cmid = y + lh / 2
        cv.line(spine, cmid, lx, cmid, "s-signal w1")
        cv.circle(spine, cmid, 4, "f-signal")
        port(cv, lx, cmid, True)
        cv.text(lx + 20, cmid - 10, lid, "label", "f-ink-muted")
        cv.text(lx + 19, cmid + 22, name, "display-m", "f-ink")
        rows = chip_rows(techs, chip_w)
        cy = y + (lh - (len(rows) * 34 - 8)) / 2
        chips(cv, lx + name_w + 20, cy, techs, chip_w)
        y += lh + 12
    return cv


def timeline() -> Canvas:
    T = C.TIMELINE
    stations = T["stations"]
    col = (RIGHT - PAD) / len(stations)
    inner = col - 20
    where_lines = [wrap(s["where"], "small", inner) for s in stations]
    role_lines = [wrap(s["role"], "body-strong", inner) for s in stations]
    h = 124 + 56 + 56 + max(len(r) for r in role_lines) * 24 + max(len(w) for w in where_lines) * 20 + 56
    alt = f"{T['title']}. " + " ".join(f"{s['year']}: {s['role']}, {s['where']}." for s in stations)
    cv = Canvas(W, h, alt)
    frame(cv)
    y = section_header(cv, T["index"], T["title"], T["note"]) + 56
    xs = [PAD + i * col + 6 for i in range(len(stations))]
    brk = (xs[0] + xs[1]) / 2
    cv.line(PAD, y, brk - 7, y, "s-line-strong w2")
    cv.line(brk + 7, y, xs[-1], y, "s-line-strong w2")
    cv.line(xs[-2], y, xs[-1], y, "s-signal w2")
    cv.line(xs[-1], y, RIGHT, y, "s-signal w2")
    cv.el(f'<path d="M{n(brk - 7)},{n(y)} h0" class="nf"/>')
    for dx in (-7, 3):
        cv.line(brk + dx, y + 8, brk + dx + 4, y - 8, "s-ink-muted w1")
    for i, s in enumerate(stations):
        x, now = xs[i], bool(s.get("now"))
        if now:
            cv.circle(x, y, 9, "f-signal-wash s-signal w2")
            cv.circle(x, y, 4, "f-signal")
        else:
            cv.circle(x, y, 6, "f-panel s-line-strong w2")
        tx = x - 6
        cv.text(tx - 1, y + 56, s["year"], "display-m", "f-signal" if now else "f-ink")
        ry = y + 86
        for k, line in enumerate(role_lines[i]):
            cv.text(tx, ry + k * 24, line, "body-strong", "f-ink")
        wy = ry + len(role_lines[i]) * 24
        for k, line in enumerate(where_lines[i]):
            cv.text(tx, wy + k * 20, line, "small", "f-ink-muted")
    return cv


def clients() -> Canvas:
    K = C.CLIENTS
    cols = 5
    cell_w, cell_h = (RIGHT - PAD) / cols, 92
    rows = (len(K["logos"]) + cols - 1) // cols
    h = 124 + 24 + rows * cell_h + 24 + 48 + 32
    names = ", ".join(name for _, name in K["logos"])
    alt = f"{K['title']}: {names}. {K['employers_label'].capitalize()} {', '.join(K['employers'])}."
    cv = Canvas(W, h, alt)
    frame(cv)
    y0 = section_header(cv, K["index"], K["title"], K["note"]) + 24
    for r in range(rows + 1):
        cv.line(PAD, y0 + r * cell_h, RIGHT, y0 + r * cell_h, "s-line w1")
    for c in range(1, cols):
        cv.line(PAD + c * cell_w, y0, PAD + c * cell_w, y0 + rows * cell_h, "s-line w1")
    box_w, box_h, area = 112, 34, 112 * 22
    for i, (stem, name) in enumerate(K["logos"]):
        cx = PAD + (i % cols + 0.5) * cell_w
        cy = y0 + (i // cols + 0.5) * cell_h
        mark = client_mark(stem)
        if mark is None:
            label = name.upper()
            cv.text(cx, cy + 5, label, "body-strong", "f-ink-muted", "middle")
            continue
        kind = mark[0]
        if kind == "png":
            aspect = mark[2]
        else:
            x0, y0b, x1, y1 = mark[2]
            aspect = (x1 - x0) / (y1 - y0b)
        lh = min(box_h, (area / aspect) ** 0.5, box_w / aspect)
        lw = lh * aspect
        if kind == "png":
            cv.tinted(cx - lw / 2, cy - lh / 2, lw, lh, mark[1], "f-ink-muted", stem)
        else:
            x0, y0b, x1, y1 = mark[2]
            cv.el(
                f'<svg x="{n(cx - lw / 2)}" y="{n(cy - lh / 2)}" width="{n(lw)}" height="{n(lh)}" '
                f'viewBox="{n(x0)} {n(y0b)} {n(x1 - x0)} {n(y1 - y0b)}"><path d="{mark[1]}" class="f-ink-muted"/></svg>'
            )
    ey = y0 + rows * cell_h + 48
    lw = cv.text(PAD, ey, K["employers_label"], "label", "f-ink-muted")
    x = PAD + lw + 24
    for k, emp in enumerate(K["employers"]):
        if k:
            cv.circle(x - 13, ey - 6, 2, "f-ink-faint")
        x += cv.text(x, ey + 2, emp, "body-strong", "f-ink") + 26
    return cv


def contact() -> Canvas:
    K = C.CONTACT
    alt = f"{' '.join(K['title'])} " + " · ".join(f"{ {'LINKEDIN': 'LinkedIn'}.get(k, k.capitalize())}: {v}" for k, v in K["rows"])
    cv = Canvas(W, 236, alt)
    frame(cv)
    cv.text(PAD + 32, 56, K["label"], "label", "f-ink-muted")
    cv.line(PAD, 51, PAD + 20, 51, "s-signal w2")
    cv.circle(PAD + 20, 51, 6, "f-signal-wash s-signal w2")
    for i, line in enumerate(K["title"]):
        cv.text(PAD - 2, 116 + i * 48, line, "display-l", "f-ink")
    x = 520
    ruler_x = x - 24
    cv.line(ruler_x, 40, ruler_x, cv.h - 40, "s-line w1")
    for i, (k, v) in enumerate(K["rows"]):
        y = 76 + i * 52
        cv.text(x, y, k, "label", "f-ink-muted")
        cv.text(x, y + 24, v, "body", "f-ink")
    return cv


def chip_specimen() -> Canvas:
    cv = Canvas(W, 120, "Chips de tecnología: por defecto y acento.")
    frame(cv)
    w = chips(cv, PAD, 32, ["@angular/ssr", "@angular-architects/native-federation", "nx", "vitest", "playwright"], RIGHT - PAD)
    chips(cv, PAD, 32 + w + 16, ["remote/logística", "remote/industria"], RIGHT - PAD, "accent")
    return cv


def header_specimen() -> Canvas:
    cv = Canvas(W, 156, "Cabecera de sección: 01, Lo que construyo.")
    frame(cv)
    section_header(cv, "01", "Lo que construyo", "CÓDIGO PRIVADO · DEMO BAJO PETICIÓN")
    return cv


def card_specimen() -> Canvas:
    card = C.MODULES["cards"][0]
    h = card_height(card)
    cv = Canvas(CARD_W + 80, h + 80, f"Tarjeta de módulo: {card['title']}.")
    frame(cv)
    module_card(cv, PAD, PAD, card, h)
    return cv


PANELS = {
    "hero": hero,
    "modulos": modules,
    "principios": principles,
    "capas": layers,
    "trayectoria": timeline,
    "clientes": clients,
    "contacto": contact,
}

PREVIEWS = {
    "SystemMap": ("Paneles", hero),
    "SectionHeader": ("Partes", header_specimen),
    "ModuleCard": ("Partes", card_specimen),
    "Chip": ("Partes", chip_specimen),
    "PrincipleGrid": ("Paneles", principles),
    "LayerStack": ("Paneles", layers),
    "TransitLine": ("Paneles", timeline),
    "LogoWall": ("Paneles", clients),
    "ContactStrip": ("Paneles", contact),
}


def preview_html(group: str, name: str, cv: Canvas) -> str:
    height = int(cv.h * 0.82) + 40
    return (
        f'<!-- @dsCard group="{group}" height={height} width={int(cv.w) + 32} -->\n'
        "<!doctype html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{name}</title>\n"
        "<style>html,body{margin:0;background:var(--canvas)}body{padding:16px}"
        "svg{display:block;width:100%;height:auto;max-width:" + n(cv.w) + "px}</style>\n"
        "</head>\n<body>\n" + render(cv, "var") + "\n</body>\n</html>\n"
    )


def picture(name: str, alt: str) -> str:
    """A panel that follows the reader's GitHub theme."""
    return (
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="./assets/{name}-dark.svg">\n'
        f'  <img src="./assets/{name}-light.svg" width="100%" alt="{html.escape(alt)}">\n'
        "</picture>"
    )


def readme(alts: dict[str, str]) -> str:
    P = C.PUBLIC
    experiments = " · ".join(
        f"[{repo}](https://github.com/mariolinares/{repo}) {what}" for repo, what in P["experiments"]
    )
    return "\n\n".join([
        "<!-- Generado por tools/build.py desde design/tokens.json y tools/content.py. No editar a mano. -->",
        picture("hero", alts["hero"]),
        picture("modulos", alts["modulos"]),
        f"<sub>Experimentos públicos sobre SSR y Native Federation: {experiments}.</sub>",
        picture("principios", alts["principios"]),
        picture("capas", alts["capas"]),
        picture("trayectoria", alts["trayectoria"]),
        picture("clientes", alts["clientes"]),
        picture("contacto", alts["contacto"]),
        (
            '<p align="center">\n'
            f'  <a href="mailto:{P["email"]}">{P["email"]}</a>\n  &nbsp;·&nbsp;\n'
            f'  <a href="{P["linkedin"]}">LinkedIn</a>\n</p>'
        ),
        (
            '<p align="center"><sub>Paneles dibujados con un sistema de diseño propio: tokens, '
            "Instrument Serif, Instrument Sans y DM Mono (OFL) incrustadas, marcas de Simple Icons (CC0) "
            "y un generador en Python. Las marcas pertenecen a sus propietarios. "
            "Siguen el tema claro u oscuro de tu GitHub.</sub></p>"
        ),
    ]) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ds", type=Path, help="design-system project folder to write previews into")
    args = ap.parse_args()
    ASSETS.mkdir(exist_ok=True)
    alts = {}
    for name, build in PANELS.items():
        cv = build()
        alts[name] = cv.alt
        for theme in THEMES:
            out = ASSETS / f"{name}-{theme}.svg"
            out.write_text(render(cv, "file", theme))
            print(f"{out.relative_to(ROOT)}  {out.stat().st_size / 1024:.0f} KB  {n(cv.w)}×{n(cv.h)}")
    (ROOT / "README.md").write_text(readme(alts))
    print("README.md")
    if args.ds:
        for comp, (group, build) in PREVIEWS.items():
            out = args.ds / "components" / comp / "preview.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(preview_html(group, comp, build()))
            print(f"preview  {comp}")
    for w in sorted(set(WARNINGS)):
        print("warning:", w, file=sys.stderr)


if __name__ == "__main__":
    main()
