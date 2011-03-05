import cv
import os
import binarize, extract, linguistics, match, typeset, segment, threshold
import copy
import platform

def eachChar(fn, lines):
    return eachWord(lambda word: map(fn, word), lines)

def eachWord(fn, lines):
    return [[fn(word) for word in line] for line in lines]

class OCRRunner(object):
    def __init__(self):
        self.options = None

    def varChanged(self, attr, other):
        return self.options is None or getattr(self.options, attr) != getattr(other, attr) \
            or True in (self.varChanged(at, other) for at in other.potential(attr))

    def withOptions(self, options):
        targetChanged = self.varChanged('target', options)
        if targetChanged:
            options.showStatus("Loading image")
            self.image = cv.LoadImage(options.target, cv.CV_LOAD_IMAGE_COLOR)
        binarizerChanged = self.varChanged('binarizer', options)
        if binarizerChanged:
            options.showStatus("Initializing binarizer")
            self.binarizer = options.get('binarizer')
        redoBinarizeImage = targetChanged or binarizerChanged
        if redoBinarizeImage:
            options.showStatus("Binarizing image")
            self.blackAndWhite = self.binarizer.binarize(self.image)
            if options.saveBinarized != None:
                cv.SaveImage(options.saveBinarized, self.blackAndWhite)
        segmenterChanged = self.varChanged('segmenter', options)
        if segmenterChanged:
            options.showStatus("Initializing segmenter")
            self.segmenter = options.get('segmenter')
        redoSegmentedImage = segmenterChanged or redoBinarizeImage
        if redoSegmentedImage:
            options.showStatus("Segmenting image")
            self.characterPieces = self.segmenter.segment(self.blackAndWhite)
            if options.saveSegmented != None:
                segVisual = segment.visualize(self.blackAndWhite, self.characterPieces)
                cv.SaveImage(options.saveSegmented, segVisual)
        thresholdChanged = self.varChanged('threshold', options)
        if thresholdChanged:
            options.showStatus("Initializing threshold")
            self.threshold = options.get('threshold')
        redoThreshold = thresholdChanged or redoSegmentedImage
        if redoThreshold:
            options.showStatus("Thresholding image")
            self.thresholdCharacterPieces = self.threshold.filter(self.characterPieces)
            if options.saveThreshold != None:
                threshVisual = segment.visualize(self.blackAndWhite, self.thresholdCharacterPieces)
                cv.SaveImage(options.saveThreshold, threshVisual)
        typesetterChanged = self.varChanged('typesetter', options)
        if typesetterChanged:
            options.showStatus("Initializing typesetter")
            self.typesetter = options.get('typesetter')
        redoTypeset = typesetterChanged or redoThreshold
        if redoTypeset:
            options.showStatus("Typesetting image")
            self.pieces = self.typesetter.typeset(self.thresholdCharacterPieces)
            if options.saveTypeset != None:
                typesetVisual = typeset.visualize(self.pieces)
                cv.SaveImage(options.saveTypeset, typesetVisual)
        scalerChanged = self.varChanged('scaler', options) or self.varChanged('dimension', options)
        if scalerChanged:
            options.showStatus("Initializing scaler")
            self.scaler = options.get('scaler', options.dimension)
        redoScale = scalerChanged or redoTypeset
        if redoScale:
            options.showStatus("Scaling image")
            bin = binarize.SimpleBinarizer()
            def scaleAndRebinarize(image):
                return bin.binarize(self.scaler.scale(image))
            self.scaled = eachChar(scaleAndRebinarize, self.pieces)
        featureExtractorChanged = self.varChanged('featureExtractor', options)
        if featureExtractorChanged:
            options.showStatus("Initializing feature extractor")
            self.featureExtractor = options.get('featureExtractor')
        redoFeatureExtractor = featureExtractorChanged or redoScale
        if redoFeatureExtractor:
            options.showStatus("Extracting features from image")
            self.features = eachChar(self.featureExtractor.extract, self.scaled)
            if options.saveFeatures != None:
                featuresVisual = extract.visualize(self.scaled, self.features)
                cv.SaveImage(options.saveFeatures, featuresVisual)
        libraryChanged = not hasattr(self, 'rawLibrary')
        if libraryChanged or self.varChanged('library', options):
            options.showStatus("Generating image files for library")
            self.rawLibrary = extract.buildLibrary(options.library)
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
            self.matcher = match.Matcher(self.library, options.k)
        redoPossibilities = matcherChanged or redoFeatureExtractor
        if redoPossibilities:
            options.showStatus("Matching characters to library")
            best = eachChar(self.matcher.bestFew, self.features)
            self.voteDict = eachChar(self.matcher.voteDict, best)
            if options.saveMatcher != None:
                matcherVisual = match.visualize(self.features, best)
                cv.SaveImage(options.saveMatcher, matcherVisual)
        linguistChanged = self.varChanged('linguist', options) or self.varChanged('selfImportance', options)
        if linguistChanged:
            options.showStatus("Initializing linguist")
            self.linguist = options.get('linguist', options.selfImportance)
        if linguistChanged or redoPossibilities:
            options.showStatus("Applying linguistic correction")
            linguistOutput = self.linguist.correct(self.voteDict)
            self.output = linguistOutput.result()
            if options.saveLinguist != None:
                if platform.system() == "Linux":
                    cv.SaveImage(options.saveLinguist, extract.render("arial", linguistOutput.visualize(), options.library))
                else:
                    cv.SaveImage(options.saveLinguist, extract.render("Arial", linguistOutput.visualize(), options.library))
        self.options = copy.copy(options)
        options.showStatus("Complete")
        return self.output


classMap = {
    'binarizer': {'global': binarize.SimpleBinarizer, 'local': binarize.LocalBinarizer},
    'segmenter': {'connected-component': segment.ConnectedComponentSegmenter, 'bounding-box': segment.BoundingBoxSegmenter},
    'typesetter': {'null': typeset.Typesetter, 'linear': typeset.LinearTypesetter},
    'featureExtractor': {
        'template': extract.TemplateComparisonNewFormula,
        'template-old': extract.TemplateComparisonOldFormula,
        'diagonal-template': extract.DiagonalTemplateComparisonNewFormula,
        'diagonal-template-old': extract.DiagonalTemplateComparisonOldFormula,
        'histogram': extract.HistogramComparison,
        'vertical-histogram': extract.VerticalHistogramComparison,
        'horizontal-histogram': extract.HorizontalHistogramComparison,
        'fourier-descriptor': extract.FourierComparison
     },
    'scaler': {'proportional': extract.ProportionalScaler, 'simple': extract.Scaler},
    'linguist': {
        'null': linguistics.NullLinguist,
        'n-gram': linguistics.NGramLinguist,
        'whole-word-n-gram': linguistics.WholeWordNGramLinguist,
        'spelling': linguistics.SpellingLinguist
    },
    'threshold': {
        'const-threshold': threshold.ConstThreshold,
        'proportion-threshold': threshold.ProportionThreshold,
        'adaptive-threshold': threshold.AdaptiveThreshold
    }
}

class Options:
    def potential(self, parent):
        opts = {}
        for opt in dependentOptions:
            if opt.parent == parent and getattr(self, parent) in opt.parentValues:
                opts[opt.attrName()] = getattr(self, opt.attrName(), opt.default)
        return opts
    def get(self, attr, *args):
        return classMap[attr][getattr(self, attr)](*args, **self.potential(attr))

defaultOptions = Options()
defaultOptions.spaceWidth = .4
defaultOptions.dimension = 50
defaultOptions.k = 10
defaultOptions.binarizer = 'local'
defaultOptions.segmenter = 'connected-component'
defaultOptions.typesetter = 'linear'
defaultOptions.featureExtractor = 'template'
defaultOptions.scaler = 'proportional'
defaultOptions.linguist = 'n-gram'
defaultOptions.threshold = 'adaptive-threshold'
defaultOptions.selfImportance = .3
defaultOptions.saveBinarized = None
defaultOptions.saveSegmented = None
defaultOptions.saveTypeset = None
defaultOptions.saveFeatures = None
defaultOptions.saveMatcher = None
defaultOptions.saveLinguist = None
defaultOptions.saveThreshold = None
defaultOptions.showStatus = lambda status: None
if platform.system() == "Darwin":
    defaultOptions.library = "/Library/Fonts/"
if platform.system() == "Linux":
    defaultOptions.library = "/usr/share/fonts/TTF/"

class DependentOption:
    def __init__(self, name, type, parent, parentValues, default, help=None):
        self.name = name
        self.type = type
        self.parent = parent
        self.parentValues = parentValues
        self.default = default
        self.help = help or self.guiName()
    def cliName(self):
        return self.name.replace(' ', '-')
    def guiName(self):
        return self.name[0].upper() + self.name[1:]
    def attrName(self):
        pieces = self.name.split(' ')
        return pieces[0]+''.join(name[0].upper()+name[1:] for name in pieces[1:])

dependentOptions = [
    DependentOption('lookback', int, 'typesetter', ['linear'], 0),
    DependentOption('space width', float, 'typesetter', ['linear'], 0.4, "What proportion of the average character width is the width of a space"),
    DependentOption('proportion', float, 'binarizer', ['adaptive'], .3),
    DependentOption('fourier points', int, 'featureExtractor', ['fourier-descriptor'], 16),
    DependentOption('tolerance', float, 'featureExtractor', ['fourier-descriptor'], .1),
    DependentOption('filter fraction', float, 'featureExtractor', ['fourier-descriptor'], .5),
    DependentOption('letters in ngram', float, 'linguist', ['n-gram', 'spelling'], 3),
    DependentOption('edit distance', int, 'linguist', ['spelling', 'whole-word-n-gram'], 5),
    DependentOption('pixel threshold', int, 'threshold', ['const-threshold'], 5),
    DependentOption('threshold proportion', float, 'threshold', ['proportion-threshold'], .025),
    DependentOption('area threshold', float, 'threshold', ['adaptive-threshold'], .025)
]

for option in dependentOptions:
    setattr(defaultOptions, option.attrName(), option.default)

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
