
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
    def __init__(self, content=None, fileParser=None):
        super().__init__(content, fileParser)
        self.stemmer = Stemmer.Stemmer('english')
        self.stopWords = []
        f = open("snowball_stopwords_EN.txt", "r")
        for line in f:
            self.stopWords.append(line.strip())
        self.regex0 = re.compile(" +| *_+ *")
        self.regex1 = re.compile(" +| *_+ *| *-+ *")
        self.regex2 = re.compile("([,;.:?!\(\)\[\]\{\}\"\|#])")
        self.regex3 = re.compile("[0-9]+(/|-)[0-9]+(/|-)[0-9]+")
        self.regex4 = re.compile("([,;.:?!\(\)\[\]\{\}/\"\|#])")
        self.regex5 = re.compile("^(-)?[0-9]")

    def tokenize(self, processText):
        intermidiateTokens = self.regex0.split(processText.lower())
        resultingTokens = []
        idx = 0
        while idx < len(intermidiateTokens):
            t = tokens.pop()
            t = self.regex2.sub(" ", t) if self.regex3.search(
                t) else self.regex4.sub(" ", t)
            additionalWords = list(filter(None, self.regex0.split(t))) if self.regex5.match(
                t) else list(filter(None, self.regex1.split(t)))
            if len(additionalWords) == 0:
                idx += 1
                continue
            resultingTokens += additionalWords
            idx += 1

        return self.stemmer.stemWords(resultingtokens)
