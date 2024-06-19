from .items import ItemGraphicsFactory
from PIL import Image, ImageDraw
from graphics import Direction, CommonGraphics
from pydantic import BaseModel
from typing import overload
import csv


__all__ = ["Candle", "CandleGraphicsResources", "CandleStructure", "CandleGroup"]


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
    spacing: int
    green_up: bool

    @staticmethod
    def create_solid(color: str, width: int, scale: int = 1) -> Image.Image:
        image = Image.new("RGBA", (width * scale, scale))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, image.width, image.height), fill=color, width=scale)
        return image

    @classmethod
    def static_init(cls, factory: ItemGraphicsFactory):
        cls.sword = factory["sword"]
        cls.green = factory["green-pipe"]
        cls.red = factory["red-pipe"]
        assert cls.sword and cls.green and cls.red, "Invalid graphics"
        cls.spacing = int(factory.properties['coordinate']['spacing'])
        cls.green_up = bool(factory.properties['candlestick']['green_up'])
        # cls.scale = max(cls.green.scale, cls.red.scale, cls.sword.scale)
        cls.scale = int(factory.properties['candlestick']['scale']) # 让像分比例统一，并统一配置
        cls.width = max(cls.green.width.maximun, cls.red.width.maximun, cls.sword.width.maximun)
        cls.green_solid = cls.create_solid('green', cls.width, cls.scale)
        cls.red_solid = cls.create_solid('red', cls.width, cls.scale)
        cls.black_solid = cls.create_solid('black', cls.width, cls.scale)

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
        length += length // abs(length) # 补偿缺的一分
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
        # 不再需要占用别的部分的长度，整数对齐天然给了一倍空间
        # if body_length == 0:
        #     if up_image:
        #         up_image = up_image.crop((0, 0, up_image.width, up_image.height - 1))
        #     elif down_image:
        #         down_image = down_image.crop((0, 1, down_image.width, down_image.height))
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


class CandleGroup:
    @overload
    def __init__(self, *, candles: list[Candle]) -> None:
        """
        使用给定K线数据创建K线组

        :param candles: K线数据列表
        """
        ...

    @overload
    def __init__(self, *, csv_file: str) -> None:
        """
        使用给定CSV文件创建K线组

        1. 必须满足以下格式:

        - timestamp, open, high, low, close

        2. 必须包含上述的标题行

        :param csv_file: CSV文件路径
        """
        ...

    def __init__(
        self, *,
        candles: list[Candle] | None = None,
        csv_file: str | None = None
    ) -> None:
        if candles is not None:
            self._candles = sorted(candles, key=lambda x: x.timestamp)
        elif csv_file is not None:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                _ = next(reader) # skip header
                self._candles = []
                for row in reader:
                    t, o, h, l, c = map(int, row)
                    self._candles.append(Candle(timestamp=t, open=o, high=h, low=l, close=c))
                self._candles.sort(key=lambda x: x.timestamp)
        else:
            raise ValueError("Missing required arguments: candles or csv_file")

    def __len__(self) -> int:
        return len(self._candles)

    def __getitem__(self, index: int) -> Candle:
        return self._candles[index].model_copy()

    @property
    def spacing(self) -> int:
        """
        间隔 (像素) = 间隔分值 * 像分比例

        :return: assets.coordinate.spacing * assets.candlestick.scale
        """
        return CandleGraphicsResources.spacing * CandleGraphicsResources.scale

    @property
    def candle_width(self) -> int:
        """
        每K线图像宽度
        """
        return CandleGraphicsResources.width * CandleGraphicsResources.scale

    @property
    def y_max(self) -> int:
        """
        最高分
        """
        if getattr(self, "_y_max", None) is None:
            self._y_max = max(candle.high for candle in self._candles)
        return self._y_max

    @property
    def y_min(self) -> int:
        """
        最低分
        """
        if getattr(self, "_y_min", None) is None:
            self._y_min = min(candle.low for candle in self._candles)
        return self._y_min

    @property
    def x_indexes(self):
        """
        X轴索引列表
        """
        return [x * (self.candle_width + self.spacing) for x in range(len(self))]

    @property
    def y_indexes(self):
        """
        Y轴索引列表
        """
        if getattr(self, "_y_indexes", None) is None:
            self._y_indexes = [(self.y_max - candle.high) * CandleGraphicsResources.scale for candle in self._candles]
        return self._y_indexes

    @property
    def width(self) -> int:
        """
        图像宽度
        """
        return len(self) * self.candle_width + self.spacing * (len(self) - 1)

    @property
    def height(self) -> int:
        """
        图像高度
        """
        return (self.y_max - self.y_min + 1) * CandleGraphicsResources.scale

    def _gen_klines(self):
        if getattr(self, "_images", None) is None:
            self._images = []
            self._structures = []
            for candle in self._candles:
                image, structure = candle.draw_candle(CandleGraphicsResources.green_up)
                self._images.append(image)
                self._structures.append(structure)

    @property
    def images(self) -> list[Image.Image]:
        """
        子图像列表 (每个K线的图像)
        """
        self._gen_klines()
        return self._images

    @property
    def structures(self) -> list[CandleStructure]:
        """
        子图像构建参数列表 (每个K线的绘制参数) - 用于绘制坐标轴或数值等
        """
        self._gen_klines()
        return self._structures

    @property
    def image(self) -> Image.Image:
        """
        结果图像
        """
        if getattr(self, "_image", None) is None:
            self._image = Image.new("RGBA", (self.width, self.height))
            for x_now, y_now, image in zip(self.x_indexes, self.y_indexes, self.images):
                self._image.paste(image, (x_now, y_now))
        return self._image

