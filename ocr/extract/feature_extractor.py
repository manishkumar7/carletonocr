import cv

class FeatureExtractor(object):
    def extract(self, input):
        '''Returns a features object, with a similarity method'''
        return Features()
       
class Features(object):
    def similarity(self, other):
        return 0

def whiteImage(size):
    vis = cv.CreateImage(size, 8, 3)
    cv.Rectangle(vis, (0,0), size, cv.RGB(255, 255, 255), -1)        
    return vis
