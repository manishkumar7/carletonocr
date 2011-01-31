import cv
import heapq

class knnMatcher(object):
    def __init__(self, library, k):
        self.k = k
        self.library = library

    def bestGuess(self, charFeatures):
        '''Finds the best match according to '.similarity()' and returns it'''
        best = []
        for character, features in self.library:
            similarity = charFeatures.similarity(features)
            if len(best) < self.k:
                heapq.heappush(best, (similarity, character))
            elif similarity > best[0][0]:
                heapq.heappop(best)
                heapq.heappush(best, (similarity, character))
        voteDict = {}
        for similarity, character in best:
            voteDict[character] = voteDict.get(character, 0) + similarity
        return voteDict.items()
