import cv
import math

class Segmenter:
    #Future subclasses:
    #Flood fill
    def segment(self, blackAndWhite):
        '''Given a black and white image, return a list of image
        pieces which each stand for an individual character'''
        return []

def visualize(blackAndWhite, characterPieces):
    segVisual = cv.CreateImage((blackAndWhite.width, blackAndWhite.height), 8, 3)
    for row in range(segVisual.height):
        for col in range(segVisual.width):
            segVisual[row, col] = (255,255,255)
    for piece in characterPieces:
        box = piece[0]
        image = piece[1]
        for row in range(box[3]):
            for col in range(box[2]):
                if image[row, col]  < 1:
                    segVisual[box[1]+row, box[0]+col] = (0,0,0)
        cv.Rectangle(segVisual, (box[0],box[1]), (box[0]+box[2],box[1]+box[3]), cv.RGB(0, 200, 0), 1, 8)        
    return segVisual

def box(points):
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
    return (minCol-1, minRow-1, maxCol-minCol+2, maxRow-minRow+2)

class ConnectedComponentSegmenter(Segmenter):
    def segment(self, blackAndWhite):
        output = []
        pixels = set((row,col) for row in range(blackAndWhite.height) for col in range(blackAndWhite.width))
        while pixels:
            pixel = pixels.pop()
            if blackAndWhite[pixel] == 0:
                component = self.findConnectedComponents(blackAndWhite, pixel, pixels)
                output.append(component)
        return output

    def findConnectedComponents(self, image, pixel, pixels):
        points = set([pixel])
        pointsToSearch = [pixel]
        while pointsToSearch:
            workListPoint = pointsToSearch.pop()
            wLRow, wLCol = workListPoint
            potentialAdjacentPoints = set([(wLRow, wLCol-1), (wLRow, wLCol+1), (wLRow-1, wLCol), (wLRow+1, wLCol)]) - points
            adjacentPoints = set()
            for p in potentialAdjacentPoints:
                tmpRow, tmpCol = p
                if tmpRow >= 0 and tmpCol >= 0 and tmpCol < image.width and tmpRow < image.height and image[p] == 0.0:
                    adjacentPoints.add(p)
            points |= adjacentPoints
            pointsToSearch.extend(list(adjacentPoints))
        #if len(points) < self.areaThreshold:
        #    return None
        for point in points:
            if point in pixels:
                pixels.remove(point)
        boundingBox = box(points)
        newImage = self.createImage(boundingBox, points)
        return (boundingBox, newImage, len(points))

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
            images.append((letter, newImage, letter[2]*letter[3]))
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
        return box(points)
