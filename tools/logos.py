#!/usr/bin/env python3
"""Prepare the logo marks the panels draw.

    python tools/logos.py --icons <simple-icons>/icons --cv "CV Mario Linares-sm.pdf"

Technology marks: copies the Simple Icons (CC0) the profile uses to design/logos/tech/.
Client marks: pulls the logos embedded in the CV and writes single-ink masks (white on
transparent, trimmed, 96px tall) to design/logos/clients/; the panels tint them with a
colour token, so every logo reads in the system's ink. Airbus comes from Simple Icons.
Needs pymupdf and pillow on top of tools/requirements.txt.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pymupdf
from PIL import Image, ImageOps

import content as C

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "design" / "logos"

# Image xrefs of the client logos inside the CV PDF (page 2, «Proyectos destacados»).
# BNP Paribas (xref 21) is only 112px wide there and stays as set type until a vector arrives.
CV_XREFS = {
    20: "santander",
    22: "bbva",
    24: "pibank",
    25: "caixabank",
    26: "btravel",
    27: "inditex",
    28: "adeslas",
    29: "iryo",
}
SIMPLE_ICON_CLIENTS = {"airbus": "airbus"}
HEIGHT = 96


def mask_from(im: Image.Image) -> Image.Image:
    """Logo pixels → 255, background → 0, whatever the source's background is."""
    rgba = im.convert("RGBA")
    alpha = rgba.getchannel("A")
    clear = sum(alpha.histogram()[:10]) / (rgba.width * rgba.height)
    if clear > 0.2:
        mask = alpha
    else:
        ink = ImageOps.invert(rgba.convert("L"))
        lo, hi = 24, max(ink.getextrema()[1], 25)
        mask = ink.point(lambda v: 0 if v <= lo else min(255, (v - lo) * 255 // (hi - lo)))
    return mask.crop(mask.getbbox())


def client_marks(cv: Path) -> None:
    dest = OUT / "clients"
    dest.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(cv)
    for xref, name in CV_XREFS.items():
        pix = pymupdf.Pixmap(doc, xref)
        kind, ref = doc.xref_get_key(xref, "SMask")
        if kind == "xref" and not pix.alpha:
            pix = pymupdf.Pixmap(pix, pymupdf.Pixmap(doc, int(ref.split()[0])))
        if pix.n - pix.alpha > 3:
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        im = Image.frombytes("RGBA" if pix.alpha else "RGB", (pix.width, pix.height), pix.samples)
        mask = mask_from(im)
        w = round(mask.width * HEIGHT / mask.height)
        mask = mask.resize((w, HEIGHT), Image.Resampling.LANCZOS)
        out = Image.new("LA", mask.size, (255, 0))
        out.putalpha(mask)
        out.save(dest / f"{name}.png", optimize=True)
        print(f"clients/{name}.png  {w}×{HEIGHT}  (source {pix.width}×{pix.height})")


def tech_marks(icons: Path) -> None:
    dest = OUT / "tech"
    dest.mkdir(parents=True, exist_ok=True)
    slugs = set(C.TECH_ICONS.values()) | set(C.HERO["daily"])
    for slug in sorted(slugs):
        shutil.copy(icons / f"{slug}.svg", dest / f"{slug}.svg")
    for name, slug in SIMPLE_ICON_CLIENTS.items():
        shutil.copy(icons / f"{slug}.svg", OUT / "clients" / f"{name}.svg")
    shutil.copy(icons.parent / "LICENSE.md", OUT / "LICENSE-simple-icons.md")
    print(f"tech/  {len(slugs)} marks")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--icons", type=Path, required=True, help="simple-icons/icons directory")
    ap.add_argument("--cv", type=Path, required=True, help="the CV PDF with the client logos")
    args = ap.parse_args()
    client_marks(args.cv)
    tech_marks(args.icons)


if __name__ == "__main__":
    main()
