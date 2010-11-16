import optparse
import sys
import cv
from bop import *
from nltk.corpus import brown

def main():
    options = getOptions()

    im = cv.LoadImage(options.target, cv.CV_LOAD_IMAGE_GRAYSCALE)
    binarizer = options.binarizer()
    segmenter = options.segmenter()
    typesetter = options.typesetter()
    featureExtractor = options.featureExtractor()
    scaler = options.scaler(options.dimension)
    library = extract.buildLibrary(options.library, scaler, featureExtractor)
    linguist = options.linguist()
    matcher = match.knnMatcher(library, scaler, featureExtractor, options.k)
    recognizer = OCR(im, binarizer, segmenter, typesetter, matcher, linguist)
    string = recognizer.recognize(options.saveBinarized, options.saveSegmented, options.saveTypeset, options.saveMatcher)
    print string

def getOptions():
    """
    Read in the command-line options and assign them to the appropriate places.
    Returns a parser object.
    """

    parser = optparse.OptionParser(usage="usage: %prog [options] image", version="%prog 0.1")

    parser.add_option("-l", "--library-dir", action="store", dest="library",
            default="/Accounts/courses/comps/text_recognition/300/all/",
            help="Library directory for the Matcher. This should be a directory containing subdirectories, within which are PNG files named for the character they represent. allfont.py in util can generate these on machines with freetype and PIL.")

    parser.add_option("-d", "--dimension", action="store", type="int", dest="dimension", default=100,
            help="Dimension of square scaled image within the template matcher")

    parser.add_option("-k", action="store", type="int", dest="k", default=1,
            help="How many templates should vote on which character is chosen. k=1 means the single most similar template determines the character.")

    parser.add_option("--binarizer", action="store", dest="binarizer", default="simple",
            help="Binarizer policy. Options: simple")

    parser.add_option("--segmenter", action="store", dest="segmenter", default="connected-component",
            help="Segmentation policy. Options: connected-component, bounding-box. Default: connected-component")

    parser.add_option("--typesetter", action="store", dest="typesetter", default="linear",
            help="Typesetting policy. Options: linear, null. Default: linear")

    parser.add_option("--feature-extractor", action="store", dest="featureExtractor", default="template",
            help="Feature extraction policy. Options: template, histogram")

    parser.add_option("--scaler", action="store", dest="scaler", default="proportional",
            help="Scaling policy. Options: simple, proportional. Default: proportional")

    parser.add_option("--linguist", action="store", dest="linguist", default="null",
            help="Linguistic correction policy. Options: null, n-gram. Default: null")

    parser.add_option("--save-binarized", action="store", dest="saveBinarized", default=None,
            help="Set this to a path to save the binarized image to a particular location")

    parser.add_option("--save-segmented", action="store", dest="saveSegmented", default=None,
            help="Set this to a directory to save the segmented images in")

    parser.add_option("--save-typeset", action="store", dest="saveTypeset", default=None,
            help="Set this to a directory to save the output of the typesetter")

    parser.add_option("--save-matcher", action="store", dest="saveMatcher", default=None,
            help="Set this to a path to save the matcher's results as")

    (options, args) = parser.parse_args()

    # Assure the right number of positional arguments
    if not args:
	parser.error("Requires an image to process.")
    if len(args) > 1:
	parser.error("Multiple images specified. Please specify only one.")

    options.target = args[0]

    classMap = {
        'binarizer': {'simple': binarize.SimpleBinarizer},
        'segmenter': {'connected-component': segment.ConnectedComponentSegmenter, 'bounding-box': segment.BoundingBoxSegmenter},
        'typesetter': {'null': typeset.Typesetter, 'linear': typeset.LinearTypesetter},
        'featureExtractor': {
            'template': extract.TemplateComparison,
            'histogram': extract.HistogramComparison,
            'vertical-histogram': extract.VerticalHistogramComparison,
            'horizontal-histogram': extract.HorizontalHistogramComparison
         },
        'scaler': {'proportional': extract.ProportionalScaler, 'simple': extract.Scaler},
        'linguist': {'null': linguistics.Linguist, 'n-gram': lambda: NGramLinguist(''.join(brown.words()[:1000]), 3, .3)}
    }
    for option, possibilities in classMap.items():
        value = getattr(options, option)
        if value in possibilities:
            setattr(options, option, possibilities[value])
        else:
            parser.error("Bad option for %s: %s.\nAdmissible values: %s." % (option, value, ', '.join(possibilities)))

    return options

if __name__ == "__main__":
    main()
