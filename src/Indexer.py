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
        """
        Setter function for the variable numDocs.

        :param: numDocs: number of documents to be processed.
        :type numDocs: int
        """
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
        """
        Function that normalizes the index according to a set of rules. Used in the second assignment.
        """
        pass

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.index = {}
        self.doc = {}


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


class WeightedFileIndexer(FileIndexer):
    """
    Specialization of the FileIndexer class dedicated to the second assignment.
    """

    def createIndex(self, content=None):
        """
        Creates the index the same way as its parent class.

        """
        super().createIndex(content)

    # normalize for 1 postingList -> operation called on persist index for more efficient use of time
    # post list->{docId:tf, docID:tf, ...} if no positions
    # or
    # post list->{docId:[2,3,5], docID:[5,3,2], ...} if positions
    def normalize(self, postingList):
        """
        Implementation of the function defined by the abstract class. Normalizes the postingList passed by calculating the term weights and the inverse term frequency.
        """
        if self.positions:
            tfWeights = [1+math.log10(int(len(x)))
                         for x in postingList.values()]
        else:
            tfWeights = [1+math.log10(int(x)) for x in postingList.values()]
        norme = 1/math.sqrt(sum([math.pow(x, 2) for x in tfWeights]))
        tfWeights = [round(x*norme, 2) for x in tfWeights]
        return (round(math.log10(self.numDocs/len(tfWeights)), 2), tfWeights)

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.index = {}
        self.docs = {}
