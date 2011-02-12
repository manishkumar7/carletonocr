from nltk.model.ngram import NgramModel
from nltk.corpus import brown

class Linguist(object):
    #Future subclasses:
    #n-grams (for words and for characters) -- would need library
    #Deeper linguistic knowledge?
    def correct(self, characterPossibilities):
        '''Correct errors based on linguistic knowledge'''
        output = ''
        context = self.makeContext()
        for item in characterPossibilities:
            if isinstance(item, str):
                output += item
            else:
                maxProbability = -99999
                bestLetter = ''
                for character, probability in item:
                    realProbability = self.probability(character, probability, context)
                    if probability > maxProbability:
                        bestLetter = character
                        maxProbability = probability
                self.updateContext(context, bestLetter)
                output += bestLetter
        return output
    
    def makeContext(self):
        return None
    
    def updateContext(self, context, letter):
        pass
    
    def probability(self, character, oldProbability, context):
        return oldProbability

class NGramLinguist(Linguist):

    def __init__(self, data, n, selfImportance):
        self.n = n
        self.selfImportance = selfImportance
        self.model = NgramModel(n, list(data))

    def makeContext(self):
        return []
    
    def updateContext(self, context, letter):
        context.append(letter)
        if len(context) == self.n: #context should never get longer than that
            context.pop(0)
    
    def probability(self, character, oldProbability, context):
        try:
            modelProbability = self.model.prob(character, context)
        except ZeroDivisionError:
            modelProbability = 0
        return oldProbability*(1-self.selfImportance) + modelProbability*self.selfImportance

