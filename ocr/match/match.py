import cv
import heapq

class Matcher:
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
        '''Finds the best match for 'inputIm' in the library and returns it'''
        best = (self.library[0][0], features.similarity(self.library[0][1]))
        for template in self.library[1:]:
            pDist = features.similarity(template[1])
            if pDist > best[1]:
                best = (template[0], pDist)
        return [best]
    
class knnMatcher(Matcher):
    def __init__(self, library, scaler, featureExtractor, k):
        self.k = k
        Matcher.__init__(self, library, scaler, featureExtractor)

    def bestGuess(self, inputIm):
        '''Finds the best match according to '.similarity()' and returns it'''
        best = []
        for character, features in self.library[:self.k]:
            similarity = (inputIm.similarity(features), character) 
            print "Comparing against %s" % character
            print "Similarity = %s" % similarity[0]
            heapq.heappush(best, similarity)
        for character, features in self.library[self.k:]:
            similarity = inputIm.similarity(features)
            print "Comparing against %s" % character
            print "Similarity = %s" % similarity
            if similarity > best[0][0]:
                heapq.heappop(best)
                heapq.heappush(best, (similarity, character))
        voteDict = {}
        for similarity, character in best:
            voteDict[character] = voteDict.get(character, 0) + similarity
        return voteDict.items()

#A neural network matcher might also be nice

