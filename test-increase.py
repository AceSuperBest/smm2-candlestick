import asset


factory = asset.asset_init()


group = asset.CandleGroup(candles=[
    asset.Candle(
        timestamp=0,
        open=7681,
        high=7773,
        low=7681,
        close=7753
    ),
])

group.merged_image.show()
