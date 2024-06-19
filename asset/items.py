from PIL import Image
from graphics import CommonGraphics
import json as jsonlib
from typing import Any
import os


class ItemGraphicsFactory:
    def __init__(self, assets_floder: str):
        self._assets_floder = assets_floder
        self._mapper: dict[str, CommonGraphics] = {}
        self._properties: dict[str, dict[str, Any]] = {}
        # 历遍assets_floder下的所有文件
        ## 历遍所有的png文件，构建CommonGraphics对象
        for file in os.listdir(assets_floder):
            if file.endswith(".png"):
                name = file[:-4]
                properties: dict[str, Any] = jsonlib.load(open(f"{assets_floder}/{name}.json", encoding="utf-8"))
                image = Image.open(f"{assets_floder}/{file}")
                self._mapper[name] = CommonGraphics(image, properties)
        ## 历遍剩余的json文件，构建properties
        for file in os.listdir(assets_floder):
            if file.endswith(".json"):
                name = file[:-5]
                if name not in self._mapper:
                    self._properties[name] = jsonlib.load(open(f"{assets_floder}/{file}", encoding="utf-8"))

    def __getitem__(self, key: str) -> CommonGraphics | None:
        return self._mapper.get(key, None)

    @property
    def properties(self) -> dict[str, dict[str, Any]]:
        return self._properties
