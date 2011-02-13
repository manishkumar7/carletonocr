import math
import socket, os, signal, sys
import time
import random
from nltk.corpus import brown
import itertools

# Could we use hidden markov models with the ngram linguist to do a better job with the first character?
# Could we run the ngram linguist and then apply the dictionary-based spelling correction for better results?

INFINITY = 1000000

def negativeLog(n):
    if n == 0:
        return INFINITY
    else:
        return -math.log(n)

class SimpleResult(object):
    def __init__(self, string, characterPossibilities):
        self.string = string
        self.characterPossibilities = characterPossibilities
    def result(self):
        return ''.join(self.string)
    def inputString(self):
        return NullLinguist(0.0).correct(self.characterPossibilities).result()
    def visualize(self):
        return 'Before correction: %s\nAfter correction: %s' % (self.inputString(), self.result())

class Linguist(object):
    def __init__(self, selfImportance):
        self.selfImportance = selfImportance

class StreamLinguist(Linguist):
    #Future subclasses:
    #n-grams (for words and for characters) -- would need library
    #Deeper linguistic knowledge?

    def correct(self, characterPossibilities):
        '''Correct errors based on linguistic knowledge'''
        #print characterPossibilities
        output = []
        context = [self.makeContext()]
        def transform(item):
            if isinstance(item, str):
                context[0] = self.makeContext()
                return item
            else:
                maxProbability = 10*INFINITY
                bestLetter = ''
                for character, probability in item:
                    realProbability = self.probability(probability, self.modelProbability(character, context[0]))
                    if realProbability < maxProbability:
                        bestLetter = character
                        maxProbability = realProbability
                self.updateContext(context[0], bestLetter)
                return bestLetter
        output = map(transform, characterPossibilities)
        return SimpleResult(output, characterPossibilities)

    def probability(self, oldProb, newProb):
        return negativeLog(oldProb)*(1-self.selfImportance) + negativeLog(newProb)*self.selfImportance 

class NullLinguist(StreamLinguist):

    def makeContext(self):
        return None

    def updateContext(self, context, letter):
        pass

    def modelProbability(self, character, context):
        return 1

class NGramLinguist(StreamLinguist):
    def __init__(self, selfImportance, lettersInNgram):
        StreamLinguist.__init__(self, selfImportance)
        self.n = lettersInNgram
        connected = False
        while not connected:
            connected = True
            self.port = random.randint(5000,10000)
            print "trying port", self.port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(('localhost', self.port))
            except socket.error, e:
                if e[0] == 13:
                    connected = False
                else:
                    print "Unexpected socket stuff"
                    sys.exit(1)
            s.close()
        self.server = os.spawnv(os.P_NOWAIT, 'ngram', ['ngram', '-server-port', str(self.port), '-lm', 'language-model.txt'])
        time.sleep(.1)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(('localhost', self.port))

    def __del__(self):
        os.kill(self.server, signal.SIGINT)
        self.socket.close()

    def makeContext(self):
        return []
    
    def updateContext(self, context, letter):
        context.append(letter)
        if len(context) == self.n:
            context.pop(0)
    
    def modelProbability(self, character, context):
        query = ' '.join(context+[character])+"\r\n"
        self.socket.send(query)
        while True:
            message = self.socket.recv(4096).strip('\r\n \t\0')
            for line in message.split():
                if line == '-inf':
                    return 0
                try:
                    return 2**float(line)
                except ValueError:
                    pass

class SpellingLinguist(Linguist):

    def __init__(self, selfImportance, lettersInNgram, editDistance):
        Linguist.__init__(self, selfImportance)
        dictionary = {}
        words = brown.words()
        for word in words:
            dictionary[word] = dictionary.get(word, 0) + 1
        self.dictionary = dictionary
        self.count = len(words)
        self.editDistance = editDistance
        self.n = lettersInNgram

    def backup(self):
        if not hasattr(self, 'ngram'):
            self.ngram = NGramLinguist(self.selfImportance, self.n)
        return self.ngram

    def correct(self, characterPossibilities):
        output = []
        word = []
        for character in characterPossibilities:
            if isinstance(character, str):
                output.extend(self.correctWord(word))
                word = []
                output.append(character)
            else:
                word.append(character)
        output.extend(self.correctWord(word))
        return SimpleResult(output, characterPossibilities)

    def correctWord(self, characterPossibilities):
        characterPossibilities = map(lambda lst: sorted(lst, key=lambda c: c[1], reverse=True), characterPossibilities)
        candidates = []
        def counted(iterable):
            return itertools.izip(itertools.count(), iterable)

        def extract(candidate):
            letters, probabilities = zip(*[characterPossibilities[i][c] for (i, c) in counted(candidate)])
            string = ''.join(letters)
            if string in self.dictionary:
                charactersProbability = sum(map(negativeLog, probabilities)) / len(string)
                wordProbability = negativeLog(self.dictionary[string]/float(self.count))
                probability = self.selfImportance*wordProbability + (1 - self.selfImportance)*charactersProbability
                candidates.append((string, probability))

        candidate = (0,)*len(characterPossibilities)
        theseCandidates = set([candidate])
        extract(candidate)
        # This is a pretty stupid way to generate all the possibilities
        # It makes twice as many newCandidates as it has to
        # Do it smarter, wtihout the inner if statement testing set membership!
        for i in range(self.editDistance):
            nextCandidates = set()
            for candidate in theseCandidates:
                for i in range(len(candidate)):
                    if candidate[i] < len(characterPossibilities[i])-1:
                        newCandidate = list(candidate)
                        newCandidate[i] += 1
                        newCandidate = tuple(newCandidate)
                        if newCandidate not in nextCandidates:
                            extract(newCandidate)
                            nextCandidates.add(newCandidate)
            theseCandidates = nextCandidates

        if candidates:
            return [max(candidates, key=lambda c: c[1])[0]]
        else:
            return self.backup().correct(characterPossibilities).result()
