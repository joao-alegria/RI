
# Authors: Filipe Pires [85122] & João Alegria [85048]

import re
from abc import ABC, abstractmethod
import Stemmer

# Abstract class for the several types of tokenizers


class Tokenizer(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def tokenize(self, porcessText):
        pass

# Types of tokenizer classes


class SimpleTokenizer(Tokenizer):
    def __init__(self):
        super().__init__()
        self.regex1 = re.compile("[^a-z]+")
        self.regex2 = re.compile(" +")

    def tokenize(self, processText):
        tokens = self.regex2.split(self.regex1.sub(" ", processText.lower()))
        return [t for t in tokens if len(t) >= 3]


class ComplexTokenizer(Tokenizer):
    def __init__(self):
        super().__init__()
        self.stemmer = Stemmer.Stemmer('english')
        self.stopWords = []
        f = open("snowball_stopwords_EN.txt", "r")
        for line in f:
            self.stopWords.append(line.strip())
        self.regex1 = re.compile(" +| *_+ *| *-+ *")
        self.regex2 = re.compile("([,;.:?!\(\)\[\]\{\}\"\|#])")
        self.regex3 = re.compile("[0-9]+(/)[0-9]+(/)[0-9]+")
        self.regex4 = re.compile("([,;.:?!\(\)\[\]\{\}/\"\|#])")
        self.regex5 = re.compile("^(-)?[0-9]")

    def tokenize(self, processText):
        intermidiateTokens = self.regex1.split(processText.lower())
        resultingTokens = []
        for t in intermidiateTokens:
            t = self.regex2.sub(" ", t) if self.regex3.search(
                t) else self.regex4.sub(" ", t)
            additionalWords = list(filter(None, self.regex1.split(t)))
            if len(additionalWords) == 0:
                continue
            resultingTokens += additionalWords

        return [t for t in self.stemmer.stemWords(resultingTokens) if t not in self.stopWords and len(t) > 2]
