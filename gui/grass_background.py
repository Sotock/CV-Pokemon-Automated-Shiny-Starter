import tkinter as tk

from PIL import Image, ImageDraw, ImageTk


GRASS_BACKGROUND = "#15221B"


def create_grass_texture(width, height):

    tile = Image.new(
        "RGB",
        (32, 32),
        GRASS_BACKGROUND
    )

    draw = ImageDraw.Draw(tile)

    for x, y in ((2, 3), (17, 17)):

        points = [
            (x, y + 12),
            (x, y + 5),
            (x + 3, y + 8),
            (x + 3, y + 1),
            (x + 6, y + 5),
            (x + 8, y),
            (x + 9, y + 7),
            (x + 13, y + 3),
            (x + 12, y + 12)
        ]

        draw.polygon(
            points,
            fill="#20372A"
        )

        draw.line(
            [
                (x + 3, y + 11),
                (x + 3, y + 5)
            ],
            fill="#294333",
            width=1
        )

        draw.line(
            [
                (x + 8, y + 10),
                (x + 8, y + 3)
            ],
            fill="#294333",
            width=1
        )

        draw.rectangle(
            (x + 1, y + 12, x + 11, y + 13),
            fill="#111D16"
        )

    tile = tile.resize(
        (64, 64),
        Image.Resampling.NEAREST
    )

    texture = Image.new(
        "RGB",
        (max(1, width), max(1, height)),
        GRASS_BACKGROUND
    )

    for y in range(0, height, tile.height):

        for x in range(0, width, tile.width):

            texture.paste(tile, (x, y))

    return texture


def create_ball_watermark(
        width,
        height,
        ultra=False,
        muted=False,
        background="#1C2027",
        opacity=None
):

    width = max(1, width)
    height = max(1, height)

    size = max(
        1,
        int(min(width, height) * 0.92)
    )

    resolution = 600

    ball = Image.new(
        "RGBA",
        (resolution, resolution),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(ball)

    bounds = (15, 15, 585, 585)

    outline = "#080A0D"

    if ultra:

        upper = "#292B30"
        lower = "#E5E7EB"

    elif muted:

        upper = "#747B84"
        lower = "#B7BDC5"

    else:

        upper = "#D63842"
        lower = "#E5E7EB"

    draw.pieslice(
        bounds,
        0,
        180,
        fill=lower
    )

    draw.pieslice(
        bounds,
        180,
        360,
        fill=upper
    )

    if ultra:

        draw.polygon(
            [
                (135, 75),
                (210, 35),
                (210, 220),
                (390, 220),
                (390, 35),
                (465, 75),
                (465, 300),
                (135, 300)
            ],
            fill="#F4CF48"
        )

    draw.rectangle(
        (18, 280, 582, 320),
        fill=outline
    )

    draw.ellipse(
        bounds,
        outline=outline,
        width=24
    )

    draw.ellipse(
        (205, 205, 395, 395),
        fill=outline
    )

    draw.ellipse(
        (230, 230, 370, 370),
        fill="#E5E7EB"
    )

    draw.ellipse(
        (253, 253, 347, 347),
        outline="#8B929C",
        width=6
    )

    mask = Image.new(
        "L",
        ball.size,
        0
    )

    ImageDraw.Draw(mask).ellipse(
        bounds,
        fill=255
    )

    if opacity is None:

        opacity = 0.09 if muted else 0.17

    ball.putalpha(
        mask.point(
            lambda value: int(value * opacity)
        )
    )

    ball = ball.resize(
        (size, size),
        Image.Resampling.LANCZOS
    )

    texture = Image.new(
        "RGB",
        (width, height),
        background
    )

    x = (width - size) // 2
    y = (height - size) // 2

    if height > width:

        y = min(
            max(0, height - size),
            y + int(height * 0.20)
        )

    texture.paste(
        ball,
        (x, y),
        ball
    )

    return texture


class GrassBackground(tk.Canvas):

    def __init__(
            self,
            parent,
            shaded=False,
            watermark=False,
            **kwargs
    ):

        super().__init__(
            parent,
            background=GRASS_BACKGROUND,
            highlightthickness=0,
            borderwidth=0,
            **kwargs
        )

        self.shaded = shaded
        self.watermark = watermark

        self.texture_image = None
        self.texture_size = None

        self.texture_item = self.create_image(
            0,
            0,
            anchor="nw"
        )

        self.bind(
            "<Configure>",
            self.update_texture,
            add="+"
        )

    def update_texture(self, event):

        width = max(1, event.width)
        height = max(1, event.height)

        if self.texture_size == (width, height):

            return

        texture = create_grass_texture(
            width,
            height
        )

        if self.shaded:

            backing = Image.new(
                "RGB",
                texture.size,
                "#121419"
            )

            texture = Image.blend(
                texture,
                backing,
                0.75
            )

        if self.watermark:

            size = min(
                height,
                width // 4
            )

            ball = create_ball_watermark(
                size,
                size,
                background="#14181A",
                opacity=0.15
            )

            texture.paste(
                ball,
                (
                    width - size - 12,
                    (height - size) // 2
                )
            )

        self.texture_image = ImageTk.PhotoImage(
            texture,
            master=self
        )

        self.itemconfigure(
            self.texture_item,
            image=self.texture_image
        )

        self.tag_lower(self.texture_item)

        self.texture_size = (width, height)