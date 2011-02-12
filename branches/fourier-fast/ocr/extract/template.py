import cv
from feature_extractor import *

class TemplateImage(Features):
    def __init__(self, image):
        self.image = image
    def similarity(self, other):
        '''Determines the distance between shared pixels of self.image and other.image '''
        inputIm = self.image
        templateIm = other.image
        dist = 0
        assert inputIm.width == templateIm.width and inputIm.height == templateIm.height
        n11 = .01
        n00 = .01
        n10 = .01
        n01 = .01
        for row in range(inputIm.height):
            for col in range(inputIm.width):
                input = inputIm[row, col]
                template = templateIm[row, col]
                if input == 255:
                    if template == 255:
                        n11 += 1
                    elif template == 0:
                        n10 += 1
                    else:
                        raise Exception("Why is there a pixel with value " + str(pair[0]))
                elif input == 0:
                    if template == 255:
                        n01 += 1
                    elif template == 0:
                        n00 += 1
                    else:
                        raise Exception("Why is there a pixel with value " + str(pair[0]))
                else:
                    raise Exception("Why is there a pixel with value " + str(pair[0]))
        return self.formula(n00, n01, n10, n11)
    def visualize(self):
        vis = cv.CreateImage((self.image.width, self.image.height), 8, 3)
        cv.CvtColor(self.image, vis, cv.CV_GRAY2RGB)
        return vis

class TemplateImageOldFormula(TemplateImage):
    def formula(self, n00, n01, n10, n11):
        return (n00 + n11)/float(n11 + n00 + n10 + n01)

class TemplateImageNewFormula(TemplateImage):
    def formula(self, n00, n01, n10, n11):
        return float(n11)/(n11 + n10 + n01)

class TemplateComparisonOldFormula(FeatureExtractor):
    def extract(self, image):
        return TemplateImageOldFormula(image)

class TemplateComparisonNewFormula(FeatureExtractor):
    def extract(self, image):
        return TemplateImageNewFormula(image)
