from PIL import Image, ImageDraw, ImageFont
from .items import ItemGraphicsFactory
from .utils import get_assets_path, get_i18n
from pydantic import BaseModel
import datetime
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
    upper_font: ImageFont.FreeTypeFont
    size: int
    scale: int
    border: int
    margin: Margin
    max_height: int
    upper: bool
    number_height: int
    i18n: dict[str, str]
    color: str | tuple[int, int, int]

    @classmethod
    def static_init(cls, factory: ItemGraphicsFactory):
        fontpath: str = get_assets_path(factory.properties['coordinate']['font'])
        if not os.path.exists(fontpath):
            raise FileNotFoundError("Font file not found")
        cls.size = factory.properties['coordinate']['font-size']
        cls.border = factory.properties['coordinate']['font-border-size']
        cls.font = ImageFont.truetype(fontpath, cls.size - cls.border)
        cls.upper_font = ImageFont.truetype(fontpath, cls.size - cls.border + 1)
        cls.scale = factory.properties['coordinate']['font-scale']
        margin: list[int] = factory.properties['coordinate']['font-margin']
        if len(margin) == 2:
            cls.margin = Margin(left=margin[0], top=margin[1], right=margin[0], bottom=margin[1])
        elif len(margin) == 4:
            cls.margin = Margin(left=margin[0], top=margin[1], right=margin[2], bottom=margin[3])
        elif len(margin) == 1:
            cls.margin = Margin(left=margin[0], top=margin[0], right=margin[0], bottom=margin[0])
        else:
            cls.margin = Margin()
        cls.max_height = factory.properties['coordinate']['font-max-height']
        cls.max_height = max(cls.max_height, (cls.margin.height + cls.size) * cls.scale)
        color = factory.properties['coordinate']['font-color']
        if isinstance(color, str) and color.startswith('#'):
            color = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
        cls.color = color
        test_number = cls.create_number(8888, 'black')
        cls.upper = bool(test_number.height % 2)
        cls.number_height = test_number.height
        cls.i18n = get_i18n('text')


    @classmethod
    def draw_text_with_outline(
        cls,
        text: str,
        text_color: str | tuple = 'white',
        outline_color: str | tuple = 'black',
        outline_width: int = 1,
        *,
        upper: bool = False
    ) -> Image.Image:
        font = cls.upper_font if upper else cls.font
        image = Image.new('RGBA', (font.size * len(text), 2 * font.size))
        draw = ImageDraw.Draw(image)
        # Draw outline by drawing text multiple times at different offsets
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((2 * outline_width + dx, 2 * outline_width + dy), text, font=font, fill=outline_color)
        # Draw the main text
        draw.text((2 * outline_width, 2 * outline_width), text, font=font, fill=text_color)
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
        with_box: tuple[int | None, int | None] | None = None,
        upper: bool = False
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
            cls.border,
            upper=upper
        )
        if with_margin:
            new_image = Image.new('RGBA', (image.width + cls.margin.width, max(image.height + cls.margin.height, cls.max_height)))
            if with_box:
                width, height = with_box
                new_image.paste(image, ((width or new_image.width - image.width) // 2, (height or new_image.height - image.height) // 2))
                return new_image
            else:
                new_image.paste(image, (cls.margin.left, cls.margin.top))
                return new_image
        return image

    @classmethod
    def create_datetime(
        cls,
        timestamp: int | datetime.datetime,
        color: str | tuple[int, int, int] = 'black',
        *,
        with_box: tuple[int | None, int | None] | None = None
    ) -> Image.Image:
        """
        生成日期时间的图像
        """
        if isinstance(timestamp, int):
            timestamp = datetime.datetime.fromtimestamp(timestamp)
        date_text = timestamp.date().strftime(f'%Y{cls.i18n["year"]}%m{cls.i18n["month"]}%d{cls.i18n["day"]}')
        date_image = cls.draw_text_with_outline(date_text, outline_color=color, outline_width=cls.border)
        time = timestamp.time()
        if time != time.min:
            time_text = time.strftime('%H:%M:%S')
            time_image = cls.draw_text_with_outline(time_text, outline_color=color, outline_width=cls.border)
            image = Image.new('RGBA', (max(date_image.width, time_image.width), date_image.height + time_image.height))
            image.paste(date_image, ((image.width - date_image.width) // 2, 0))
            image.paste(time_image, ((image.width - time_image.width) // 2, date_image.height))
        else: image = date_image
        if with_box:
            width, height = with_box
            width = max(width or image.width, image.width)
            height = max(height or image.height, image.height)
            new_image = Image.new('RGBA', (width, height))
            new_image.paste(image, ((width - image.width) // 2, (height - image.height) // 2))
            image = new_image
        return image
