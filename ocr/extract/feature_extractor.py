import cv, numpy

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

def visualize(lines, features):
    charHeight = lines[0][0][0].height
    charWidth = lines[0][0][0].width
    rowHeight = charHeight * 2
    lineSpacing = charHeight/2
    subSpacing = lineSpacing/2
    newLine = rowHeight + lineSpacing + subSpacing
    spaceWidth = 2*charWidth/5
    padding = spaceWidth/2
    imWidth = max(sum(map(len, line))*(charWidth+padding) - padding + spaceWidth*(len(line)+1) for line in lines)
    imHeight = len(lines) * newLine + 2*spaceWidth - lineSpacing
    featuresVisual = cv.CreateImage((imWidth, imHeight), 8, 3)
    cv.Rectangle(featuresVisual, (0, 0), (imWidth, imHeight), (255, 255, 255), cv.CV_FILLED)

    y = spaceWidth
    for chrLine, featureLine in zip(lines, features):
        x = spaceWidth
        for chrWord, featureWord in zip(chrLine, featureLine):
            for chr, feature in zip(chrWord, featureWord):
                curVis = feature.visualize()
                #assert charHeight == curVis.height == chr.height
                #assert charWidth == curVis.width == chr.width
                for row in range(charHeight):
                    for col in range(charWidth):
                        featuresVisual[y+row, x+col] = curVis[row, col]
                        if chr[row, col]  < 1:
                            featuresVisual[y+row+charHeight+subSpacing, x+col] = (0,0,0)
                x += padding + charWidth
            x += spaceWidth
        y += newLine
    return featuresVisual

def numpyOfImage(image):
    array = numpy.zeros((image.width, image.height), dtype=bool)
    for row in range(image.height):
        for col in range(image.width):
            value = image[row, col]
            if value == 255:
                array[row, col] = True
            elif value == 0:
                array[row, col] = False
            else:
                raise Exception("There is a bug in the scaler or binarizer")
    return array
