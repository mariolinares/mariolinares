#!/usr/bin/env python3
"""Render the GitHub profile as a typeset carta de porte."""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"

PAPER = (221, 216, 204)  # #DDD8CC — stone, not bakery cream
INK = (28, 27, 25)
CARBON = (30, 58, 86)
STAMP = (163, 32, 24)
RULE = (168, 160, 144)
MUTED = (90, 84, 74)
STUB = (210, 205, 192)
BIND = (138, 28, 24)

DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
HOEFLER = "/System/Library/Fonts/Supplemental/Hoefler Text.ttc"
GILL = "/System/Library/Fonts/Supplemental/GillSans.ttc"
SNELL = "/System/Library/Fonts/Supplemental/SnellRoundhand.ttc"


def font(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size, index=index)


def paper(w: int, h: int) -> Image.Image:
    img = Image.new("RGB", (w, h), PAPER)
    rnd = random.Random(2015)
    px = img.load()
    for _ in range(w * h // 18):
        x, y = rnd.randint(0, w - 1), rnd.randint(0, h - 1)
        d = rnd.randint(-10, 8)
        r, g, b = px[x, y]
        px[x, y] = (max(0, r + d), max(0, g + d), max(0, b + d))
    img = img.filter(ImageFilter.GaussianBlur(0.35))
    return img


def draw_stub(draw: ImageDraw.ImageDraw, h: int, stub_w: int = 92) -> None:
    draw.rectangle((0, 0, 18, h), fill=BIND)
    draw.rectangle((18, 0, stub_w, h), fill=STUB)
    y = 28
    while y < h - 16:
        draw.ellipse((stub_w - 5, y, stub_w + 5, y + 10), fill=PAPER, outline=RULE)
        y += 22


def vertical_label(base: Image.Image, text: str, x: int, y: int) -> None:
    f = font(GILL, 22, 0)
    tmp = Image.new("RGBA", (720, 48), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.text((0, 0), text, font=f, fill=MUTED)
    rot = tmp.rotate(90, expand=True, resample=Image.Resampling.BICUBIC)
    bbox = rot.getbbox()
    if bbox:
        rot = rot.crop(bbox)
    base.paste(rot, (x, y), rot)


def sheet_edge(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    draw.rectangle((0, 0, w - 1, h - 1), outline=RULE)


def circle_stamp(base: Image.Image, cx: int, cy: int, r: int) -> Image.Image:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ink = (*STAMP, 200)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ink, width=2)
    d.ellipse((cx - r + 9, cy - r + 9, cx + r - 9, cy + r - 9), outline=ink, width=1)

    mark = font(DIDOT, 42, 0)
    bbox = d.textbbox((0, 0), "ML", font=mark)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((cx - tw / 2, cy - th / 2 - 10), "ML", font=mark, fill=ink)

    city = font(GILL, 16, 0)
    cb = d.textbbox((0, 0), "Madrid", font=city)
    d.text((cx - (cb[2] - cb[0]) / 2, cy + 22), "Madrid", font=city, fill=ink)

    stamped = layer.rotate(-8, resample=Image.Resampling.BICUBIC, expand=False)
    return Image.alpha_composite(base.convert("RGBA"), stamped).convert("RGB")


def field(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, label: str, value: str) -> None:
    draw.line((x, y + 62, x + w, y + 62), fill=RULE, width=1)
    draw.text((x, y), label, font=font(GILL, 20, 0), fill=MUTED)
    draw.text((x, y + 26), value, font=font(HOEFLER, 30, 0), fill=INK)


def render_portada() -> None:
    w, h = 2000, 1120
    img = paper(w, h)
    d = ImageDraw.Draw(img)
    draw_stub(d, h)
    vertical_label(img, "Mario Linares  ·  Madrid  ·  desde 2015", 38, 210)

    left = 140
    right = w - 72

    d.text((left, 56), "Carta de porte técnica", font=font(HOEFLER, 28, 2), fill=CARBON)
    serie = "Serie ML–15"
    sw = d.textbbox((0, 0), serie, font=font(GILL, 22, 0))[2]
    d.text((right - sw, 60), serie, font=font(GILL, 22, 0), fill=MUTED)

    d.line((left, 108, right, 108), fill=INK, width=2)
    d.line((left, 114, right, 114), fill=RULE, width=1)

    d.text((left, 168), "El expedidor", font=font(GILL, 22, 0), fill=MUTED)
    d.text((left, 208), "Mario", font=font(DIDOT, 64, 1), fill=CARBON)
    d.text((left, 286), "Linares", font=font(DIDOT, 168, 0), fill=INK)

    d.line((left, 490, right, 490), fill=RULE, width=1)

    gap = 36
    col = (right - left - gap * 3) / 4
    fields = (
        ("Plaza", "Madrid"),
        ("Oficio", "Arquitecto de software"),
        ("Desde", "2015"),
        ("Ámbito", "Banca, industria, operación"),
    )
    for i, (lab, val) in enumerate(fields):
        field(d, int(left + i * (col + gap)), 524, int(col), lab, val)

    quote = "Diseño sistemas que tienen que ser válidos ante una inspección, no solo verse bien."
    d.text((left, 660), quote, font=font(HOEFLER, 32, 2), fill=CARBON)

    d.line((left, 980, right, 980), fill=RULE, width=1)
    d.text((left, 1010), "Naturaleza de la mercancía", font=font(GILL, 20, 0), fill=MUTED)
    d.text(
        (left, 1044),
        "Microfrontends, monorepos y producto propio. Angular, NestJS, Nx.",
        font=font(HOEFLER, 28, 0),
        fill=INK,
    )

    sheet_edge(d, w, h)
    stamped = circle_stamp(img, 1765, 800, 108)
    stamped.save(OUT / "portada.png", "PNG", optimize=True)


def render_sistemas() -> None:
    w, h = 2000, 1280
    img = paper(w, h)
    d = ImageDraw.Draw(img)
    draw_stub(d, h)
    vertical_label(img, "Mercancías declaradas  ·  repos privados", 38, 240)

    left, right = 140, w - 72
    d.text((left, 56), "Mercancías declaradas", font=font(HOEFLER, 28, 2), fill=CARBON)
    nota = "Los repositorios son privados. Esto es lo que hay detrás."
    nw = d.textbbox((0, 0), nota, font=font(GILL, 22, 0))[2]
    d.text((right - nw, 60), nota, font=font(GILL, 22, 0), fill=MUTED)
    d.line((left, 108, right, 108), fill=INK, width=2)
    d.line((left, 114, right, 114), fill=RULE, width=1)

    d.text((left, 150), "Sistema", font=font(GILL, 20, 0), fill=MUTED)
    d.text((left + 340, 150), "Descripción", font=font(GILL, 20, 0), fill=MUTED)
    d.text((left + 1280, 150), "Hecho con", font=font(GILL, 20, 0), fill=MUTED)
    d.line((left, 186, right, 186), fill=RULE, width=1)

    rows = (
        ("Portes", "SaaS de portes. Carta de Porte y DeCA.\nUn campo mal puesto invalida el documento.", "Angular 21  NestJS  Nx  PWA"),
        ("Zunix", "Cadena de frío con validez sanitaria.\nEl registro oficial vive en el hardware.", "Angular 22  NestJS  MQTT  Omron"),
        ("Routes", "Distribución alimentaria: VRP, conductor,\npredicción y un asistente RAG.", "Angular  Ionic  NestJS  Python"),
        ("Vinolo", "ERP + WMS B2B. Diez bounded contexts.\nEl dominio manda; el framework no.", "NestJS  Nx  TypeORM  DDD"),
        ("Sienta", "Reservas, aforo y menú del día.\nProducto pequeño, operación real.", "Angular  NestJS  Prisma  GCP"),
        ("Iryo", "Microfrontends con Native Federation\ny deploys independientes.", "Angular 19  Nx  Vite"),
    )

    y = 214
    for name, desc, stack in rows:
        d.text((left, y + 8), name, font=font(DIDOT, 40, 0), fill=INK)
        d.multiline_text((left + 340, y + 6), desc, font=font(HOEFLER, 26, 0), fill=INK, spacing=8)
        d.text((left + 1280, y + 18), stack.replace("  ", "  ·  "), font=font(GILL, 21, 0), fill=CARBON)
        y += 156
        d.line((left, y - 18, right, y - 18), fill=RULE, width=1)

    d.text(
        (left, 1188),
        "También: RAG local con Ollama, fotovoltaica, Solidity y un chat en streaming.",
        font=font(HOEFLER, 26, 2),
        fill=MUTED,
    )
    sheet_edge(d, w, h)
    img.save(OUT / "sistemas.png", "PNG", optimize=True)


def render_oficio() -> None:
    w, h = 2000, 780
    img = paper(w, h)
    d = ImageDraw.Draw(img)
    draw_stub(d, h)
    vertical_label(img, "Oficio  ·  VASS  ·  Atmira  ·  Babel", 38, 180)

    left, right = 140, w - 72
    d.text((left, 56), "Oficio", font=font(HOEFLER, 28, 2), fill=CARBON)
    d.line((left, 108, right, 108), fill=INK, width=2)
    d.line((left, 114, right, 114), fill=RULE, width=1)

    items = (
        ("VASS", "2021 —", "Arquitecto frontend. Microfrontends, librerías compartidas,\nmigraciones Angular 4 a 14 para banca."),
        ("Atmira", "2019 — 2021", "BNP Paribas y Banco Santander. Infraestructura,\nTDD, NgRx, híbrido AngularJS cuando hacía falta."),
        ("Babel", "2017 — 2019", "Airbus. SPAs Angular, tiempo real, componentes\ny rendimiento en planta de trabajo."),
    )
    y = 160
    for house, dates, blurb in items:
        d.text((left, y), house, font=font(DIDOT, 42, 0), fill=INK)
        d.text((left + 280, y + 14), dates, font=font(GILL, 22, 0), fill=CARBON)
        d.multiline_text((left + 560, y + 4), blurb, font=font(HOEFLER, 26, 0), fill=INK, spacing=8)
        y += 140
        d.line((left, y - 24, right, y - 24), fill=RULE, width=1)

    d.text((left, 620), "Cómo construyo", font=font(GILL, 20, 0), fill=MUTED)
    d.multiline_text(
        (left, 654),
        "El dominio primero. Monorepo cuando hay sistema. Migrar sin parar el negocio.\nLa arquitectura que no se enseña no se adopta.",
        font=font(HOEFLER, 28, 2),
        fill=CARBON,
        spacing=10,
    )
    sheet_edge(d, w, h)
    img.save(OUT / "oficio.png", "PNG", optimize=True)


def render_firma() -> None:
    w, h = 2000, 520
    img = paper(w, h)
    d = ImageDraw.Draw(img)
    draw_stub(d, h)
    vertical_label(img, "Firma del expedidor", 38, 150)

    left, right = 140, w - 72
    d.text((left, 56), "Para hablar", font=font(HOEFLER, 28, 2), fill=CARBON)
    d.line((left, 108, right, 108), fill=INK, width=2)
    d.line((left, 114, right, 114), fill=RULE, width=1)

    d.multiline_text(
        (left, 168),
        "Si hay que ordenar, migrar o poner en planta\nun sistema — no una landing — escribe.",
        font=font(HOEFLER, 34, 0),
        fill=INK,
        spacing=10,
    )

    d.text((left, 310), "Mario Linares", font=font(SNELL, 64, 0), fill=CARBON)
    d.line((left, 400, left + 420, 400), fill=RULE, width=1)
    d.text((left, 418), "mariolinaresparra@icloud.com", font=font(GILL, 24, 0), fill=INK)
    d.text((left, 454), "linkedin.com/in/mario-linares-131b84146", font=font(GILL, 22, 0), fill=MUTED)

    d.text((right - 280, 430), "Hecho en Madrid", font=font(HOEFLER, 24, 2), fill=MUTED)
    sheet_edge(d, w, h)
    img.save(OUT / "firma.png", "PNG", optimize=True)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    render_portada()
    render_sistemas()
    render_oficio()
    render_firma()
    print("ok", list(OUT.glob("*.png")))
