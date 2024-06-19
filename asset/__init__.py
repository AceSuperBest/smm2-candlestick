from asset.items import ItemGraphicsFactory
from asset.candle import *


# 从assets文件夹中加载所有的图片资源
factory = ItemGraphicsFactory("assets")
CandleGraphicsResources.static_init(factory)