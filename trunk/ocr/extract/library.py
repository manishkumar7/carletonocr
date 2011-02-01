import cv
import os
from ocr.typeset import characterCombine
import Image, ImageFont, ImageDraw, ImageChops

fonts = ["Times New Roman", "Arial", "Courier New", "Georgia", "Verdana", "Tahoma"]
pointSize = 100
charsToGenerate = map(chr, range(ord('!'), ord('~')+1))

def trim(im, border):
    bg = Image.new(im.mode, im.size, border)
    diff = ImageChops.difference(im, bg)
    diff.save("lib2.png")
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    else:
        # found no content
        raise ValueError("cannot trim; image was empty")

def render(font, char):
    font = ImageFont.truetype('/Library/Fonts/'+font+'.ttf', pointSize)
    im = Image.new("L", (20, 20), 255)
    draw = ImageDraw.Draw(im)
    size = draw.textsize(char, font=font)
    im = im.resize(size)
    draw = ImageDraw.Draw(im)
    draw.text((0,0), char, font=font)
    im = trim(im, 255)
    cv_im = cv.CreateImageHeader(im.size, cv.IPL_DEPTH_8U, 1)
    cv.SetData(cv_im, im.tostring())
    return cv_im

def buildLibrary():
    chars = []
    for font in fonts:
        for char in charsToGenerate:
            chars.append((char, render(font, char)))
    return chars
