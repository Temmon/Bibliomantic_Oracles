import sys
import os
import pickler

from collections import Counter

from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
import spacy

import similar


MAX_LEN = 2000000
animal = wn.synset("animal.n.01")
person = wn.synset("person.n.01")
location = wn.synset("location.n.01")
brown_ic = wordnet_ic.ic('ic-brown.dat')


def calcSimilarity(syn, test, pos=wn.NOUN):
    return syn.res_similarity(test, brown_ic)

def checkCategories(lemma, pos=wn.NOUN):
    ret = []
    for syn in wn.synsets(lemma, pos):
        ret.append(similar.Similarity(lemma, syn.name(), 
            calcSimilarity(syn, animal), calcSimilarity(syn, person), calcSimilarity(syn, location)))
    return ret


def getWords(doc, calcSim=True):
    verbs = Counter()
    nouns = Counter()
    adjs = Counter()

    sims = []
    medieval = 1

    for token in doc:
        lemma = token.lemma_.lower()
        if not lemma.isalpha():
            continue

        if len(lemma) < 3:
            continue

        if token.pos_ == "VERB":
            verbs[lemma] += 1
        elif token.pos_ == "NOUN":
            if lemma in blacklist:
                continue

            if calcSim and lemma not in nouns:
                s = checkCategories(lemma)
                sims += s

            nouns[lemma] += 1
        elif token.pos_ == "ADJ":
            adjs[lemma] += 1

    return verbs, nouns, adjs, sims

def stripMeta(text):
    startKey = "*** START "
    startIdx = text.find(startKey)
    lineEnd = text.find("\n", startIdx)
    text = text[lineEnd+1:]


    endKey = "*** END "
    endIdx = text.find(endKey)
    text = text[:endIdx]

    return text

def main(path):
    nlp = spacy.load("en_core_web_sm")
    nlp.max_length = MAX_LEN
    verbs = pickler.loadPickleFile(pickler.verbPath, Counter)
    nouns = pickler.loadPickleFile(pickler.nounPath, Counter)
    adjs = pickler.loadPickleFile(pickler.adjPath, Counter)

    sims = pickler.loadPickleFile(pickler.simsPath, list)

    readFiles = pickler.loadPickleFile(pickler.readPath, list)

    allFiles = sorted(os.listdir(path))
    for f in allFiles:
        if f in readFiles:
            print(f"Skipping {f}. Already read.")
            continue

        percent = ((len(readFiles) * 1.0) / len(allFiles)) * 100
        print(f"Loading {f}. {percent}% processed.")

        if not os.path.isfile(os.path.join(path, f)):
            continue

        with open(os.path.join(path, f), "r", encoding="ISO-8859-1") as inFile:
            text = inFile.read()
            text = stripMeta(text)
            text = text.replace("\n", " ")

        if len(text) > MAX_LEN:
            continue

        doc = nlp(text)

        v, n, j, s = getWords(doc)
        verbs += v
        nouns += n
        adjs += j
        sims += s
        readFiles.append(f)

        pickler.dumpPickleFile(pickler.verbPath, verbs)
        pickler.dumpPickleFile(pickler.nounPath, nouns)
        pickler.dumpPickleFile(pickler.adjPath, adjs)
        pickler.dumpPickleFile(pickler.simsPath, sims)

        pickler.dumpPickleFile(pickler.readPath, readFiles)


if __name__ == "__main__":
    inDir = sys.argv[1]
    main(inDir)


blacklist = ["fag", "bitch"]

