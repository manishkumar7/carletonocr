import cv

class Typesetter(object):
    def typeset(self, characterPieces):
        return [character[1] for character in characterPieces]
    def showTypesetting(self, pieces):
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
        spaceWidth = float(totX)/sum([l[1] for l in lines])
        for i in range(len(lines)):
            lines[i][1] += lines[i][0]*spaceWidth + lines[i][2]*spaceWidth*9
        imWidth = max([l[1] for l in lines]) + 2*spaceWidth
        imHeight = numLines * yMax + (numLines - 1) * .5 * yMax + 2*spaceWidth
        typesetVisual = cv.CreateImage((int(imWidth), int(imHeight)), 8, 3)
        for row in range(typesetVisual.height):
            for col in range(typesetVisual.width):
                typesetVisual[row, col] = (255,255,255)
        xStart = int(spaceWidth)
        y = int(spaceWidth)
        x = xStart
        for chr in pieces:
            if chr == ' ':
                cv.Rectangle(typesetVisual, (x,y), (int(x+spaceWidth*9), y+yMax), cv.RGB(10, 200, 10), -1)        
                x += int(spaceWidth * 9)
            elif chr == '\n':
                x = xStart
                y += int(yMax*1.5)
                cv.Rectangle(typesetVisual, (0, int(y-yMax*.5)), (typesetVisual.width, y), cv.RGB(10, 10, 200), -1)        
            else:
                for row in range(chr.height):
                    for col in range(chr.width):
                        if chr[row, col]  < 1:
                            typesetVisual[y+row, x+col] = (0,0,0)
                x += (int(spaceWidth) + chr.width)
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
        global SPACE_WIDTH
        averageWidth = sum(character[0][2] for character in line)/float(len(line))
        #Naive way to get the space width when displaying
        SPACE_WIDTH = averageWidth
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
        output = []
        for line in lines:
            lastChar = None
            for char in line:
                if lastChar != None:
                    if self.isaSpaceBetween(char, lastChar, line):
                        output.append(' ')
                lastChar = char
                output.append(char) #OK up to here
            output.append('\n')
        return output[:-1]
    
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
        pieces = self.spacesAndNewlines([self.combineVertical(line) for line in self.lines(characterPieces)])
        output = []
        for p in pieces:
            if p == ' ' or p == '\n':
                output.append(p)
            else:
                output.append(p[1])
        return output
