mport pandas as pd
import random


class Game(object):


    def __init__(self):
        self.score = 0
        self.capitals = pd.read_csv('capitals.txt', sep='[. ]+\t', names = ['land', 'hauptstadt'], engine='python')
        self.indexes = list(self.capitals.index.values)

    def dice(self):
        index = random.choice(self.indexes)
        return index

    def ask(self, index):
        print('Was ist die Hauptstadt von ' + self.capitals['land'][index] + '?')

    def enter(self, index):
        answer = raw_input()
        if answer == self.capitals['hauptstadt'][index]:
            print('Richtig!')
            self.score += 1
        elif self.similar(answer, self.capitals['hauptstadt'][index]):
            print('Lass gelt!')
            print('Eigentlich richtig: ' + self.capitals['hauptstadt'][index])
            self.score += 1

        else:
            print('Falsch!')
            print('Richtige Antwort: ' + self.capitals['hauptstadt'][index])
        self.indexes.remove(index)

    def stats():
        print

    def in_both(self, s1, s2):
        s1 = s1.lower()
        s2 = s2.lower()
        s1_chars = set(s1)
        s2_chars = set(s2)
        result = sorted(s1_chars.intersection(s2_chars))
        return result

    def similar(self, guess, correct, p=0.7):
        both = self.in_both(guess, correct)
        if len(both) >= p * len (set(correct).intersection(set(correct))):
            return True
        else:
            return False

    def loop(self):
        while len(self.indexes) > 0:
            index = self.dice()
            self.ask(index)
            self.enter(index)
            print('Punktzahl: ' + str(self.score) + '/' + str(195 - len(self.indexes)) + ' (195)/ ' )

if __name__ == 'main':
    game = Game()
    game.loop()
