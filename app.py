import asset
from PIL import Image
import locale
import sys
import os

WINDOWS = os.name == 'nt'

current_locale, encoding = locale.getdefaultlocale()

if current_locale is None:
    current_locale = 'en'
else:
    current_locale = current_locale.split('_')[0]

factory = asset.asset_init()
i18n = asset.utils.get_i18n(current_locale, 'notice')

CANDLE_NAME = str(factory.properties['candlestick']['name'])

CANDLE_FILENAMES = {
    'csv': f'{CANDLE_NAME}.csv',
    'candlestick': f'{CANDLE_NAME}.png',
    'number': f'{CANDLE_NAME}-number.png',
    'merged': f'{CANDLE_NAME}-merged.png'
}

CANDLE_FILEPATHS = {
    name: asset.utils.get_executable_directory(filename)
    for name, filename in CANDLE_FILENAMES.items()
}


if WINDOWS:
    from utils.winhelper import create_selector, message_box

    def get_file():
        return create_selector(i18n['file-selector-title'], [(i18n['file-selector-filter'], "*.csv")])
else:
    def message_box(message):
        print(message)

    def get_file():
        return None


try:
    if not os.path.exists(CANDLE_FILEPATHS['csv']):
        filepath = get_file()
        if not filepath:
            message_box(i18n['please-precreate'].format(csv=CANDLE_FILENAMES['csv']))
            sys.exit(1)
        group = asset.CandleGroup(csv_file=filepath)
    else: group = asset.CandleGroup(csv_file=CANDLE_FILEPATHS['csv'])
    image = group.image
    number = group.number_image
    image.save(CANDLE_FILEPATHS['candlestick'])
    number.crop(number.getbbox()).save(CANDLE_FILEPATHS['number'])
    big_image = Image.new('RGBA', (number.width, number.height))
    big_image.paste(image, (0, asset.NumberGraphicsResources.max_height * 2))
    merged = Image.alpha_composite(big_image, number)
    merged.crop(merged.getbbox()).save(CANDLE_FILEPATHS['merged'])
    message_box(i18n['success'].format(**CANDLE_FILENAMES))
except Exception as e:
    import traceback
    traceback.print_exc()
    message_box(i18n['error'].format(error=e, **CANDLE_FILENAMES), title=i18n['error-title'])
    sys.exit(-1)
