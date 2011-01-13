import cv
import os
from nltk.corpus import brown
import binarize, extract, linguistics, match, typeset, segment

class OCR:
    def __init__(self, image, binarizer, segmenter, typesetter, matcher, linguist):
        self.image = image
        self.binarizer = binarizer
        self.segmenter = segmenter
        self.typesetter = typesetter
        self.matcher = matcher
        self.linguist = linguist
        
    def recognize(self, saveBinarized, saveSegmented, saveTypeset, saveMatcher):
        blackAndWhite = self.binarizer.binarize(self.image)
        if saveBinarized != None:
            cv.SaveImage(saveBinarized, blackAndWhite)
        characterPieces = self.segmenter.segment(blackAndWhite)
        if saveSegmented != None:
            os.mkdir(saveSegmented)
            for i in range(len(characterPieces)):
                cv.SaveImage(saveSegmented+"/"+str(i)+".png", characterPieces[i][1])
        pieces = self.typesetter.typeset(characterPieces)
        if saveTypeset != None:
            os.mkdir(saveTypeset)
            for i in range(len(pieces)):
                if not isinstance(pieces[i], str):
                    cv.SaveImage(saveTypeset+"/"+str(i)+".png", pieces[i])
        possibilities = self.matcher.match(pieces)
        if saveMatcher != None:
            matcherOutput = file(saveMatcher, "w")
            matcherOutput.write(str(possibilities))
            matcherOutput.close()
        output = self.linguist.correct(possibilities)
        return output

def useOptions(options):
    im = cv.LoadImage(options.target, cv.CV_LOAD_IMAGE_COLOR)
    binarizer = options.binarizer()
    segmenter = options.segmenter()
    typesetter = options.typesetter(options.spaceWidth)
    featureExtractor = options.featureExtractor()
    scaler = options.scaler(options.dimension)
    library = extract.buildLibrary(options.library, binarizer, scaler, featureExtractor)
    linguist = options.linguist()
    matcher = match.knnMatcher(library, scaler, featureExtractor, options.k)
    recognizer = OCR(im, binarizer, segmenter, typesetter, matcher, linguist)
    string = recognizer.recognize(options.saveBinarized, options.saveSegmented, options.saveTypeset, options.saveMatcher)
    return string

classMap = {
    'binarizer': {'simple': binarize.SimpleBinarizer, 'adaptive': binarize.LocalBinarizer},
    'segmenter': {'connected-component': segment.ConnectedComponentSegmenter, 'bounding-box': segment.BoundingBoxSegmenter},
    'typesetter': {'null': typeset.Typesetter, 'linear': typeset.LinearTypesetter},
    'featureExtractor': {
        'template': extract.TemplateComparisonNewFormula,
        'template-old': extract.TemplateComparisonOldFormula,
        'histogram': extract.HistogramComparison,
        'vertical-histogram': extract.VerticalHistogramComparison,
        'horizontal-histogram': extract.HorizontalHistogramComparison
     },
    'scaler': {'proportional': extract.ProportionalScaler, 'simple': extract.Scaler},
    'linguist': {
        'null': linguistics.Linguist,
        'n-gram': lambda: linguistics.NGramLinguist(''.join(brown.words()[:1000]), 3, .3)
    }
}

class Options: pass
defaultOptions = Options()
defaultOptions.spaceWidth = .3
defaultOptions.library = "/Accounts/courses/comps/text_recognition/300/all/"
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
defaultOptions.saveMatcher = None

def processOptions(options, parser=None):
    newOptions = copy.copy(options)
    for option, possibilities in classMap.items():
        value = getattr(options, option)
        if value in possibilities:
            setattr(newOptions, option, possibilities[value])
        else:
            if parser is not None:
                parser.error("Bad option for %s: %s.\nAdmissible values: %s." % (option, value, ', '.join(possibilities)))
            else:
                print "Bad option for %s: %s.\nAdmissible values: %s." % (option, value, ', '.join(possibilities))
                sys.exit(1)
    return newOptions
