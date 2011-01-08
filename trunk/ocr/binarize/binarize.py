import cv

class Binarizer:
    #Future subclasses:
    #Thresholding (how do we get the threshold?)
    #Locally adaptive binarization
    def binarize(self, image):
        '''Given an image, return a black and white image, together with
        a probability that this is correct'''
        #Potential pain point in the future:
        #What if we want to use a grayscale algorithm?
        return image
        
class SimpleBinarizer(Binarizer):
    def binarize(self, im):
        '''Given an image, return a black and white image, together with
        a probability that it is correct. Uses OPenCV's adaptive
        thresholding with blockSize as large as possible'''
        #create an image that will eventually be a binarization of the input image
        thresh = cv.CreateImage((im.width, im.height), 8, 1)
        #get parameter values
        maxVal = 255
        bSize = self.getBlockSize(im)
        #create the binarized image
        cv.AdaptiveThreshold(im, thresh, maxVal, blockSize=bSize)
        return thresh
        
    def getBlockSize(self, image):
        '''Given an image, determines the blockSize argument for binarize().
        Chooses largest possible blockSize''' 
        blockSize = min(image.width, image.height)
        if blockSize % 2 == 0:
                blockSize = blockSize - 1
        return blockSize

