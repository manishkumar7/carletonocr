'''
Command-line interface for optical character recognition system
'''

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

    def addOption(name, attr, help, type="string"):
        parser.add_option(name, action="store", dest=attr, default=getattr(defaultOptions, attr), help=help, type=type)

    def addClassOption(name, attr, desc):
        addOption(name, attr, help="%s. Options: %s. Default: %s" % (desc, ', '.join(classMap[attr].keys()), getattr(defaultOptions, attr)))

    parser = optparse.OptionParser(usage="usage: %prog [options] image", version="%prog 0.1")

    addOption('--space-width', 'spaceWidth', type='float', help="What proportion of the average character width is the width of a space")
    addOption('--library-dir', 'library', help="Library directory for the Matcher. This should be a directory containing subdirectories, within which are PNG files named for the character they represent. allfont.py in util can generate these on machines with freetype and PIL.")
    addOption('--dimension', 'dimension', type='int', help="Dimension of square scaled image within the template matcher")
    addOption('-k', 'k', type='int', help="How many templates should vote on which character is chosen. k=1 means the single most similar template determines the character.")

    addClassOption('--binarizer', 'binarizer', "Binarizer policy")
    addClassOption('--segmenter', 'segmenter', "Segmentation policy")
    addClassOption('--typesetter', 'typesetter', "Typesetting policy")
    addClassOption('--feature-extractor', 'featureExtractor', "Feature extraction policy")
    addClassOption('--scaler', 'scaler', "Scaling policy")
    addClassOption('--linguist', 'linguist', "Linguistic correction policy")

    addOption('--save-binarized', 'saveBinarized', 'Set this to a path to save the binarized image to a particular location')
    addOption('--save-segmented', 'saveSegmented', 'Set this to a path to save the segmented image to a particular location')
    addOption('--save-typeset', 'saveTypeset', 'Set this to a path to save the segmented image to a particular location')
    addOption('--save-matcher', 'saveMatcher', 'Set this to a path to save the matched image to a particular location')

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
