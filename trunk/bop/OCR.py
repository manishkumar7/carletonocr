class OCR:
    def __init__(self, image, binarizer, segmenter, typesetter, matcher, linguist):
        self.image = image
        self.binarizer = binarizer
        self.segmenter = segmenter
        self.typesetter = typesetter
        self.matcher = matcher
        self.linguist = linguist
        
    def recognize(self):
        blackAndWhite = self.binarizer.binarize(self.image)
        characterPieces = self.segmenter.segment(blackAndWhite)
        pieces = self.typesetter.typeset(characterPieces)
        output = self.matcher.match(pieces)
        output = self.linguist.correct(output)
        return output
