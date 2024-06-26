import csv

klines: list[list[int]] = []


with open('template/kline.csv', 'r+') as f:
    reader = csv.reader(f)
    header = next(reader)
    kline_ts: list[int] = []
    kline_datas: list[list[int]] = []
    for row in reader:
        timestamp, *data = map(int, row)
        kline_ts.append(timestamp)
        kline_datas.append(data)
    kline_ts.reverse()
    for ts, data in zip(kline_ts, kline_datas):
        klines.append([ts, *data])
    f.seek(0)
    f.truncate()
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(klines)
