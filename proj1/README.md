# RI - Project1 - Indexer

This project was developed under the discipline of Information Retrieval.

Its main porpuse is to read a corpus of data, without a size limitation, process it by extracting the most important information(PMID and TI, in this case), tokenizing the content, creating an index and persisting it.

### Prerequisites

1. Clone the repository.
2. Change to the source directory, by running:
```
cd proj1/src
```
3. Install necessary libraries:
```
pip3 install -r requirements.txt
```

### Examples

For running the code, please do so inside the src directory. Access the input and the output files by accessing the respective directories.

An example for the Simple Tokenizer with output file and various input files is:

```
python3 CreateIndex.py -o ../output/output.txt ../input/2004_TREC_ASCII_MEDLINE_1.gz ../input/2004_TREC_ASCII_MEDLINE_2.gz
```

An example for the Simple Tokenizer with output file, various input files and a limit is:

```
python3 CreateIndex.py -o ../output/output.txt -t simple -l 100 ../input/2004_TREC_ASCII_MEDLINE_1.gz ../input/2004_TREC_ASCII_MEDLINE_2.gz
```

An example for the Complex Tokenizer with output file, various input files and a limit is:

```
python3 CreateIndex.py -o ../output/output.txt -t complex -l 100 ../input/2004_TREC_ASCII_MEDLINE_1.gz ../input/2004_TREC_ASCII_MEDLINE_2.gz
```


## Authors

* **João Alegria** - joao.p@ua.pt
* **Filipe Pires** - filipesnetopires@ua.pt
