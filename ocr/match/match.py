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
        possibilities = []
        for similarity, character, features in best:
            #voteDict[character] = voteDict.get(character, 0) + similarity
            voteDict[character] = [(voteDict[character][0] if character in voteDict else 0) + similarity, features]
            possibilities.append((similarity,features))
        return voteDict.items(), possibilities
    
    def visualize(self, chFeatures, possFeatures):
        chFeatures = [x for x in chFeatures if isinstance(x,str) == False]
        visList = []
        for i in range(len(possFeatures)):
            possFeatures[i].sort()
            possFeatures[i].reverse()
            vis = []
            for feat in possFeatures[i]:
                vis.append(feat[1].visualize())
            visList.append(vis)
        for i in range(len(chFeatures)):
            chFeatures[i] = chFeatures[i].visualize()
        border = chFeatures[0].width/8
        mostMatches = 0
        for vis in visList:
            if len(vis) > mostMatches:
                mostMatches = len(vis)
        width = chFeatures[0].width + (visList[0][0].width+border)*mostMatches+border
        height = len(chFeatures) * (chFeatures[0].height+border) + border
        matchVis = cv.CreateImage((int(width), int(height)), 8, 3)
        cv.Rectangle(matchVis, (0,0),(int(width),int(height)),(255,255,255),-1)
        x = border
        y = border
        for i in range(len(chFeatures)):
            chFeat = chFeatures[i]
            for row in range(chFeat.height):
                for col in range(chFeat.width):
                    matchVis[y+row, x+col] = chFeat[row,col]
            x += chFeat.width + border
            for possFeat in visList[i]:
                for row in range(possFeat.height):
                    for col in range(possFeat.width):
                        matchVis[y+row, x+col] = possFeat[row, col]
                x += possFeat.width + border
            if i != len(chFeatures)-1:
                y += chFeat.height
                x = border
                cv.Line(matchVis, (0, int(y+border/2)),(matchVis.width, int(y+border/2)), (0,0,0), 3)
                y += border
        cv.Line(matchVis, (int(chFeatures[0].width+border*1.5),0),(int(chFeatures[0].width+border*1.5),matchVis.height), (0,0,0), 3)
        cv.SaveImage('matchVis.png',matchVis)
        return matchVis
        
                