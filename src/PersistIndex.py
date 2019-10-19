"""
.. module:: PersistIndex
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & João Alegria [85048]
"""
import re
from abc import ABC, abstractmethod


class PersistIndex(ABC):
    """
    Abstract class and interface for several types of index persistance implementations, due to file format or processing method

    :param filename: name of the file were the information should be written too
    :type filename: str
    :param indexer: instance of the indexer used in the context to create the corpus index
    :type indexer: Indexer
    """

    def __init__(self, filename, indexer=None):
        """
        Class constructor
        """
        if indexer:
            self.content = indexer.createIndex()
        self.filename = filename
        super().__init__()

    @abstractmethod
    def persist(self, content=None):
        """
        Function that effectively persists the data.
        """
        if content:
            self.content = content
        print("Persisting...")


class PersistCSV(PersistIndex):
    """
    Implementation of the index persister dedicated to the current context of RI. This instance persists the index in a text file, following a csv-like format, such as:
        token1,docID1:numOcur,docID2:numOcur,...
        token2,docID1:numOcur,docID2:numOcur,...
    """

   def persist(self, content=None):
        super().persist()
        self.content = sorted(self.content.items())
        f = open(self.filename, "w")
        currStr = ""
        for token, freqs in self.content:
            currStr += token
            for docID, count in freqs.items():
                currStr += ","+docID+":"+str(count)
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()


class PersistCSVWeighted(PersistIndex):
    def persist(self, content=None):
        super().persist()
        self.content = sorted(self.content.items())
        f = open(self.filename, "w")
        currStr = ""
        for token, freqs in self.content:
            currStr += token+":1"
            for docID, count in freqs.items():
                currStr += ";"+docID+":"+str(count)
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()


class PersistCSVWeightedPosition(PersistIndex):
    def persist(self, content=None):
        super().persist()
        index, positions = self.content
        index = sorted(index.items())
        f = open(self.filename, "w")
        currStr = ""
        for token, freqs in index:
            currStr += token+":1"
            for docID, count in freqs.items():
                currStr += ";"+docID+":" + \
                    str(count)+":"+str(positions[token][docID][0])
                for pos in positions[token][docID][1:]:
                    currStr += ","+str(pos)
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()
