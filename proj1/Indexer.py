
# Authors: Filipe Pires [85122] & João Alegria [85048]

import re
from abc import ABC, abstractmethod

# Abstract class for several types of index persistances


class Indexer(ABC):

    def __init__(self, fileParser, tokenizer):
        self.tokenizer = tokenizer
        self.fileParser = fileParser
        self.docs = fileParser.getContent()
        self.index = {}
        super().__init__()

    @abstractmethod
    def createIndex(self):
        print("Indexing...")

# Types of index persistance classes


class FileIndexer(Indexer):
    def createIndex(self):
        super().createIndex()
        for docID, docContent in self.docs.items():
            tokens = self.tokenizer.tokenize(docContent)
            for t in tokens:
                if t not in self.index:
                    self.index[t] = {docID: 1}
                elif docID not in self.index[t]:
                    self.index[t][docID] = 1
                else:
                    self.index[t][docID] += 1
        return self.index
