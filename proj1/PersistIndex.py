
# Authors: Filipe Pires [85122] & João Alegria [85048]

import re
from abc import ABC, abstractmethod

# Abstract class for several types of index persistances

class PersistIndex(ABC): 

    def __init__(self, content, filename):
        self.content = content
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
        for token, freqs in self.content.items():
            f.write(token)
            for docID, count in freqs.items():
                f.write(",")
                f.write(docID+":"+str(count))
            f.write("\n")
        f.close()
