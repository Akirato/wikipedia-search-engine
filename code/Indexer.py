#!/usr/bin/python

import re
import TokenStemmer
import os.path
import operator
import bz2

TermFreqMap = {}
outfile = None
titles_file = None
freq_string_detection = re.compile("([0-9]*)t([0-9]*)b([0-9]*)c([0-9]*)i([0-9]*)")
articleCount = 0
toDumpCount = 0

def doInit(ofile):
    global outfile
    outfile = ofile
    global titles_file
    titles_file = open(outfile+".titles","w")

def doIndex(wikiArticle, outfile):
    global articleCount
    global toDumpCount
    articleCount += 1
    toDumpCount += 1
    titles_file.write("{0}={1}\n".format(wikiArticle.id,wikiArticle.title))
    buildTermFreqMap(wikiArticle)
    checkTermFreqMapSizeAndWrite(outfile)
    
    

def buildTermFreqMap(wikiArticle):
    title_tokens = TokenStemmer.getStemmedTokens(wikiArticle.title)
    for token in title_tokens:
        #putTitleTokenInTermFreqMap(token, wikiArticle.id)
        checkIfTokenInTermFreqMap(token,wikiArticle.id)
        TermFreqMap[token][wikiArticle.id]["t"] += 1
    #link_tokens = wikiArticle.external_links
    #for token in link_tokens:
    #    putTokenInTermFreqMap(token)
    cat_tokens = TokenStemmer.getStemmedTokens(getStringFromListofStrings(wikiArticle.categories))
    for token in cat_tokens:
        #putCatTokenInTermFreqMap(token, wikiArticle.id)
        checkIfTokenInTermFreqMap(token,wikiArticle.id)
        TermFreqMap[token][wikiArticle.id]["c"] += 1
    ib_tokens = TokenStemmer.getStemmedTokens(wikiArticle.infobox_values_string)
    for token in ib_tokens:
        #putIBTokenInTermFreqMap(token, wikiArticle.id)
        checkIfTokenInTermFreqMap(token,wikiArticle.id)
        TermFreqMap[token][wikiArticle.id]["i"] += 1
    text_tokens = TokenStemmer.getStemmedTokens(wikiArticle.text)
    for token in text_tokens:
        #putBodyTokenInTermFreqMap(token, wikiArticle.id)
        checkIfTokenInTermFreqMap(token,wikiArticle.id)
        TermFreqMap[token][wikiArticle.id]["b"] += 1
    

def checkTermFreqMapSizeAndWrite(outfile):
    #if len(TermFreqMap) > 10000:
        #IndexWriter().mergeWriter()
    global toDumpCount
    if toDumpCount >= 10000:
        #mergeWriter(outfile)
        linearWriter(outfile)
        toDumpCount = 0
        

def checkIfTokenInTermFreqMap(token, wAid):
    if token not in TermFreqMap:
        freq_obj = {}
        TermFreqMap[token] = freq_obj
    if wAid not in TermFreqMap[token]:
        freq_doc_obj = {}
        freq_doc_obj["t"] = 0 #title
        freq_doc_obj["b"] = 0 #body
        freq_doc_obj["c"] = 0 #cat
        freq_doc_obj["i"] = 0 #infobox
        TermFreqMap[token][wAid] = freq_doc_obj

def putTitleTokenInTermFreqMap(token,wAid):
    checkIfTokenInTermFreqMap(token,wAid)
    TermFreqMap[token][wAid]["t"] += 1
    
def putBodyTokenInTermFreqMap(token,wAid):
    checkIfTokenInTermFreqMap(token,wAid)
    TermFreqMap[token][wAid]["b"] += 1
    
def putCatTokenInTermFreqMap(token,wAid):
    checkIfTokenInTermFreqMap(token,wAid)
    TermFreqMap[token][wAid]["c"] += 1
    
def putIBTokenInTermFreqMap(token,wAid):
    checkIfTokenInTermFreqMap(token,wAid)
    TermFreqMap[token][wAid]["i"] += 1

def getStringFromListofStrings(strlist):
    return ''.join(strlist)
        

        
# HERE STARTS THE WRITER PART.....
        
def getFOFromLine(fline):
    freq_obj = {}
    docs = fline.split(';')
    for doc in docs:
        parts = doc.split(':')
        if len(parts) != 2:
            continue
        did = parts[0]
        fstring = parts[1]
        freq_doc_obj = {}
        
        matches = re.finditer(freq_string_detection, fstring)
        if matches:
            for match in matches:
                title = 0
                title_match = match.group(2)
                if title_match != "":
                    title = int(title_match)
                body = 0
                body_match = match.group(3)
                if body_match != "":
                    body = int(body_match)
                cat = 0
                cat_match = match.group(4)
                if cat_match != "":
                    cat = int(cat_match)
                infob = 0
                infob_match = match.group(5)
                if infob_match != "":
                    infob = int(infob_match)
                freq_doc_obj["t"] = title #title
                freq_doc_obj["b"] = body #body
                freq_doc_obj["c"] = cat #cat
                freq_doc_obj["i"] = infob #infobox
        freq_obj[did] = freq_doc_obj
    return freq_obj

def getNewFO(word, ffo):
    if word in TermFreqMap:
        mfo = TermFreqMap[word]
        cfo = dict(mfo.items() + ffo.items())
        return cfo
    else:
        return ffo

def removeMFO(word):
    if word in TermFreqMap:
        del TermFreqMap[word]

linearWriterCount = 0
def linearWriter(outfile):
    global linearWriterCount
    
    with open("{0}.tmp{1}".format(outfile,linearWriterCount),"w") as temp_file:
        sorted_map = sorted(TermFreqMap.iteritems(), key=operator.itemgetter(0))
        for stuple in sorted_map:
            word = stuple[0]
            fo = stuple[1]
            toWrite = u"{0}={1}".format(word, getFOString(fo))
            temp_file.write(toWrite.encode('utf-8'))
        TermFreqMap.clear()
    print("tempfile {0} created :::: Article Count = {1}".format(linearWriterCount,articleCount))
    linearWriterCount += 1

def getSortedTuples(freq_map):
    sorted_tuples = sorted(freq_map.iteritems(), key=operator.itemgetter(1))
    return sorted_tuples
    
def linearMerger(outfile):
    global linearWriterCount
    linearMergerN(outfile, linearWriterCount)
    
def linearMergerN(outfile, lWCount):
    tmpFiles = {}
    tmpLines = {}
    tmpWords = {}
    completedFiles = 0
    with open(outfile+".tmp","w") as new_file:
        for i in xrange(0,lWCount):
            tmpFiles[i] = open("{0}.tmp{1}".format(outfile,i),"r")
            tmpLines[i] = tmpFiles[i].readline()
            tmpWords[i] = tmpLines[i].split("=")[0]
        #print "tmpFilesCount={0}".format(len(tmpFiles))
        #print "tmpLinesCount={0}".format(len(tmpLines))
        #print "tmpWordsCount={0}".format(len(tmpWords))
        while completedFiles < lWCount:
            #print "completedFiles = {0}".format(completedFiles)
            sortedT = getSortedTuples(tmpWords)
            pIndexWord = sortedT[0][1]
            toMergeCount = 0
            for stuple in sortedT:
                if stuple[1] == pIndexWord:
                    toMergeCount += 1
                else:
                    break
            top_sorted = sortedT[:toMergeCount]
            toMergeFO = []
            listOfIndexFileIds = []
            for stuple in top_sorted:
                ti = stuple[0]
                listOfIndexFileIds.append(ti)
                tline = tmpLines[ti]
                parts = tline.split('=')
                if len(parts) == 2:
                    #word = parts[0]
                    #tfo = getFOFromLine(parts[1])
                    #toMergeFO.append(tfo)
                    toMergeFO.append(parts[1].strip())
            #print len(toMergeFO)
            #freqObj = dict((k,v) for d in toMergeFO for (k,v) in d.items())
            #toWrite = u"" + pIndexWord + "=" + getFOString(freqObj)
            mergedStr = ''.join(toMergeFO)
            toWrite = u"" + pIndexWord + "=" + mergedStr + "\n"
            #print toWrite.encode('utf-8')
            new_file.write(toWrite.encode('utf-8'))
            for ti in listOfIndexFileIds:
                nextLine = tmpFiles[ti].readline()
                if nextLine == "":
                    completedFiles += 1
                    print "linear merger: completedFiles = {0}".format(completedFiles)
                    del tmpWords[ti]
                else:
                    tmpLines[ti] = nextLine
                    tmpWords[ti] = tmpLines[ti].split("=")[0]
        for f in tmpFiles:
            tmpFiles[f].close()
    #with open(outfile+".indexFileCount","w") as temp_file:
        #temp_file.write("{0}".format(lWCount))
      
def mergeWriter(outfile):
    with open(outfile+".tmp","w") as temp_file:
        with open(outfile,"r") as old_file:
            for line in old_file:
                parts = line.split('=')
                if len(parts) == 2:
                    word = parts[0]
                    ffo = getFOFromLine(parts[1])
                    cfo = getNewFO(word, ffo)
                    removeMFO(word)
                    toWrite = u"" + word + "=" + getFOString(cfo)
                    temp_file.write(toWrite.encode('utf-8'))
        for word in TermFreqMap:
            fo = TermFreqMap[word]
            toWrite = u"" + word + "=" + getFOString(fo)
            temp_file.write(toWrite.encode('utf-8'))
        TermFreqMap.clear()
    
    with open(outfile+".tmp","r") as temp_file:
        with open(outfile,"w") as new_file:
            for line in temp_file:
                new_file.write(line)
    
    with open(outfile+".tmp","w") as temp_file:
        print("tempfile copied and erased :::: Article Count = {0}".format(articleCount))

def getFOString(fo):
    toWrite = u""
    for did in fo:
        toWrite += did+":"
        fdo = fo[did]
        tfreq = fdo["t"]
        bfreq = fdo["b"]
        cfreq = fdo["c"]
        ifreq = fdo["i"]
        total_freq = tfreq+bfreq+cfreq+ifreq
        if total_freq != 0 :
            toWrite += "{0}".format(total_freq)
        toWrite += "t"
        if tfreq != 0 :
            toWrite += "{0}".format(tfreq)
        toWrite += "b"
        if bfreq != 0 :
            toWrite += "{0}".format(bfreq)
        toWrite += "c"
        if cfreq != 0 :
            toWrite += "{0}".format(cfreq)
        toWrite += "i"
        if ifreq != 0 :
            toWrite += "{0}".format(ifreq)
        toWrite += ";"
        #toWrite += "{0}t{1}b{2}c{3}i{4};".format(total_freq,tfreq,bfreq,cfreq,ifreq)
    toWrite += "\n"
    return toWrite
        
# def writeDocIdTitlesToFile(outfile):
#     with open(outfile+".titles","w") as titles_file:
#         for docid in DocumentIDTitleMap.keys():
#             titles_file.write("{0}={1}\n".format(docid,DocumentIDTitleMap[docid]))

def writeIndexPartFiles(outfile):
    wordCounter = 0
    indexCounter = 0
    indexWordMap = {}
    with open(outfile+".tmp","r") as uncompressed_file:
        #global wordCounter
        #global indexCounter
        #ipartF = open("{0}.index{1}".format(outfile,indexCounter),"w")
        ipartF = bz2.BZ2File("{0}.index{1}.bz2".format(outfile,indexCounter), 'wb', compresslevel=9)
        for line in uncompressed_file:
            wordCounter += 1
            if wordCounter == 1:
                parts = line.split("=")
                word = parts[0]
                indexWordMap[indexCounter] = word
            ipartF.write(line)
            if wordCounter >= 20000 :
                wordCounter = 0
                ipartF.close()
                indexCounter += 1
                ipartF = bz2.BZ2File("{0}.index{1}.bz2".format(outfile,indexCounter), 'wb', compresslevel=9)
        ipartF.close()
    #with open(outfile+".indexFileCount","w") as temp_file:
        #temp_file.write("{0}".format(indexCounter))
    with open(outfile+".indexWordMap","w") as temp_file:
        for index in indexWordMap.keys():
            temp_file.write("{0}={1}\n".format(index,indexWordMap[index]))

def writeTitlePartFiles(outfile):
    articleCounter = 0
    wordCounter = 0
    indexCounter = 0
    indexWordMap = {}
    with open(outfile+".titles","r") as uncompressed_file:
        #global wordCounter
        #global indexCounter
        #ipartF = open("{0}.index{1}".format(outfile,indexCounter),"w")
        ipartF = bz2.BZ2File("{0}.titles{1}.bz2".format(outfile,indexCounter), 'wb', compresslevel=9)
        for line in uncompressed_file:
            articleCounter +=1
            wordCounter += 1
            if wordCounter == 1:
                parts = line.split("=")
                word = parts[0]
                indexWordMap[indexCounter] = word
            ipartF.write(line)
            if wordCounter >= 20000 :
                wordCounter = 0
                ipartF.close()
                indexCounter += 1
                ipartF = bz2.BZ2File("{0}.titles{1}.bz2".format(outfile,indexCounter), 'wb', compresslevel=9)
        ipartF.close()
    #with open(outfile+".indexFileCount","w") as temp_file:
        #temp_file.write("{0}".format(indexCounter))
    with open(outfile+".indexTitleMap","w") as temp_file:
        for index in indexWordMap.keys():
            temp_file.write("{0}={1}\n".format(index,indexWordMap[index]))
    with open(outfile+".titlesCount","w") as temp_file:
        temp_file.write("{0}".format(articleCounter))
