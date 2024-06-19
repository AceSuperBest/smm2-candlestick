from asset import *
import sys
import os

WINDOWS = os.name == 'nt'

def get_executable_directory():
    if getattr(sys, 'frozen', False):
        # 如果程序是被PyInstaller打包后的可执行文件
        application_path = os.path.dirname(sys.executable)
    else:
        # 如果是直接运行的脚本
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path

factory = ItemGraphicsFactory(os.path.join(get_executable_directory(), 'assets'))
CandleGraphicsResources.static_init(factory)

CANDLE_NAME = 'kline'

if WINDOWS:
    from utils.winhelper import create_selector, message_box

    def get_file():
        return create_selector("选择K线数据文件", [("CSV文件", "*.csv")])
else:
    def message_box(message):
        print(message)

    def get_file():
        return None


try:
    if not os.path.exists('kline.csv'):
        filepath = get_file()
        if not filepath:
            message_box("请先创建kline.csv文件")
            sys.exit(1)
        group = CandleGroup(csv_file=filepath)
    else: group = CandleGroup(csv_file='kline.csv')
    image = group.image
    image.save("kline.png")
    message_box("生成kline.png成功")
except Exception as e:
    import traceback
    traceback.print_exc()
    message_box(f"生成kline.png失败: {e}")
    sys.exit(-1)
