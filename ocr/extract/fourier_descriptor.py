import numpy
import cv
from feature_extractor import *
from scaler import ProportionalScaler
import math
import operator
import subprocess
import tempfile
import Image

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
        vis = cv.CreateImage((10,10), 8, 3)
        cv.Rectangle(vis, (0,0), (self.dimension[0],self.dimension[1]), (255,255,255), cv.CV_FILLED)
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

def minusTuples(tup1, tup2):
    return tuple(map(operator.sub, tup1, tup2))

class FourierComparison(FeatureExtractor):
    def __init__(self, fourierPoints, tolerance, filterFraction):
        self.fourierPoints = fourierPoints
        self.tolerance = tolerance
        self.filterLength = int(filterFraction * fourierPoints)

    class Curve(object):
        def __init__(self, contour):
            self.points = contour[0]
            self.centroid = averagePoint(contour[0])
            self.area = contour[1]

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

    def extract(self, image):
        image = pad(image)
        contours = allContours(cv.FindContours(image, cv.CreateMemStorage(), mode=cv.CV_RETR_TREE, method=cv.CV_CHAIN_APPROX_SIMPLE))
        data = [FourierComparison.Curve(curve) for curve in contours[1:]]
        curveKinds = partition(data, lambda curve: curve.area > 0)
        displacement = minusTuples(self.averageCentroid(curveKinds[0]), self.averageCentroid(curveKinds[1]))
        curveAggregate = []
        for kind in curveKinds:
            ordinals = self.sortOrdinals(kind, (image.width, image.height))
            curves = [FourierDescriptor.Curve(ordinal, minusTuples(curve.centroid, displacement), curve.points, self.fourierPoints, self.filterLength) for (ordinal, curve) in ordinals]
            curveAggregate.append(curves)
        return FourierDescriptor(displacement, curveAggregate, (image.width, image.height), self.tolerance)

def allContours(contour, sign = -1):
    """Takes the output of cv.FindContours and turns it into a Python
    list with the same order as opencv's TreeNodeIterator in the C API."""
    contours = []
    if contour:
        contours.append((contour, sign*int(cv.ContourArea(contour))))
        contours.extend(allContours(contour.v_next(), sign*-1))
        contours.extend(allContours(contour.h_next(), sign))
    return contours

def pad(image):
    """Return a copy of an image with a 2px border"""
    new = cv.CreateImage((image.width+4, image.height+4), image.depth, image.channels)
    cv.CopyMakeBorder(image, new, (2,2), cv.BORDER_CONSTANT, cv.CV_RGB(255,255,255))
    return new

