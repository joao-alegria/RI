"""
.. module:: Tokenizer
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & João Alegria [85048]
"""
import re
from abc import ABC, abstractmethod
import Stemmer


class Tokenizer(ABC):
    """
    Abstract class and interface for the various possible implementations of tokenizers
    """

    def __init__(self):
        """
        Class constructor
        """
        super().__init__()

    @abstractmethod
    def tokenize(self, porcessText):
        """
        Function that receives a string and tokenizes it, applying as many rules as implemented by the user.

        :param processText: text that will be tokenized
        :type processText: str

        """
        pass

# Types of tokenizer classes


class SimpleTokenizer(Tokenizer):
    """
    Implementation of a tokenizer dedicated to the current context of RI. This instance is the simple implementation porposed in 2.1, spliting by " " and eliminating all non-alphabetic characters.
    """

    def __init__(self):
        super().__init__()
        # storing usefull regex
        self.regex1 = re.compile("[^a-z]+")
        self.regex2 = re.compile(" +")

    def tokenize(self, processText):
        tokens = self.regex2.split(self.regex1.sub(" ", processText.lower()))
        return [t for t in tokens if len(t) >= 3]


class ComplexTokenizer(Tokenizer):
    """
    Implementation of a tokenizer dedicated to the current context of RI. This instance is the complex implementation porposed in 2.2. This version uses the PorterStemmer, eliminates stop words and implements some personal rules in relation to special characters(split by [ -_], keeps dates, emails, money, digits, ... ; eliminates majority of the punctuantion)
    """

    def __init__(self):
        super().__init__()
        # loading PorterStemmer
        self.stemmer = Stemmer.Stemmer('english')
        # fetching stopWords
        self.stopWords = []
        f = open("snowball_stopwords_EN.txt", "r")
        for line in f:
            self.stopWords.append(line.strip())
        # storing usefull regex
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
