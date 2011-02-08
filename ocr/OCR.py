import cv
import os
from nltk.corpus import brown
import binarize, extract, linguistics, match, typeset, segment
import copy

class OCRRunner:
    def __init__(self):
        self.options = None

    def varChanged(self, attr, other):
        return self.options is None or getattr(self.options, attr) != getattr(other, attr)

    def dependentVarChanged(self, attr, other):
        return True in (self.varChanged(at, other) for at in other.potential(attr))

    def toNonString(self, fn, lst):
        def do(piece):
            if isinstance(piece, str):
                return piece
            else:
                return fn(piece)
        return map(do, lst)

    def withOptions(self, options):
        targetChanged = self.varChanged('target', options)
        if targetChanged:
            options.showStatus("Loading image")
            self.image = cv.LoadImage(options.target, cv.CV_LOAD_IMAGE_COLOR)
        binarizerChanged = self.varChanged('binarizer', options) or self.dependentVarChanged('binarizer', options)
        if binarizerChanged:
            options.showStatus("Initializing binarizer")
            self.binarizer = options.get('binarizer')(**options.potential('binarizer'))
        redoBinarizeImage = targetChanged or binarizerChanged
        if redoBinarizeImage:
            options.showStatus("Binarizing image")
            self.blackAndWhite = self.binarizer.binarize(self.image)
            if options.saveBinarized != None:
                cv.SaveImage(options.saveBinarized, self.blackAndWhite)
        segmenterChanged = self.varChanged('segmenter', options)
        if segmenterChanged:
            options.showStatus("Initializing segmenter")
            self.segmenter = options.get('segmenter')()
        redoSegmentedImage = segmenterChanged or redoBinarizeImage
        if redoSegmentedImage:
            options.showStatus("Segmenting image")
            self.characterPieces = self.segmenter.segment(self.blackAndWhite)
            if options.saveSegmented != None:
                segVisual = self.segmenter.showSegments(self.blackAndWhite, self.characterPieces)
                cv.SaveImage(options.saveSegmented, segVisual)
        typesetterChanged = self.varChanged('typesetter', options) or self.varChanged('spaceWidth', options) or self.dependentVarChanged('typesetter', options)
        if typesetterChanged:
            options.showStatus("Initializing typesetter")
            self.typesetter = options.get('typesetter')(options.spaceWidth, **options.potential('typesetter'))
        redoTypeset = typesetterChanged or redoSegmentedImage
        if redoTypeset:
            options.showStatus("Typesetting image")
            self.pieces = self.typesetter.typeset(self.characterPieces)
            if options.saveTypeset != None:
                typesetVisual = self.typesetter.showTypesetting(self.pieces)
                cv.SaveImage(options.saveTypeset, typesetVisual)
        scalerChanged = self.varChanged('scaler', options) or self.varChanged('dimension', options)
        if scalerChanged:
            options.showStatus("Initializing scaler")
            self.scaler = options.get('scaler')(options.dimension)
        redoScale = scalerChanged or redoTypeset
        if redoScale:
            options.showStatus("Scaling image")
            bin = binarize.SimpleBinarizer()
            def scaleAndRebinarize(image):
                return bin.binarize(self.scaler.scale(image))
            self.scaled = self.toNonString(scaleAndRebinarize, self.pieces)
        featureExtractorChanged = self.varChanged('featureExtractor', options) or self.dependentVarChanged('featureExtractor', options)
        if featureExtractorChanged:
            options.showStatus("Initializing feature extractor")
            self.featureExtractor = options.get('featureExtractor')(**options.potential('featureExtractor'))
        redoFeatureExtractor = featureExtractorChanged or redoScale
        if redoFeatureExtractor:
            options.showStatus("Extracting features from image")
            self.features = self.toNonString(self.featureExtractor.extract, self.scaled)
            if options.saveFeatures != None:
                featuresVisual = extract.visualizeFeatures(self.scaled, self.features)
                cv.SaveImage(options.saveFeatures, featuresVisual)
        libraryChanged = not hasattr(self, 'rawLibrary')
        if libraryChanged:
            options.showStatus("Loading image files for library")
            self.rawLibrary = extract.buildLibrary()
        redoLibraryScale = libraryChanged or scalerChanged
        if redoLibraryScale:
            options.showStatus("Scaling library")
            self.scaledLibrary = [(char, self.scaler.scale(im)) for (char, im) in self.rawLibrary]
        redoLibraryBinarize = redoLibraryScale or binarizerChanged
        if redoLibraryBinarize:
            options.showStatus("Binarizing library")
            self.binScaleLibrary = [(char, self.binarizer.binarize(im)) for (char, im) in self.scaledLibrary]
        #Maybe here use the typesetter? The segmenter? to preprocess the library
        redoLibraryFeatureExtract = redoLibraryBinarize or featureExtractorChanged
        if redoLibraryFeatureExtract:
            options.showStatus("Extracting library features")
            self.library = [(char, self.featureExtractor.extract(im)) for (char, im) in self.binScaleLibrary]
        kChanged = self.varChanged('k', options)
        matcherChanged = kChanged or redoLibraryFeatureExtract
        if matcherChanged:
            options.showStatus("Initializing matcher")
            self.matcher = match.knnMatcher(self.library, options.k)
        redoPossibilities = matcherChanged or redoFeatureExtractor
        if redoPossibilities:
            options.showStatus("Matching characters to library")
            best = self.toNonString(self.matcher.bestFew, self.features)
            self.voteDict = self.toNonString(self.matcher.voteDict, best)
            if options.saveMatcher != None:
                matcherVisual = self.matcher.visualize(self.features, best)
                cv.SaveImage(options.saveMatcher, matcherVisual)
        linguistChanged = self.varChanged('linguist', options)
        if linguistChanged:
            options.showStatus("Initializing linguist")
            self.linguist = options.get('linguist')()
        if linguistChanged or redoPossibilities:
            options.showStatus("Applying linguistic correction")
            self.output = self.linguist.correct(self.voteDict)
        self.options = copy.copy(options)
        options.showStatus("Complete")
        return self.output


classMap = {
    'binarizer': {'simple': binarize.SimpleBinarizer, 'adaptive': binarize.LocalBinarizer},
    'segmenter': {'connected-component': segment.ConnectedComponentSegmenter, 'bounding-box': segment.BoundingBoxSegmenter},
    'typesetter': {'null': typeset.Typesetter, 'linear': typeset.LinearTypesetter},
    'featureExtractor': {
        'template': extract.TemplateComparisonNewFormula,
        'template-old': extract.TemplateComparisonOldFormula,
        'histogram': extract.HistogramComparison,
        'vertical-histogram': extract.VerticalHistogramComparison,
        'horizontal-histogram': extract.HorizontalHistogramComparison,
        'fourier-descriptor': extract.FourierComparison
     },
    'scaler': {'proportional': extract.ProportionalScaler, 'simple': extract.Scaler},
    'linguist': {
        'null': linguistics.Linguist,
        'n-gram': lambda: linguistics.NGramLinguist(''.join(brown.words()[:1000]), 3, .3)
    }
}

class Options:
    def potential(self, parent):
        opts = {}
        for opt in dependentOptions:
            if opt.parent == parent and opt.parentValue == getattr(self, parent):
                opts[opt.name] = getattr(self, opt.name, opt.default)
        return opts
    def get(self, attr):
        return classMap[attr][getattr(self, attr)]

defaultOptions = Options()
defaultOptions.spaceWidth = .4
defaultOptions.dimension = 100
defaultOptions.k = 1
defaultOptions.binarizer = 'simple'
defaultOptions.segmenter = 'connected-component'
defaultOptions.typesetter = 'linear'
defaultOptions.featureExtractor = 'template'
defaultOptions.scaler = 'proportional'
defaultOptions.linguist = 'null'
defaultOptions.saveBinarized = None
defaultOptions.saveSegmented = None
defaultOptions.saveTypeset = None
defaultOptions.saveFeatures = None
defaultOptions.saveMatcher = None
defaultOptions.showStatus = lambda status: None

class DependentOption:
    def __init__(self, name, type, parent, parentValue, default):
        self.name = name
        self.type = type
        self.parent = parent
        self.parentValue = parentValue
        self.default = default

dependentOptions = [
    DependentOption('lookback', int, 'typesetter', 'linear', 0),
    DependentOption('backgroundWhiteLimit', float, 'binarizer', 'adaptive', .9),
    DependentOption('proportion', float, 'binarizer', 'adaptive', .5),
    DependentOption('fourierPoints', int, 'featureExtractor', 'fourier-descriptor', 8),
    DependentOption('centroidTolerance', float, 'featureExtractor', 'fourier-descriptor', .1),
    DependentOption('areaThreshold', float, 'featureExtractor', 'fourier-descriptor', 4),
    DependentOption('filterFraction', float, 'featureExtractor', 'fourier-descriptor', .5)
]

for option in dependentOptions:
    setattr(defaultOptions, option.name, option.default)

def checkOptions(options, parser=None):
    newOptions = copy.copy(options)
    for option, possibilities in classMap.items():
        value = getattr(options, option)
        if value not in possibilities:
            if parser is not None:
                parser.error("Bad option for %s: %s.\nAdmissible values: %s." % (option, value, ', '.join(possibilities)))
            else:
                print "Bad option for %s: %s.\nAdmissible values: %s." % (option, value, ', '.join(possibilities))
                sys.exit(1)
    return newOptions
