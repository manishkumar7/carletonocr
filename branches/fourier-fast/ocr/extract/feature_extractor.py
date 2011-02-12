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

def visualizeFeatures(pieces, features):
    numLines = pieces.count('\n') + 1
    lines = []
    for i in range(numLines):
        #line = [# chrs, sum of chr widths, # spaces]
        lines.append([0,0,0])
    curLine = 0
    yMax = 0
    for chr in pieces:
        if chr == ' ':
            lines[curLine][2] += 1
        elif chr == '\n':
            curLine += 1
        else:
            lines[curLine][0] += 1
            lines[curLine][1] += chr.width
            if chr.height > yMax:
                yMax = chr.height
    totX = sum([l[1] for l in lines])
    spaceWidth = pieces[0].width * .15
    for i in range(len(lines)):
        lines[i][1] += lines[i][0]*spaceWidth + lines[i][2]*spaceWidth*9
    imWidth = max([l[1] for l in lines]) + 2*spaceWidth
    betwLines = 10
    imHeight = numLines * ((2 * yMax) + betwLines)
    featuresVisual = cv.CreateImage((int(imWidth), int(imHeight)), 8, 3)
    cv.Rectangle(featuresVisual, (0,0), (featuresVisual.width, featuresVisual.height), (255,255,255), -1)
    xStart = spaceWidth
    y = 0
    x = xStart
    for chr, feature in zip(pieces, features):
        if chr == ' ':
            x += int(spaceWidth * 9)
        elif chr == '\n':
            x = xStart
            y += int(yMax*2)+betwLines
        else:
            curVis = feature.visualize()
            for row in range(curVis.height):
                for col in range(curVis.width):
                    featuresVisual[y+row, x+col] = curVis[row, col]
            for row in range(chr.height):
                for col in range(chr.width):
                    if chr[row, col]  < 1:
                        featuresVisual[y+row+curVis.height, x+col] = (0,0,0)
            x += (int(spaceWidth) + chr.width)
    return featuresVisual
