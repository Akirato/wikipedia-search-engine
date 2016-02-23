#!/usr/bin/python
#coding: utf8

from sys import argv
import TokenStemmer


def parseQuery(queryString):
    tokensObject = {}
    tokensObject["type"] = "union" # Or can be union
    tokensObject["tT"] = [] # title Tokens
    tokensObject["bT"] = [] # bodytext Tokens
    tokensObject["cT"] = [] # category Tokens
    tokensObject["iT"] = [] # infobox Tokens
    tokensObject["gT"] = [] # Genaral Tokens
    queryTokens = queryString.lower().split(" ")
    for qT in queryTokens:
        if qT.startswith("t:"):
            tT = qT.replace("t:","")
            stemmed = TokenStemmer.getStemmedToken(tT)
            if stemmed != "":
                tokensObject["tT"].append(stemmed)
                tokensObject["type"] = "intersection"
        elif qT.startswith("b:"):
            bT = qT.replace("b:","")
            stemmed = TokenStemmer.getStemmedToken(bT)
            if stemmed != "":
                tokensObject["bT"].append(stemmed)
                tokensObject["type"] = "intersection"
        elif qT.startswith("c:"):
            cT = qT.replace("c:","")
            stemmed = TokenStemmer.getStemmedToken(cT)
            if stemmed != "":
                tokensObject["cT"].append(stemmed)
                tokensObject["type"] = "intersection"
        elif qT.startswith("i:"):
            iT = qT.replace("i:","")
            stemmed = TokenStemmer.getStemmedToken(iT)
            if stemmed != "":
                tokensObject["iT"].append(stemmed)
                tokensObject["type"] = "intersection"
        else:
            stemmed = TokenStemmer.getStemmedToken(qT)
            if stemmed != "":
                tokensObject["gT"].append(stemmed)
                tokensObject["type"] = "intersection"
            
    return tokensObject

