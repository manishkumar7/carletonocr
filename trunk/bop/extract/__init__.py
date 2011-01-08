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


class Scaler(object):
    def __init__(self, dimension):
        self.dimension = dimension
    def scale(self, image):
        scaled = cv.CreateImage((self.dimension, self.dimension), 8, 1)
        cv.Resize(image, scaled, cv.CV_INTER_NN)
        return scaled

class ProportionalScaler(Scaler):
    def __init__(self, dimension):
        Scaler.__init__(self, dimension)
    def scale(self, image):
        scaled = cv.CreateImage((self.dimension, self.dimension), 8, 1)
        if image.width > image.height:
            factor = float(self.dimension) / image.width
            targetWidth = self.dimension
            targetHeight = image.height*factor
        else:
            factor = float(self.dimension) / image.height
            targetWidth = image.width*factor
            targetHeight = self.dimension
        matrix = cv.CreateMat(2, 3, cv.CV_64FC1)
        cv.GetAffineTransform([(0, 0), (image.height, 0), (0, image.width)], [(0, 0), (targetHeight, 0), (0, targetWidth)], matrix)
        #print "The transform is", matrix
        cv.WarpAffine(image, scaled, matrix, fillval=255)
        return scaled 

class FeatureExtractor(object):
    def extract(self, input):
        '''Returns a features object, with a similarity method'''
        return Features()
       
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
            #else:
                #raise Exception("Why is there a pixel with value " + str(pair[0]))
        return self.formula(n00, n01, n10, n11)

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

class ImageTranspose(object):
    def __init__(self, image):
        self.image = image
        self.width = image.width
        self.height = image.height
    def __getitem__(self, index):
        return self.image[index[1], index[0]]

def VerticalHistogram(image):
    return HorizontalHistogram(ImageTranspose(image))

class HorizontalHistogram(Features):
    def __init__(self, image):
        self.histogram = [sum(((image[row, col] == 0 and 1) or 0) for col in range(image.width)) for row in range(image.height)]
    def similarity(self, other):
        return 1.0/(sum(abs(mine-yours) for (mine, yours) in zip(self.histogram, other.histogram))+1)

class VerticalAndHorizontalHistogram(Features):
    def __init__(self, image):
        self.verticalHistogram = VerticalHistogram(image)
        self.horizontalHistogram = HorizontalHistogram(image)
    def similarity(self, other):
        return self.verticalHistogram.similarity(other.verticalHistogram) \
            + self.horizontalHistogram.similarity(other.horizontalHistogram)

class HistogramComparison(FeatureExtractor):
    def extract(self, image):
        return VerticalAndHorizontalHistogram(image)

class VerticalHistogramComparison(FeatureExtractor):
    def extract(self, image):
        return VerticalHistogram(image)

class HorizontalHistogramComparison(FeatureExtractor):
    def extract(self, image):
        return HorizontalHistogram(image)
