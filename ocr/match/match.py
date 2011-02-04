import cv
import heapq

class knnMatcher(object):
    def __init__(self, library, k):
        self.k = k
        self.library = library

    def bestGuess(self, charFeatures):
        '''Finds the best match according to '.similarity()' and returns it'''
        best = []
        #We keep track of features now for the visualization
        for character, features in self.library:
            similarity = charFeatures.similarity(features)
            if len(best) < self.k:
                heapq.heappush(best, (similarity, character, features))
            elif similarity > best[0][0]:
                heapq.heappop(best)
                heapq.heappush(best, (similarity, character, features))
        voteDict = {}
        for similarity, character, features in best:
            #voteDict[character] = voteDict.get(character, 0) + similarity
            voteDict[character] = [(voteDict[character][0] if character in voteDict else 0) + similarity, features]
        return voteDict.items()
