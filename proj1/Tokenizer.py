
# Authors: Filipe Pires [85122] & João Alegria [85048]

import re
from abc import ABC, abstractmethod

# Abstract class for the several types of tokenizers

class Tokenizer(ABC): 
    def __init__(self, content):
        self.tokens = {}
        self.content = content
        super().__init__()

    @abstractmethod
    def tokenize(self):
        print("Processing...")
        pass

# Types of tokenizer classes

class SimpleTokenizer(Tokenizer):
    def tokenize(self):
        super().tokenize()
        for docID, docContent in self.content.items():
            normalizeData = re.sub("[^a-zA-Z]+", " ", docContent).lower()
            token = normalizeData.split(" ")
            for t in token:
                if t not in self.tokens:
                    self.tokens[t] = {docID: 1}
                else:
                    if docID not in self.tokens[t]:
                        self.tokens[t][docID] = 1
                    else:
                        self.tokens[t][docID] = self.tokens[t][docID]+1

class ComplexTokenizer(Tokenizer):
    def __init__(self, content):
        self.tokens = {}
        self.content = content

    def tokenize(self):
        super().tokenize()
        pass
    # to do ...
