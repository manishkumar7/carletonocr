import cv
import heapq

class Matcher:
    def __init__(self, library, scaler, featureExtractor):
        self.library = library
        self.featureExtractor = featureExtractor
        self.scaler = scaler
    
    def match(self,characterPieces):
        output = []
        self.inputVisList = []
        self.scaledPieces = []
        for piece in characterPieces:
            if isinstance(piece, str):
                output += piece
                self.scaledPieces.append(piece)
            else:
                scaled = self.scaler.scale(piece)
                self.scaledPieces.append(scaled)
                features = self.featureExtractor.extract(scaled)
                newChar = self.bestGuess(features)
                self.inputVisList.append(features.visualize())
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
        
    def visualizeFeatures(self):
        pieces = self.scaledPieces
        inputVis = self.inputVisList
        numLines = pieces.count('\n') + 1
        lines = []
        for i in range(numLines):
            #line = [# chrs, sum of chr widths, # spaces]
            lines.append([0,0,0])
        curLine = 0
        yMax = 0
        for chr in pieces:
            if chr == ' ':
                lines[curLine][2] += 1
            elif chr == '\n':
                curLine += 1
            else:
                lines[curLine][0] += 1
                lines[curLine][1] += chr.width
                if chr.height > yMax:
                    yMax = chr.height
        totX = sum([l[1] for l in lines])
#        spaceWidth = float(totX)/sum([l[1] for l in lines])
        spaceWidth = pieces[0].width * .15
        for i in range(len(lines)):
            lines[i][1] += lines[i][0]*spaceWidth + lines[i][2]*spaceWidth*9
        imWidth = max([l[1] for l in lines]) + 2*spaceWidth
        betwLines = 10
        imHeight = numLines * ((2 * yMax) + betwLines)
        featuresVisual = cv.CreateImage((int(imWidth), int(imHeight)), 8, 3)
        cv.Rectangle(featuresVisual, (0,0), (featuresVisual.width, featuresVisual.height), (255,255,255), -1)
        xStart = spaceWidth
        y = 0
        x = xStart
        curVisInd = 0
        for chr in pieces:
            if chr == ' ':
                x += int(spaceWidth * 9)
            elif chr == '\n':
                x = xStart
                y += int(yMax*2)+betwLines
            else:
                curVis = inputVis[curVisInd]
                for row in range(curVis.height):
                    for col in range(curVis.width):
                        featuresVisual[y+row, x+col] = curVis[row, col]
                for row in range(chr.height):
                    for col in range(chr.width):
                        if chr[row, col]  < 1:
                            featuresVisual[y+row+curVis.height, x+col] = (0,0,0)
                x += (int(spaceWidth) + chr.width)
                curVisInd += 1
        return featuresVisual

class knnMatcher(Matcher):
    def __init__(self, library, scaler, featureExtractor, k):
        self.k = k
        Matcher.__init__(self, library, scaler, featureExtractor)

    def bestGuess(self, inputIm):
        '''Finds the best match according to '.similarity()' and returns it'''
        best = []
        for character, features in self.library[:self.k]:
            similarity = (inputIm.similarity(features), character) 
            #print "Comparing against %s" % character
            #if character == '.':
            #    print '**************look here*****************'
            #print "Similarity = %s" % similarity[0]
            heapq.heappush(best, similarity)
        for character, features in self.library[self.k:]:
            similarity = inputIm.similarity(features)
            #print "Comparing against %s" % character
            #if character == '.':
            #    print '****************look here***************'
            #print "Similarity = %s" % similarity
            if similarity > best[0][0]:
                heapq.heappop(best)
                heapq.heappush(best, (similarity, character))
        print best
        voteDict = {}
        for similarity, character in best:
            voteDict[character] = voteDict.get(character, 0) + similarity
        #print '-------------' + str(self.k) + '------------------'
        return voteDict.items()

#A neural network matcher might also be nice

