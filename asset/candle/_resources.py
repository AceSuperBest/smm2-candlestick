from PIL import Image, ImageDraw
from asset.items import ItemGraphicsFactory
from ._structure import CandleStructure
from asset.utils import get_i18n
from graphics import CommonGraphics, Direction


class CandleGraphicsResources:
    arrow: CommonGraphics
    green: CommonGraphics
    red: CommonGraphics
    green_solid: Image.Image
    red_solid: Image.Image
    black_solid: Image.Image
    width: int
    scale: int
    spacing: int
    vertical: int
    green_up: bool
    i18n: dict[str, str]

    @staticmethod
    def create_solid(color: str, width: int, scale: int = 1) -> Image.Image:
        image = Image.new("RGBA", (width * scale, scale))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, image.width, image.height), fill=color, width=scale)
        return image

    @classmethod
    def static_init(cls, factory: ItemGraphicsFactory):
        cls.arrow = factory[factory.properties['candlestick']['arrow']]
        cls.green = factory[factory.properties['candlestick']['green']]
        cls.red = factory[factory.properties['candlestick']['red']]
        assert cls.arrow and cls.green and cls.red, "Invalid graphics"
        cls.spacing = int(factory.properties['coordinate']['spacing'])
        cls.vertical = int(factory.properties['coordinate']['vertical-spacing'])
        cls.green_up = bool(factory.properties['candlestick']['green_up'])
        # cls.scale = max(cls.green.scale, cls.red.scale, cls.arrow.scale)
        cls.scale = int(factory.properties['candlestick']['scale']) # 让像分比例统一，并统一配置
        cls.width = max(cls.green.width.maximun, cls.red.width.maximun, cls.arrow.width.maximun)
        cls.green_solid = cls.create_solid('green', cls.width, cls.scale)
        cls.red_solid = cls.create_solid('red', cls.width, cls.scale)
        cls.black_solid = cls.create_solid('black', cls.width, cls.scale)
        cls.i18n = get_i18n('candle')

    @classmethod
    def vertical_round(cls, value: int) -> int:
        return value + (cls.vertical - value % cls.vertical) % cls.vertical

    @classmethod
    def vertical_floor(cls, value: int) -> int:
        return value - value % cls.vertical

    @classmethod
    def gen_arrow(cls, length: int, up: bool = True) -> Image.Image | None:
        if length <= 0:
            return None
        return cls.arrow.gen_image(
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
            return (should_up > 0) ^ green_up and cls.red_solid or cls.green_solid
        length += length // abs(length) # 补偿缺的一分
        return ((length > 0) ^ green_up and cls.red or cls.green).gen_image(
            abs(length),
            scale=cls.scale,
            direction=(Direction.down if length < 0 else Direction.up)
        )

    @classmethod
    def gen_candle(cls, up_length: int, body_length: int, down_length: int):
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
        body_image = cls.gen_body(body_length, should_up, cls.green_up)
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
