"""
.. module:: PersistIndex
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & João Alegria [85048]
"""
import re
import io
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
        super().__init__()
        if indexer:
            indexer.createIndex()
            indexer.normalizeIndex()
            self.index = indexer.index
            self.positionIndex = indexer.positionIndex
        self.filename = filename

    @abstractmethod
    def persist(self, index=None, positionIndex=None, overrideFile=None):
        """
        Function that effectively persists the data.
        """
        if index:
            self.index = index
        if positionIndex:
            self.positionIndex = positionIndex
        if overrideFile:
            self.currentFilename = overrideFile
        else:
            self.currentFilename = self.filename
        if self.index == {}:
            return False
        print("Persisting...")

    def clearVar(self):
        self.index = {}
        self.positionIndex = {}


class PersistCSV(PersistIndex):
    """
    Implementation of the index persister dedicated to the current context of RI. This instance persists the index in a text file, following a csv-like format, such as:
        token1,docID1:numOcur,docID2:numOcur,...
        token2,docID1:numOcur,docID2:numOcur,...
    """

    def persist(self, index=None, positionIndex=None, overrideFile=None):
        super().persist(index, positionIndex, overrideFile)
        if self.index == {}:
            return False
        self.index = sorted(self.index.items())
        f = open(self.currentFilename, "w")
        currStr = ""
        for token, freqs in self.index:
            currStr += token
            for docID, count in freqs.items():
                currStr += ","+docID+":"+str(count)
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()
        self.index = {}
        self.positionIndex = {}
        return True

    def clearVar(self):
        self.index = {}
        self.positionIndex = {}


class PersistCSVWeighted(PersistIndex):
    def persist(self, index=None, positionIndex=None, overrideFile=None):
        super().persist(index, positionIndex, overrideFile)
        if self.index == {}:
            return False
        self.index = sorted(self.index.items())
        f = open(self.currentFilename, "w")
        currStr = ""
        for token, freqs in self.index:
            currStr += token+":1"
            for docID, count in freqs.items():
                currStr += ";"+docID+":"+str(count)
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()
        self.index = {}
        self.positionIndex = {}
        return True

    def clearVar(self):
        self.index = {}
        self.positionIndex = {}


class PersistCSVPosition(PersistIndex):
    def persist(self, index=None, positionIndex=None, overrideFile=None):
        super().persist(index, positionIndex, overrideFile)
        if self.index == {}:
            return False
        self.index = sorted(self.index.items())
        f = open(self.currentFilename, "w")
        currStr = ""
        for token, freqs in self.index:
            currStr += token
            for docID, count in freqs.items():
                currStr += ";"+docID+":" + \
                    str(count)+":"+str(self.positionIndex[token][docID][0])
                for pos in self.positionIndex[token][docID][1:]:
                    currStr += ","+str(pos)
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()
        self.index = {}
        self.positionIndex = {}
        return True

    def clearVar(self):
        self.index = {}
        self.positionIndex = {}


class PersistCSVWeightedPosition(PersistIndex):

    def persist(self, index=None, positionIndex=None, overrideFile=None):
        super().persist(index, positionIndex, overrideFile)
        if self.index == {}:
            return False
        self.index = sorted(self.index.items())
        f = open(self.currentFilename, "w")
        currStr = ""
        for token, freqs in self.index:
            currStr += token+":1"
            for docID, count in freqs.items():
                currStr += ";"+docID+":" + \
                    str(count)+":"+str(self.positionIndex[token][docID][0])
                for pos in self.positionIndex[token][docID][1:]:
                    currStr += ","+str(pos)
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()
        self.index = {}
        self.positionIndex = {}
        return True

    def clearVar(self):
        self.index = {}
        self.positionIndex = {}
