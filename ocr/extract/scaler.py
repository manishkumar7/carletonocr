import cv

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

