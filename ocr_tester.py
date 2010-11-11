import optparse
import sys
import cv
from bop import *

def main():
    options = getOptions()

    im = cv.LoadImage(sys.argv[1], cv.CV_LOAD_IMAGE_GRAYSCALE)
    binarizer = binarize.SimpleBinarizer()
    segmenter = segment.ConnectedComponentSegmenter()
    typesetter = typeset.LinearTypesetter()
    featureExtractor = extract.TemplateComparison()
    scaler = extract.ProportionalScaler(options.xSize)
    library = extract.buildLibrary(options.library, scaler, featureExtractor)
    matcher = match.knnMatcher(library, scaler, featureExtractor, 5)
    linguist = linguistics.Linguist()
    #linguist = NGramLinguist(''.join(brown.words()[1000:]), 3, .3)
    string = OCR(im, binarizer, segmenter, typesetter, matcher, linguist).recognize()
    print string

def getOptions():
    """
    Read in the command-line options and assign them to the appropriate places.
    Returns a parser object.
    """

    parser = optparse.OptionParser()

    parser.add_option("-l", "--library-dir", action="store", dest="library",
            default="/Accounts/courses/comps/text_recognition/300/all/",
            help="Library directory for the Matcher. This should be a directory containing subdirectories, within which are PNG files named for the character they represent. allfont.py in util can generate these on machines with freetype and PIL.")

    parser.add_option("-x", action="store", type="int", dest="xSize", default=100,
            help="x-dimension of scaled image within the matcher")

    parser.add_option("-y", action="store", type="int", dest="ySize", default=100,
            help="y-dimension of scaled image within the matcher")

    parser.add_option("-k", action="store", type="int", dest="k", default=20,
            help="k for use in the k-Nearest Neighbors matcher. k=1 is equivalent to the old template matcher.")

    (options, args) = parser.parse_args()

    # Sanity checks
    if not args:
        print "No target image specified. Nothing to do."
        sys.exit(1)
    if len(args) > 1:
        print "Multiple images specified or garbled input. Please specify only one file."
        sys.exit(1)

    # Because I really have no reason to return the single-item args by itself
    options.target = args[0]

    return options

if __name__ == "__main__":
    main()
