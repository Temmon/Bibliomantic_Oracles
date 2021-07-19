import sys
import os
#import urllib.request
import requests
import hashlib
import itertools

import argparse
import pathlib

from collections import Counter
from tabulate import tabulate
from freq import Frequency

import pickler

parser = argparse.ArgumentParser(description='Find the top unusual words in a book.')
parser.add_argument('--count', '-c', type=int, help="Number of results in each list", default=10)
parser.add_argument('-n', action='store_true', help="Analyze nouns.")
parser.add_argument('-v', action='store_true', help="Analyze verbs.")
parser.add_argument('-a', action='store_true', help="Analyze adjectives.")
parser.add_argument('frequency_dir', type=pathlib.Path, help="Path to folder containing corpus frequency information.")
parser.add_argument('book', type=pathlib.Path, help="Path to book to analyze")
parser.add_argument('--output', '-o', default="", type=pathlib.Path, help="Path to folder to store human readable unusual words.")
parser.add_argument('--temp', '-t', default="", type=pathlib.Path, help="Path to folder to store temporary information about book frequency.")
parser.add_argument('--bookDir', action=store_true, default=False, help="If true, will analyze all files in the specified book directory")

class ParseError(Exception):
    def __init__(self, message):
        self.message = message

class Unusual():

    def __init__(self, args):
        self.count = args.count

        self.frequencies = Frequency()

        self.allNouns = pickler.loadPickleFile(os.path.join(self.freqPath, "nouns.pickle"), Counter)
        self.allVerbs = pickler.loadPickleFile(os.path.join(self.freqPath, "verbs.pickle"), Counter)
        self.allAdjs  = pickler.loadPickleFile(os.path.join(self.freqPath, "adjs.pickle" ), Counter)

        m = hashlib.md5()
        m.update(self.bookPath.encode())
        self.bookHash = m.hexdigest()



    def hasTempFiles(self):
        return self.tempDir and os.path.exists(os.path.join(self.tempDir, self.bookHash))

    def run(self):

        #One of these needs to be run before compare can be run.
        try:
            if self.hasTempFiles():
                self.loadBookFiles()
            else:
                self.parseBook()
        except ParseError as err:
            return err.message

        ret = None

        if self.runNouns:
            ret = self.save(self.compare(self.allNouns, self.frequencies.nouns), "nouns")
        if self.runVerbs:
            ret = self.save(self.compare(self.allVerbs, self.frequencies.verbs), "verbs")
        if self.runAdjs:
            ret = self.save(self.compare(self.allAdjs,  self.frequencies.adjs ), "adjs")

        return ret

    def loadBookFiles(self):
        self.frequencies = pickler.loadPickleFile(os.path.join(self.tempDir, self.bookHash), Frequency)

    def parseBook(self):
        #Importing them here, instead of the top because just importing these libraries can take a lot of time.
        #No need to waste that time when we don't need them.

        import spacy
        import verber

        nlp = spacy.load("en_core_web_sm")
        #nlp.max_length = MAX_LEN

        text = self.loadText()
        text = verber.stripMeta(text)

        texts = verber.chunkify(text)

        for t in texts:
            if len(t) > verber.MAX_LEN:
                raise ParseError("Sorry, that file is too large for me to read! If you can find a copy with paragraph breaks, I can break it up for myself.")

            t = t.replace("\n", " ")

            doc = nlp(t) 

            self.frequencies.update(*verber.getWords(doc, False))

        if self.tempDir and self.tempDir != ".":
            self.outputTemp()


    def compare(self, allWords, bookWords):
        simpleCutoff = allWords.most_common(int(len(allWords) * .01))[-1][1]


        allCount = sum([c[1] for c in allWords.most_common(1000)])
        bookCount = sum([c[1] for c in bookWords.most_common(1000)])
 
        #simpleCutoff = allWords.most_common(int(len(allWords) * .01))[-1][1]
        #simpleCutoff2 = allWords.most_common(int(len(allWords) * .001))[-1][1]

        simpleCutoff = 50000

        simple = []
        unusual = []

        for word in bookWords.most_common():
            word = word[0]
            bookCheck = bookWords[word]

            #if bookCheck < 4:
            #    continue

            if word not in allWords:
                unusual.append((word, bookCheck * .0001))
                simple.append(word)
            else:
                check = allWords[word]

                unusual.append((word, (bookCheck / bookCount) - (check / allCount)))

                if check < simpleCutoff:
                    simple.append(word)

        unusual = sorted(unusual, key=lambda u: u[1], reverse=True)
        unusual = [u[0] for u in unusual]

        tops = [c[0] for c in bookWords.most_common()]
        res = Results([tops, simple, unusual], ["Top", "Count1", "Percentage1"])

        return res

    def outputTemp(self):
        pickler.dumpPickleFile(os.path.join(self.tempDir, self.bookHash), self.frequencies)


class UnusualBot(Unusual):
    def __init__(self, args):
        self.runNouns = False
        self.runVerbs = False
        self.runAdjs  = False
        self.bookPath = args.bookPath
        self.freqPath = args.freqPath
        self.tempDir = args.tempDir
        self.outputDir = None
        self.mode = args.mode

        if args.pos == "n":
            self.runNouns = True
        elif args.pos == "v":
            self.runVerbs = True
        elif args.pos == "a":
            self.runAdjs = True

        super().__init__(args)

        print("Received request to parse a book.")


    def loadText(self):
        response = requests.get(self.bookPath)
        if response.status_code != 200:
            raise ParseError(f"Could not read the file at {self.bookPath}. Check to make sure the page loads properly.")

        if "text/plain" not in response.headers['content-type'].lower():
            raise ParseError(f"The file at {self.bookPath} doesn't appear to be plain text. Let Temmon know if you're certain it should be.")

        return response.text

    def save(self, res, name):
        if self.mode == "unusual":
            return "```" + "\n".join(res.lists[1][:self.count+1]) + "```"

        if self.mode == "top":
            return "```" + "\n".join(res.lists[0][:self.count+1]) + "```"

        if self.mode == "percentage":
            return "```" + "\n".join(res.lists[2][:self.count+1]) + "```"


        #return "```" + str(res.prettify(self.count)) + "```"


class UnusualCmd(Unusual):
    def __init__(self, args):
        self.runNouns = args.n
        self.runVerbs = args.v
        self.runAdjs = args.a
        self.book = args.book
        self.freqPath = args.frequency_dir
        self.outputDir = args.output
        self.tempDir = args.temp
        self.cumu = args.cumulativeFile

        self.bookPath = self.book.name
        self.bookName = pathlib.Path(self.bookPath).stem

        if not any([self.runNouns, self.runAdjs, self.runVerbs]):
            self.runVerbs = True
            self.runAdjs = True
            self.runNouns = True    

        super().__init__(args)


    def loadText(self):
        with open(self.book, "r", encoding="ISO-8859-1") as inFile:
            return inFile.read()


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
        data = itertools.zip_longest(*[l[:count] for l in self.lists])
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
    UnusualCmd(args).run()

