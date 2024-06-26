import asset


factory = asset.asset_init()

group = asset.CandleGroup(candles=[
    asset.Candle(
        timestamp=1627603100,
        open=7025,
        close=7025,
        high=7026,
        low=7025
    ),
    asset.Candle(
        timestamp=1627603200,
        open=7000,
        high=7100,
        low=6900,
        close=7050
    ),
    asset.Candle(
        timestamp=1627603300,
        open=7025,
        close=7025,
        high=7030,
        low=7020
    ),
    asset.Candle(
        timestamp=1627603350,
        open=7025,
        close=7025,
        high=7025,
        low=7025
    ),
    asset.Candle(
        timestamp=1627603400,
        open=7050,
        high=7100,
        low=6900,
        close=7000
    ),
    asset.Candle(
        timestamp=1627603500,
        open=7025,
        close=7025,
        high=7025,
        low=7024
    ),
])


group.merged_image.show()
