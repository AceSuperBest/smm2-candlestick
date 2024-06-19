from asset import *

group = CandleGroup(csv_file='kline.csv')

print('最高分', group.y_max, '最低分', group.y_min)

image = group.image

image.save("kline.png")
