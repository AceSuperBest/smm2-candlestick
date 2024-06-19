from PIL import Image

ico_png = Image.open("template/kline-ico.png")

ico_png.save("kline.ico", format="ICO", sizes=[(256, 256)])
