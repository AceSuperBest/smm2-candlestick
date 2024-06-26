import asset


factory = asset.asset_init()


group = asset.CandleGroup(candles=[
    asset.Candle(
        timestamp=0,
        open=7000,
        close=7025,
        high=7026,
        low=7000
    ),
])

group.merged_image.show()
