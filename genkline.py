import random
import datetime
import csv


today = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
days = [today - datetime.timedelta(days=i) for i in range(26)]

header = ["timestamp", "open", "high", "low", "close"]
datas: list[list[int]] = []

now = 7500

for day in days:
    t = int(day.timestamp())
    delta = random.randint(-100, 100)
    o = now
    c = now + delta
    h = max(o, c) + random.randint(0, 50)
    l = min(o, c) - random.randint(0, 50)
    datas.append([t, o, h, l, c])
    now = c

# save to csv
with open("kline-ico.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(datas)
