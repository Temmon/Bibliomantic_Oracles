
from nltk.corpus import wordnet as wn

abstract_entity = wn.synset("abstract_entity.n.01")
physical_object = wn.synset("physical_entity.n.01")
person = wn.synset("person.n.01")

abstractWords = {}
objectWords = {}
personWords = {}

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

def checkPerson(word):
    return check(word, person, personWords)


if __name__ == "__main__":
    print(checkAbstract('love'))
    print(checkAbstract('barrier'))
    print(checkAbstract('apple'))
    print(checkAbstract('desire'))
    print(checkAbstract('doughnut'))
    print(checkAbstract('spider'))

    print()

    print(checkObject('love'))
    print(checkObject('barrier'))
    print(checkObject('apple'))
    print(checkObject('desire'))
    print(checkObject('doughnut'))
    print(checkObject('spider'))
