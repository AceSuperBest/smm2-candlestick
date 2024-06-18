from PIL import Image
from abc import ABC, abstractmethod
from typing import Any


class Graphics(ABC):
    def __init__(self, image: Image.Image):
        self._image = image

    @abstractmethod
    def draw(self, image: Image.Image, **args) -> Image.Image:
        """
        将图像在image上
        """
        raise NotImplementedError("Method draw is not implemented")


class PropertiesGraphics(Graphics):
    def __init__(self, image: Image.Image, properties: dict[str, Any]):
        super().__init__(image)
        self._properties = properties

    def __getitem__(self, key: str) -> Any:
        return self._properties[key]


__all__ = ["Graphics", "PropertiesGraphics"]
