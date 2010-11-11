import cv
import sys
import os

from nltk.model.ngram import NgramModel
from nltk.corpus import brown

class OCR:
    def __init__(self, image, binarizer, segmenter, typesetter, matcher, linguist):
        self.image = image
        self.binarizer = binarizer
        self.segmenter = segmenter
        self.typesetter = typesetter
        self.matcher = matcher
        self.linguist = linguist
        
    def recognize(self):
        blackAndWhite = self.binarizer.binarize(self.image)
        characterPieces = self.segmenter.segment(blackAndWhite)
        pieces = self.typesetter.typeset(characterPieces)
        output = self.matcher.match(pieces)
        output = self.linguist.correct(output)
        return output
        
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

class Segmenter:
    #Future subclasses:
    #Flood fill
    def segment(self, blackAndWhite):
        '''Given a black and white image, return a list of image
        pieces which each stand for an individual character'''
        #Potential pain point in the future:
        #Segmentation maybe should use knowledge about characters;
        #What do we do with overlapping characters
        #or characters that aren't contiguous
        return []
    
class ConnectedComponentSegmenter(Segmenter):
    
    def segment(self, blackAndWhite):
        pixels = set((row,col) for row in range(blackAndWhite.height) for col in range(blackAndWhite.width))
        output = []
        while pixels:
            pixel = pixels.pop()
            if blackAndWhite[pixel] == 0:
                 output.append(self.findConnectedComponents(blackAndWhite, pixel, pixels))
        return output
    
    def findConnectedComponents(self, image, pixel, pixels):
        points = set([pixel])
        pointsToSearch = [pixel]
        while pointsToSearch:
            workListPoint = pointsToSearch.pop()
            #print "Searching for points adjacent to %d, %d!" % workListPoint
            wLRow, wLCol = workListPoint
            potentialAdjacentPoints = set([(wLRow, wLCol-1), (wLRow, wLCol+1), (wLRow-1, wLCol), (wLRow+1, wLCol)]) - points
            adjacentPoints = set()
            for p in potentialAdjacentPoints:
                #print p
                tmpRow, tmpCol = p
                if tmpRow >= 0 and tmpCol >= 0 and tmpCol < image.width and tmpRow < image.height and image[p] == 0.0:
                    #print "Including an adjacent point!"
                    adjacentPoints.add(p)
            points |= adjacentPoints
            pointsToSearch.extend(list(adjacentPoints))
        for point in points:
            if point in pixels:
                pixels.remove(point)
        boundingBox = self.boundingBox(points)
        newImage = self.createImage(boundingBox, points)
        return (boundingBox, newImage)
    
    def boundingBox(self, points):
        minRow, minCol, maxRow, maxCol = 99999999999,99999999999,0,0
        for point in points:
            if point[0] < minRow:
                minRow = point[0]
            if point[0] > maxRow:
                maxRow = point[0]
        for point in points:
            if point[1] < minCol:
                minCol = point[1]
            if point[1] > maxCol:
                maxCol = point[1]
        #(x,y,width,height)
        return (minCol, minRow, maxCol-minCol, maxRow-minRow)
    
    def createImage(self, boundingBox, points):
        newImage = cv.CreateImage((boundingBox[2], boundingBox[3]), 8, 1)
        for row in range(boundingBox[3]):
            for col in range(boundingBox[2]):
                if (row+boundingBox[1], col+boundingBox[0]) in points:
                    newImage[row,col] = 0
                else:
                    newImage[row,col] = 255
        return newImage


class BoundingBoxSegmenter(Segmenter):

    def segment(self, blackAndWhite):
        letters = []
        images = []
        for col in range(blackAndWhite.width):
            for row in range(blackAndWhite.height):
                if blackAndWhite[row,col] == 0.0 and not self.inBoundingBox(letters, (row, col)):
                    #print "Adding a box starting from the pixel %d, %d!" % (row, col)
                    newBox = self.findBox(blackAndWhite, row, col)
                    #print "Added a box at",  newBox
                    letters.append(newBox)
                    #print letters
        #print letters
        for letter in letters:
            newImage = cv.CreateImage((letter[2], letter[3]+1), 8, 1)
            src_region = cv.GetSubRect(blackAndWhite, (letter[0], letter[1], letter[2], letter[3]+1))
            cv.Copy(src_region, newImage)
            images.append((letter, newImage))
        return images

    def inBoundingBox(self, boundingBoxes, point):
        for box in boundingBoxes:
            #print box, point
            if point[0] >= box[1] and point[0] <= box[3]+box[1] and point[1] >= box[0] and point[1] <= box[2] + box[0]:
                return True
        return False
    
    def findBox(self, image, row, col):
        points = set([(row, col)])
        pointsToSearch = [(row, col)]
        while pointsToSearch:
            workListPoint = pointsToSearch.pop()
            #print "Searching for points adjacent to %d, %d!" % workListPoint
            wLRow, wLCol = workListPoint
            potentialAdjacentPoints = set([(wLRow, wLCol-1), (wLRow, wLCol+1), (wLRow-1, wLCol), (wLRow+1, wLCol)]) - points
            adjacentPoints = set()
            for p in potentialAdjacentPoints:
                #print p
                tmpRow, tmpCol = p
                if tmpRow >= 0 and tmpCol >= 0 and tmpCol < image.width and tmpRow < image.height and image[p] == 0.0:
                    #print "Including an adjacent point!"
                    adjacentPoints.add(p)
            points |= adjacentPoints
            pointsToSearch.extend(list(adjacentPoints))
        return self.boundingBox(points)
        
    def boundingBox(self, points):
        minRow, minCol, maxRow, maxCol = 99999999999,99999999999,0,0
        for point in points:
            if point[0] < minRow:
                minRow = point[0]
            if point[0] > maxRow:
                maxRow = point[0]
        for point in points:
            if point[1] < minCol:
                minCol = point[1]
            if point[1] > maxCol:
                maxCol = point[1]
        #(x,y,width,height)
        return (minCol, minRow, maxCol-minCol, maxRow-minRow)

class FeatureExtractor:
    #Future subclasses:
    #dummy, normalizing (for template matching)
    #Thinning
    #Contours
    #Zernike moment
    def extractFeatures(self, imagePiece):
        '''Given part of an image, extract its features
        so that they're in a form suitable for matching'''
        return None
        
class Matcher:
    #Future subclasses:
    #kNN, with different distance metrics
    #Neural networks
    def __init__(self, library, featureExtractor):
        self.library = self.createLibrary(library) #library of characters; all matchers need this
        self.featureExtractor = featureExtractor

    def createLibrary(self, library):
        dirs = os.listdir(library)
        chars = []
        for dir in dirs:
                chars.extend(self.__addDirectoryContents(library+'/'+dir))
        return chars
        
        
    
    def __addDirectoryContents(self, dir):
        #try:
            files = os.listdir(dir)
            library = []
            for file in files:
                im = cv.LoadImage(dir + '/' + file, cv.CV_LOAD_IMAGE_GRAYSCALE)
                library.append([file[0],im])
            return library
        #except IOError: return []
    
    def match(self,characterPieces):
        output = []
        for piece in characterPieces:
            if isinstance(piece, str):
                output += piece
            else:
                features = self.featureExtractor.extract(piece)
                newChar = self.bestGuess(features)
                output.append(newChar)
        return output
        
    def bestGuess(self, features):
        '''Given a feature list, choose a character from the library'''
        return ''
        
    def geometricMean(self, list):
        return reduce(lambda x, y: x*y, list)**(1.0/len(list))

class TemplateMatcher(Matcher):      
    def __init__(self, library, featureExtractor, width, height):
        self.width = width #width that all images will be scaled to
        self.height = height #height that all images will be scaled to
        Matcher.__init__(self, library, featureExtractor)

    def resize(self, image):
        scaled = cv.CreateImage((self.width, self.height), 8, 1)
        cv.Resize(image, scaled, cv.CV_INTER_NN)
        return scaled
        
    def pixelDist(self, inputIm, templateIm):
        '''Determines the distance between shared pixels of 'inputIm' and 'templateIm' '''
        dist = 0
        inputLi = cv.InitLineIterator(inputIm, (0, 0), (self.width, self.height))
        templateLi = cv.InitLineIterator(templateIm, (0, 0), (self.width, self.height))
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
            else:
                print "Why is there a pixel with value", pair[0]
        distJ = float(n11)/(n11 + n10 + n01)
        distY = (float(n11) * n00 - float(n10) * n01)/(float(n11) * n00 + float(n10) * n01)
        return distJ                
        
    def findPixelMatch(self, inputIm, templateList):
        '''Finds the best match according to 'pixelDist()' and returns it if less than the cutoff'''
        best = (templateList[0][0], self.pixelDist(inputIm, templateList[0][1]))
        for template in templateList[1:]:
            pDist = self.pixelDist(inputIm, template[1])
            if pDist > best[1]:
                best = (template[0], pDist)
        return [(best[0], best[1])]
                
    def findMatch(self, inputIm, templateList):
        '''Finds the best match for 'inputIm' in 'templateList' and returns it if it satisfies the
        given cutoffs'''
        inputIm = self.resize(inputIm)
        for template in templateList:
                template[1] = self.resize(template[1])
        match = self.findPixelMatch(inputIm, templateList)
        return match
    
    def bestGuess(self, features):
        '''Given a feature list, choose a character from the library. Assumes the library is a list'''
        return self.findMatch(features, self.library)   
    
class knnTemplateMatcher(TemplateMatcher):
    def __init__(self, library, featureExtractor, width, height, k):
        self.k = k
        TemplateMatcher.__init__(self, library, featureExtractor, width, height)

    def findPixelMatch(self, inputIm, templateList):
        '''Finds the best match according to 'pixelDist()' and returns it if less than the cutoff'''
        k = min(len(templateList), self.k)
        best = []
        for i in range(k):
            best.append((self.pixelDist(inputIm, templateList[i][1]), templateList[i][0]))
        best.sort()
        for template in templateList[k:]:
            pDist = self.pixelDist(inputIm, template[1])
            if pDist > best[0][0]:
                best.pop(0)
                best.append((pDist, template[0]))
                best.sort()
        voteDict = {}
        for match in best:
                if match[1] in voteDict:
                    voteDict[match[1]] += match[0]
                else:
                    voteDict[match[1]] = match[0]
        cands = voteDict.keys()
        #print voteDict
        if len(cands) == 0:
            return []
        else:
            return voteDict.items()

class Linguist(object):
    #Future subclasses:
    #n-grams (for words and for characters) -- would need library
    #Deeper linguistic knowledge?
    def correct(self, characterPossibilities):
        '''Correct errors based on linguistic knowledge'''
        output = ''
        context = self.makeContext()
        for item in characterPossibilities:
            if isinstance(item, str):
                output += item
            else:
                maxProbability = -99999
                bestLetter = ''
                for character, probability in item:
                    realProbability = self.probability(character, probability, context)
                    if probability > maxProbability:
                        bestLetter = character
                        maxProbability = probability
                self.updateContext(context, bestLetter)
                output += bestLetter
        return output
    
    def makeContext(self):
        return None
    
    def updateContext(self, context, letter):
        pass
    
    def probability(self, character, oldProbability, context):
        return oldProbability

class NGramLinguist(Linguist):

    def __init__(self, data, n, selfImportance):
        self.n = n
        self.selfImportance = selfImportance
        self.model = NgramModel(n, list(data))

    def makeContext(self):
        return []
    
    def updateContext(self, context, letter):
        context.append(letter)
        if len(context) == self.n: #context should never get longer than that
            context.pop(0)
    
    def probability(self, character, oldProbability, context):
        modelProbability = self.model.prob(character, context)
        return oldProbability*(1-self.selfImportance) + modelProbability*self.selfImportance
        
class FeatureExtractor(object):
    def extract(self, input):
        return input
        

class Typesetter(object):
    def typeset(self, characterPieces):
        return [character[1] for character in characterPieces]

class LinearTypesetter(Typesetter):

    def bestPieceBy(self, pieces, utility):
        bestPiece = None
        bestUtility = None
        for piece in pieces:
            if bestPiece == None:
                myUtility = utility(piece)
                if myUtility:
                    bestPiece = piece
                    bestUtility = myUtility
            else:
                myUtility = utility(piece)
                if myUtility and myUtility < bestUtility:
                    bestPiece = piece
                    bestUtility = myUtility
        if bestPiece != None:
            pieces.remove(bestPiece)
        return bestPiece

    def findFirstPiece(self, pieces):
        return self.bestPieceBy(pieces, lambda piece: piece[0][0]+piece[0][1])
    
    def findNextPiece(self, piecesLeft, currentLine):
        minRow = 999999999
        maxRow = 0
        for (box, image) in currentLine[-5:]:
            if box[1] < minRow:
                minRow = box[1]
            if box[1]+box[3] > maxRow:
                maxRow = box[1]+box[3]
        minCol = currentLine[-1][0][0]
        def utility(piece):
            if piece[0][0] < minCol or piece[0][1]+piece[0][3] < minRow or piece[0][1] > maxRow:
                return False
            else:
                return piece[0][0]
        return self.bestPieceBy(piecesLeft, utility)
    
    def isaSpaceBetween(self, char, lastChar, line):
        averageWidth = sum(character[0][2] for character in line)/float(len(line))
        return char[0][0]-(lastChar[0][0]+lastChar[0][2]) > averageWidth/4
        
    def lines(self, characterPieces):
        piecesLeft = set(characterPieces)
        lines = []
        while len(piecesLeft) != 0:
            firstPiece = self.findFirstPiece(piecesLeft)
            currentLine = [firstPiece]
            while True:
                next = self.findNextPiece(piecesLeft, currentLine)
                if next == None: break
                currentLine.append(next)
            lines.append(currentLine)
        return lines
    
    def spacesAndNewlines(self, lines):
        output = []
        for line in lines:
            lastChar = None
            for char in line:
                if lastChar != None:
                    if self.isaSpaceBetween(char, lastChar, line):
                        output.append(' ')
                lastChar = char
                output.append(char[1]) #OK up to here
            output.append('\n')
        return output
    
    def rangesOverlap(self, box1, box2, offset):
        return box1[offset] < box2[offset]+box2[offset+2] and box2[offset] < box1[offset]+box1[offset+2]
    
    def combineImages(self, box1, image1, box2, image2):
        outputBox = (min(box1[0], box2[0]), min(box1[1], box2[1]), max(box1[0]+box1[2], box2[0]+box2[2])-min(box1[0], box2[0]), max(box1[1]+box1[3], box2[1]+box2[3])-min(box1[1], box2[1]))
        outputImage = cv.CreateImage((outputBox[2], outputBox[3]), 8, 1)
        cv.Rectangle(outputImage,(0,0),(outputImage.height, outputImage.width),255,-1)
        for box, image in [(box1, image1), (box2, image2)]:
            offset = (box[0] - outputBox[0], box[1] - outputBox[1])
            for row in range(image.height):
                for col in range(image.width):
                    #print 'setting a pixel at', (row, col)
                    outputImage[row+offset[1], col+offset[0]] = image[row,col]
        #cv.SaveImage("j.png",outputImage)
        return outputBox, outputImage
    
    def combineVertical(self, line):
        #print 'doing a line'
        accumulatedBox = None
        accumulatedImage = None
        newLine = []
        for box, image in line:
            #print 'looking at a character'
            if accumulatedBox == None:
                accumulatedBox = box
                accumulatedImage = image
            else:
                if self.rangesOverlap(accumulatedBox, box, 0) and not self.rangesOverlap(accumulatedBox, box, 1):
                    #print 'combining'
                    accumulatedBox, accumulatedImage = self.combineImages(box, image, accumulatedBox, accumulatedImage)
                else:
                    #print 'not combining'
                    newLine.append((accumulatedBox, accumulatedImage))
                    accumulatedBox = box
                    accumulatedImage = image
        if accumulatedBox != None:
            newLine.append((accumulatedBox, accumulatedImage))
        return newLine
    
    def typeset(self, characterPieces):
        return self.spacesAndNewlines([self.combineVertical(line) for line in self.lines(characterPieces)])
        
'''
Example usage:
image = cv.LoadImageImage('foo.jpg')
binarizer = AdaptiveBinarization()
segmenter = FloodSegmenter()
matcher = KNN(5, CharacterLibrary('/dev/urandom', ContourFeatures())
linguist = NGramCorrector('/dev/null')
text, confidence = OCR(image, binarizer, segmenter, matcher, linguist)
'''


if __name__ == '__main__':
    im = cv.LoadImage(sys.argv[1], cv.CV_LOAD_IMAGE_GRAYSCALE)
    binarizer = SimpleBinarizer()
    segmenter = ConnectedComponentSegmenter()
    typesetter = LinearTypesetter()
    #matcher = TemplateMatcher('/Accounts/courses/comps/text_recognition/300/all', FeatureExtractor(), 100, 100)
    matcher = knnTemplateMatcher('/Accounts/courses/comps/text_recognition/300/all', FeatureExtractor(), 100, 100, 1)
    linguist = Linguist()
    #linguist = NGramLinguist(''.join(brown.words()), 3, .3)
    string = OCR(im, binarizer, segmenter, typesetter, matcher, linguist).recognize()
    print string