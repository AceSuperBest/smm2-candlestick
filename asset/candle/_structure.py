from PIL import Image
from pydantic import BaseModel


class CandleStructure(BaseModel):
    up: int
    body: int
    down: int
    scale: int
    width: int

    @property
    def up_height(self) -> int:
        return self.up * self.scale

    @property
    def body_height(self) -> int:
        return (abs(self.body) + 1) * self.scale

    @property
    def down_height(self) -> int:
        return self.down * self.scale

    @property
    def height(self) -> int:
        return self.up_height + self.body_height + self.down_height

    @property
    def empty_canvas(self) -> Image.Image:
        return Image.new("RGBA", (self.width, self.height))

    def extend_canvas(self, width: int, height: int) -> Image.Image:
        return Image.new("RGBA", (self.width + width, self.height + height))

    def generate_image(
        self,
        tops: list[Image.Image],
        body_up: Image.Image | None,
        body_down: Image.Image | None,
        bottoms: list[Image.Image]
    ) -> tuple[Image.Image, int]:
        """
        基于给定的图像区域拼接K线画板
        
        :return: 拼接后的图像, 与K线主要部分的高度
        """
        up_height = sum(map(lambda x: x.height, tops))
        body_height = 0
        if body_up:
            body_height += body_up.height
        if body_down:
            body_height += body_down.height
        down_height = sum(map(lambda x: x.height, bottoms))
        height = up_height + self.height + down_height
        image = Image.new("RGBA", (self.width, height))
        y = 0
        for img in tops:
            image.paste(img, ((self.width - img.width) // 2, y))
            y += img.height
        y += self.up_height
        if self.body_height > body_height:
            if body_up:
                image.paste(body_up, ((self.width - body_up.width) // 2, y))
            if body_down:
                y = y + self.body_height - body_down.height
                image.paste(body_down, ((self.width - body_down.width) // 2, y))
                y += body_down.height
            else:
                y += self.body_height
        else:
            y += self.body_height
        y += self.down_height
        for img in bottoms:
            image.paste(img, ((self.width - img.width) // 2, y))
            y += img.height
        return image, up_height
