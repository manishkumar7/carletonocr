import cv
import heapq
import math

class knnMatcher(object):
    def __init__(self, library, k):
        self.k = k
        self.library = library
        self.templFeatures = []

    def bestFew(self, charFeatures):
        '''Finds the best match according to '.similarity()' and returns it'''
        best = []
        sum = 0.0
        #We keep track of features now for the visualization
        for character, features in self.library:
            similarity = charFeatures.similarity(features)
            if len(best) < self.k:
                heapq.heappush(best, (similarity, character, features))
            elif similarity > best[0][0]:
                heapq.heappop(best)
                heapq.heappush(best, (similarity, character, features))
        return best

    def voteDict(self, best):
        sum = 0
        for similarity, character, features in best:
            sum += similarity
        best = sorted(best, key=lambda guess: guess[0], reverse=True)
        voteDict = {}
        def weight(similarity, place):
            return similarity/(sum*(place+1))
        for (scf, place) in zip(best, range(len(best))):
            voteDict[scf[1]] = voteDict.get(scf[1], 0) + weight(scf[0], place)
        return voteDict.items()

    def visualize(self, chFeatures, possFeatures):
        visualizations = [ \
            (chFeature.visualize(), \
            [feature.visualize() for (similarity, character, feature) in sorted(best, reverse=True)]) \
            for (chFeature, best) in zip(chFeatures, possFeatures) \
            if not isinstance(chFeature, str)]
        charWidth = visualizations[0][0].width
        charHeight = visualizations[0][0].height
        border = charWidth/2
        mostMatches = max(len(vis[1]) for vis in visualizations)
        width = (charWidth+border) * (mostMatches+1)
        height = len(visualizations) * (charHeight+border) + border
        matchVis = cv.CreateImage((width, height), 8, 3)
        cv.Rectangle(matchVis, (0,0), (width, height), (255,255,255), -1)
        for i in range(len(visualizations)):
            y = border + i*(charHeight+border)
            x = border
            chVis, possVises = visualizations[i]
            for row in range(chVis.height):
                for col in range(chVis.width):
                    matchVis[y+row, x+col] = chVis[row,col]
            x += charWidth + border
            for possVis in possVises:
                for row in range(possVis.height):
                    for col in range(possVis.width):
                        matchVis[y+row, x+col] = possVis[row, col]
                x += charWidth + border
            if i != len(visualizations)-1:
                lineRow = y + charHeight + border/2
                cv.Line(matchVis, (0, lineRow), (width, lineRow), (0,255,0), 2)
        lineCol = charWidth + 3*border/2
        cv.Line(matchVis, (lineCol, 0), (lineCol, height), (0,255,0), 3)
        return matchVis
