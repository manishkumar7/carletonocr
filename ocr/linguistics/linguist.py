import math
import socket, os, signal, sys
import time
import random
from nltk.corpus import brown
import itertools

# Could we use hidden markov models with the ngram linguist to do a better job with the first character?
# Could we run the ngram linguist and then apply the dictionary-based spelling correction for better results?

INFINITY = 1000000

def toString(lines):
    return '\n'.join(' '.join(''.join(word) for word in line) for line in lines)

def splitWords(line, fn):
    def split(word):
        output = []
        lastChar = None
        currentWord = []
        for char in word:
            if lastChar and fn(char, lastChar):
                if currentWord: output.append(currentWord)
                currentWord = []
            currentWord.append(char)
            lastChar = char
        if currentWord: output.append(currentWord)
        return output
    return map(split, line)

def eachWord(fn, lines):
    return [[fn(word) for word in line] for line in lines]

def concat(lst):
    output = []
    for sub in lst: output.extend(sub)
    return lst

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
        return toString(self.string)
    def inputString(self):
        return NullLinguist(0.0).correct(self.characterPossibilities).result()
    def visualize(self):
        return 'Before correction: %s\nAfter correction: %s' % (self.inputString(), self.result())

punctuation = set([')',',','.','!','?',':',';','"',"'",'*', '(', '~', ']', '['])
def isPunct(possibilities):
    '''returns true if we expect that there is a break between the characters'''
    yes = 0
    no = 0
    for char, prob in possibilities:
        if char in punctuation:
            yes += prob
        else:
            no += prob
    return yes > no

class Linguist(object):
    def __init__(self, selfImportance):
        self.selfImportance = selfImportance

    def correct(self, lines):
        def shouldSplit(first, second):
            return isPunct(first) or isPunct(second)
        output = []
        for line in lines:
            lineOutput = []
            words = splitWords(line, shouldSplit)
            for word in words:
                wordOutput = []
                for subword in word:
                    wordOutput.extend(self.correctWord(subword))
                lineOutput.append(wordOutput)
            output.append(lineOutput)
        return SimpleResult(output, lines)

class StreamLinguist(Linguist):
    #Future subclasses:
    #n-grams (for words and for characters) -- would need library
    #Deeper linguistic knowledge?

    def correctWord(self, characterPossibilities):
        '''Correct errors based on linguistic knowledge'''
        #print characterPossibilities
        context = self.makeContext()
        def transform(item):
            maxProbability = 10*INFINITY
            bestLetter = ''
            for character, probability in item:
                realProbability = self.chance(probability, character, context)
                if realProbability < maxProbability:
                    bestLetter = character
                    maxProbability = realProbability
            self.updateContext(context, bestLetter)
            return bestLetter
        return map(transform, characterPossibilities)

    def chance(self, oldProb, character, context):
        newProb = self.probability(character, context)
        return negativeLog(oldProb)*(1-self.selfImportance) + newProb*self.selfImportance 

class NullLinguist(StreamLinguist):

    def makeContext(self):
        return None

    def updateContext(self, context, letter):
        pass

    def probability(self, character, context):
        return 1

class NGramProgram(object):
    def __init__(self):
        connected = False
        while not connected:
            connected = True
            self.port = random.randint(5000,50000)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                print "trying", self.port
                s.bind(('localhost', self.port))
            except socket.error, e:
                if e[0] == 13:
                    connected = False
                else:
                    sys.exit(1)
            s.close()
        self.server = os.spawnv(os.P_NOWAIT, 'ngram', ['ngram', '-server-port', str(self.port), '-lm', 'language-model.txt'])
        time.sleep(.5)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(('localhost', self.port))

    def __del__(self):
        os.kill(self.server, signal.SIGINT)
        self.socket.close()

    def probability(self, query):
        self.socket.send(query+"\r\n")
        while True:
            message = self.socket.recv(4096).strip('\r\n \t\0')
            for line in message.split():
                if line == '-inf':
                    return 10000
                try:
                    return -float(line)
                except ValueError:
                    pass

class NGramLinguist(StreamLinguist):
    def __init__(self, selfImportance, lettersInNgram):
        StreamLinguist.__init__(self, selfImportance)
        self.n = lettersInNgram
        self.ngramProgram = NGramProgram()

    def makeContext(self):
        return []
    
    def updateContext(self, context, letter):
        context.append(letter)
        if len(context) == self.n:
            context.pop(0)
    
    def probability(self, character, context):
        return self.ngramProgram.probability(' '.join(context+[character]))

def counted(iterable):
    return itertools.izip(itertools.count(), iterable)

class WordLinguist(Linguist):

    def correctWord(self, characterPossibilities):
        characterPossibilities = map(lambda lst: sorted(lst, key=lambda c: c[1], reverse=True), characterPossibilities)
        candidates = []

        def extract(candidate):
            letters, probabilities = zip(*[characterPossibilities[i][c] for (i, c) in counted(candidate)])
            string = ''.join(letters)
            wordProbability = self.probability(string)
            if wordProbability is not None:
                charactersProbability = sum(map(negativeLog, probabilities)) / len(string)
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
            return [min(candidates, key=lambda c: c[1])[0]]
        else:
            return self.backup().correct(characterPossibilities).result()

class SpellingLinguist(WordLinguist):

    def __init__(self, selfImportance, lettersInNgram, editDistance):
        WordLinguist.__init__(self, selfImportance)
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

    def probability(self, string):
        if string in self.dictionary:
            return negativeLog(self.dictionary[string]/float(self.count))
        else:
            return None

class WholeWordNGramLinguist(WordLinguist):

    def __init__(self, selfImportance, editDistance):
        WordLinguist.__init__(self, selfImportance)
        self.editDistance = editDistance
        self.ngramProgram = NGramProgram()

    def backup(self):
        raise Exception("This should never happen")

    def probability(self, string):
        query = ' '.join(string)
        return self.ngramProgram.probability(query)
