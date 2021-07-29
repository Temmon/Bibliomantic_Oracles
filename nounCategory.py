
from nltk.corpus import wordnet as wn

abstract_entity = wn.synset("abstract_entity.n.01")
physical_object = wn.synset("physical_object.n.01")

abstractWords = {}
objectWords = {}

def check(word, target, record={}):
    if word in record:
        return record[word]
    #TODO: Check all? synsets
    nounSets = [s for s in wn.synsets(word) if s.pos() == wn.NOUN]

    allHypers = set(nounSets)
    hypers = set(nounSets)

    while hypers:
        hyper = hypers.pop()
        if hyper == target:
#            print(f"{word} is {hyper.name()}")
            record[word] = True
            return True
        for h in hyper.hypernyms():
            if h not in allHypers:
                allHypers.add(h)
                hypers.add(h)
    record[word] = False
    return False

def checkObject(word):
    return check(word, physical_object, objectWords)

def checkAbstract(word):
    return check(word, abstract_entity, abstractWords)


if __name__ == "__main__":
    checkAbstract('love')
    checkAbstract('barrier')
    checkAbstract('apple')
    checkAbstract('desire')

    checkObject('love')
    checkObject('barrier')
    checkObject('apple')
    checkObject('desire')