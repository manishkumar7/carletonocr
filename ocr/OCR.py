import cv
import os

class OCR:
    def __init__(self, image, binarizer, segmenter, typesetter, matcher, linguist):
        self.image = image
        self.binarizer = binarizer
        self.segmenter = segmenter
        self.typesetter = typesetter
        self.matcher = matcher
        self.linguist = linguist
        print self.image.channels, "init"
        
    def recognize(self, saveBinarized, saveSegmented, saveTypeset, saveMatcher):
    	print self.image.channels, "rec"
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

