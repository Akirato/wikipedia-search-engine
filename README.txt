Wikipedia Search Engine:

Running:

Indexer:
./index.sh {input file} {output directory or file}
You can get a sample input dump from:
https://drive.google.com/file/d/0B_8j_IupNoCtXzZCUUI5c1Z6MUk/view?usp=sharing

Searcher:
./search.sh {index file} < {query file}

Query file:

- First Line has no. of queries(N)
- Next N lines have one query in each line
- Sample File query is present in the directory

Implementation:

- Implemented Tokenizer
- Category Detection
- Infobox Detection
- Link Detection
- Section and SubSection Detection
- Citation Detection
- Compressed Files for storing index
- Synsets for better search

Save Format for the words:
t: for title, b: for body, c: for category, i: for infobox

Incase of doubts:
Mail to nurendrachoudhary31@gmail.com with the subject Wikipedia Search Engine Queries

