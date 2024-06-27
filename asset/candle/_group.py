import datetime
from typing import overload
from ._candle import Candle
from ._enum import CandleErrorStatus
from ._resources import CandleGraphicsResources
from ._structure import CandleStructure
from ._coordination import Coordination
from asset.number import NumberGraphicsResources
from PIL import Image
import csv


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
                    try:
                        t, *ohlc = row
                        o, h, l, c = map(int, ohlc)
                        if not t.isdigit():
                            t = t.replace("T", " ").replace("Z", "").replace("/", "-").replace(".", "-")
                            t = datetime.datetime.fromisoformat(t).timestamp()
                        t = int(t)
                    except: continue
                    self._candles.append(Candle(timestamp=t, open=o, high=h, low=l, close=c))
                self._candles.sort(key=lambda x: x.timestamp)
        else:
            raise ValueError("Missing required arguments: candles or csv_file")

    def __len__(self) -> int:
        return len(self._candles)

    def __getitem__(self, index: int) -> Candle:
        return self._candles[index].model_copy()

    def check_error(self):
        errors = [candle for candle in self._candles if candle.check != CandleErrorStatus.NORMAL]
        if errors:
            raise ValueError(f"{CandleGraphicsResources.i18n['invalid-candles']}\n{'\n'.join(error.error_message for error in errors)}")

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
                image, structure = candle.draw_candle()
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

    @property
    def big_image(self) -> Image.Image:
        """
        大图像
        """
        if getattr(self, "_big_image", None) is None:
            self._big_image = Image.new("RGBA", (self.width, self.height + 4 * NumberGraphicsResources.max_height))
            self._big_image.paste(self.image, (0, 2 * NumberGraphicsResources.max_height))
        return self._big_image

    @property
    def number_images(self):
        """
        数值图像列表 (每个K线的数值图像)
        """
        if getattr(self, "_number_images", None) is None:
            self._number_images: list[tuple[Image.Image, int]] = []
            for candle, structure in zip(self._candles, self.structures):
                self._number_images.append(candle.draw_number(structure))
        return self._number_images

    @property
    def number_image(self) -> Image.Image:
        """
        数值结果图像
        """
        if getattr(self, "_number_image", None) is None:
            self._number_image = Image.new("RGBA", (self.width, self.height + 4 * NumberGraphicsResources.max_height))
            for x_now, y_now, (image, y_offset) in zip(self.x_indexes, self.y_indexes, self.number_images):
                self._number_image.paste(image, (x_now, y_now + 2 * NumberGraphicsResources.max_height - y_offset))
        return self._number_image

    @property
    def coordinate(self) -> Image.Image:
        """
        坐标轴图像
        """
        if getattr(self, "_coordinate", None) is None:
            self._coordinate = Coordination.vertical(self.y_max, self.y_min)
        return self._coordinate

    @property
    def horizontal(self) -> Image.Image:
        """
        水平坐标图像
        """
        if getattr(self, "_horizontal", None) is None:
            self._horizontal = Coordination.horizontal(self._candles)
        return self._horizontal

    @property
    def merged_image(self) -> Image.Image:
        """
        合并结果图像
        """
        if getattr(self, "_merged_image", None) is None:
            self._merged_image = Image.alpha_composite(self.big_image, self.number_image)
        return self._merged_image

    @property
    def merged_tuple(self) -> tuple[Image.Image, ...]:
        """
        合并结果图像元组
        """
        return (
            self.image,
            self.number_image.crop(self.number_image.getbbox()),
            self.merged_image.crop(self.merged_image.getbbox()),
            self.coordinate,
            self.horizontal,
        )