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

    def __init__(self, tokenizer, fileParser=None, positions=False):
        """
        Class constructor
        """
        super().__init__()
        self.tokenizer = tokenizer
        self.docs = {}
        self.numDocs = 1
        if fileParser:  # if fileParser != None
            fileParser.getContent()
            self.docs = fileParser.content
            fileParser.content = {}
            self.numDocs = fileParser.docID
        self.positions = positions
        # when postions=True, index is only positions cuz the frequency is the position array length
        self.index = {}

    def setNumDocs(self, numDocs):
        self.numDocs = numDocs

    @abstractmethod
    def createIndex(self, content=None):
        """
        Function that creates the entire index by iterating over the corpus content and with the help of the tokenizer process and create the token index
        """
        if content:
            # overwriting docs with recent content passed to the function
            self.docs = content
        # print("Indexing...")

    @classmethod
    def normalize(self):
        pass

    def clearVar(self):
        self.index = {}
        self.doc = {}


class FileIndexer(Indexer):
    """
    Implementation of a indexer dedicated to the current context of RI.
    """

    def createIndex(self, content=None):
        """
        Implementation of the function defined by the abstract class. Creates the index and returns it.

        :returns: dictionary where the key is the token and the value is a dictionary were the key is the docId and the value the number of occurences of that token in that document, i.e., the index
        :rtype: map<str, map<str, str>>

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
        self.index = {}
        self.docs = {}


class WeightedFileIndexer(FileIndexer):
    def createIndex(self, content=None):
        super().createIndex(content)

    # normaliza for 1 postingList -> operation called on persist index for more efficient use of time
    # post list->{docId:tf, docID:tf, ...} if no positions
    # or
    # post list->{docId:[2,3,5], docID:[5,3,2], ...} if positions
    def normalize(self, postingList):
        if self.positions:
            tfWeights = [1+math.log10(int(len(x)))
                         for x in postingList.values()]
        else:
            tfWeights = [1+math.log10(int(x)) for x in postingList.values()]
        norme = 1/math.sqrt(sum([math.pow(x, 2) for x in tfWeights]))
        tfWeights = [round(x*norme, 2) for x in tfWeights]
        return (round(math.log10(self.numDocs/len(tfWeights)), 2), tfWeights)

    def clearVar(self):
        self.index = {}
        self.docs = {}
