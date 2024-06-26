import asset
import sys
import os


WINDOWS = os.name == 'nt'

factory = asset.asset_init()
i18n = asset.utils.get_i18n('notice')

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
    argv1 = (sys.argv[1] if len(sys.argv) > 1 else '').lower().strip()
    csv_file = argv1 if argv1 and argv1.endswith('.csv') else CANDLE_FILEPATHS['csv']
    if not os.path.exists(csv_file):
        filepath = get_file()
        if not filepath:
            message_box(i18n['please-precreate'].format(csv=CANDLE_FILENAMES['csv']))
            sys.exit(1)
        group = asset.CandleGroup(csv_file=filepath)
    else: group = asset.CandleGroup(csv_file=csv_file)
    group.check_error()
    candlestick, number, merged = group.merged_tuple
    candlestick.save(CANDLE_FILEPATHS['candlestick'])
    number.save(CANDLE_FILEPATHS['number'])
    merged.save(CANDLE_FILEPATHS['merged'])
    message_box(i18n['success'].format(**CANDLE_FILENAMES))
except Exception as e:
    import traceback
    traceback.print_exc()
    message_box(i18n['error'].format(error=e, **CANDLE_FILENAMES), title=i18n['error-title'])
    sys.exit(-1)
