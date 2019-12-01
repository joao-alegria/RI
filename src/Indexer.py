"""
.. module:: Indexer
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & Joao Alegria [85048]
"""
import re
import math
from decimal import *
import time
from abc import ABC, abstractmethod

getcontext().prec = 2


class Indexer(ABC):
    """
    Abstract class and interface for several types of index persistances implementations.

    :param fileParser: instance of the file parser used in the context to retrieve the data from the corpus
    :type fileParser: FileParser
    :param tokenizer: instance of the tokenizer used in the context to process the content of the corpus
    :type tokenizer: Tokenizer
    :param tokenizer: flag that indicates if it's necessary process positions
    :type tokenizer: boolean

    """

    def __init__(self, tokenizer, positions, weights, fileParser=None):
        """
        Class constructor
        """
        super().__init__()
        self.tokenizer = tokenizer
        self.docs = {}
        if fileParser:  # if fileParser != None
            fileParser.getContent()
            self.docs = fileParser.content
            fileParser.content = {}
        # when postions=True, index is only positions cuz the frequency is the position array length
        self.positions = positions
        self.weights = weights
        self.index = {}

    @abstractmethod
    def createIndex(self, content=None):
        """
        Function that creates the entire index by iterating over the corpus content and with the help of the tokenizer process and create the token index
        """
        if content:
            # overwriting docs with recent content passed to the function
            self.docs = content
        # print("Indexing...")

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.index = {}
        self.docs = {}


class FileIndexer(Indexer):
    """
    Implementation of a indexer dedicated to the first assignment.
    """

    def createIndex(self, content=None):
        """
        Implementation of the function defined by the abstract class.
        """
        super().createIndex(content)
        docID = list(content.keys())[0]
        docContent = list(content.values())[0]
        self.tokenizer.tokenize(docContent)
        tmpTC = {}
        for idx, t in enumerate(self.tokenizer.tokens):
            if t not in tmpTC:
                if self.positions:
                    tmpTC[t] = {docID: [1, [idx+1]]}
                else:
                    tmpTC[t] = {docID: [1, None]}
            elif docID not in tmpTC[t]:
                if self.positions:
                    tmpTC[t][docID] = [1, [idx+1]]
                else:
                    tmpTC[t][docID] = [1, None]
            else:
                tmpTC[t][docID][0] = tmpTC[t][docID][0]+1
                if self.positions:
                    tmpTC[t][docID][1].append(idx+1)
        if self.weights:
            norme = 0
            for term, docs in tmpTC.items():
                for doc, posts in docs.items():
                    posts[0] = 1+math.log10(posts[0])
                    norme += posts[0]**2
            for term, docs in tmpTC.items():
                for doc, posts in docs.items():
                    posts[0] = round(posts[0]/math.sqrt(norme), 2)

        for x in tmpTC:
            if x not in self.index:
                self.index[x] = tmpTC[x]
            else:
                self.index[x].update(**tmpTC[x])
        tmpTC = {}
        self.tokenizer.tokens = []

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.index = {}
        self.docs = {}
