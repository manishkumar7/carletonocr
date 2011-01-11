import cv

class Binarizer:
    #Future subclasses:
    #Thresholding (how do we get the threshold?)
    #Locally adaptive binarization
    def binarize(self, image):
        '''Given an image, return a black and white image'''
        #Potential pain point in the future:
        #What if we want to use a grayscale algorithm?
        return image

class SimpleBinarizer(Binarizer):
    def binarize(self, im):
        grayIm = cv.CreateImage((im.width, im.height), 8, 1)
    	cv.CvtColor(im, grayIm, cv.CV_RGB2GRAY)
        '''Given an image, return a black and white image. Uses OPenCV's 
        adaptive thresholding with blockSize as large as possible'''
        #create an image that will eventually be a binarization of the input image
        thresh = cv.CreateImage((grayIm.width, grayIm.height), 8, 1)
        #get parameter values
        maxVal = 255
        bSize = self.getBlockSize(grayIm)
        #create the binarized image
        cv.AdaptiveThreshold(grayIm, thresh, maxVal, blockSize=bSize)
        return thresh
        
    def getBlockSize(self, image):
        '''Given an image, determines the blockSize argument for binarize().
        Chooses largest possible blockSize''' 
        blockSize = min(image.width, image.height)
        if blockSize % 2 == 0:
                blockSize = blockSize - 1
        return blockSize

class LocalBinarizer(Binarizer):
    def binarize(self, im):
        '''Given an image, return a black and white image. Uses OPenCV's 
        adaptive thresholding with blockSize as large as possible'''
        #create an image that will eventually be a binarization of the input image
        thresh = [cv.CreateImage((im.width, im.height), 8, 1) for i in range(3)]
        #get parameter values
        maxVal = 255
        bSize = self.getBlockSize(im)
        #create the binarized image
        numWhitePixels, bestPixels = 0,0
        channels = [cv.CreateImage((im.width, im.height), 8, 1) for i in range(3)]
        cv.Split(im, channels[0], channels[1], channels[2], None)
        for (threshold, channel) in zip(thresh, channels):
        	cv.AdaptiveThreshold(channel, threshold, maxVal, blockSize=bSize)
        for threshold in thresh:
        	for row in range(threshold.height):
        		for col in range(threshold.width):
        			if threshold[row,col] == 255:
        				numWhitePixels += 1
        	if numWhitePixels > bestPixels:
        		bestPixels = numWhitePixels
        		bestThreshold = threshold
        	numWhitePixels = 0
        return bestThreshold
        
    def getBlockSize(self, image, proportion=1):
        '''Given an image, determines the blockSize argument for binarize().
        Defaults to the largest possible blockSize, which can be scaled down.'''
        if proportion > 1:
        	blockSize = min(image.width, image.height)
        else:
        	blockSize = int(min(image.width, image.height) * proportion)
        if blockSize % 2 == 0:
                blockSize = blockSize - 1
        return blockSize