FONT_DIR = "/home/fivre/work/comps/Library/Fonts/"
FONT_SIZE = 300
TARGET_DIR = "/tmp/ocr/"

import samples
import os

for font in os.listdir(FONT_DIR):
    if font[-4:] == ".ttf":
        try:
            os.mkdir(TARGET_DIR+font[:-4])
            samples.run(FONT_DIR+font, FONT_SIZE, TARGET_DIR, outdir=TARGET_DIR+font[:-4]+'/')
        except OSError, IOError:
            continue
