import cv
import os

class FeatureExtractor(object):
    def extract(self, input):
        '''Returns a features object, with a similarity method'''
        return Features()


def buildLibrary(path, scaler, featureExtractor):
    dirs = os.listdir(path)
    chars = []
    for dir in dirs:
    	place = path+os.sep+dir
        files = os.listdir(place)
        library = []
        for file in files:
            im = cv.LoadImage(place + os.sep + file, cv.CV_LOAD_IMAGE_GRAYSCALE)
            library.append([file[0],featureExtractor.extract(scaler.scale(im))])
        chars.extend(library)
    return chars


class Scaler(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def scale(self, image):
        scaled = cv.CreateImage((self.width, self.height), 8, 1)
        cv.Resize(image, scaled, cv.CV_INTER_NN)
        return scaled
'''
class ProportionalScaler(Scaler):
    def __init__(self, width, height):
        Scaler.__init__(self, width, height)
    def scale(self, image):
        scaled = cv.CreateImage((self.width, self.height), 8, 1)
        if float(image.width)/image.height > float(self.width)/self.height:
            
        else:
            ...
        return scaled
'''     
       
class Features(object):
    def similarity(self, other):
        return 0

class TemplateImage(Features):
    def __init__(self, image):
        self.image = image
    def similarity(self, other):
        '''Determines the distance between shared pixels of self.image and other.image '''
        inputIm = self.image
        templateIm = other.image
        dist = 0
        assert inputIm.width == templateIm.width and inputIm.height == templateIm.height
        size = (inputIm.width, inputIm.height)
        inputLi = cv.InitLineIterator(inputIm, (0, 0), size)
        templateLi = cv.InitLineIterator(templateIm, (0, 0), size)
        zipped = zip(inputLi, templateLi)
        n11 = .01
        n00 = .01
        n10 = .01
        n01 = .01
        for pair in zipped:
            if round(pair[0]) == 255:
                if round(pair[1]) == 255:
                    n11 += 1
                elif round(pair[1]) == 0:
                    n10 += 1
            elif round(pair[0]) == 0:
                if round(pair[1]) == 255:
                    n01 += 1
                elif round(pair[1]) == 0:
                    n00 += 1
            else:
                raise Exception("Why is there a pixel with value " + str(pair[0]))
        distJ = float(n11)/(n11 + n10 + n01)
        distY = (float(n11) * n00 - float(n10) * n01)/(float(n11) * n00 + float(n10) * n01)
        return distJ

class TemplateComparison(FeatureExtractor):
    def extract(self, image):
        return TemplateImage(image)
