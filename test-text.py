from asset import *

asset_init()

date = NumberGraphicsResources.draw_text_with_outline('2024年88月88日')
time = NumberGraphicsResources.draw_text_with_outline('00:00:00')

print('date:', date.width, date.height)
print('time:', time.width, time.height)

date.save('test-date.png')
time.save('test-time.png')
datetime = CandleGraphicsResources.vertical_combine_images(date, time)

print('datetime:', datetime.width, datetime.height)

datetime.save('test-datetime.png')
