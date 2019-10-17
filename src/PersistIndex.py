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

    def __init__(self, filename, indexer):
        """
        Class constructor
        """
        self.content = sorted(indexer.createIndex().items())
        self.filename = filename
        super().__init__()

    @abstractmethod
    def persist(self):
        """
        Function that effectively persists the data.
        """
        print("Persisting...")


class PersistCSV(PersistIndex):
    """
    Implementation of the index persister dedicated to the current context of RI. This instance persists the index in a text file, following a csv-like format, such as:
        token1,docID1:numOcur,docID2:numOcur,...
        token2,docID1:numOcur,docID2:numOcur,...
    """

    def persist(self):
        super().persist()
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
