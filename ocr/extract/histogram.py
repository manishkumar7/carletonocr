import numpy
from feature_extractor import *

class Histogram(Features):
    def __init__(self, image, axis):
        self.size = (image.width, image.height)
        self.histogram = numpy.sum(numpy.invert(numpyOfImage(image)), axis=axis)
    def similarity(self, other):
        return 1.0/(numpy.sum(numpy.absolute(numpy.subtract(self.histogram, other.histogram)))+1)

class HorizontalHistogram(Histogram):
    def __init__(self, image):
        Histogram.__init__(self, image, 1)
    def visualize(self):
        vis = whiteImage(self.size)
        for i in range(len(self.histogram)):
            for j in range(self.histogram[i]):
                vis [i,j] = (0,0,255)
        return vis

class VerticalHistogram(Histogram):
    def __init__(self, image):
        Histogram.__init__(self, image, 0)
    def visualize(self):
        vis = whiteImage(self.size)
        for i in range(len(self.histogram)):
            for j in range(self.histogram[i]):
                vis [j,i] = (255,0,0)
        return vis

class VerticalAndHorizontalHistogram(Features):
    def __init__(self, image):
        self.verticalHistogram = VerticalHistogram(image)
        self.horizontalHistogram = HorizontalHistogram(image)
    def similarity(self, other):
        return self.verticalHistogram.similarity(other.verticalHistogram) \
            + self.horizontalHistogram.similarity(other.horizontalHistogram)
    def visualize(self):
        vis = self.horizontalHistogram.visualize()
        for i in range(len(self.verticalHistogram.histogram)):
            for j in range(self.verticalHistogram.histogram[i]):
                if vis [j,i] != (255,255,255):
                    vis[j,i] = (255,40,200)
                else:
                    vis[j,i] = (255,0,0)
        return vis

class HistogramComparison(FeatureExtractor):
    def extract(self, image):
        return VerticalAndHorizontalHistogram(image)

class VerticalHistogramComparison(FeatureExtractor):
    def extract(self, image):
        return VerticalHistogram(image)

class HorizontalHistogramComparison(FeatureExtractor):
    def extract(self, image):
        return HorizontalHistogram(image)
