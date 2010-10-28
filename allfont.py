FONT_DIR = "/Library/Fonts/"
FONT_SIZE = 32
TARGET_DIR = "/tmp/ocr/"

import samples
import os

for font in os.listdir(FONT_DIR):
    if font[-4:] == ".ttf":
        os.mkdir(TARGET_DIR+font[:-4])
        samples.run(FONT_DIR+font, FONT_SIZE, TARGET_DIR, TARGET_DIR+font[:-4])
