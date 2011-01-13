import optparse
import ocr
from ocr import defaultOptions

def main():
    options, parser = getOptions()
    options = ocr.processOptions(options, parser)
    print ocr.useOptions(options)


def getOptions():
    """
    Read in the command-line options and assign them to the appropriate places.
    Returns a parser object.
    """

    parser = optparse.OptionParser(usage="usage: %prog [options] image", version="%prog 0.1")

    parser.add_option("--space-width", action="store", type="float", dest="spaceWidth", default=defaultOptions.spaceWidth,
            help="What proportion of the average character width is the width of a space")

    parser.add_option("-l", "--library-dir", action="store", dest="library",
            default=defaultOptions.library,
            help="Library directory for the Matcher. This should be a directory containing subdirectories, within which are PNG files named for the character they represent. allfont.py in util can generate these on machines with freetype and PIL.")

    parser.add_option("-d", "--dimension", action="store", type="int", dest="dimension", default=defaultOptions.dimension,
            help="Dimension of square scaled image within the template matcher")

    parser.add_option("-k", action="store", type="int", dest="k", default=defaultOptions.k,
            help="How many templates should vote on which character is chosen. k=1 means the single most similar template determines the character.")

    parser.add_option("--binarizer", action="store", dest="binarizer", default=defaultOptions.binarizer,
            help="Binarizer policy. Options: simple, adaptive")

    parser.add_option("--segmenter", action="store", dest="segmenter", default=defaultOptions.segmenter,
            help="Segmentation policy. Options: connected-component, bounding-box. Default: connected-component")

    parser.add_option("--typesetter", action="store", dest="typesetter", default=defaultOptions.typesetter,
            help="Typesetting policy. Options: linear, null. Default: linear")

    parser.add_option("--feature-extractor", action="store", dest="featureExtractor", default=defaultOptions.featureExtractor,
            help="Feature extraction policy. Options: template, template-old, histogram, histogram-vertical, histogram-horizontal")

    parser.add_option("--scaler", action="store", dest="scaler", default=defaultOptions.scaler,
            help="Scaling policy. Options: simple, proportional. Default: proportional")

    parser.add_option("--linguist", action="store", dest="linguist", default=defaultOptions.linguist,
            help="Linguistic correction policy. Options: null, n-gram. Default: null")

    parser.add_option("--save-binarized", action="store", dest="saveBinarized", default=defaultOptions.saveBinarized,
            help="Set this to a path to save the binarized image to a particular location")

    parser.add_option("--save-segmented", action="store", dest="saveSegmented", default=defaultOptions.saveSegmented,
            help="Set this to a directory to save the segmented images in")

    parser.add_option("--save-typeset", action="store", dest="saveTypeset", default=defaultOptions.saveTypeset,
            help="Set this to a directory to save the output of the typesetter")

    parser.add_option("--save-matcher", action="store", dest="saveMatcher", default=defaultOptions.saveMatcher,
            help="Set this to a path to save the matcher's results as")

    (options, args) = parser.parse_args()

    # Assure the right number of positional arguments
    if not args:
	parser.error("Requires an image to process.")
    if len(args) > 1:
	parser.error("Multiple images specified. Please specify only one.")

    options.target = args[0]
    return options, parser

if __name__ == "__main__":
    main()
