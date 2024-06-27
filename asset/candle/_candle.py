from PIL import Image
from pydantic import BaseModel
from ._resources import CandleGraphicsResources
from ._structure import CandleStructure
from ._enum import CandleErrorStatus
from asset.number import NumberGraphicsResources


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

    @property
    def should_up(self) -> int:
        return self.body_length or self.up_length - self.down_length

    @property
    def should_up_check(self) -> bool:
        return self.should_up > 0

    @property
    def color(self) -> str:
        return self.should_up_check ^ CandleGraphicsResources.green_up and 'red' or (self.should_up == 0) and 'black' or 'green'

    @property
    def check(self):
        if self.open < 0 or self.high < 0 or self.low < 0 or self.close < 0:
            return CandleErrorStatus.SCORE_NEGATIVE
        if self.high < max(self.open, self.close):
            return CandleErrorStatus.HIGH_LESS_THAN_MAX
        if self.low > min(self.open, self.close):
            return CandleErrorStatus.LOW_GREATER_THAN_MIN
        return CandleErrorStatus.NORMAL

    @property
    def error_message(self):
        return f'{self.timestamp}: {CandleGraphicsResources.i18n.get(self.check.name, 'UNKNOWN')}'

    def _draw_number(self, with_box: tuple[int | None, int | None] | None = None) -> Image.Image | tuple[Image.Image, Image.Image, Image.Image, Image.Image]:
        color = self.color
        if self.body_length == 0 and self.should_up == 0 and self.up_length == 0 and self.down_length == 0:
            return NumberGraphicsResources.create_number(self.close, color, with_margin=True, with_box=with_box)
        return (
            NumberGraphicsResources.create_number(-self.open, color, with_margin=True, with_box=with_box),
            NumberGraphicsResources.create_number(self.high, color, with_margin=True, with_box=with_box),
            NumberGraphicsResources.create_number(self.low, color, with_margin=True, with_box=with_box),
            NumberGraphicsResources.create_number(-self.close, color, with_margin=True, with_box=with_box)
        )

    def draw_candle(self):
        """
        基于当前的K线数据绘制K线柱

        :param green: 是否为绿涨红跌(国际标准)
        """
        return CandleGraphicsResources.gen_candle(self.up_length, self.body_length, self.down_length)

    def draw_number(self, structure: CandleStructure):
        """
        绘制K线柱的数值

        :param structure: 绘制参数
        :param green: 是否为绿涨红跌(国际标准)
        """
        images = self._draw_number(with_box=(None, None))
        if isinstance(images, Image.Image):
            canvas = structure.empty_canvas
            return CandleGraphicsResources.vertical_combine_images(canvas, images), 0
        o, h, l, c = images
        body_need = o.height + c.height
        body_top = self.should_up_check and c or o
        body_down = self.should_up_check and o or c
        if structure.body_height < body_need:
            return structure.generate_image([h, body_top], None, None, [body_down, l])
        return structure.generate_image([h], body_top, body_down, [l])

    def draw_datetime(self, with_box: tuple[int | None, int | None] | None = None):
        """
        绘制K线柱的时间

        :param with_box: 是否需要边框 (以及边框的配置)
        """
        return NumberGraphicsResources.create_datetime(self.timestamp, self.color, with_box=with_box)
