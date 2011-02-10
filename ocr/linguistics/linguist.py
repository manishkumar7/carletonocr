from nltk.model.ngram import NgramModel
from nltk.corpus import brown
import math

INFINITY = 1000000

def negativeLog(n):
    if n == 0:
        return INFINITY
    else:
        return -math.log(n)

class Linguist(object):
    #Future subclasses:
    #n-grams (for words and for characters) -- would need library
    #Deeper linguistic knowledge?
    
    def __init__(self, selfImportance):
        self.selfImportance = selfImportance
        
    def correct(self, characterPossibilities):
        '''Correct errors based on linguistic knowledge'''
        #print characterPossibilities
        output = ''
        context = self.makeContext()
        for item in characterPossibilities:
            if isinstance(item, str):
                output += item
            else:
                maxProbability = 10*INFINITY
                bestLetter = ''
                for character, probability in item:
                    realProbability = self.probability(probability, self.modelProbability(character, context))
                    if realProbability < maxProbability:
                        bestLetter = character
                        maxProbability = realProbability
                self.updateContext(context, bestLetter)
                output += bestLetter
        return output
    
    def makeContext(self):
        return None
    
    def updateContext(self, context, letter):
        pass
    
    def modelProbability(self, character, context):
        return 1
    
    def probability(self, oldProb, newProb):
        return negativeLog(oldProb)*(1-self.selfImportance) + negativeLog(newProb)*self.selfImportance 

class NGramLinguist(Linguist):

    def __init__(self, selfImportance, brownCorpusLength, numberOfCharacters):
        Linguist.__init__(self, selfImportance)
        self.n = numberOfCharacters
        self.model = NgramModel(numberOfCharacters, brown.words()[:brownCorpusLength])

    def makeContext(self):
        return []
    
    def updateContext(self, context, letter):
        context.append(letter)
        if len(context) == self.n: #context should never get longer than that
            context.pop(0)
    
    def modelProbability(self, character, context):
        try:
            probability = self.model.prob(character, context)
        except ZeroDivisionError:
            probability = 0
        print 'the probability of', character, 'given', context, 'is', probability
        return probability

if __name__ == '__main__':
    ngl = NGramLinguist(''.join(brown.words()[:10000]), 3, .5)
    #print ngl.correct([[('T', 0.0086476158434295354)], [('a', 0.0014644120247568524), ('e', 0.0036955325864065102)], [('I', 0.0051943103886207768), ('l', 0.01), ('>', 0.0043958944281524926)], [('I', 0.0051943103886207768), ('l', 0.01), ('>', 0.0043958944281524926)], ' ', [('m', 0.0070622421944015233)], [('a', 0.0016005252747515876), ('e', 0.0024544468140831367), ('o', 0.0014874257941023402)], ' ', [('w', 0.0084440866095709839)], [('h', 0.0049931955962481305), ('b', 0.0023549989726514547)], [('a', 0.0026203615572904081), ('s', 0.0012722661400481152), ('e', 0.0013000832774168998)], [('t', 0.011137860871976022)], ' ', [('y', 0.007495792929572519), (',', 0.0031171004987360796)], [('e', 0.0017966110929497655), ('o', 0.004191174601633544)], [('0', 0.0018189793161631895), ('u', 0.004208631909992694)], ' ', [('k', 0.0079282307374859071)], [('n', 0.0055344540032470843)], [('e', 0.0017966110929497655), ('o', 0.004191174601633544)], [('w', 0.0068155724660038967)], '\n', [('a', 0.0024628029535896166), ('s', 0.0012421495123307313), ('e', 0.0012781232620456039)], [('b', 0.0055341002417975266), ('d', 0.0027341277070944453)], [('0', 0.0019014742692215413), ('o', 0.0044531378862136834)], [('u', 0.006382281307215942)], [('t', 0.011244688865714048)], ' ', [('t', 0.011244688865714048)], [('i', 0.010069442465625812), ('!', 0.0050649350649350656)], [('9', 0.0023316848863439181), ('g', 0.0053666331354080823)], [('a', 0.0016113727105079405), ('e', 0.0024880677444187836), ('o', 0.0014950520234688657)], [('r', 0.007448002685330273)], [('a', 0.0017444907943302685), ('s', 0.0028891994081867503), ('o', 0.0018870072458455739)], [('.', 0.0044062443168365068)]])
    ngl.normalize([('c',2),('c',4),('c',4),('c',4),('c',5),('c',5),('c',7),('c',9)]) 

