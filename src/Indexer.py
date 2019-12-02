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

    """

    def __init__(self, tokenizer, positions, fileParser=None):
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
        for docID, docContent in self.docs.items():
            self.tokenizer.tokenize(docContent)
            for idx, t in enumerate(self.tokenizer.tokens):
                if t not in self.index:
                    if self.positions:
                        self.index[t] = {docID: [idx+1]}
                    else:
                        self.index[t] = {docID: 1}
                elif docID not in self.index[t]:
                    if self.positions:
                        self.index[t][docID] = [idx+1]
                    else:
                        self.index[t][docID] = 1
                else:
                    if self.positions:
                        self.index[t][docID].append(idx+1)
                    else:
                        self.index[t][docID] += 1
            self.tokenizer.tokens = []

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.index = {}
        self.docs = {}
