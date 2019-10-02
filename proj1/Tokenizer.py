
# Authors: Filipe Pires [85122] & João Alegria [85048]

import re
from abc import ABC, abstractmethod
import Stemmer

# Abstract class for the several types of tokenizers


class Tokenizer(ABC):
    def __init__(self, content=None, fileParser=None):
        super().__init__()
        self.tokens = {}
        if not fileParser:
            self.content = content
        else:
            self.content = fileParser.getContent()

    @abstractmethod
    def tokenize(self):
        print("Processing...")
        pass

# Types of tokenizer classes


class SimpleTokenizer(Tokenizer):
    def tokenize(self):
        super().tokenize()
        for docID, docContent in self.content.items():
            token = re.sub(
                "[^a-z]+", " ", docContent.lower()).split()
            for t in token:
                if len(t) >= 3:
                    if t not in self.tokens:
                        self.tokens[t] = {docID: 1}
                    elif docID not in self.tokens[t]:
                        self.tokens[t][docID] = 1
                    else:
                        self.tokens[t][docID] = self.tokens[t][docID]+1
        return self.tokens


class ComplexTokenizer(Tokenizer):
    def __init__(self, content=None, fileParser=None):
        super().__init__(content, fileParser)
        self.stemmer = Stemmer.Stemmer('english')
        self.stopWords = []
        f = open("snowball_stopwords_EN.txt", "r")
        for line in f:
            self.stopWords.append(line.strip())

    def tokenize(self):
        super().tokenize()
        for docID, docContent in self.content.items():
            normalizeData = docContent.lower()
            token = re.split(" +", normalizeData)
            stemmedTokens = self.stemmer.stemWords(token)
            for t in stemmedTokens:
                t = t if re.match(
                    "[0-9]*(/|-)[0-9]*(/|-)[0-9]*", t) else re.sub(
                    "([,;.:?!\(\)\[\]\{\}/\"\|])", " ", t)
                additionalWords = re.split(" +|_+|-+", t)
                t = additionalWords[0]
                tokens = stemmedTokens + \
                    self.stemmer.stemWords(additionalWords[1:])
                if t not in self.stopWords:
                    if t not in self.tokens:
                        self.tokens[t] = {docID: 1}
                    elif docID not in self.tokens[t]:
                        self.tokens[t][docID] = 1
                    else:
                        self.tokens[t][docID] = self.tokens[t][docID]+1
        return self.tokens
