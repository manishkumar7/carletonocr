import cv

class FeatureExtractor(object):
    #Future subclasses:
    #dummy, normalizing (for template matching)
    #Thinning
    #Contours
    #Zernike moment
    def extract(self, input):
        '''Given part of an image, extract its features
        so that they're in a form suitable for matching'''
        return input
