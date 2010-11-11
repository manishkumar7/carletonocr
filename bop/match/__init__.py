import cv

class Matcher:
    #Future subclasses:
    #kNN, with different distance metrics
    #Neural networks
    def __init__(self, library, scaler, featureExtractor):
        self.library = library
        self.featureExtractor = featureExtractor
        self.scaler = scaler
    
    def match(self,characterPieces):
        output = []
        for piece in characterPieces:
            if isinstance(piece, str):
                output += piece
            else:
                scaled = self.scaler.scale(piece)
                features = self.featureExtractor.extract(scaled)
                newChar = self.bestGuess(features)
                output.append(newChar)
        return output
        
    def bestGuess(self, features):
        '''Finds the best match for 'inputIm' in the library and returns it if it satisfies the
        given cutoffs'''
        best = (self.library[0][0], features.similarity(self.library[0][1]))
        for template in self.library[1:]:
            pDist = features.similarity(template[1])
            if pDist > best[1]:
                best = (template[0], pDist)
        return [(best[0], best[1])]
    
class knnMatcher(Matcher):
    def __init__(self, library, scaler, featureExtractor, k):
        self.k = k
        Matcher.__init__(self, library, scaler, featureExtractor)

    def bestGuess(self, inputIm):
        '''Finds the best match according to 'pixelDist()' and returns it if less than the cutoff'''
        k = min(len(self.library), self.k)
        best = []
        for template in self.library[:k]:
            best.append((inputIm.similarity(template[1]), template[0]))
        best.sort()
        for template in self.library[k:]:
            pDist = inputIm.similarity(template[1])
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
        return voteDict.items()
