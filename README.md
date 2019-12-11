# RI - Projects 1,2 and 3 - Indexer and Ranked Retrieval

This project was developed under the discipline of Information Retrieval.

CreateIndex.py is the Python program developed for generating indexes for a given number of text corpus.
Its main porpuse is to read a corpus of data, process it by extracting the most important information, tokenizing the content, creating an index and persisting it.
It can also calculate the term frequency weights, the inverse document frequency and store the term positions.

QueryIndex.py is the program created to use generated indexes to answer queries.
Its main purpose is to tokenize a query, find the indexes that can answer it, rank the collected indexed documents and return the most relevant ones.
The program is capable of accepting relevance feedback to improve the results' precision, with the help of the Rocchio algorithm.

Both programs are capable of executing their jobs within a memory limitation. 
For more information on the code itself, all the documentation is acessible through docs/build/html/index.html.

### Prerequisites

1. Clone the repository. (https://github.com/joao-alegria/RI)
2. Change to the source directory, by running:
```
cd src
```
3. Install necessary libraries:
```
pip3 install -r requirements.txt
```

### Examples

For running the code, please do so inside the src directory. Access the input and the output files by accessing the respective directories.

#### Creating Indexes

An example for the Simple Tokenizer with output going to ../index and various input files located in ../input:

```
python3 CreateIndex.py -o ../index ../input
```

An example for the Simple Tokenizer with limit is(limited by 10000 documents):

```
python3 CreateIndex.py -l 10000 -o ../index ../input
```

An example for the Complex Tokenizer is:

```
python3 CreateIndex.py -t complex -l 100 -o ../index ../input
```

An example for the Complex Tokenizer  and the enabling of the weights calculation is:

```
python3 CreateIndex.py -w -t complex -l 100 -o ../index ../input
```

An example for the Complex Tokenizer  and the enabling of the weights calculation, position storage and memory limitation(500Mb) is:

```
python3 CreateIndex.py -r 0.5 -wp -t complex -l 100 -o ../index ../input
```

#### Querying Indexes

An example using the Simple Tokenizer and a memory limitation of 300Mb, a champions list of size 1000 with output going to ../results, queries located in ../queries.txt and index files in ../input, and returning only the top 10 results:

```
python3 QueryIndex.py -o ../results -t simple -r 0.3 -c 1000 -l 10 ../queries.txt ../input
```

An example using the same configuration but for an index with positions included and using the user feedback considering the top 5 documents retrieved and passing 1, 0.5 and 0.25 as Rocchio's alpha, beta and gamma parameters:

```
python3 QueryIndex.py -p -o ../results -t simple -r 0.3 -c 1000 -l 10 -f user -n 5 ../queries.txt ../input 1 0.5 0.25
```

An example using the same configuration as the first but using the Complex Tokenizer, using the pseudo feedback considering the top 20 documents retrieved and passing 1 and 0.5 as Rocchio's alpha and beta parameters:


```
python3 QueryIndex.py -o ../results -r 0.3 -c 1000 -l 10 -f pseudo -n 20 ../queries.txt ../input 1 0.5
```


## Authors

* **João Alegria** - joao.p@ua.pt
* **Filipe Pires** - filipesnetopires@ua.pt
