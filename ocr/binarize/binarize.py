import cv
import optparse

class Binarizer:
    #Future subclasses:
    #Thresholding (how do we get the threshold?)
    #Locally adaptive binarization
    def __init__(self, offset):
        self.offset = offset
    def binarize(self, image):
        '''Given an image, return a black and white image'''
        #Potential pain point in the future:
        #What if we want to use a grayscale algorithm?
        return image

class SimpleBinarizer(Binarizer):

    def __init__(self, offset):
        Binarizer.__init__(self, offset)
        
        
    def binarize(self, im):
        '''Given an image, return a black and white image. Uses OPenCV's 
        adaptive thresholding with blockSize as large as possible'''
        grayIm = self.formatImage(im)
        #create an image that will eventually be a binarization of the input image
        thresh = cv.CreateImage((grayIm.width, grayIm.height), 8, 1)
        #get parameter values
        maxVal = 255
        bSize = self.getBlockSize(grayIm)
        #create the binarized image
        cv.AdaptiveThreshold(grayIm, thresh, maxVal, blockSize=bSize)
        return thresh
    
    def formatImage(self, image):
        if image.nChannels == 1:
            return image
        elif image.nChannels == 3:
            grayIm = cv.CreateImage((image.width, image.height), 8, 1)
            cv.CvtColor(image, grayIm, cv.CV_RGB2GRAY)
            return grayIm
        else:
            raise Exception("Incorrect number of image channels.")
        
    def getBlockSize(self, image):
        '''Given an image, determines the blockSize argument for binarize().
        Chooses largest possible blockSize''' 
        blockSize = min(image.width, image.height)
        if blockSize % 2 == 0:
                blockSize = blockSize - 1
        return blockSize

class LocalBinarizer(Binarizer):
    def __init__(self, offset, proportion):
        Binarizer.__init__(self, offset)
        self.proportion = proportion

    def binarize(self, im):
        '''Given an image, return a black and white image. Uses OPenCV's 
        adaptive thresholding with blockSize as large as possible'''
        #create an image that will eventually be a binarization of the input image
        #get parameter values
        maxVal = 255
        bSize = self.getBlockSize(im)
        #create the binarized image
        numWhitePixels, bestPixels = 0,0
        bestThreshold = None
        channels = self.formatImage(im)
        thresh = [cv.CreateImage((im.width, im.height), 8, 1) for i in range(len(channels))]
        for (threshold, channel) in zip(thresh, channels):
            cv.AdaptiveThreshold(channel, threshold, maxVal, adaptive_method=cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C, blockSize=bSize, param1=1+self.offset)
        if len(thresh) == 1:
            return thresh[0]
        for (threshold, channel) in zip(thresh, channels):
            for row in range(threshold.height):
                for col in range(threshold.width):
                    if threshold[row,col] == 255:
                        numWhitePixels += 1
            if numWhitePixels >= bestPixels or im.width*im.height - numWhitePixels >= bestPixels:
                if numWhitePixels == im.width*im.height or numWhitePixels == 0: #This is a huge hack and should be fixed
                    cv.Copy(channel, threshold)
                    if bestThreshold == None:
                        bestThreshold = threshold
                else:
                    if im.width*im.height - numWhitePixels >= bestPixels:
                        newThreshold = cv.CreateImage((im.width, im.height), 8, 1)
                        cv.Not(threshold, newThreshold)
                        print "inverting"
                        threshold = newThreshold
                    bestPixels = numWhitePixels
                    #print bSize, "assigning threshold"
                    bestThreshold = threshold
            numWhitePixels = 0
        #for (threshold, i) in zip(thresh, range(3)):
            #cv.SaveImage("/Accounts/mccartya/carletonocr/"+str(i)+".png", threshold)
        return bestThreshold

    def formatImage(self, image):
        if image.nChannels == 1:
            return [image]
        elif image.nChannels == 3:
            channels = [cv.CreateImage((image.width, image.height), 8, 1) for i in range(3)]
            cv.Split(image, channels[0], channels[1], channels[2], None)
            return channels
        else:
            raise Exception("Incorrect number of image channels.")

    def getBlockSize(self, image):
        '''Given an image, determines the blockSize argument for binarize().
        Defaults to the largest possible blockSize, which can be scaled down.'''
        if self.proportion > 1:
            blockSize = max(image.width, image.height)
        else:
            blockSize = int(max(image.width, image.height) * self.proportion)
        if blockSize % 2 == 0:
            blockSize = blockSize + 1
        #print blockSize
        return blockSize

def main():
    parser = optparse.OptionParser(usage="usage: %prog [options] image", version="%prog 0.1")
    (options, args) = parser.parse_args()
    image = cv.LoadImage(args[0])
    binarizer = LocalBinarizer()
    binarizer.binarize(image)
if __name__ == "__main__":
    main()
