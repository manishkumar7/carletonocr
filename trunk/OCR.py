import cv
import sys

class OCR:
  def __init__(self, image, binarizer, segmenter, matcher, linguist):
    self.image = image
    self.binarizer = binarizer
    self.segmenter = segmenter
    self.matcher = matcher
    self.linguist = linguist
    
  def recognize(self):
    confidence = 1.0
    blackAndWhite, binConfidence = self.binarizer.binarize(self.image)
    confidence *= binConfidence
    characterPieces, segmentConfidence = self.segmenter.segment(blackAndWhite)
    confidence *= segmentConfidence
    output, matchConfidence = self.matcher.match(characterPieces)
    confidence *= matchConfidence
    output, linguisticConfidence = self.linguist.correct(output)
    confidence *= linguisticConfidence
    return output, confidence
    
class Binarizer:
  #Future subclasses:
  #Thresholding (how do we get the threshold?)
  #Locally adaptive binarization
  def binarize(self, image):
    '''Given an image, return a black and white image, together with
    a probability that this is correct'''
    #Potential pain point in the future:
    #What if we want to use a grayscale algorithm?
    return image, 1.0
    
class SimpleBinarizer(Binarizer):
  def binarize(self, im):
    '''Given an image, return a black and white image, together with
    a probability that it is correct. Uses OPenCV's adaptive
    thresholding with blockSize as large as possibe'''
    #create an image that will eventually be a binarization of the input image
    thresh = cv.CreateImage((im.width, im.height), 8, 1)
    #get parameter values
    maxVal = 255
    bSize = self.getBlockSize(im)
    #create the binarized image
    cv.AdaptiveThreshold(im, thresh, maxVal, blockSize=bSize)
    return thresh, 1.0
    
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
    return [], 1.0
    
class ConnectedComponentSegmenter(Segmenter):

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
            images.append(newImage)
        return images, 1.0

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
    self.library = library #library of characters; all matchers need this
    self.featureExtractor = featureExtractor

  def match(self,characterPieces):
    charConfidences = []
    output = ''
    for piece in characterPieces:
      features = self.featureExtractor.extract(piece)
      newChar, newConfidence = self.bestGuess(features)
      output += newChar
      charConfidences.append(newConfidence)
    outputConfidence = self.geometricMean(charConfidences)
    #output *= self._geometricMean(charConfidences)
    # I'm not entirely clear as to how the above (original) line works:
    # output, a string, is multiplied by _geometricMean, a float?
    # Might just be a typo, the main confidence is what's multiplied during the other steps
    # Anyway, this is a minor point unrelated to the other changes.
    return output, outputConfidence
    
  def bestGuess(self, features):
    '''Given a feature list, choose a character from the library'''
    return '', 1.0
    
  def geometricMean(self, list):
    return reduce(lambda x, y: x*y, list)**(1.0/len(list))

class TemplateMatcher(Matcher):    
  def __init__(self, library, featureExtractor, width, height):
    self.width = width #width that all images will be scaled to
    self.height = height #height that all images will be scaled to
    Matcher.__init__(self, library, featureExtractor)

  def resize(self, image):
    scaled = cv.CreateImage((self.width, self.height), 8, 1)
    cv.Resize(image, scaled)
    return scaled
    
  def pixelDist(self, inputIm, templateIm):
    '''Determines the distance between shared pixels of 'inputIm' and 'templateIm' '''
    dist = 0
    inputLi = cv.InitLineIterator(inputIm, (0, 0), (self.width, self.height))
    templateLi = cv.InitLineIterator(templateIm, (0, 0), (self.width, self.height))
    zipped = zip(inputLi, templateLi)
    for pair in zipped:
      if round(pair[0]) != round(pair[1]):
        dist = dist + 1
    return float(dist)/self.height/self.width        
    
  def findPixelMatch(self, inputIm, templateList, cutoff):
    '''Finds the best match according to 'pixelDist()' and returns it if less than the cutoff'''
    best = (templateList[0][0], self.pixelDist(inputIm, templateList[0][1]))
    for template in templateList[1:]:
      pDist = self.pixelDist(inputIm, template[1])
      if pDist < best[1]:
        best = (template[0], pDist)
    if best[1] < cutoff:
      return   (best[0], 1-best[1])
    else:
      return None
        
  def findMatch(self, inputIm, templateList, pixelCutoff):
    '''Finds the best match for 'inputIm' in 'templateList' and returns it if it satisfies the
    given cutoffs'''
    inputIm = self.resize(inputIm)
    for i in range(len(templateList)):
        templateList[i][1] = self.resize(templateList[i][1])
    match = self.findPixelMatch(inputIm, templateList, pixelCutoff)
    return match
  
  def bestGuess(self, features):
    '''Given a feature list, choose a character from the library. Assumes the library is a list'''
    sizeCutoff = 50
    pixelCutoff = 0.2
    return self.findMatch(features, self.library, pixelCutoff)   

class Linguist(object):
  #Future subclasses:
  #n-grams (for words and for characters) -- would need library
  #Deeper linguistic knowledge?
  def correct(self, string):
    '''Correct errors based on linguistic knowledge'''
    return string, 1.0

class FeatureExtractor(object):
	def extract(self, input):
		return input
		
'''
Example usage:
image = cv.LoadImageImage('foo.jpg')
binarizer = AdaptiveBinarization()
segmenter = FloodSegmenter()
matcher = KNN(5, CharacterLibrary('/dev/urandom', ContourFeatures())
linguist = NGramCorrector('/dev/null')
text, confidence = OCR(image, binarizer, segmenter, matcher, linguist)
'''

def templateLibrary():
    library = []
    for i in range(65,91):
        im = cv.LoadImage('Archive/'+str(chr(i))+'.tif', cv.CV_LOAD_IMAGE_GRAYSCALE)
        #print str(chr(i))+'.tif'
        library.append([chr(i),im])
    for i in range(97,123):
        im = cv.LoadImage('Archive/'+'l_'+str(chr(i))+'.tif', cv.CV_LOAD_IMAGE_GRAYSCALE)
        #print str(chr(i))+'.tif'
        library.append([chr(i),im])
    return library

if __name__ == '__main__':
    im = cv.LoadImage(sys.argv[1], cv.CV_LOAD_IMAGE_GRAYSCALE)
    binarizer = SimpleBinarizer()
    segmenter = ConnectedComponentSegmenter()
    matcher = TemplateMatcher(templateLibrary(), FeatureExtractor(), 30, 400)
    linguist = Linguist()
    string, confidence = OCR(im, binarizer, segmenter, matcher, linguist).recognize()
    print "It says", string, "with confidence", confidence