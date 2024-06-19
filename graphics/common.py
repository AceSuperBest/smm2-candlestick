from .base import *
from .enumeratement import *
from typing import Any
from PIL import Image
from pydantic import BaseModel
from typing_extensions import deprecated


class Structure(BaseModel):
    static: int
    region: int
    duplication: int

    @property
    def maximun(self) -> int:
        return max(self.static, self.region, self.duplication)

    def centralize_static(self, width: int | None = None) -> int:
        """
        配置static居中的x坐标在(upper-left)
        """
        return (width or self.maximun - self.static) // 2

    def centralize_region(self, width: int | None = None) -> int:
        """
        配置region居中的x坐标在(upper-left)
        """
        return (width or self.maximun - self.region) // 2

    def centralize_duplication(self, width: int | None = None) -> int:
        """
        配置duplication居中的x坐标在(upper-left)
        """
        return (width or self.maximun - self.duplication) // 2


def process_coord_str(image: Image.Image, isx: bool, coord_str: int | str) -> int:
    if isinstance(coord_str, int):
        if coord_str < 0:
            return image.width if isx else image.height + coord_str
        return coord_str
    if coord_str.isdigit():
        return int(coord_str)
    if coord_str.endswith("%"):
        return int(coord_str[:-1]) * (image.width if isx else image.height) // 100
    if coord_str.endswith("px"):
        return int(coord_str[:-2])
    match coord_str:
        case "center":
            return image.width // 2 if isx else image.height // 2
        case "min":
            return 0
        case "max":
            return image.width if isx else image.height
        case _:
            raise ValueError(f"Invalid coord_str {coord_str}")


def process_coord(image: Image.Image, x: int | str, y: int | str, w: int | str, h: int | str):
    return (
        process_coord_str(image, True, x),
        process_coord_str(image, False, y),
        process_coord_str(image, True, w),
        process_coord_str(image, False, h)
    )


class CommonGraphics(PropertiesGraphics):
    __GRAPHICS_PROPERTIES__ = { "static", "region", "duplication" }

    @staticmethod
    def transfer(image: Image.Image, x: int | str, y: int | str, w: int | str, h: int | str):
        coord = process_coord(image, x, y, w, h)
        box = (coord[0], coord[1], coord[0] + coord[2], coord[1] + coord[3])
        return image.crop(box)

    def __init__(self, image: Image.Image, properties: dict[str, Any]):
        super().__init__(image, properties)
        assert 'center' not in properties or isinstance(properties["center"], list) and len(properties["center"]) == 2, "Center must be a list with 2 elements"
        self._center: tuple[int, int] = tuple(properties.get("center", (image.width // 2, 0)))
        mode_name = str(properties.get("mode", "")).strip('_')
        assert mode_name in CommonGraphicsMode.__dict__, "Invalid mode"
        self._mode = CommonGraphicsMode[mode_name]
        self._scale = int(properties.get("scale", 1))
        assert self.__GRAPHICS_PROPERTIES__.issubset(properties.keys()), "Invalid properties"
        self._statics = [self.transfer(image, *static) for static in properties.get("static", [])]
        self._regions = [self.transfer(image, *region) for region in properties.get("region", [])]
        self._duplications = [self.transfer(image, *duplication) for duplication in properties.get("duplication", [])]
        assert len(self._statics) <= 1 and len(self._regions) <= 1 and len(self._duplications) == 1, "Not Implemented for multiple statics, regions or duplications"

    @property
    @deprecated("不再支持配置文件的scale")
    def scale(self) -> int:
        return self._scale

    @property
    def static(self) -> Image.Image:
        if getattr(self, "_static", None) is None:
            self._static = self._statics[0] if self._statics else Image.new("RGBA", (0, 0))
        return self._static

    @property
    def region(self) -> Image.Image:
        if getattr(self, "_region", None) is None:
            self._region = self._regions[0] if self._regions else Image.new("RGBA", (0, 0))
        return self._region

    def gen_region(self, length: int):
        if self.region.height <= 0:
            return None, length
        if length < self.region.height:
            return self.region.crop((0, 0, self.region.width, length)), 0
        return self.region, length - self.region.height

    @property
    def duplication(self) -> Image.Image:
        if getattr(self, "_duplication", None) is None:
            self._duplication = self._duplications[0] if self._duplications else Image.new("RGBA", (0, 0))
        return self._duplication

    def gen_duplication(self, length: int):
        if self.duplication.height <= 0:
            return None, length
        quotient, remainder = divmod(length, self.duplication.height)
        new_image = Image.new("RGBA", (self.duplication.width, length))
        for i in range(quotient):
            new_image.paste(self.duplication, (0, i * self.duplication.height))
        new_image.paste(self.duplication.crop((0, 0, self.duplication.width, remainder)), (0, quotient * self.duplication.height))
        return new_image, 0

    @property
    def width(self) -> Structure:
        if getattr(self, "_width", None) is None:
            self._width = Structure(
                static=self.static.width,
                region=self.region.width,
                duplication=self.duplication.width
            )
        return self._width

    @property
    def height(self) -> Structure:
        if getattr(self, "_height", None) is None:
            self._height = Structure(
                static=self.static.height,
                region=self.region.height,
                duplication=self.duplication.height
            )
        return self._height

    def centralize(self, width: int):
        """
        配置居中的x坐标在(upper-left)
        """
        return (width - self.width.maximun) // 2

    def gen_image(self, length: int, *, scale: int | None = None, direction: Direction = Direction.up) -> Image.Image:
        new_image = Image.new("RGBA", (self.width.maximun, self.height.static + length))
        new_image.paste(self.static, (self.width.centralize_static(), 0))
        if length > 0:
            region, length = self.gen_region(length)
            if region:
                new_image.paste(region, (self.width.centralize_region(), self.height.static))
            if length > 0:
                duplication, length = self.gen_duplication(length)
                if duplication:
                    new_image.paste(duplication, (self.width.centralize_duplication(), self.height.static + self.region.height))
        match direction:
            case Direction.up:
                pass
            case Direction.down:
                new_image = new_image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        if scale and scale > 1:
            new_image = new_image.resize((new_image.width * scale, new_image.height * scale), Image.Resampling.NEAREST)
        return new_image

    def draw(self, image: Image.Image, length: int, direction: Direction) -> Image.Image:
        """
        将图像在image上绘制在(x, y)位置
        """
        width_maximun = max(image.width, this_image.width)
        this_image = self.gen_image(length, scale=self._scale, direction=direction)
        height_maximun = image.height + this_image.height
        new_image = Image.new("RGBA", (width_maximun, height_maximun))
        new_image.paste(image, ((width_maximun - image.width) // 2, 0))
        new_image.paste(this_image, (self.centralize(width_maximun), image.height))
        return new_image
