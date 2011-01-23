import cv
import os
from ocr.typeset import characterCombine

def buildLibrary(path, binarizer, scaler, segmenter, featureExtractor):
    dirs = os.listdir(path)
    chars = []
    for dir in dirs:
    	place = path+os.sep+dir
        try:
            files = os.listdir(place)
            for file in files:
                #print file
                im = cv.LoadImage(place + os.sep + file, cv.CV_LOAD_IMAGE_COLOR)
                try: 
                    processed = binarizer.binarize(scaler.scale(binarizer.binarize(im)))
                    chars.append([file[0],featureExtractor.extract(processed)])
                except cv.error:
                    pass
                #processed = characterCombine(typesetter.typeset(processed))
                #cv.SaveImage("/Accounts/ehrenbed/Desktop/stuff2/"+file, processed)
        except OSError:
            # Goddamn OS X and its goddamn DS_STORE crap
            pass
    return chars
