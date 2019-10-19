"""
.. module:: Indexer
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & João Alegria [85048]
"""
import re
import math
from decimal import *
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

    def __init__(self, fileParser, tokenizer):
        """
        Class constructor
        """
        self.tokenizer = tokenizer
        self.fileParser = fileParser
        self.docs = fileParser.getContent()
        self.index = {}
        super().__init__()

    @abstractmethod
    def createIndex(self):
        """
        Function that creates the entire index by iterating over the corpus content and with the help of the tokenizer process and create the token index
        """
        print("Indexing...")


class FileIndexer(Indexer):
    """
    Implementation of a indexer dedicated to the current context of RI.
    """

    def createIndex(self):
        """
        Implementation of the function defined by the abstract class. Creates the index and returns it.

        :returns: dictionary where the key is the token and the value is a dictionary were the key is the docId and the value the number of occurences of that token in that document, i.e., the index
        :rtype: map<str, map<str, str>>

        """
        super().createIndex()
        for docID, docContent in self.docs.items():
            tokens = self.tokenizer.tokenize(docContent)
            for t in tokens:
                if t not in self.index:
                    self.index[t] = {docID: 1}
                elif docID not in self.index[t]:
                    self.index[t][docID] = 1
                else:
                    self.index[t][docID] += 1
        return self.index


class WeightedFileIndexer(FileIndexer):
    def createIndex(self):
        super().createIndex()
        for token, postingList in self.index.items():
            for docID, tf in postingList.items():
                postingList[docID] = 1+math.log10(tf)
            vectorNorme = math.sqrt(
                sum([math.pow(x, 2) for x in postingList.values()]))
            for docID, tf in postingList.items():
                postingList[docID] = Decimal(
                    postingList[docID])/Decimal(vectorNorme)


class WeightedFilePositionIndexer(Indexer):
    def createIndex(self):
        super().createIndex()
        positionIndex = {}
        for docID, docContent in self.docs.items():
            tokens = self.tokenizer.tokenize(docContent)
            for idx, t in enumerate(tokens):
                if t not in self.index:
                    self.index[t] = {docID: 1}
                    positionIndex[t] = {docID: [idx+1]}
                elif docID not in self.index[t]:
                    self.index[t][docID] = 1
                    positionIndex[t][docID] = [idx+1]
                else:
                    self.index[t][docID] += 1
                    positionIndex[t][docID].append(idx+1)

        for token, postingList in self.index.items():
            for docID, tf in postingList.items():
                postingList[docID] = 1+math.log10(tf)
            vectorNorme = math.sqrt(
                sum([math.pow(x, 2) for x in postingList.values()]))
            for docID, tf in postingList.items():
                postingList[docID] = Decimal(
                    postingList[docID])/Decimal(vectorNorme)

        return self.index, positionIndex
