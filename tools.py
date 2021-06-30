import sys
import nltk.data

import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet

import categories

def word_scorer(w1, w2 = None, with_similarity_score = False):
    '''
    Retrive the list of wordnet synonyms for a given word, and it's definition. Scores each against one specific synset.
    
    Args:
    w1 = word, text string, 'code'
    w2 = defined synset for similarity comparison, e.g. 'code.v.01' (default = None)
    with_similarity_score = set to True to include similarity scores of w1 with w2 synsets (default = False)
    
    Outputs:
    list of tuples (synonym name, synonym definition, similarity score)
    '''

    syns = []
    for i in range(len(wordnet.synsets(w1))):
        if with_similarity_score:
            if w2 is not None:
                syns.append((wordnet.synsets(w1)[i].name(),
                             wordnet.synsets(w1)[i].definition(),
                             wordnet.synset(w2).wup_similarity(wordnet.synsets(w1)[i])))
            else:
                print('with_similarity_score set to True, but no w2 defined')
                break
        else:
            syns.append((wordnet.synsets(w1)[i].name(),
                         wordnet.synsets(w1)[i].definition()))
    return syns

def sentencize(text):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(text)

def stripNewLine(f):
    data = f.readlines()
    data = [l.strip() for l in data if l]
    data = " ".join(data)
    data = data.replace("  ", " ")
    return data

def massageText():
    if len(sys.argv) < 3:
        print("Need an in path and an out path")
    inPath = sys.argv[1]
    outPath = sys.argv[2]

    with open(inPath, "r") as infile:
        text = stripNewLine(infile)
        sentences = sentencize(text)

    with open(outPath, "w") as outfile:
        for s in sentences:
            outfile.write(s + "\n")   

def scores():
    word = sys.argv[1]
    print(word_scorer(word))

def prep_phrase(phrase):
    '''
    Removes stopwords, punctuation from text, and converts into a list of word tokens
    
    Args:
    phrase = text string
    
    Outputs:
    list of word tokens
    '''
    
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(phrase)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return filtered_sentence

def topic_scorer(phrase, topic, sim_thresh = 0.8, return_hits = False):
    '''
    For each word in a sentence, retrieves the synonym set. For each synonym we measure the wup_similarity
    to the topic at hand. If similarity > sim_threshold, the topic is said to have been mentioned.
    The wup_similarity threshold can be configured: where a higher threshold for increases the strictness of the word-to-topic similarity condition.
    If return_hits is set to True, the words in the phrase that were mapped to each topic will be returned.
    
    Args:
    filtered_sentence = tokenized sentence, preferrably stripped of stopwords
    topic = synset of the topic in question.
    sim_thresh = wup_similarity threshold for word and topic to be deemed similar enough (default 0.6)
    return_hits = return the words that matched to each topic (default = False)
    
    Outputs:
    Integer count of the number of mentions of the topic in the filtered_sentence
    '''
    
    phrase = prep_phrase(phrase)
    word_scores = []
    
    for w in range(len(phrase)):
        syns = wordnet.synsets(phrase[w])
        syns_sim = [topic.wup_similarity(syns[synonym]) for synonym in range(len(syns))]
        syns_sim = [sim if sim is not None else 0 for sim in syns_sim]
        try:
            syns_sim = np.max([1 if sim > sim_thresh else 0 for sim in syns_sim])
        except ValueError:
            syns_sim = 0
        word_scores.append(syns_sim)
    hits = [phrase[w] for w in range(len(phrase)) if word_scores[w] == 1]
        
    if return_hits:    
        return (np.sum(word_scores), hits)
    else:
        return np.sum(word_scores)

def multi_topic_scorer(phrase, topic_dictionary, sim_thresh=0.8, return_hits=False):
    '''
    Takes a passage of text and maps words in that text to topics that have been defined in a topic dictionary.
    The wup_similarity threshold can be configured: where a higher threshold for increases the strictness of the word-to-topic similarity condition.
    If return_hits is set to True, the words in the phrase that were mapped to each topic will be returned.
    
    Args:
    phrase = passage of text
    topic_dictionary = dictionary where key:value is reader-friendly topic name:assigned synonym in wordnet
    sim_thresh = wup_similarity threshold for word and topic to be deemed similar enough (default 0.6)
    return_hits = return the words that matched to each topic (default = False)
    
    Outputs:
    sim_scores = dictionary where key:value is the reader-friendly topic name:number of synonyms present in the text
    '''

    sim_scores = {}
    
    for topic in list(topic_dictionary.keys()):
        topic_synset = wordnet.synset(topic_dictionary['{}'.format(topic)])
        sim_scores['{}'.format(topic)] = topic_scorer(phrase, topic_synset, sim_thresh, return_hits)
    return sim_scores

if __name__ == "__main__":
    with open(sys.argv[1], "r") as inFile:
        lines = inFile.readlines()
        for l in lines[11:17]:
            print(l)
            print(multi_topic_scorer(l, categories.appearance, return_hits=True))


