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
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    else:
        # found no content
        raise ValueError("cannot trim; image was empty")

def render(font, char, path):
    font = ImageFont.truetype(path+font+'.ttf', pointSize)
    im = Image.new("L", (20, 20), 255)
    draw = ImageDraw.Draw(im)
    width, height = draw.textsize(char, font=font)
    lines = char.split('\n')
    im = im.resize((width, height*len(lines)))
    draw = ImageDraw.Draw(im)
    y = 0
    for line in lines:
        draw.text((0,y), line, font=font)
        y += height
    im = trim(im, 255)
    cv_im = cv.CreateImageHeader(im.size, cv.IPL_DEPTH_8U, 1)
    cv.SetData(cv_im, im.tostring())
    return cv_im

def buildLibrary(path):
    chars = []
    for font in fonts:
        for char in charsToGenerate:
            chars.append((char, render(font, char, path)))
    return chars
