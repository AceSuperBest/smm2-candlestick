from PIL import Image
from graphics import CommonGraphics
import json as jsonlib
from typing import Any, Callable
import os


class ItemGraphicsFactory:
    def __init__(self, assets_floder: str):
        self._assets_floder = assets_floder
        self._mapper: dict[str, CommonGraphics] = {}
        # 历遍assets_floder下的所有文件
        for file in os.listdir(assets_floder):
            if file.endswith(".png"):
                name = file[:-4]
                properties: dict[str, Any] = jsonlib.load(open(f"{assets_floder}/{name}.json", encoding="utf-8"))
                image = Image.open(f"{assets_floder}/{file}")
                self._mapper[name] = CommonGraphics(image, properties)

    def __getitem__(self, key: str) -> CommonGraphics | None:
        return self._mapper.get(key, None)


class StaticGraphicsFactory:
    statics: dict[str, Image.Image] = {}

    @classmethod
    def create(cls, name: str, generator: Callable[[], Image.Image]):
        if name not in cls.statics:
            cls.statics[name] = generator()
        return cls.statics[name]
