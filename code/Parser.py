#!/usr/bin/python

import xml.sax as sax
import re
from StringIO import StringIO
from sys import argv

from shutil import copyfileobj
import bz2

import Indexer
from WikiSAXHandler import WikiContentHandler
import TokenStemmer

script, infile, outfile = argv

Indexer.doInit(outfile)

if infile.endswith(".bz2"):
    with bz2.BZ2File(infile, 'rb', compresslevel=9) as compressed_infile:
        sax.parse(compressed_infile, WikiContentHandler(outfile))
else:
    sax.parse(infile, WikiContentHandler(outfile))

Indexer.linearWriter(outfile)

Indexer.linearMerger(outfile)

Indexer.writeIndexPartFiles(outfile)

Indexer.writeTitlePartFiles(outfile)


