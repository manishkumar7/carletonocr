import cv
import os

class Matcher:
    #Future subclasses:
    #kNN, with different distance metrics
    #Neural networks
    def __init__(self, library, featureExtractor):
        self.library = self.createLibrary(library) #library of characters; all matchers need this
        self.featureExtractor = featureExtractor

    def createLibrary(self, library):
        dirs = os.listdir(library)
        chars = []
        for dir in dirs:
                chars.extend(self.__addDirectoryContents(library+'/'+dir))
        return chars
        
        
    
    def __addDirectoryContents(self, dir):
        #try:
            files = os.listdir(dir)
            library = []
            for file in files:
                im = cv.LoadImage(dir + '/' + file, cv.CV_LOAD_IMAGE_GRAYSCALE)
                library.append([file[0],im])
            return library
        #except IOError: return []
    
    def match(self,characterPieces):
        output = []
        for piece in characterPieces:
            if isinstance(piece, str):
                output += piece
            else:
                features = self.featureExtractor.extract(piece)
                newChar = self.bestGuess(features)
                output.append(newChar)
        return output
        
    def bestGuess(self, features):
        '''Given a feature list, choose a character from the library'''
        return ''
        
    def geometricMean(self, list):
        return reduce(lambda x, y: x*y, list)**(1.0/len(list))

class TemplateMatcher(Matcher):      
    def __init__(self, library, featureExtractor, width, height):
        self.width = width #width that all images will be scaled to
        self.height = height #height that all images will be scaled to
        Matcher.__init__(self, library, featureExtractor)

    def resize(self, image):
        scaled = cv.CreateImage((self.width, self.height), 8, 1)
        cv.Resize(image, scaled, cv.CV_INTER_NN)
        return scaled
        
    def pixelDist(self, inputIm, templateIm):
        '''Determines the distance between shared pixels of 'inputIm' and 'templateIm' '''
        dist = 0
        inputLi = cv.InitLineIterator(inputIm, (0, 0), (self.width, self.height))
        templateLi = cv.InitLineIterator(templateIm, (0, 0), (self.width, self.height))
        zipped = zip(inputLi, templateLi)
        n11 = .01
        n00 = .01
        n10 = .01
        n01 = .01
        for pair in zipped:
            if round(pair[0]) == 255:
                if round(pair[1]) == 255:
                    n11 += 1
                elif round(pair[1]) == 0:
                    n10 += 1
            elif round(pair[0]) == 0:
                if round(pair[1]) == 255:
                    n01 += 1
                elif round(pair[1]) == 0:
                    n00 += 1
            else:
                print "Why is there a pixel with value", pair[0]
        distJ = float(n11)/(n11 + n10 + n01)
        distY = (float(n11) * n00 - float(n10) * n01)/(float(n11) * n00 + float(n10) * n01)
        return distJ                
        
    def findPixelMatch(self, inputIm, templateList):
        '''Finds the best match according to 'pixelDist()' and returns it if less than the cutoff'''
        best = (templateList[0][0], self.pixelDist(inputIm, templateList[0][1]))
        for template in templateList[1:]:
            pDist = self.pixelDist(inputIm, template[1])
            if pDist > best[1]:
                best = (template[0], pDist)
        return [(best[0], best[1])]
                
    def findMatch(self, inputIm, templateList):
        '''Finds the best match for 'inputIm' in 'templateList' and returns it if it satisfies the
        given cutoffs'''
        inputIm = self.resize(inputIm)
        for template in templateList:
                template[1] = self.resize(template[1])
        match = self.findPixelMatch(inputIm, templateList)
        return match
    
    def bestGuess(self, features):
        '''Given a feature list, choose a character from the library. Assumes the library is a list'''
        return self.findMatch(features, self.library)   
    
class knnTemplateMatcher(TemplateMatcher):
    def __init__(self, library, featureExtractor, width, height, k):
        self.k = k
        TemplateMatcher.__init__(self, library, featureExtractor, width, height)

    def findPixelMatch(self, inputIm, templateList):
        '''Finds the best match according to 'pixelDist()' and returns it if less than the cutoff'''
        k = min(len(templateList), self.k)
        best = []
        for i in range(k):
            best.append((self.pixelDist(inputIm, templateList[i][1]), templateList[i][0]))
        best.sort()
        for template in templateList[k:]:
            pDist = self.pixelDist(inputIm, template[1])
            if pDist > best[0][0]:
                best.pop(0)
                best.append((pDist, template[0]))
                best.sort()
        voteDict = {}
        for match in best:
                if match[1] in voteDict:
                    voteDict[match[1]] += match[0]
                else:
                    voteDict[match[1]] = match[0]
        cands = voteDict.keys()
        #print voteDict
        if len(cands) == 0:
            return []
        else:
            return voteDict.items()
