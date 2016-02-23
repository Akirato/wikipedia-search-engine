#!/usr/bin/python
#coding: utf8

#works when run with index.sh
fil = open("./code/stopwords.txt","rb")
data = fil.read()
StopWordsList = data.split(', ')
print "Stop Words List Length:",len(StopWordsList)
StopWordsSet = set(StopWordsList)

def isStopWord(token):
    if token in StopWordsSet:
        return True
    else: 
        return False
