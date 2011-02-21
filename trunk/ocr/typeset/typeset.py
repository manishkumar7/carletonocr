import cv
import itertools

def counted(iterable):
    return itertools.izip(itertools.count(), iterable)

class Typesetter(object):
    def typeset(self, characterPieces):
        return [[[character[1] for character in characterPieces]]]

def splitLines(lines, fn):
    def splitLine(line):
        lastChar = None
        currentWord = []
        newLine = [currentWord]
        for char in line:
            if lastChar and fn(char, lastChar, line):
                currentWord = []
                newLine.append(currentWord)
            currentWord.append(char[1])
            lastChar = char
        return newLine
    return map(splitLine, lines)

def visualize(lines):
    widths = [sum(char.width for word in line for char in word) for line in lines]
    lineHeight = max(char.height for line in lines for word in line for char in word)
    lineSpacing = lineHeight/2
    newLine = lineHeight + lineSpacing
    numChars = sum(len(word) for line in lines for word in line)
    spaceWidth = int((.4*sum(widths))/numChars)
    imWidth = max(width + spaceWidth*(len(line)+1) for width, line in zip(widths, lines))
    imHeight = len(lines) * newLine + 2*spaceWidth - lineSpacing
    typesetVisual = cv.CreateImage((imWidth, imHeight), 8, 3)
    cv.Rectangle(typesetVisual, (0, 0), (imWidth, imHeight), (255, 255, 255), cv.CV_FILLED)
    y = spaceWidth
    for lineNum, line in counted(lines):
        if lineNum != 0:
            y += newLine
            cv.Rectangle(typesetVisual, (0, y-lineSpacing), (imWidth, y-1), cv.RGB(10, 10, 200), -1)        
        x = spaceWidth
        for wordNum, word in counted(line):
            if wordNum != 0:
                cv.Rectangle(typesetVisual, (x,y), (x+spaceWidth, y+lineHeight), cv.RGB(10, 200, 10), -1)        
                x += spaceWidth
            for char in word:
                heightOffset = lineHeight - char.height
                for row in range(char.height):
                    for col in range(char.width):
                        if char[row, col] < 1:
                            typesetVisual[y+row+heightOffset, x+col] = (0,0,0)
                x += char.width
    return typesetVisual

def combineImages(box1, image1, box2, image2):
    outputBox = (min(box1[0], box2[0]), min(box1[1], box2[1]), max(box1[0]+box1[2], box2[0]+box2[2])-min(box1[0], box2[0]), max(box1[1]+box1[3], box2[1]+box2[3])-min(box1[1], box2[1]))
    outputImage = cv.CreateImage((outputBox[2], outputBox[3]), 8, 1)
    cv.Rectangle(outputImage, (0, 0), (outputImage.width, outputImage.height), 255, cv.CV_FILLED)
    for box, image in [(box1, image1), (box2, image2)]:
        offset = (box[0] - outputBox[0], box[1] - outputBox[1])
        for row in range(image.height):
            for col in range(image.width):
                outputImage[row+offset[1], col+offset[0]] = image[row,col]
    return outputBox, outputImage

def characterCombine(characterPieces):
    if len(characterPieces) > 2:
        raise Exception("Too many character pieces")
    if len(characterPieces) == 1:
        return characterPieces[0][1]
    return combineImages(characterPieces[0][0], characterPieces[0][1], characterPieces[1][0], characterPieces[1][1])[1]

class LinearTypesetter(Typesetter):

    def __init__(self, spaceWidth, lookback):
        self.spaceWidth = spaceWidth
        self.lookback = lookback

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
        for (box, image) in currentLine[-self.lookback:]:
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
        #Naive way to get the space width when displaying
        return char[0][0]-(lastChar[0][0]+lastChar[0][2]) > averageWidth*self.spaceWidth

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
        return splitLines(lines, self.isaSpaceBetween)

    def rangesOverlap(self, box1, box2, offset):
        return box1[offset] < box2[offset]+box2[offset+2] and box2[offset] < box1[offset]+box1[offset+2]

    def combineVertical(self, line):
        accumulatedBox = None
        accumulatedImage = None
        newLine = []
        for box, image in line:
            if accumulatedBox == None:
                accumulatedBox = box
                accumulatedImage = image
            else:
                if self.rangesOverlap(accumulatedBox, box, 0) and not self.rangesOverlap(accumulatedBox, box, 1):
                    accumulatedBox, accumulatedImage = combineImages(box, image, accumulatedBox, accumulatedImage)
                else:
                    newLine.append((accumulatedBox, accumulatedImage))
                    accumulatedBox = box
                    accumulatedImage = image
        if accumulatedBox != None:
            newLine.append((accumulatedBox, accumulatedImage))
        return newLine

    def typeset(self, characterPieces):
        return self.spacesAndNewlines([self.combineVertical(line) for line in self.lines(characterPieces)])
