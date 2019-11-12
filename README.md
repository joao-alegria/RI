# RI - Project1 - Indexer

This project was developed under the discipline of Information Retrieval.

Its main porpuse is to read a corpus of data, process it by extracting the most important information(PMID and TI, in this case), tokenizing the content, creating an index and persisting it.
The program is already capable of doing all of this within a memory limitation. The Indexer is also already capable of calculating the term frequency weights, the inverse document frequency as well as store the term positions.
For more information on the code itself all the documentation is acessible through docs/build/html/index.html.

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

## Authors

* **João Alegria** - joao.p@ua.pt
* **Filipe Pires** - filipesnetopires@ua.pt
