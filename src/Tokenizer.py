"""
.. module:: Tokenizer
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & Joao Alegria [85048]
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
        self.tokens = []

    @abstractmethod
    def tokenize(self, porcessText):
        """
        Function that receives a string and tokenizes it, applying as many rules as implemented by the user.

        :param processText: text that will be tokenized
        :type processText: str

        """
        pass

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        pass

# Types of tokenizer classes


class SimpleTokenizer(Tokenizer):
    """
    Implementation of a tokenizer dedicated to the first assignment. This instance is the simple implementation, spliting by " " and eliminating all non-alphabetic characters.
    """

    def __init__(self):
        """
        Class constructor
        """
        super().__init__()
        # storing usefull regex
        self.regex1 = re.compile("[^a-z]+")
        self.regex2 = re.compile(" +")

    def tokenize(self, processText):
        """
        Implementation of the simple tokenization process.

        :param processText: text that will be tokenized
        :type processText: str

        """
        self.tokens = self.regex2.split(
            self.regex1.sub(" ", processText.lower()))
        self.tokens = [t for t in self.tokens if len(t) >= 3]

    def clearTokens(self):
        """
        Function that frees memory by emptying the tokens list.
        """
        self.tokens = []

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.tokens = []
        self.regex1 = None
        self.regex2 = None


class ComplexTokenizer(Tokenizer):
    """
    Implementation of a tokenizer dedicated to the current context of RI. This instance is the complex implementation porposed in 2.2. This version uses the PorterStemmer, eliminates stop words and implements some personal rules in relation to special characters(split by [ -_], keeps dates, emails, money, digits, ... ; eliminates majority of the punctuantion)
    """

    def __init__(self):
        """
        Class constructor
        """
        super().__init__()
        # loading PorterStemmer
        # self.stemmer = Stemmer.Stemmer('english')
        # fetching stopWords
        self.stopWords = []
        f = open("snowball_stopwords_EN.txt", "r")
        for line in f:
            self.stopWords.append(line.strip())
        # storing usefull regex
        self.regex0 = re.compile(" +")
        self.regex1 = re.compile(" +| *_+ *| *-+ *")
        self.regex2 = re.compile("([',;.:?!\(\)\[\]\{\}\"\|#])")
        self.regex3 = re.compile("[0-9]+(/)[0-9]+(/)[0-9]+")
        self.regex4 = re.compile("([',;.:?!\(\)\[\]\{\}/\"\|#])")
        self.regex5 = re.compile("^(-)?[0-9]")

    def tokenize(self, processText):
        """
        Implementation of the more complex tokenization process, with the use of a Stemmer and list of stop words.

        :param processText: text that will be tokenized
        :type processText: str

        """
        stemmer = Stemmer.Stemmer('english')
        self.tokens = []
        intermidiateTokens = [t for t in self.regex0.split(
            processText.lower()) if t not in self.stopWords]
        for t in intermidiateTokens:
            t = self.regex2.sub(" ", t) if self.regex3.search(
                t) else self.regex4.sub(" ", t)
            additionalWords = list(filter(None, self.regex1.split(t)))
            self.tokens += additionalWords
        self.tokens = [t for t in stemmer.stemWords(self.tokens)if len(t) > 2]
        stemmer = None

    def clearTokens(self):
        """
        Function that frees memory by emptying the tokens list.
        """
        self.tokens = []

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.regex1 = None
        self.regex2 = None
        self.regex3 = None
        self.regex4 = None
        self.regex5 = None
        self.tokens = []
        self.stopWords = []
