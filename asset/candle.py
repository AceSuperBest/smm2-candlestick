from .items import ItemGraphicsFactory
from PIL import Image, ImageDraw
from graphics import Direction, CommonGraphics
from pydantic import BaseModel


__all__ = ["Candle", "CandleGraphicsResources", "CandleStructure"]


class CandleStructure(BaseModel):
    up: int
    body: int
    down: int
    scale: int
    width: int

    @property
    def up_height(self) -> int:
        if self.body == 0 and self.up:
            return self.up * self.scale - 1
        return self.up * self.scale

    @property
    def body_height(self) -> int:
        return self.body * self.scale or 1

    @property
    def down_height(self) -> int:
        if self.body == 0 and self.down and not self.up:
            return self.down * self.scale - 1
        return self.down * self.scale


class CandleGraphicsResources:
    sword: CommonGraphics
    green: CommonGraphics
    red: CommonGraphics
    green_solid: Image.Image
    red_solid: Image.Image
    black_solid: Image.Image
    width: int
    scale: int

    @staticmethod
    def create_solid(color: str, width: int) -> Image.Image:
        image = Image.new("RGBA", (width, 1))
        draw = ImageDraw.Draw(image)
        draw.line((0, 0, image.width, 0), fill=color, width=image.width)
        return image

    @classmethod
    def static_init(cls, factory: ItemGraphicsFactory):
        cls.sword = factory["sword"]
        cls.green = factory["green-pipe"]
        cls.red = factory["red-pipe"]
        assert cls.sword and cls.green and cls.red, "Invalid graphics"
        cls.scale = max(cls.green.scale, cls.red.scale, cls.sword.scale)
        cls.width = max(cls.green.width.maximun, cls.red.width.maximun, cls.sword.width.maximun)
        cls.green_solid = cls.create_solid('green', cls.width * cls.scale)
        cls.red_solid = cls.create_solid('red', cls.width * cls.scale)
        cls.black_solid = cls.create_solid('black', cls.width * cls.scale)

    @classmethod
    def gen_arrow(cls, length: int, up: bool = True) -> Image.Image | None:
        if length <= 0:
            return None
        return cls.sword.gen_image(
            length,
            scale=cls.scale,
            direction=(Direction.up if up else Direction.down)
        )

    @classmethod
    def gen_body(cls, length: int, should_up: int, green_up: bool = False) -> Image.Image:
        """
        生成K线的实体部分
        
        :param length: 实体长度(符号携带方向)
        :param should_up: 是否为上涨(-1: 下跌, 0: 横盘, 1: 上涨)
        :param green_up: 是否为绿涨红跌(国际标准)
        """
        if length == 0:
            if should_up == 0:
                return cls.black_solid
            return (should_up < 0) ^ green_up and cls.green_solid or cls.red_solid
        return ((length > 0) ^ green_up and cls.green or cls.red).gen_image(
            abs(length),
            scale=cls.scale,
            direction=(Direction.down if length > 0 else Direction.up)
        )

    @classmethod
    def gen_candle(cls, up_length: int, body_length: int, down_length: int, green_up: bool = False):
        """
        生成单个K线的图像，以及绘制参数
        """
        should_up = up_length - down_length
        up_image = cls.gen_arrow(up_length, up=True)
        down_image = cls.gen_arrow(down_length, up=False)
        if body_length == 0:
            # 无实体时占用up/down的1px
            if up_image:
                up_image = up_image.crop((0, 0, up_image.width, up_image.height - 1))
            elif down_image:
                down_image = down_image.crop((0, 1, down_image.width, down_image.height))
        body_image = cls.gen_body(body_length, should_up, green_up)
        image = cls.vertical_combine_images(up_image, body_image, down_image)
        return image, CandleStructure(
            up=up_length,
            body=body_length,
            down=down_length,
            scale=cls.scale,
            width=image.width
        )

    @staticmethod
    def vertical_combine_images(*images: Image.Image | None) -> Image.Image:
        """
        垂直居中合并Image对象
        """
        images = list(filter(None, images))
        max_width = max(map(lambda x: x.width, images))
        max_height = sum(map(lambda x: x.height, images))
        image = Image.new("RGBA", (max_width, max_height))
        y = 0
        for img in images:
            image.paste(img, ((max_width - img.width) // 2, y))
            y += img.height
        return image


class Candle(BaseModel):
    timestamp: int
    open: int
    high: int
    low: int
    close: int

    @property
    def up_length(self) -> int:
        return self.high - max(self.open, self.close)

    @property
    def body_length(self) -> int:
        return self.close - self.open

    @property
    def down_length(self) -> int:
        return min(self.open, self.close) - self.low

    def draw_candle(self, green: bool = False):
        """
        基于当前的K线数据绘制K线柱
        
        :param green: 是否为绿涨红跌(国际标准)
        """
        return CandleGraphicsResources.gen_candle(self.up_length, self.body_length, self.down_length, green)
