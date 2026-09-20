#!/usr/bin/env python3
"""Генерация иконок сайта из фирменного знака.

Знак повторяет .brand__mark из assets/scss/main.scss: скруглённый квадрат,
разделённый крестом на четыре квадранта. В шапке он рисуется рамкой и линиями
через currentColor, здесь — как иконка: сплошная заливка фирменным синим и
белый крест.

Отдельный скрипт, а не ручная нарезка, потому что иконок четыре размера и их
надо перегенерировать целиком при смене фирменного цвета.

Запуск: python scripts/make_icons.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

# Фирменный синий: --primary из светлой темы (assets/scss/main.scss).
BRAND = (31, 79, 216)
WHITE = (255, 255, 255)

# Крест в знаке занимает всю ширину квадрата (как ::before/::after в CSS),
# толщина подобрана так, чтобы на 16 px оставалось 2 целых пикселя.
SS = 1024                 # рендерим крупно и уменьшаем — сглаживание по краям
RADIUS_RATIO = 0.22
BAR_RATIO = 0.145


def brand_mark(size: int, corner_radius: bool = True) -> Image.Image:
    """Знак: синий скруглённый квадрат с белыми угловыми визирами и точкой.

    Вариант с крестом через весь квадрат отвергнут: на синем фоне он читается
    как флаг Финляндии (или аптечный крест), а не как бренд. Визиры по углам
    в рамке с точкой в центре однозначно считываются как «инженерный
    прицел/калибровка» и не смазываются в 16 px.

    corner_radius=False — для apple-touch-icon: iOS сам применяет маску,
    поэтому иконка должна быть во весь квадрат, без прозрачных углов.
    """
    img = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    radius = int(SS * RADIUS_RATIO) if corner_radius else 0
    d.rounded_rectangle([(0, 0), (SS - 1, SS - 1)], radius=radius, fill=BRAND)

    inset = int(SS * 0.215)          # отступ визиров от края
    arm = int(SS * 0.175)            # длина плеча визира
    stroke = int(SS * 0.085)         # толщина: ~1.4 px в размере 16
    dot = int(SS * 0.145)            # сторона центральной точки

    # Четыре Г-образных визира — «уголки кадра».
    for cx, cy, sx, sy in (
        (inset, inset, 1, 1),
        (SS - inset, inset, -1, 1),
        (inset, SS - inset, 1, -1),
        (SS - inset, SS - inset, -1, -1),
    ):
        d.rectangle([(min(cx, cx + sx * arm), min(cy, cy + sy * stroke)),
                     (max(cx, cx + sx * arm), max(cy, cy + sy * stroke))], fill=WHITE)
        d.rectangle([(min(cx, cx + sx * stroke), min(cy, cy + sy * arm)),
                     (max(cx, cx + sx * stroke), max(cy, cy + sy * arm))], fill=WHITE)

    c = SS // 2
    half = dot // 2
    d.rectangle([(c - half, c - half), (c - half + dot - 1, c - half + dot - 1)], fill=WHITE)

    return img.resize((size, size), Image.LANCZOS)


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

    f_brand = font("consolab.ttf", 30)
    f_title = font("arialbd.ttf", 74)
    f_sub = font("segoeui.ttf", 36)

    d.text((80, 86), "ENGINEERING AI", font=f_brand, fill=ACCENT)
    d.line([(80, 140), (150, 140)], fill=ACCENT, width=3)

    lines = ["Искусственный интеллект", "для роботов и автономных", "транспортных систем"]
    y = 200
    for ln in lines:
        d.text((80, y), ln, font=f_title, fill=TEXT)
        y += 92

    d.text((80, y + 24), "AMR / AGV · SOTIF · V2X · MLOps · secure OTA", font=f_sub, fill=MUTED)

    mark = brand_mark(120)
    img.paste(mark, (W - 200, 86), mark)
    return img


def main() -> None:
    STATIC.mkdir(parents=True, exist_ok=True)

    png32 = brand_mark(32)
    png32.save(STATIC / "favicon-32.png", optimize=True)

    # .ico с несколькими размерами: 16 px нужен вкладкам, 48 px — панели задач.
    brand_mark(48).save(
        STATIC / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48)],
    )

    # apple-touch-icon: во весь квадрат, без прозрачности (iOS маскирует сам).
    brand_mark(180, corner_radius=False).convert("RGB").save(STATIC / "apple-touch-icon.png", optimize=True)

    og_image().save(STATIC / "og-image.png", optimize=True)

    for f in ("favicon.ico", "favicon-32.png", "apple-touch-icon.png", "og-image.png"):
        p = STATIC / f
        print(f"{f:24} {p.stat().st_size:>8} bytes")

    # Контроль: 16 px не должен «замылиться» в одно пятно.
    small = brand_mark(16)
    px = small.convert("RGB").load()
    print("16px центр:", px[8, 8], "| угол:", px[0, 0], "| середина ребра:", px[8, 1])


if __name__ == "__main__":
    main()
