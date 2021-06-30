import os
import pickle


verbPath = "verbs.pickle"
nounPath = "nouns.pickle"
adjPath = "adjs.pickle"
readPath = "read.pickle"
simsPath = "sims.pickle"

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
