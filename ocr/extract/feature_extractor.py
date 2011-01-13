import cv

class FeatureExtractor(object):
    def extract(self, input):
        '''Returns a features object, with a similarity method'''
        return Features()
       
class Features(object):
    def similarity(self, other):
        return 0

class TemplateImage(Features):
    def __init__(self, image):
        self.image = image
    def similarity(self, other):
        '''Determines the distance between shared pixels of self.image and other.image '''
        inputIm = self.image
        templateIm = other.image
        dist = 0
        assert inputIm.width == templateIm.width and inputIm.height == templateIm.height
        size = (inputIm.width, inputIm.height)
        inputLi = cv.InitLineIterator(inputIm, (0, 0), size)
        templateLi = cv.InitLineIterator(templateIm, (0, 0), size)
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
            #else:
                #raise Exception("Why is there a pixel with value " + str(pair[0]))
        return self.formula(n00, n01, n10, n11)

class TemplateImageOldFormula(TemplateImage):
    def formula(self, n00, n01, n10, n11):
        return (n00 + n11)/float(n11 + n00 + n10 + n01)

class TemplateImageNewFormula(TemplateImage):
    def formula(self, n00, n01, n10, n11):
        return float(n11)/(n11 + n10 + n01)

class TemplateComparisonOldFormula(FeatureExtractor):
    def extract(self, image):
        return TemplateImageOldFormula(image)

class TemplateComparisonNewFormula(FeatureExtractor):
    def extract(self, image):
        return TemplateImageNewFormula(image)

class ImageTranspose(object):
    def __init__(self, image):
        self.image = image
        self.width = image.width
        self.height = image.height
    def __getitem__(self, index):
        return self.image[index[1], index[0]]

def VerticalHistogram(image):
    return HorizontalHistogram(ImageTranspose(image))

class HorizontalHistogram(Features):
    def __init__(self, image):
        self.histogram = [sum(((image[row, col] == 0 and 1) or 0) for col in range(image.width)) for row in range(image.height)]
    def similarity(self, other):
        return 1.0/(sum(abs(mine-yours) for (mine, yours) in zip(self.histogram, other.histogram))+1)

class VerticalAndHorizontalHistogram(Features):
    def __init__(self, image):
        self.verticalHistogram = VerticalHistogram(image)
        self.horizontalHistogram = HorizontalHistogram(image)
    def similarity(self, other):
        return self.verticalHistogram.similarity(other.verticalHistogram) \
            + self.horizontalHistogram.similarity(other.horizontalHistogram)

class HistogramComparison(FeatureExtractor):
    def extract(self, image):
        return VerticalAndHorizontalHistogram(image)

class VerticalHistogramComparison(FeatureExtractor):
    def extract(self, image):
        return VerticalHistogram(image)

class HorizontalHistogramComparison(FeatureExtractor):
    def extract(self, image):
        return HorizontalHistogram(image)

FOURIER_POINTS = 256
TOLERANCE = .1
AREA_THRESHOLD = 4
CENTROID_THRESHOLD = 0

class FourierDescriptor(Features):
    class Curve(object):
        def fourier(self, points, coordinate):
            return []
        def __init__(self, ordinal, offset, points):
            self.ordinal = ordinal
            self.offset = offset
            self.fourierX = self.fourier(points, 0)
            self.fourierY = self.fourier(points, 1)

    def __init__(self, difference, curves, dimension):
        '''
        Centroids should be a list of coordinate pairs
        Fouriers should be a list of pairs of Fourier transforms of functions
        each fourier transform is a list of floats of length FOURIER_POINTS/4
        '''
        self.difference = difference
        self.curves = curves
        self.dimension = dimension
        
    def comparable(self, other):
        return [curve.ordinal for curve in self.curves] == [curve.ordinal for curve in other.curves]

    def similarCoordinates(self, c1, c2):
        difference = [abs(c1[i]-c2[i]) for i in range(2)]
        for i in range(2):
            if difference[i] > TOLERANCE * self.dimension[i]:
                return sum(difference)
        return 0

    def similarity(self, other):
        if self.comparable(other):
            difference = self.similarCoordinates(self.difference, other.difference)
            if difference > 0: return difference
            sum = 0
            count = 0
            for myCurve, yourCurve in zip(self.curves, other.curves):
                difference = self.similarCoordinates(myCurve.offset, yourCurve.offset)
                sum += difference
                if difference > 0: count += 1
            if count > CENTROID_THRESHOLD:
                return sum + 10000
            return 1000000 #Actually compare fourier descriptors here
        else:
            return 0

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
    
def addTuples(tup1, tup2):
	return tuple(t1+t2 for (t1, t2) in zip(tup1, tup2))
	

class FourierComparison(FeatureExtractor):
    class Curve(object):
        def __init__(self, points):
            self.points = points
            self.centroid = averagePoint(points)
            self.area = cv.ContourArea(points)
 
    def averageCentroid(self, data):
        return averagePoint([curve.centroid for curve in data])
    
    def sortOrdinals(self, data, imgDim):
        output = [([-1, -1], curve) for curve in data]
        sortedX = self.sortOrdinalCoords(data, 0, imgDim, output)
        sortedY = self.sortOrdinalCoords(data, 1, imgDim, output)
        return sorted(output, key=lambda pair: pair[0])
        
    def sortOrdinalCoords(self, data, coord, imgDim, output):
        sortedOrds = sorted(zip(range(len(data)), data), key=lambda pair: pair[1].centroid[coord])
        ordinalOffset = 0
        for ordinal in range(len(sortedOrds)):
            output[sortedOrds[ordinal][0]][coord] = ordinal-ordinalOffset
            if ordinal+1 < len(sortedOrds) and (sortedOrds[ordinal].centroid[coord] - sortedOrds[ordinal+1].centroid[coord]) / imgDim[coord] < TOLERANCE:
                ordinalOffset += 1
        return output

    def contours(self, image):
        unvisited = set((row, col) for col in range(image.width) for row in range(image.height))
        contours = []
        while len(unvisited) > 0:
            pixel = unvisited.pop()
            direction = self.pixelDirection(image, pixel)
            if direction != (0, 0):
            	contour = []
            	while len(unvisited) > 0 and addTuples(pixel, direction) in unvisited:
            		contour.append(pixel)
            		pixel = unvisited.pop(addTuples(pixel, direction))
            		direction = self.pixelDirection(image, pixel)
            	contours.append(contour)
            	assert addTuples(contour[-1],direction) == contour[0]
        return contours
    
    def extract(self, image):
        contours = self.contours(image)
        for contour in contours:
        	print contour
        data = [FourierComparison.Curve(curve) for curve in contours]
        data = [curve for curve in data if curve.area > AREA_THRESHOLD]
        positive, negative = partition(data, lambda curve: curve.area > 0)
        displacement = self.averageCentroid(positive) - self.averageCentroid(negative)
        ordinals = self.sortOrdinals(data, (image.width, image.height))
        curves = [FourierDescriptor.Curve(ordinal, curve.centroid - displacement, curve.points) for (ordinal, curve) in ordinals]
        return FourierDescriptor(displacement, curves, (image.width, image.height))
