import math
import socket, os, signal, sys
import time
import random

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

PORT = 5319

class NGramLinguist(Linguist):

    def __init__(self, selfImportance, lettersInNgram):
        Linguist.__init__(self, selfImportance)
        self.n = lettersInNgram
        self.port = random.randint(10000, 50000) #We should really retry if the port is taken, but this is unlikely
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
