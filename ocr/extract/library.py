import cv
import os
from ocr.typeset import characterCombine

def buildLibrary(path, binarizer, scaler, segmenter, featureExtractor):
    dirs = os.listdir(path)
    chars = []
    for dir in dirs:
    	place = path+os.sep+dir
        files = os.listdir(place)
        for file in files:
            #print file
            im = cv.LoadImage(place + os.sep + file, cv.CV_LOAD_IMAGE_COLOR)
            processed = scaler.scale(binarizer.binarize(im))
            #processed = characterCombine(typesetter.typeset(processed))
            #cv.SaveImage("/Accounts/ehrenbed/Desktop/stuff2/"+file, processed)
            chars.append([file[0],featureExtractor.extract(processed)])
    return chars
