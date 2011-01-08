import cv

class Typesetter(object):
    def __init__(self, spaceWidth):
        self.spaceWidth = spaceWidth
    def typeset(self, characterPieces):
        return [character[1] for character in characterPieces]

class LinearTypesetter(Typesetter):

    def __init__(self, spaceWidth):
        Typesetter.__init__(self, spaceWidth)

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
                output.append(char[1]) #OK up to here
            output.append('\n')
        return output[:-1]
    
    def rangesOverlap(self, box1, box2, offset):
        return box1[offset] < box2[offset]+box2[offset+2] and box2[offset] < box1[offset]+box1[offset+2]
    
    def combineImages(self, box1, image1, box2, image2):
        outputBox = (min(box1[0], box2[0]), min(box1[1], box2[1]), max(box1[0]+box1[2], box2[0]+box2[2])-min(box1[0], box2[0]), max(box1[1]+box1[3], box2[1]+box2[3])-min(box1[1], box2[1]))
        outputImage = cv.CreateImage((outputBox[2], outputBox[3]), 8, 1)
        #cv.Rectangle(outputImage,(0,0),(outputImage.height, outputImage.width),255, cv.CV_FILLED)
        for i in range(outputImage.height):
            for j in range(outputImage.width):
                outputImage[i, j] = 255
        for box, image in [(box1, image1), (box2, image2)]:
            offset = (box[0] - outputBox[0], box[1] - outputBox[1])
            for row in range(image.height):
                for col in range(image.width):
                    outputImage[row+offset[1], col+offset[0]] = image[row,col]
        return outputBox, outputImage
    
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
                    accumulatedBox, accumulatedImage = self.combineImages(box, image, accumulatedBox, accumulatedImage)
                else:
                    newLine.append((accumulatedBox, accumulatedImage))
                    accumulatedBox = box
                    accumulatedImage = image
        if accumulatedBox != None:
            newLine.append((accumulatedBox, accumulatedImage))
        return newLine
    
    def typeset(self, characterPieces):
        return self.spacesAndNewlines([self.combineVertical(line) for line in self.lines(characterPieces)])

