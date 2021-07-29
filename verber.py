import sys
import os
import pickler

from collections import Counter

#from nltk.corpus import wordnet_ic
import spacy

import similar


MAX_LEN = 100000

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

            nouns[lemma] += 1
        elif token.pos_ == "ADJ":
            adjs[lemma] += 1

    return verbs, nouns, adjs, sims

def stripMeta(text):
    startKey = "*** START "
    startIdx = text.find(startKey)
    if startIdx < 0:
        return text

    lineEnd = text.find("\n", startIdx)
    text = text[lineEnd+1:]


    endKey = "*** END "
    endIdx = text.find(endKey)
    text = text[:endIdx]

    return text


def chunkify(text):
    ret = []

    maxChunk = 50000

    while len(text) > maxChunk:
        breakidx = text.find("\n\n", maxChunk)
        if breakidx < 0:
            breakidx = text.find("\r\n\r\n", maxChunk)

        if breakidx < 0:
            break

        ret.append(text[:breakidx])
        text = text[breakidx:]

    return ret + [text]

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

