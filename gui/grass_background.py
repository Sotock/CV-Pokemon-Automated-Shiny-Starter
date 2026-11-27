import tkinter as tk

from PIL import Image, ImageDraw, ImageTk


GRASS_BACKGROUND = "#111E19"


def create_grass_texture(width, height):

    tile = Image.new(
        "RGB",
        (64, 48),
        GRASS_BACKGROUND
    )

    draw = ImageDraw.Draw(tile)

    draw.polygon(
        [
            (5, 37),
            (5, 24),
            (10, 24),
            (10, 30),
            (15, 30),
            (15, 15),
            (20, 15),
            (20, 28),
            (25, 28),
            (25, 20),
            (30, 20),
            (30, 37)
        ],
        fill="#244C35"
    )

    draw.polygon(
        [
            (37, 18),
            (37, 7),
            (42, 7),
            (42, 12),
            (47, 12),
            (47, 2),
            (52, 2),
            (52, 11),
            (57, 11),
            (57, 6),
            (62, 6),
            (62, 18)
        ],
        fill="#1D3E2D"
    )

    draw.rectangle(
        (39, 36, 43, 42),
        fill="#31563C"
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


class GrassBackground(tk.Canvas):

    def __init__(self, parent, **kwargs):

        super().__init__(
            parent,
            background=GRASS_BACKGROUND,
            highlightthickness=0,
            borderwidth=0,
            **kwargs
        )

        self.texture_image = None

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

        texture = create_grass_texture(
            event.width,
            event.height
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