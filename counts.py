import pickler
import os


def tops(inPath, outPath):
    verbs = pickler.loadPickleFile(inPath, list)

    tops = verbs.most_common(2000)

    with open(os.path.join("processed", outPath), "w") as outFile:
        for t in tops:
            outFile.write(f"{t[0]}\n")

def checkSim(sims, cat):
    sort = sorted(sims, key=lambda s : s.__getattribute__(cat), reverse=True)

    unique = []
    for s in sort:
        if s.lemma not in unique:
            unique.append(s.lemma)
        if len(unique) > 500:
            break

    with open(os.path.join("processed", f"{cat}.txt"), "w") as out:
        for s in unique:
            out.write(f"{s}\n")


def checkSims(sims):
    checkSim(sims, "animal")
    checkSim(sims, "person")
    checkSim(sims, "location")


def main():
    tops("verbcheck.pickle", "topVerbs.txt")
    tops("nouncheck.pickle", "topNouns.txt")
    tops("adjcheck.pickle", "topAdjs.txt")

    checkSims(pickler.loadPickleFile("simscheck.pickle", list))

if __name__ == "__main__":
    main()



