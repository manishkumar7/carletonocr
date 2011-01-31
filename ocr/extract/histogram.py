import cv, math
from feature_extractor import *

class ImageTranspose(object):
    def __init__(self, image):
        self.image = image
        self.width = image.width
        self.height = image.height
    def __getitem__(self, index):
        return self.image[index[1], index[0]]

class HorizontalHistogram(Features):
    def __init__(self, image):
        self.size = (image.width, image.height)
        self.histogram = [sum(((image[row, col] == 0 and 1) or 0) for col in range(image.width)) for row in range(image.height)]
    def similarity(self, other):
        return 1.0/(sum(abs(mine-yours) for (mine, yours) in zip(self.histogram, other.histogram))+1)
    def visualize(self):
        vis = whiteImage(self.size)
        for i in range(len(self.histogram)):
            for j in range(self.histogram[i]):
                vis [i,j] = (0,0,255)
        return vis

class VerticalHistogram(HorizontalHistogram):
    def __init__(self, image):
        image = ImageTranspose(image)
        self.histogram = [sum(((image[row, col] == 0 and 1) or 0) for col in range(image.width)) for row in range(image.height)]
        self.size = (image.width, image.height)
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
