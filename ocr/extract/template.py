import cv
from feature_extractor import *
import numpy

class TemplateImage(Features):

    def __init__(self, image):
        self.image = image
        self.array = numpyOfImage(image)
        self.notarray = numpy.invert(self.array)

    def similarity(self, other):
        '''Determines the distance between shared pixels of self.image and other.image '''
        assert self.image.width == other.image.width and self.image.height == other.image.height
        def maybe(features, num):
             if num == 0:
                 return features.notarray
             else:
                 return features.array
        def count(a, b):
             return numpy.sum(numpy.bitwise_and(maybe(self, a), maybe(other, b)))
        return self.formula(count(0, 0), count(0, 1), count(1, 0), count(1, 1))

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
