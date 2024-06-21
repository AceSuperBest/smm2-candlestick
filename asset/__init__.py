from asset.items import ItemGraphicsFactory
from asset.candle import *
from asset.number import *
from asset import utils


def asset_init():
    factory = ItemGraphicsFactory(utils.get_executable_directory('assets'))
    CandleGraphicsResources.static_init(factory)
    NumberGraphicsResources.static_init(factory)
    return factory
