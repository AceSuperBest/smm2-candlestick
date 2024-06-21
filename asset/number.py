from PIL import Image, ImageDraw, ImageFont
from .items import ItemGraphicsFactory
from .utils import get_assets_path
from pydantic import BaseModel
import os


__all__ = ["NumberGraphicsResources"]


class Margin(BaseModel):
    left: int = 0
    top: int = 0
    right: int = 0
    bottom: int = 0

    @property
    def width(self):
        return self.left + self.right

    @property
    def height(self):
        return self.top + self.bottom


class NumberGraphicsResources:
    font: ImageFont.FreeTypeFont
    size: int
    scale: int
    border: int
    margin: Margin
    max_height: int

    @classmethod
    def static_init(cls, factory: ItemGraphicsFactory):
        fontpath: str = get_assets_path(factory.properties['coordinate']['font'])
        if not os.path.exists(fontpath):
            raise FileNotFoundError("Font file not found")
        cls.font = ImageFont.truetype(fontpath, 24)
        cls.size = factory.properties['coordinate']['font-size']
        cls.border = factory.properties['coordinate']['font-border-size']
        cls.scale = factory.properties['coordinate']['font-scale']
        cls.max_height = factory.properties['coordinate']['font-max-height']
        margin: list[int] = factory.properties['coordinate']['font-margin']
        if len(margin) == 2:
            cls.margin = Margin(left=margin[0], top=margin[1], right=margin[0], bottom=margin[1])
        elif len(margin) == 4:
            cls.margin = Margin(left=margin[0], top=margin[1], right=margin[2], bottom=margin[3])
        elif len(margin) == 1:
            cls.margin = Margin(left=margin[0], top=margin[0], right=margin[0], bottom=margin[0])
        else:
            cls.margin = Margin()


    @classmethod
    def draw_text_with_outline(
        cls,
        text: str,
        text_color: str | tuple = 'white',
        outline_color: str | tuple = 'black',
        outline_width: int = 1
    ):
        image = Image.new('RGBA', (cls.font.size * len(text), 2 * cls.font.size))
        draw = ImageDraw.Draw(image)
        # Draw outline by drawing text multiple times at different offsets
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((2 * outline_width + dx, 2 * outline_width + dy), text, font=cls.font, fill=outline_color)
        # Draw the main text
        draw.text((2 * outline_width, 2 * outline_width), text, font=cls.font, fill=text_color)
        image = image.crop(image.getbbox())
        return image.resize((image.width * cls.scale, image.height * cls.scale), Image.Resampling.NEAREST)

    @classmethod
    def create_number(
        cls,
        number: int,
        line_color: str | tuple,
        inner_color: str | tuple = 'white',
        *,
        with_margin: bool = False,
        with_box: tuple[int | None, int | None] | None = None
        ) -> Image.Image:
        """
        分值的绘制
        
        :param number: 分值 (正数表示正常分值，负数表示括号的分数)
        :param line_color: 分值线的颜色
        :param inner_color: 分值字体的颜色
        """
        image = cls.draw_text_with_outline(
            str(number) if number > 0 else f'({-number})',
            inner_color,
            line_color,
            cls.border
        )
        if with_margin:
            new_image = Image.new('RGBA', (image.width + cls.margin.width, image.height + cls.margin.height))
            if with_box:
                width, height = with_box
                new_image.paste(image, ((width or new_image.width - image.width) // 2, (height or new_image.height - image.height) // 2))
                return new_image
            else:
                new_image.paste(image, (cls.margin.left, cls.margin.top))
                return new_image
        return image
