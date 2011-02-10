'''
Command-line interface for optical character recognition system
'''

import optparse
import ocr
import sys
import copy

def main():
    options, parser = getOptions()
    ocr.checkOptions(options, parser)
    print ocr.OCRRunner().withOptions(options)


def getOptions():
    """
    Read in the command-line options and assign them to the appropriate places.
    Returns a parser object.
    """

    def addOption(name, attr, help, type="string"):
        parser.add_option(name, action="store", dest=attr, default=getattr(ocr.defaultOptions, attr), help=help, type=type)

    def addClassOption(name, attr, desc):
        addOption(name, attr, help="%s. Options: %s. Default: %s" % (desc, ', '.join(ocr.classMap[attr].keys()), getattr(ocr.defaultOptions, attr)))

    parser = optparse.OptionParser(usage="usage: %prog [options] image", version="%prog 0.1")

    addOption('--dimension', 'dimension', type='int', help="Dimension of square scaled image within the template matcher")
    addOption('-k', 'k', type='int', help="How many templates should vote on which character is chosen. k=1 means the single most similar template determines the character.")
    addOption('--linguist-weight', 'selfImportance', type='float', help="How much weight should the linguistic correction be given?")

    addClassOption('--binarizer', 'binarizer', "Binarizer policy")
    addClassOption('--segmenter', 'segmenter', "Segmentation policy")
    addClassOption('--typesetter', 'typesetter', "Typesetting policy")
    addClassOption('--feature-extractor', 'featureExtractor', "Feature extraction policy")
    addClassOption('--scaler', 'scaler', "Scaling policy")
    addClassOption('--linguist', 'linguist', "Linguistic correction policy")

    addOption('--save-binarized', 'saveBinarized', 'Set this to a path to save the binarized image to a particular location')
    addOption('--save-segmented', 'saveSegmented', 'Set this to a path to save the segmented image to a particular location')    
    addOption('--save-typeset', 'saveTypeset', 'Set this to a path to save the typeset image to a particular location')
    addOption('--save-features', 'saveFeatures', 'Set this to a path to save the features image to a particular location')
    addOption('--save-matcher', 'saveMatcher', 'Set this to a path to save the matched image to a particular location')

    parser.add_option('--verbose', action="store_true", dest='showStatus', help='Enable verbose output')

    for option in ocr.dependentOptions:
        addOption('--'+option.cliName(), option.attrName(), type=option.type.__name__, help=option.help + ". This option is only meaningful if %s is set to %s" % (option.parent, option.parentValue))

    (options, args) = parser.parse_args()

    # Assure the right number of positional arguments
    if not args:
	parser.error("Requires an image to process.")
    if len(args) > 1:
	parser.error("Multiple images specified. Please specify only one.")

    options.target = args[0]

    if options.showStatus:
        options.showStatus = lambda status: sys.stderr.write(status + "\n")
    else:
        options.showStatus = ocr.defaultOptions.showStatus

    #pretend these three gross lines aren't there
    realOptions = copy.copy(ocr.defaultOptions)
    for attr in (at for at in dir(options) if '_' not in at):
        setattr(realOptions, attr, getattr(options, attr))

    return realOptions, parser

if __name__ == "__main__":
    main()
