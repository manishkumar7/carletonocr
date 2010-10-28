FONT_DIR = "/usr/share/fonts/TTF/"
FONT_SIZE = 32
TARGET_DIR = "/tmp/ocr/"

import samples
import os

for font in os.listdir(FONT_DIR):
    if font[-4:] == ".ttf":
        try:
            os.mkdir(TARGET_DIR+font[:-4])
            samples.run(FONT_DIR+font, FONT_SIZE, TARGET_DIR, outdir=TARGET_DIR+font[:-4]+'/')
        except OSError:
            continue
