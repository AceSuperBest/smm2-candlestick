from asset import *
from PIL import Image
import csv


factory = ItemGraphicsFactory("assets")
CandleGraphicsResources.static_init(factory)

klines: list[Candle] = []

with open('kline.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        t, o, h, l, c = map(int, row)
        klines.append(Candle(timestamp=t, open=o, high=h, low=l, close=c))
    klines.sort(key=lambda x: x.timestamp)

spacing = 25 * CandleGraphicsResources.scale # 间隔(multiplied by scale)

kline_groups = [kline.draw_candle() for kline in klines]
kline_images = [group[0] for group in kline_groups]
kline_structures = [group[1] for group in kline_groups]

y_max = max(kline.high for kline in klines)
y_min = min(kline.low for kline in klines)
y_range = (y_max - y_min) * CandleGraphicsResources.scale
x_range = sum(image.width for image in kline_images) + spacing * (len(klines) - 1)

image = Image.new("RGBA", (x_range, y_range))
x_now = 0

for i, (kline, kline_image) in enumerate(zip(klines, kline_images)):
    image.paste(kline_image, (
        x_now,
        (y_max - kline.high) * CandleGraphicsResources.scale
    ))
    x_now += kline_image.width + spacing


image.save("kline.png")
