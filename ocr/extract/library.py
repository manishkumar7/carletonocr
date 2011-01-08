import cv
import os

def buildLibrary(path, binarizer, scaler, featureExtractor):
    dirs = os.listdir(path)
    chars = []
    for dir in dirs:
    	place = path+os.sep+dir
        files = os.listdir(place)
        library = []
        for file in files:
            im = cv.LoadImage(place + os.sep + file, cv.CV_LOAD_IMAGE_GRAYSCALE)
            library.append([file[0],featureExtractor.extract(scaler.scale(binarizer.binarize(im)))])
        chars.extend(library)
    return chars
