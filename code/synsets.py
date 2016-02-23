from nltk.corpus import wordnet as wn

def synsets(word):
    return [i.name().split('.')[0] for i in wn.synsets(word)]

