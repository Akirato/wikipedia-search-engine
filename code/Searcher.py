#!/usr/bin/python

import QueryHandler
import sys
import operator
import Indexer
import bisect
import bz2
import time
import TokenStemmer
import synsets
script, infile = sys.argv

TotalDocNum = 0
docIDTitleMap = {}
def getdocIDTitleMap():
    global TotalDocNum
    with open(infile+".titles","r") as titles_file:
        for line in titles_file:
            parts = line.strip().split('=')
            if len(parts) == 2:
                id = parts[0]
                title = parts[1]
                docIDTitleMap[id] = title
    TotalDocNum = len(docIDTitleMap)

indexFileCount = 0
indexFileWordMap = {}
sortedIndexFileWordMapKeys = []
def getIndexFileWordMap():
    global indexFileCount, indexFileWordMap, sortedIndexFileWordMapKeys
    with open(infile+".indexWordMap","r") as temp_file:
        for line in temp_file:
            parts = line.strip().split('=')
            if len(parts) == 2:
                index = parts[1]
                word = parts[0]
                indexFileWordMap[index] = word
    indexFileCount = len(indexFileWordMap)
    sortedIndexFileWordMapKeys = sorted(indexFileWordMap.keys())

indexFileTitleCount = 0
indexFileTitleMap = {}
sortedIndexFileTitleMapKeys = []
def getIndexFileTitleMap():
    global indexFileTitleCount, indexFileTitleMap, sortedIndexFileTitleMapKeys, TotalDocNum
    with open(infile+".titlesCount","r") as temp_file:
        TotalDocNum = int(temp_file.readline())
    with open(infile+".indexTitleMap","r") as temp_file:
        for line in temp_file:
            parts = line.strip().split('=')
            if len(parts) == 2:
                docID = int(parts[1])
                index = parts[0]
                indexFileTitleMap[docID] = index
    indexFileTitleCount = len(indexFileTitleMap)
    sortedIndexFileTitleMapKeys = sorted(indexFileTitleMap.keys())

def checkInIndexFileWordMap(term):
    pos = bisect.bisect(sortedIndexFileWordMapKeys,term)
    if pos > 0:
        pos = pos - 1
    key = sortedIndexFileWordMapKeys[pos]
    index = indexFileWordMap[key]
    with bz2.BZ2File("{0}.index{1}.bz2".format(infile,index), 'rb', compresslevel=9) as ipartF:
        for line in ipartF:
            if line.startswith("{0}=".format(term)):
                parts = line.strip().split("=")
                if len(parts) == 2:
                    ffo = Indexer.getFOFromLine(parts[1])
                    return ffo
    return {}
    
def checkInIndexFileTitleMap(docID):
    pos = bisect.bisect(sortedIndexFileTitleMapKeys,int(docID))
    if pos > 0:
        pos = pos - 1
    key = sortedIndexFileTitleMapKeys[pos]
    index = indexFileTitleMap[key]
    with bz2.BZ2File("{0}.titles{1}.bz2".format(infile,index), 'rb', compresslevel=9) as ipartF:
        for line in ipartF:
            if line.startswith("{0}=".format(docID)):
                parts = line.strip().split("=")
                if len(parts) == 2:
                    return parts[1]
    return ""

def intersectLists(lists):
    if len(lists)==0:
        return []
    lists.sort(key=len)
    new_lists = []
    for l in lists:
        if len(l) != 0:
            new_lists.append(l)
    if len(new_lists)==0:
        return []
    return list(reduce(lambda x,y: set(x)&set(y),new_lists))

def getSortedTuples(freq_map):
    sorted_tuples = sorted(freq_map.iteritems(), key=operator.itemgetter(1))
    return sorted_tuples
    
def doSearch(queryObject, numOfResults):
    queryDocList = []
    ffoMap = {}
    gTqueryDocList = {}
    tTqueryDocList = {}
    bTqueryDocList = {}
    cTqueryDocList = {}
    iTqueryDocList = {}
    # synsets.synsets(queryObject) 
    for gT in queryObject["gT"]:
        ffoMap[gT] = checkInIndexFileWordMap(gT)
    for tT in queryObject["tT"]:
        ffoMap[tT] = checkInIndexFileWordMap(tT)
    for bT in queryObject["bT"]:
        ffoMap[bT] = checkInIndexFileWordMap(bT)
    for cT in queryObject["cT"]:
        ffoMap[cT] = checkInIndexFileWordMap(cT)
    for iT in queryObject["iT"]:
        ffoMap[iT] = checkInIndexFileWordMap(iT)
    
    toUseDocIdList = set([])
    if queryObject["type"] == "intersection":
        toIntersect = []
        for word in ffoMap:
            wordDocs = []
            for docid in ffoMap[word]:
                wordDocs.append(docid)
            toIntersect.append(set(wordDocs))
        toUseDocIdList = set.intersection(*toIntersect)
    else:
        toUseAllDocIdList = []
        for word in ffoMap:
            toUseAllDocIdList.extend(ffoMap[word].keys())
        toUseDocIdList = set(toUseAllDocIdList)
                
    for gT in queryObject["gT"]:
        ffo = ffoMap[gT]
        if len(ffo) > 0:
            DF = len(ffo.keys())
            IDF = TotalDocNum / DF
            for docID in ffo.keys():
                if docID not in toUseDocIdList:
                    continue
                if ffo[docID]["t"] > 0:
                    TF = ffo[docID]["t"]
                    tTqueryDocList[docID] = TF * IDF
                if ffo[docID]["b"] > 0:
                    TF = ffo[docID]["b"]
                    bTqueryDocList[docID] = TF * IDF
                if ffo[docID]["c"] > 0:
                    TF = ffo[docID]["c"]
                    cTqueryDocList[docID] = TF * IDF
                if ffo[docID]["i"] > 0:
                    TF = ffo[docID]["i"]
                    iTqueryDocList[docID] = TF * IDF
                
    for tT in queryObject["tT"]:
        ffo = ffoMap[tT]
        if len(ffo) > 0:
            DF = len(ffo.keys())
            IDF = TotalDocNum / DF
            for docID in ffo.keys():
                if docID not in toUseDocIdList:
                    continue
                if ffo[docID]["t"] > 0:
                    TF = ffo[docID]["t"]
                    tTqueryDocList[docID] = TF * IDF
    
    for bT in queryObject["bT"]:
        ffo = ffoMap[bT]
        if len(ffo) > 0:
            DF = len(ffo.keys())
            IDF = TotalDocNum / DF
            for docID in ffo.keys():
                if docID not in toUseDocIdList:
                    continue
                if ffo[docID]["b"] > 0:
                    TF = ffo[docID]["b"]
                    bTqueryDocList[docID] = TF * IDF
    
    for cT in queryObject["cT"]:
        ffo = ffoMap[cT]
        if len(ffo) > 0:
            DF = len(ffo.keys())
            IDF = TotalDocNum / DF
            for docID in ffo.keys():
                if docID not in toUseDocIdList:
                    continue
                if ffo[docID]["c"] > 0:
                    TF = ffo[docID]["c"]
                    cTqueryDocList[docID] = TF * IDF
    
    for iT in queryObject["iT"]:
        ffo = ffoMap[iT]
        if len(ffo) > 0:
            DF = len(ffo.keys())
            IDF = TotalDocNum / DF
            for docID in ffo.keys():
                if docID not in toUseDocIdList:
                    continue
                if ffo[docID]["i"] > 0:
                    TF = ffo[docID]["i"]
                    iTqueryDocList[docID] = TF * IDF
    
    tfidfDOCMap = {}
    
        
    for doc in toUseDocIdList:
        TFIDF = 0
        if doc in iTqueryDocList:
            TFIDF += iTqueryDocList[doc]*0.2
        if doc in cTqueryDocList:
            TFIDF += cTqueryDocList[doc]*0.2
        if doc in bTqueryDocList:
            TFIDF += bTqueryDocList[doc]*0.1
        if doc in tTqueryDocList:
            TFIDF += tTqueryDocList[doc]*6
        if doc in gTqueryDocList:
            TFIDF += gTqueryDocList[doc]*0.2
        if TFIDF >0:
            tfidfDOCMap[doc] = TFIDF
    
    sorted_tuples = getSortedTuples(tfidfDOCMap)
    sorted_tuples.reverse()
    toReturnList = []
    topNtuples = sorted_tuples[:numOfResults]
    for pair in topNtuples:
        toReturnList.append(pair[0])
    return toReturnList

def getTitlesFromDocIds(docIDList):
    titlesList = []
    for docID in docIDList:
        titlesList.append(checkInIndexFileTitleMap(docID))
    return titlesList

def checkQueryInTitle(query,docTitleList):
    toReturn = [""]
    queryTokens = set(TokenStemmer.getStemmedTokens(query))
    for title in docTitleList:
        if queryTokens == set(TokenStemmer.getStemmedTokens(title)):
            toReturn[0] = title
        else:
            toReturn.append(title)
    if toReturn[0] == "":
        del toReturn[0]
    return toReturn
    

start = int(round(time.time()*1000))

getIndexFileWordMap()
getIndexFileTitleMap()



f = sys.stdin
queries =  []
for line in f.readlines():
    queries.append(line.strip())
queryNo = int(queries[0])
queries = queries[1:]

for query in queries:
    queryObject = QueryHandler.parseQuery(query)
    listOfDocIDs = doSearch(queryObject,10)
    print "Query = {0}".format(query)
    listOfTitles = getTitlesFromDocIds(listOfDocIDs)
    listOfTitles = checkQueryInTitle(query, listOfTitles)
    for title in listOfTitles:
        print title
    print ""
    
end = int(round(time.time()*1000))
with open(infile+".doneSearch","w") as done_file:
    toPrint = "Process is complete. Time Taken in milliseconds = {0}".format((end-start))
    print toPrint
    done_file.write(toPrint)
