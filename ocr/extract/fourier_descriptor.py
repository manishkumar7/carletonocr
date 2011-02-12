import numpy
import cv
from feature_extractor import *
from scaler import ProportionalScaler
import math
import operator

FOURIER_POINTS = 16 
TOLERANCE = .1
AREA_THRESHOLD = 4
CENTROID_THRESHOLD = 0
FILTER_LENGTH = FOURIER_POINTS/2

class FourierDescriptor(Features):
    class Curve(object):
        def __init__(self, ordinal, offset, points, fourierPoints, filterLength):
            self.ordinal = ordinal
            self.offset = offset
            #print "I am a curve and my offset is", offset, "and my ordinal is", ordinal
            self.points = points
            self.fourierPoints = fourierPoints
            self.filterLength = filterLength
            self.fourierX = self.fourier(points, 0)
            self.fourierY = self.fourier(points, 1)

        def fourier(self, points, coordinate):
            # T-shift isn't implemented because I don't understand the actual math
            # However, I'm additionally not clear if it needs to be done per-comparison
            # or can be done once.
            points = [point[coordinate] for point in points]
            def interpolate(i):
                index = len(points)*(float(i)/self.fourierPoints)
                before = int(math.floor(index))
                after = int(math.ceil(index))
                if after >= len(points):
                    return points[before]
                else:
                    return int(points[before]*(index - before) + points[after]*(after - index))
            interpolated = [interpolate(i) for i in range(self.fourierPoints)]
            return numpy.fft.fft(interpolated)[:self.filterLength]

    def __init__(self, difference, curves, dimension, tolerance):
        '''
        Centroids should be a list of coordinate pairs
        Fouriers should be a list of pairs of Fourier transforms of functions
        each fourier transform is a list of floats of length FOURIER_POINTS/4
        '''
        self.difference = difference
        self.curves = curves
        self.dimension = dimension
        self.tolerance = tolerance
        
    def comparable(self, other):
        for myKind, yourKind in zip(self.curves, other.curves):
            if [curve.ordinal for curve in myKind] != [curve.ordinal for curve in yourKind]:
                return False
        return True

    def similarCoordinates(self, c1, c2):
        difference = [abs(c1[i]-c2[i]) for i in range(2)]
        for i in range(2):
            if difference[i] > self.tolerance * self.dimension[i]:
                return sum(difference)
        return 0

    def similarity(self, other):
        if self.comparable(other):
            difference = self.similarCoordinates(self.difference, other.difference)
            if difference > 0: return difference
            sum = 0
            count = 0
            for myCurves, yourCurves in zip(self.curves, other.curves):
                for myCurve, yourCurve in zip(myCurves, yourCurves):
                    difference = self.similarCoordinates(myCurve.offset, yourCurve.offset)
                    sum += difference
                    if difference > 0: count += 1
            if count > CENTROID_THRESHOLD:
                return sum + 100
            return 1.0/(self.fourierDistance(other)+1) + 500
        else:
            return 0

    def fourierDistance(self, other):
        """Given another descriptor, compare the Fourier coefficients of that curve against
        this curve, and return their symmetric difference."""
        diffX = 0
        diffY = 0
        for myCurves, yourCurves in zip(self.curves, other.curves):
            for myCurve, yourCurve in zip(myCurves, yourCurves):
                diffX += sum([abs(matched[0] - matched[1]) for matched in 
                    zip(myCurve.fourierX[1:], yourCurve.fourierX[1:])]) # Don't include the offset coeff
                diffY += sum([abs(matched[0] - matched[1]) for matched in 
                    zip(myCurve.fourierY[1:], yourCurve.fourierY[1:])]) 
        return diffX + diffY # Don't think the paper specifies if this should be an average
                             # or anything else.

    def visualize(self):
        vis = cv.CreateImage((50, 50), 8, 3)
        return vis
        # I don't know if this code should work at all, so we're not running it for now
        x = 0
        y = 0
        allCurves = []
        print self.curves
        for pn in self.curves:
            for curve in pn:
                invX = numpy.fft.ifft(curve.fourierX) - curve.offset[0]
                invY = numpy.fft.ifft(curve.fourierY) - curve.offset[1]
                #new = numpy.zeros((int(invX.max())+1, int(invY.max())+1), int)
                if invX.max()+1>x: x = invX.max()+1
                if invY.max()+1>y: y = invY.max()+1
                allCurves.append(numpy.column_stack((invX, invY)))
        positive, negative = self.curves
        new = numpy.zeros((int(x)+10, int(y)+10), int)
        for curve in allCurves:
            for pt in curve:
                for i in xrange(4):
                    for j in xrange(4):
                        new[int(pt[0])-i][int(pt[1])-j] = 255 
                        #try: new[int(pt[0])-i][int(pt[1])-j] = 255 
                        #except IndexError: pass
        new = new^255
        # It should not take this many steps to do this OpenCV >:(
        vis = cv.fromarray(new)
        scaled = cv.fromarray(numpy.zeros(self.dimension, int)) 
        depthed = cv.CreateImage(self.dimension, 8, 1)
        rgb = whiteImage(self.dimension)
        cv.Resize(vis, scaled, interpolation=cv.CV_INTER_NN)
        cv.ConvertScale(scaled, depthed)
        cv.MixChannels([depthed], [rgb], [(0,0),(0,1),(0,2)] )
        for positiveCurve in positive:
            ordinal = tuple(map(int, positiveCurve.offset))
            cv.Circle(rgb, ordinal, 5, (0, 0, 255), -1)
        for negativeCurve in negative:
            ordinal = tuple(map(int, negativeCurve.offset))
            cv.Circle(rgb, ordinal, 5, (0, 255, 0), -1)
        return rgb 

def partition(list, predicate):
    yes, no = [], []
    for item in list:
        if predicate(item):
            yes.append(item)
        else:
            no.append(item)
    return yes, no

def averagePoint(data):
    sumX = 0.0
    sumY = 0.0
    for point in data:
        sumX += point[0]
        sumY += point[1]
    return (sumX/len(data), sumY/len(data))

def addTuples(A, B):
    return tuple(map(operator.add, A, B))
    
def negTuple(tup):
    return tuple(-t for t in tup)

def minusTuples(tup1, tup2):
    return addTuples(tup1, negTuple(tup2))

#See http://en.wikipedia.org/wiki/Polygonal_area#Area_and_centroid
#Assumes non-self-intersecting contours, which I think is safe
def contourArea(points):
    area = 0
    for i in range(len(points)-1):
        area += points[i][0]*points[i+1][1]-points[i+1][0]*points[i][1]
    return .5 * area
                        

class FourierComparison(FeatureExtractor):
    def __init__(self, fourierPoints, tolerance, areaThreshold, filterFraction):
        self.fourierPoints = fourierPoints
        self.tolerance = tolerance
        self.areaThreshold = areaThreshold
        self.filterLength = int(filterFraction * fourierPoints)

    class Curve(object):
        def __init__(self, points):
            self.points = points
            self.centroid = averagePoint(points)
            self.area = contourArea(points)
            #print "I am the other type of curve and my centroid is", self.centroid, "and my area is ", self.area

    def averageCentroid(self, data):
        if data:
            return averagePoint([curve.centroid for curve in data])
        return (0,0)

    def sortOrdinals(self, data, imgDim):
        output = [([-1, -1], curve) for curve in data]
        sortedX = self.sortOrdinalCoords(data, 0, imgDim, output)
        sortedY = self.sortOrdinalCoords(data, 1, imgDim, output)
        return sorted(output, key=lambda pair: pair[0])

    def sortOrdinalCoords(self, data, coord, imgDim, output):
        sortedOrds = sorted(zip(range(len(data)), data), key=lambda pair: pair[1].centroid[coord])
        ordinalOffset = 0
        for ordinal in range(len(sortedOrds)):
            output[sortedOrds[ordinal][0]][0][coord] = ordinal-ordinalOffset
            if ordinal+1 < len(sortedOrds) and float(sortedOrds[ordinal+1][1].centroid[coord] - sortedOrds[ordinal][1].centroid[coord]) / imgDim[coord] < self.tolerance:
                ordinalOffset += 1
        return output

    def contours(self, image):
        unvisited = set((row, col) for col in range(image.width+1) for row in range(image.height+1))
        contours = []
        while len(unvisited) > 0:
            vertex = unvisited.pop()
            direction = self.direction(image, vertex)
            if direction != (0, 0):
                contour = [vertex]
                #print 'starting a new contour'
                while len(unvisited) > 0 and addTuples(vertex, direction) in unvisited:
                    vertex = addTuples(vertex, direction)
                    #print 'adding', vertex
                    contour.append(vertex)
                    unvisited.remove(vertex)
                    direction = self.direction(image, vertex)
                    #print "The direction is", direction
                #print contour
                assert addTuples(contour[-1],direction) == contour[0]
                contours.append(contour)
        return contours

    def direction(self, image, vertex):
        #print 'finding the direction from', vertex
        offsets = [(0, 0), (-1, 0), (-1, -1), (0, -1)]
        direction = [(0, 1), (-1, 0), (0, -1), (1, 0)]
        def lookup(i):
            coordinate = addTuples(vertex, offsets[i % len(offsets)])
            if coordinate[0] < 0 or coordinate[1] < 0 or coordinate[0] >= image.height or coordinate[1] >= image.width:
                return 255
            return image[coordinate]
        for i in range(4):
            v = addTuples(vertex, offsets[i])
            #print 'at pixel', v, 'the pixel is', lookup(i)
        candidates = [d for i, d in zip(range(len(offsets)), direction) if lookup(i) == 255 and lookup(i+1) == 0]
        if len(candidates) == 0:
            return (0, 0)
        elif len(candidates) == 1:
            return candidates[0]
        else:
            print 'dim', image.width, image.height
            print 'vertex', vertex
            print 'values', [(lookup(i), offsets[i]) for i in range(4)]
            raise Exception("The image has not been correctly prepared")

    def broaden(self, image):
        #print 'broadening'
        dst = cv.CreateImage((image.width, image.height), 8, 1)
        cv.Copy(image, dst)
        keepGoing = True
        while keepGoing:
           #print 'looping'
           keepGoing = False
           for row in range(image.height-1):
               for col in range(image.width-1):
                   for i in range(2):
                       blackWhite = [0, 255]
                       if dst[row, col] == blackWhite[i] == dst[row+1, col+1] and dst[row+1, col] == blackWhite[(i+1)%2] == dst[row, col+1]:
                           #print 'blackening'
                           dst[row, col] = 0
                           dst[row+1, col] = 0
                           keepGoing = True
        #print 'broadened'
        return dst

    def extract(self, image):
        image = self.broaden(image)
        contours = self.contours(image)
        data = [FourierComparison.Curve(curve) for curve in contours]
        data = [curve for curve in data if curve.area > AREA_THRESHOLD]
        curveKinds = partition(data, lambda curve: curve.area > 0)
        displacement = minusTuples(self.averageCentroid(curveKinds[0]), self.averageCentroid(curveKinds[1]))
        curveAggregate = []
        for kind in curveKinds:
            ordinals = self.sortOrdinals(kind, (image.width, image.height))
            curves = [FourierDescriptor.Curve(ordinal, minusTuples(curve.centroid, displacement), curve.points, self.fourierPoints, self.filterLength) for (ordinal, curve) in ordinals]
            curveAggregate.append(curves)
        return FourierDescriptor(displacement, curveAggregate, (image.width, image.height), self.tolerance)

