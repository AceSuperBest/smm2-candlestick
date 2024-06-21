# SMM2 - Candlestick Chart Generator

[![Build and Release](https://github.com/AceSuperBest/smm2-candlestick/actions/workflows/build.yaml/badge.svg)](https://github.com/AceSuperBest/smm2-candlestick/actions/workflows/build.yaml)

## Introduction
Create a python script that generates candlestick charts from multiplayer scores in SMM2 (Super Mario Maker 2).

**Inspired by the Bai fan community.**

This project isn't perfect yet—there's still a lot to do, and the mechanics are likely to change quite a bit. So, if you have any requests or suggestions, please drop them in the issues.

## Quick Start
Minimum Requirement: Install [Python](https://www.python.org/downloads/)
### Installation
*If a virtual environment is required, it needs to be created and activated in advance.*

```shell
pip install pillow pydantic
```

or

```shell
pip install -r requirements.txt
```

or In Release

Download Release

### Populate kline.csv
Currently, the timestamp is not used; it only needs to be logically sequential. The program will automatically sort the timestamp field in the CSV data in ascending order.

kline.csv:

```csv
timestamp,open,high,low,close
1718640000,7500,7622,7488,7583
1718553600,7583,7603,7491,7536
1718467200,7536,7572,7442,7445
1718380800,7445,7452,7406,7426
1718294400,7426,7456,7359,7394
1718208000,7394,7440,7314,7335
1718121600,7335,7461,7299,7412
...
```

### Generate
Run in the current directory path (ensure the 'assets' folder and 'kline.csv' are present).

```shell
python app.py
```

or In Release

Open the app.exe

### Result
kline.png:

![kline](template/kline.png)