from ._candle import Candle
from ._resources import CandleGraphicsResources
from asset.number import NumberGraphicsResources
from PIL import Image


class Coordination:
    @classmethod
    def vertical(cls, y_max: int, y_min: int) -> Image.Image:
        """
        生成垂直坐标系的数据图像 (分数)
        """
        y_max = CandleGraphicsResources.vertical_floor(y_max)
        y_min = CandleGraphicsResources.vertical_round(y_min)
        section = CandleGraphicsResources.scale * CandleGraphicsResources.vertical
        spacing = section - NumberGraphicsResources.number_height - int(NumberGraphicsResources.upper)
        images: list[Image.Image] = []
        for y in range(y_max, y_min - 1, -CandleGraphicsResources.vertical):
            images.append(NumberGraphicsResources.create_number(
                y,
                NumberGraphicsResources.color,
                upper=NumberGraphicsResources.upper,
            ))
            images.append(Image.new("RGBA", (CandleGraphicsResources.spacing * CandleGraphicsResources.scale, spacing)))
        images.pop()
        return CandleGraphicsResources.vertical_combine_images(*images)

    @classmethod
    def horizontal(cls, candles: list[Candle]) -> Image.Image:
        """
        生成水平坐标系的数据图像 (日期/时间)
        """
        x_images = [candle.draw_datetime((
            (CandleGraphicsResources.width + CandleGraphicsResources.spacing) * CandleGraphicsResources.scale,
            None
        )) for candle in candles]
        image = Image.new("RGBA", (sum(x.width for x in x_images), max(x.height for x in x_images)))
        x = 0
        for x_image in x_images:
            image.paste(x_image, (x, 0))
            x += x_image.width
        return image
