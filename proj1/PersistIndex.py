
# Authors: Filipe Pires [85122] & João Alegria [85048]

import re
from abc import ABC, abstractmethod

# Abstract class for several types of index persistances


class PersistIndex(ABC):

    def __init__(self, filename, indexer):
        self.content = sorted(indexer.createIndex().items())
        self.filename = filename
        super().__init__()

    @abstractmethod
    def persist(self):
        print("Persisting...")

# Types of index persistance classes


class PersistCSV(PersistIndex):
    def persist(self):
        super().persist()
        f = open(self.filename, "w")
        currStr = ""
        for token, freqs in self.content:
            currStr += token
            for docID, count in freqs.items():
                currStr += ","+docID+":"+str(count)
            f.write(currStr+"\n")
            currStr = ""
        f.close()
