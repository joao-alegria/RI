"""
.. module:: FileParser
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & Joao Alegria [85048]
"""

import re
from abc import ABC, abstractmethod
import gzip
import io
import os


class FileParser(ABC):
    """
    Abstract class that serves as template and interface for future instances and implementations.

    :param inputFolder: name of the folder containing the files to be used as input
    :type inputFolder: str
    :param limit: limit number of documents to have in consideration, None if no limit
    :type limit: int

    """

    def __init__(self, inputFolder, limit=None):
        """
        Class constructor
        """
        super().__init__()
        self.content = {}
        self.files = []
        inputFiles = os.listdir(inputFolder)
        for f in inputFiles:
            self.files.append(inputFolder+"/"+f)
        self.numDocs = 0
        if limit == None:
            # a number bigger than all the rest
            self.limit = float('inf')
        else:
            self.limit = limit

    @abstractmethod
    def getContent(self):
        """
        Function that processes the files passed to the object during it's creation.
        """
        print("Reading...")
        pass

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.content = None
        self.files = None
        self.numDocs = None
        self.limit = None


class LimitedRamFileParser(FileParser):

    def __init__(self, inputFolder, limit):
        """
        Class constructor
        """
        super().__init__(inputFolder, limit)
        if self.files != []:
            self.gz = gzip.open(self.files.pop(0), "rb")
            self.f = io.BufferedReader(self.gz)

    def getContent(self):
        """
        Implementation of the function defined by the abstract class. Fetches the PMID, the TI and the AB.
        This implementation processes one document at the time. 
        This implementation opts by concatenating the TI with the AB field.

        :returns: dictionary where the key is the sequential ID of the document and the value the TI
        :rtype: map<str, str>

        """
        docContent = ""
        docID = ""
        add = False
        for line in self.f:
            line = line.decode("ISO-8859-1")
            if line.startswith("PMID"):
                docID = line[6:].strip()
            elif line.startswith("TI"):
                docContent += line[6:].strip()+" "
                add = True
            elif line.startswith("AB"):
                docContent += line[6:].strip()+" "
                add = True
            elif line.startswith("  "):
                if add:
                    docContent += line[6:].strip()+" "
            elif line == "\n":
                self.numDocs += 1
                if self.numDocs >= self.limit:
                    self.gz.close()
                    return None
                if docContent == "":
                    continue
                return {str(docID): docContent}
            else:
                add = False
                continue
        self.gz.close()

        if self.files != []:
            self.gz = gzip.open(self.files.pop(0), "rb")
            self.f = io.BufferedReader(self.gz)
            return self.getContent()
        else:
            return None

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.content = None
        self.files = None
        self.numDocs = None
        self.limit = None
        self.gz = None
        self.f = None
