from collections import Counter

class Frequency():
    def __init__(self):
        self.nouns = Counter()
        self.verbs = Counter()
        self.adjs = Counter()

    def update(self, verbs, nouns, adjs, *args):
        self.nouns += nouns
        self.verbs += verbs
        self.adjs += adjs
