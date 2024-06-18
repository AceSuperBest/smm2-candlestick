from asset import *


factory = ItemGraphicsFactory("assets")
CandleGraphicsResources.static_init(factory)


while True:
    try:
        datas: list[str] = input().split()
        if len(datas) != 4:
            print("Invalid input")
            continue
        o, h, l, c = map(int, datas)
        candle = Candle(timestamp=0, open=o, high=h, low=l, close=c)
        image, struct = candle.draw_candle(factory)
        image.show()
    except KeyboardInterrupt:
        print("Exit")
        break
