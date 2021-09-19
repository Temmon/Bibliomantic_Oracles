import sys
import os
#import urllib.request
import requests
import hashlib
import itertools
import csv

import pathlib

from collections import Counter
from tabulate import tabulate
from freq import Frequency
import nounCategory

import pickler
import cutupargs

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
        if not self.tempDir or self.tempDir.name == ".":
            return False
        return os.path.exists(os.path.join(self.tempDir, self.bookHash))

    def run(self):
        #One of these needs to be run before compare can be run.
        try:
            if self.hasTempFiles():
                self.loadBookFiles()
            else:
                self.parseBook()
        except ParseError as err:
            return err.message

        #print(len(self.frequencies.nouns))

        ret = None

        if self.runNouns:
            ret = self.save(self.compare(self.allNouns, self.frequencies.nouns), "nouns")
        if self.abstract:
            ret = self.save(self.compare(self.allNouns, self.frequencies.nouns, abstract=True), "abstract")
        if self.physical:
            ret = self.save(self.compare(self.allNouns, self.frequencies.nouns, physical=True), "physical")
        if self.people:
            ret = self.save(self.compare(self.allNouns, self.frequencies.nouns, people=True), "people")
        if self.runVerbs:
            ret = self.save(self.compare(self.allVerbs, self.frequencies.verbs), "verbs")
        if self.runAdjs:
            ret = self.save(self.compare(self.allAdjs,  self.frequencies.adjs ), "adjs")

        return ret

    def loadBookFiles(self):
        if self.frequencies:
            oldFrequencies = self.frequencies
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

        if self.tempDir.name and self.tempDir.name != ".":
            self.outputTemp()


    def compare(self, allWords, bookWords, abstract=False, physical=False, people=False):
        allCount = sum([c[1] for c in allWords.most_common(1000)])
        bookCount = sum([c[1] for c in bookWords.most_common(1000)])
 
        #simpleCutoff = allWords.most_common(int(len(allWords) * .01))[-1][1]
        #simpleCutoff2 = allWords.most_common(int(len(allWords) * .001))[-1][1]

        simpleCutoff = 50000

        simple = []
        unusual = []
        tops = []

        for word in bookWords.most_common():
            word = word[0]
            bookCheck = bookWords[word]
            if abstract or physical or people:
                if abstract: 
                    if not nounCategory.checkAbstract(word):
                        continue
                    if self.strict and nounCategory.checkObject(word):
                        continue
                if physical:
                    if not nounCategory.checkObject(word):
                        continue
                    if self.strict and nounCategory.checkAbstract(word):
                        continue
                if people:
                    if not nounCategory.checkPerson(word):
                        continue

            if word not in allWords:
                unusual.append((word, bookCheck * .0001))
                simple.append(word)
            else:
                check = allWords[word]

                unusual.append((word, (bookCheck / bookCount) - (check / allCount)))

                if check < simpleCutoff:
                    simple.append(word)

            tops.append(word)

        unusual = sorted(unusual, key=lambda u: u[1], reverse=True)
        unusual = [u[0] for u in unusual]

        #tops = [c[0] for c in bookWords.most_common()]
        res = Results([tops, simple, unusual], ["Top", "Count1", "Percentage1"])

        return res

    def outputTemp(self):
        pickler.dumpPickleFile(os.path.join(self.tempDir, self.bookHash), self.frequencies)


class UnusualBot(Unusual):
    def __init__(self, args):
        self.runNouns = args.nouns
        self.runVerbs = args.verbs
        self.runAdjs = args.adjectives
        self.bookPath = args.bookPath
        self.freqPath = args.freqPath
        self.tempDir = pathlib.Path(args.tempDir)
        self.outputDir = None
        self.mode = args.mode

        self.command = args.command

        self.flat = False

        self.abstract = args.abstract
        self.physical = args.physical
        self.people = args.people

        self.strict = args.strict

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
        ret =  "Results for: " + " ".join(self.command)

        if self.mode == "unusual":
            return ret + "\n```\n" + "\n".join(res.lists[1][:self.count]) + "```"

        if self.mode == "top":
            return ret + "\n```\n" + "\n".join(res.lists[0][:self.count]) + "```"

        if self.mode == "percentage":
            return ret + "\n```\n" + "\n".join(res.lists[2][:self.count]) + "```"


class UnusualCmd(Unusual):
    def __init__(self, args):
        self.runNouns = args.n
        self.runVerbs = args.v
        self.runAdjs = args.a
        self.book = args.book
        self.freqPath = args.frequency_dir
        self.outputDir = args.output
        self.tempDir = args.temp

        self.bookDir = args.bookDir

        self.bookPath = self.book.name
        self.bookName = pathlib.Path(self.bookPath).stem
        self.flat = args.flat

        self.strict = True

        if not any([self.runNouns, self.runAdjs, self.runVerbs]):
            self.runVerbs = True
            self.runAdjs = True
            self.runNouns = True    


        self.abstract = self.runNouns
        self.physical = self.runNouns
        self.people = self.runNouns

        super().__init__(args)

    def setBook(self, book):
        self.book = book
        self.bookPath = self.book.name
        #self.bookName = pathlib.Path(self.bookPath).stem

        m = hashlib.md5()
        m.update(self.bookPath.encode())
        self.bookHash = m.hexdigest()


    def loadText(self):
        with open(self.book, "r", encoding="ISO-8859-1") as inFile:
            return inFile.read()


    def save(self, res, name):
        if not self.outputDir:
            res.print(self.count)
            return

        if not os.path.exists(os.path.join(self.outputDir, self.bookName)):
            os.mkdir(os.path.join(self.outputDir, self.bookName))        

        res.write(self.count, os.path.join(self.outputDir, self.bookName, name + ".txt"), self.flat)



class Results():
    def __init__(self, lists, headers):
        self.table = None
        self.lists = lists
        self.headers = headers

    def prettify(self, count):
        data = itertools.zip_longest(*[l[:count] for l in self.lists])
        self.table = tabulate(data, headers=self.headers, tablefmt="tsv")

        return self.table

    def write(self, count, outPath, flat=False):
        if flat:
            self.writeflat(count, outPath)
            return

        if not self.table:
            self.prettify(count)
        with open(outPath, "w") as outFile:
            outFile.write(self.table)

    def writeflat(self, count, outPath):
        ret = set([])
        for l in self.lists:
            ret.update(l[:count])

        with open(outPath, "w") as outFile:
            outFile.write("\n".join(ret))

    def print(self, count):
        if not self.table:
            self.prettify(count)
        print(self.table)


def createParser():
    parser = cutupargs.getParser()
    parser.add_argument('frequency_dir', type=pathlib.Path, help="Path to folder containing corpus frequency information.")
    parser.add_argument('book', type=pathlib.Path, help="Path to book to analyze")
    parser.add_argument('--output', '-o', default="", type=pathlib.Path, help="Path to folder to store human readable unusual words.")
    parser.add_argument('--temp', '-t', default="", type=pathlib.Path, help="Path to folder to store temporary information about book frequency.")
    parser.add_argument('--bookDir', action='store_true', default=False, help="If true, will analyze all files in the specified book directory")
    parser.add_argument('--flat', '-f', action='store_true', default=False, help="Save the output as a flat list, rather than a table.")
    parser.add_argument('-n', action='store_true', help="Analyze nouns.")
    parser.add_argument('-v', action='store_true', help="Analyze verbs.")
    parser.add_argument('-a', action='store_true', help="Analyze adjectives.")

    return parser


if __name__ == "__main__":
    args = createParser().parse_args()
    cmd = UnusualCmd(args)
    if args.bookDir:
        d = args.book
        for f in os.listdir(d):
            cmd.setBook(pathlib.Path(os.path.join(args.book, f)))
            print("Running: ", str(cmd.book))
            cmd.run()
    else:
        cmd.run()

