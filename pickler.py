import os
import pickle


verbPath = os.path.join("newFrequencies", "verbs.pickle")
nounPath = os.path.join("newFrequencies", "nouns.pickle")
adjPath = os.path.join("newFrequencies", "adjs.pickle")
readPath = os.path.join("newFrequencies", "read.pickle")
simsPath = os.path.join("newFrequencies", "sims.pickle")

paths = ["verbs.pickle", "nouns.pickle", "adjs.pickle", "read.pickle"]


def loadPickleFile(path, default):
    if os.path.exists(path): 
        with open(path, "rb") as f:
            return pickle.load(f)
    else:
        return default()

def dumpPickleFile(path, con):    
    with open(path, "wb") as p:
        pickle.dump(con, p)
