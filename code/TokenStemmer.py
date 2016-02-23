#!/usr/bin/python
#coding: utf8

import nltk
from nltk import PorterStemmer
import re
import StopWords
import gc
from tokenizer import tokenize

primitive_token_detection = re.compile(u'[^\s]+')
primitive_word_detection = re.compile(u'\A[\w-]+\Z')
primitive_pipe_detection = re.compile(u'\|')


def getStemmedTokens(text):
    #Case-Folding
    lowerText = text.lower()
    content = re.sub(u'[^a-zA-Z0-9]+', ' ', lowerText)
    tokens = content.split(" ")
    #Removing StopWords
    tokens1 = []
    for token in tokens:
        if token == "":
            continue
        if not StopWords.isStopWord(token):
            tokens1.append(token)
    stemTokens = []
    for token in tokens1:
        try:
            stemTokens.append(PorterStemmer().stem_word(token))
        except Exception as e:
            stemTokens.append(token)
    return stemTokens
    
def getStemmedToken(word):
    token = word.lower()
    if StopWords.isStopWord(token):
        return ""
    if re.match(primitive_word_detection, token):
        return PorterStemmer().stem_word(token)
    else:
        return token
