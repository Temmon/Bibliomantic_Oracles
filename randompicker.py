import sys
import os
import random


groups = ["adjs", "nouns", "verbs", "abstract", "physical", "people"]


def main(lists):

    og = ["adjs", "nouns"]

    conversion = {"n": "nouns", "a": "adjs", "v": "verbs", "b": "abstract", "p": "physical", "e": "people"}
    parts = og

    words = []

    randomType = 2

    randoms = {1: [["abstract", "nouns", "physical"], [70, 20, 10]], 
                2: [["people", "nouns", "abstract", "physical"], [70, 10, 10, 10]],
                3: [["physical", "nouns", "abstract"], [70, 20, 10]]}

    while True:
        try:
            if randomType:
                parts = ["adjs"]
                parts += random.choices(*randoms[randomType])

            words = [random.choice(lists.lists[p]) for p in parts]

            print(" ".join(words).capitalize())

            cat = input()

            if cat:
                cat = cat.lower()
                if cat == "random" or cat == "r":
                    randomType = 1
                elif cat == "rp":
                    randomType = 2
                elif cat == "rt":
                    randomType = 3
                else:
                    randomType = 0
                    if " " in cat or cat in groups:
                        parts = cat.split()
                    else:
                        parts = [conversion[c] for c in cat]



        except KeyError:
            print("Invalid parts")
            parts = og


def vote():
    count = 0
    while True:
        count += 1
        population = [i for i in range(1, 16)]
        weights = [i for i in range(15, 0, -1)]

        print(f"{random.choices(population, weights)} ({count})")

        input()




class Lists():
    def __init__(self, path):
        self.lists = {}

        for g in groups:
            with open(os.path.join(path, g + ".txt")) as inFile:
                lines = [l.strip() for l in inFile.readlines()]

                setattr(self, g, lines)
                self.lists[g] = lines

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Specify path to lists")
        sys.exit()

    if(sys.argv[1].lower()) == "vote":
        vote()
        sys.exit()

    main(Lists(sys.argv[1]))

