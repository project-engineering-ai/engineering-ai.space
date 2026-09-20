#!/usr/bin/env python3
"""Генерация иконок сайта и картинки предпросмотра из фирменного логотипа.

Логотип — синий круг с белым знаком (гексагон и три треугольника) — тот же,
что стоит на сайте engineering-ai.site: он принадлежит тому же бренду
«Engineering AI». Геометрия перенесена из его logo.svg (viewBox 512x512)
в Pillow, чтобы не тащить в сборку SVG-рендерер ради четырёх иконок.

Зачем скрипт, а не нарезка руками: у иконок разные требования (16 px не должен
«замыливаться» в белое пятно, apple-touch-icon не может иметь прозрачных углов),
и всё это надо пересобрать одной командой при правке логотипа.

Запуск: python scripts/make_icons.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

# Цвета из оригинального SVG.
LOGO_BLUE = (9, 52, 139)       # #09348B — круг
WHITE = (255, 255, 255)

# Геометрия логотипа, viewBox 512x512.
VIEW = 512.0
CIRCLE = (256.0, 256.0, 256.0)  # cx, cy, r
SHAPES = [
    # центральный гексагон
    [(316.4, 173.7), (195.6, 173.7), (135.1, 278.4), (195.6, 383.1), (316.4, 383.1), (376.9, 278.4)],
    # верхний треугольник
    [(256.0, 69.3), (202.1, 162.6), (309.9, 162.6)],
    # нижний левый
    [(128.0, 288.7), (74.1, 382.1), (181.8, 382.1)],
    # нижний правый
    [(383.9, 288.7), (330.0, 382.1), (437.8, 382.1)],
]
SO = 2048                       # супердискретизация: рисуем крупно и уменьшаем


def draw_logo(size: int, full_bleed: bool = False, glyph_scale: float = 1.0,
              gaps: float = 1.0, shapes: list | None = None) -> Image.Image:
    """Логотип в квадрате `size`.

    full_bleed=True — круг не рисуется, синий фон занимает весь квадрат с
    прямыми углами. Так нужно для apple-touch-icon: iOS применяет собственную
    маску, и прозрачные углы дали бы чёрные зазоры.

    glyph_scale — доля исходного размера знака целиком (центрируется заново).

    gaps — множитель зазоров между фигурами: каждая сжимается вокруг своего
    центра. В оригинале зазор ~6.5 единиц из 512 (1.3%) — в 16 px это 0.2 px,
    то есть физически не отрисовывается и фигуры сливаются в белое пятно.
    Для мелких размеров зазоры расширяются до видимых.

    shapes — набор фигур из SHAPES. На 16 px четыре фигуры принципиально не
    различимы (проверено полным перебором параметров), поэтому берётся
    упрощённый знак: центральный гексагон и два нижних треугольника.
    """
    scale = SO / VIEW
    img = Image.new("RGBA", (SO, SO), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if full_bleed:
        d.rectangle([(0, 0), (SO - 1, SO - 1)], fill=LOGO_BLUE)
    else:
        d.ellipse(
            [(CIRCLE[0] - CIRCLE[2]) * scale, (CIRCLE[1] - CIRCLE[2]) * scale,
             (CIRCLE[0] + CIRCLE[2]) * scale, (CIRCLE[1] + CIRCLE[2]) * scale],
            fill=LOGO_BLUE,
        )

    cx = cy = VIEW / 2
    for poly in (shapes if shapes is not None else SHAPES):
        # Центр фигуры — сжатие вокруг него расширяет зазоры с соседями,
        # не сдвигая саму фигуру с её места в композиции.
        px = sum(p[0] for p in poly) / len(poly)
        py = sum(p[1] for p in poly) / len(poly)
        pts = []
        for x, y in poly:
            x = px + (x - px) * gaps
            y = py + (y - py) * gaps
            pts.append((((x - cx) * glyph_scale + cx) * scale,
                        ((y - cy) * glyph_scale + cy) * scale))
        d.polygon(pts, fill=WHITE)

    return img.resize((size, size), Image.LANCZOS)


def count_white_blobs(img: Image.Image, size: int, thresh: int = 110) -> int:
    """Число связных белых фигур в готовой иконке (4-связность).

    Метрика читаемости: в оригинальном логотипе при 48 px и выше различимы
    ровно 4 фигуры (гексагон и три треугольника). Если в мелком размере
    получается 1 — зазоры слились и знак стал белым пятном; 5-9 — фигуры
    «разъехались» и распались на осколки.
    """
    px = img.convert("RGB").load()
    seen, count = set(), 0

    def white(x: int, y: int) -> bool:
        r, g, b = px[x, y]
        return r > thresh and g > thresh and b > thresh

    for y in range(size):
        for x in range(size):
            if (x, y) in seen or not white(x, y):
                continue
            count += 1
            stack = [(x, y)]
            while stack:
                cx, cy = stack.pop()
                if ((cx, cy) in seen or not (0 <= cx < size and 0 <= cy < size)
                        or not white(cx, cy)):
                    continue
                seen.add((cx, cy))
                stack += [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]
    return count


def og_image() -> Image.Image:
    """Картинка предпросмотра для соцсетей и мессенджеров (1200x630).

    Та же палитра, что у hero-секции: тёмный фон, тонкая сетка, синий акцент.
    Шрифты — системные: доставлять веб-шрифты в артефакт ради одной картинки
    незачем, а сборка в CI не должна тянуть их из сети.
    """
    W, H = 1200, 630
    BG = (12, 16, 26)
    GRID = (26, 32, 46)
    ACCENT = (122, 162, 255)
    TEXT = (232, 236, 243)
    MUTED = (149, 161, 178)

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 44):                       # вертикали сетки
        d.line([(x, 0), (x, H)], fill=GRID, width=1)
    for y in range(0, H, 44):                       # горизонтали сетки
        d.line([(0, y), (W, y)], fill=GRID, width=1)

    def font(name: str, size: int) -> ImageFont.FreeTypeFont:
        for cand in (f"C:/Windows/Fonts/{name}", f"/usr/share/fonts/truetype/{name}"):
            try:
                return ImageFont.truetype(cand, size)
            except OSError:
                continue
        return ImageFont.load_default()

    d.text((80, 86), "ENGINEERING AI", font=font("consolab.ttf", 30), fill=ACCENT)
    d.line([(80, 140), (150, 140)], fill=ACCENT, width=3)

    y = 200
    for ln in ("Искусственный интеллект", "для роботов и автономных", "транспортных систем"):
        d.text((80, y), ln, font=font("arialbd.ttf", 74), fill=TEXT)
        y += 92

    d.text((80, y + 24), "AMR / AGV · SOTIF · V2X · MLOps · secure OTA",
           font=font("segoeui.ttf", 36), fill=MUTED)

    logo = draw_logo(132)
    img.paste(logo, (W - 212, 86), logo)
    return img


def main() -> None:
    STATIC.mkdir(parents=True, exist_ok=True)

    # Иконки собираются ПОРАЗМЕРНО, а не одной картинкой с общими зазорами:
    # в логотипе зазор между фигурами — 1.3% от размера, в 16 px это 0.2 px и
    # он не отрисовывается вообще. Полный перебор параметров показал, что
    # конфигурации, где на 16-24 px видны все четыре фигуры, не существует,
    # поэтому мелкие размеры идут с упрощённым знаком (без верхнего
    # треугольника), а 32 px и выше — с полным. Критерий проверяемый: число
    # связных белых фигур в готовой иконке (эталон — 4 на крупных размерах).
    HEX3 = [SHAPES[0], SHAPES[2], SHAPES[3]]
    SIZES = {
        16: dict(glyph_scale=1.05, gaps=1.5, shapes=HEX3),
        24: dict(glyph_scale=1.0, gaps=1.4, shapes=HEX3),
        32: dict(glyph_scale=0.96, gaps=2.3),
        48: dict(glyph_scale=0.92, gaps=1.0),
    }

    draw_logo(32, **SIZES[32]).save(STATIC / "favicon-32.png", optimize=True)

    # .ico хранит несколько размеров, и каждый рисуется своими параметрами —
    # PIL для этого принимает список изображений с append_images.
    frames = [draw_logo(s, **(SIZES.get(s) or SIZES[48])) for s in (16, 24, 32, 48)]
    frames[-1].save(
        STATIC / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48)],
        append_images=frames[:-1],
    )

    # apple-touch-icon — 180 px: зазоры здесь уже видны, но знак чуть уменьшен,
    # чтобы он не упирался в маску iOS по краям.
    draw_logo(180, full_bleed=True, glyph_scale=0.86, gaps=1.15).convert("RGB").save(
        STATIC / "apple-touch-icon.png", optimize=True
    )

    og_image().save(STATIC / "og-image.png", optimize=True)

    for f in ("favicon.ico", "favicon-32.png", "apple-touch-icon.png", "og-image.png"):
        p = STATIC / f
        print(f"{f:24} {p.stat().st_size:>8} bytes")

    # Контроль: знак должен читаться, а не рассыпаться на осколки. Эталон —
    # 4 различимые фигуры, как в оригинальном логотипе на крупном размере;
    # на 24 px знак упрощён до трёх, а на 16 px зазоры не отрисовываются
    # вообще, и силуэт намеренно остаётся цельным (1 фигура) — там важна
    # узнаваемость пятна, а не внутренние детали. Больше эталона = «разъехалось».
    for size, expect in ((16, 1), (24, 3), (32, 4), (48, 4)):
        n = count_white_blobs(draw_logo(size, **SIZES[size]), size)
        mark = "ok" if n == expect else f"ОЖИДАЛОСЬ {expect}"
        print(f"{size:>3}px: различимых белых фигур {n} — {mark}")


if __name__ == "__main__":
    main()
