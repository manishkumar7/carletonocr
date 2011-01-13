import optparse
import ocr
from ocr import defaultOptions, classMap

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

    def addOption(name, attr, desc):
        parser.add_option(name, action="store", dest=attr, default=getattr(defaultOptions, attr),
            help = "%s. Options: %s. Default: %s" % (desc, ', '.join(classMap[attr].keys()), getattr(defaultOptions, attr)))

    addOption('--binarizer', 'binarizer', "Binarizer policy")
    addOption('--segmenter', 'segmenter', "Segmentation policy")
    addOption('--typesetter', 'typesetter', "Typesetting policy")
    addOption('--feature-extractor', 'featureExtractor', "Feature extraction policy")
    addOption('--scaler', 'scaler', "Scaling policy")
    addOption('--linguist', 'linguist', "Linguistic correction policy")

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
