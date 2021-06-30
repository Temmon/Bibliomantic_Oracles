import sys
import os

import argparse
import pathlib

from collections import Counter
from tabulate import tabulate

import pickler

parser = argparse.ArgumentParser(description='Find the top unusual words in a book.')
parser.add_argument('--count', '-c', type=int, help="Number of results in each list", default=100)
parser.add_argument('-n', action='store_true', help="Analyze nouns.")
parser.add_argument('-v', action='store_true', help="Analyze verbs.")
parser.add_argument('-a', action='store_true', help="Analyze adjectives.")
parser.add_argument('frequency_dir', type=pathlib.Path, help="Path to folder containing corpus frequency information.")
parser.add_argument('book', type=argparse.FileType('r', encoding="ISO-8859-1"), help="Path to book to analyze")
parser.add_argument('--output', '-o', default="", type=pathlib.Path, help="Path to folder to store human readable unusual words.")
parser.add_argument('--temp', '-t', default="", type=pathlib.Path, help="Path to folder to store temporary information about book frequency.")


class Unusual():

    def __init__(self, args):
        self.count = args.count
        self.runNouns = args.n
        self.runVerbs = args.v
        self.runAdjs = args.a
        self.book = args.book
        self.freqPath = args.frequency_dir
        self.outputDir = args.output
        self.tempDir = args.temp

        self.bookName = pathlib.Path(self.book.name).stem

        self.allNouns = pickler.loadPickleFile(os.path.join(self.freqPath, "nouns.pickle"), Counter)
        self.allVerbs = pickler.loadPickleFile(os.path.join(self.freqPath, "verbs.pickle"), Counter)
        self.allAdjs  = pickler.loadPickleFile(os.path.join(self.freqPath, "adjs.pickle" ), Counter)

        if not any([self.runNouns, self.runAdjs, self.runVerbs]):
            self.runVerbs = True
            self.runAdjs = True
            self.runNouns = True

    def hasTempFiles(self):
        if not self.tempDir or not os.path.exists(os.path.join(self.tempDir, self.bookName)):
            return False

        files = ["nouns.pickle", "verbs.pickle", "adjs.pickle"]

        return all([os.path.exists(os.path.join(self.tempDir, self.bookName, f)) for f in files])


    def run(self):

        #One of these needs to be run before compare can be run.
        if self.hasTempFiles():
            self.loadBookFiles()
        else:
            self.parseBook()

        if self.runNouns:
            self.save(self.compare(self.allNouns, self.nouns), "nouns")
        if self.runVerbs:
            self.save(self.compare(self.allVerbs, self.verbs), "verbs")
        if self.runAdjs:
            self.save(self.compare(self.allAdjs,  self.adjs ), "adjs")

    def loadBookFiles(self):
        self.nouns = pickler.loadPickleFile(os.path.join(self.tempDir, self.bookName, "nouns.pickle"), Counter)
        self.verbs = pickler.loadPickleFile(os.path.join(self.tempDir, self.bookName, "verbs.pickle"), Counter)
        self.adjs  = pickler.loadPickleFile(os.path.join(self.tempDir, self.bookName, "adjs.pickle"), Counter)


    def parseBook(self):
        #Importing them here, instead of the top because just importing these libraries can take a lot of time.
        #No need to waste that time when we don't need them.

        import spacy
        import verber

        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            nlp = spacy.load("en_core_web_trf")
        #nlp.max_length = MAX_LEN

        path = sys.argv[1]

        text = self.book.read()
        text = text.replace("\n", " ")

        doc = nlp(text) 

        self.verbs, self.nouns, self.adjs, s = verber.getWords(doc, False)

        if not os.path.exists(os.path.join(self.tempDir, self.bookName)):
            os.mkdir(os.path.join(self.tempDir, self.bookName))

        pickler.dumpPickleFile(os.path.join(self.tempDir, self.bookName, "nouns.pickle"), self.nouns)
        pickler.dumpPickleFile(os.path.join(self.tempDir, self.bookName, "verbs.pickle"), self.verbs)
        pickler.dumpPickleFile(os.path.join(self.tempDir, self.bookName, "adjs.pickle" ), self.adjs)

    def compare(self, allWords, bookWords):
        simpleCutoff = allWords.most_common(int(len(allWords) * .01))[-1][1]


        allCount = sum([c[1] for c in allWords.most_common(100)])
        bookCount = sum([c[1] for c in bookWords.most_common()])

        simpleCutoff = allWords.most_common(int(len(allWords) * .01))[-1][1]

        simple = []
        unusual = []

        for word in bookWords.most_common():
            word = word[0]
            if word not in allWords:
                unusual.append(word)
                simple.append(word)
            else:
                check = allWords[word]
                bookCheck = bookWords[word]

                if (check / allCount) < (bookCheck / bookCount):
                    unusual.append(word)

                if check < simpleCutoff:
                    simple.append(word)

        tops = [c[0] for c in bookWords.most_common()]
        res = Results([tops, simple, unusual], ["Top", "Count1", "Percentage1"])

        return res

    def save(self, res, name):
        if not self.outputDir:
            res.print(self.count)
            return

        if not os.path.exists(os.path.join(self.outputDir, self.bookName)):
            os.mkdir(os.path.join(self.outputDir, self.bookName))        

        res.write(self.count, os.path.join(self.outputDir, self.bookName, name + ".txt"))


class Results():
    def __init__(self, lists, headers):
        self.table = None
        self.lists = lists
        self.headers = headers

    def prettify(self, count):
        data = zip(*[l[:count] for l in self.lists])
        self.table = tabulate(data, headers=self.headers)

        return self.table

    def write(self, count, outPath):
        if not self.table:
            self.prettify(count)
        with open(outPath, "w") as outFile:
            outFile.write(self.table)

    def print(self, count):
        if not self.table:
            self.prettify(count)
        print(self.table)


if __name__ == "__main__":
    args = parser.parse_args()
    Unusual(args).run()

