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
        self.docID = 0
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
        self.docID = None
        self.limit = None


class GZipFileParser(FileParser):
    """
    Implementation of a file parser dedicated to the current context of RI. Processing of one or varios zip files.
    """

    def getContent(self):
        """
        Implementation of the function defined by the abstract class. Fetches the PMID and the TI.

        :returns: dictionary where the key is the sequencial ID of the document and the value the TI
        :rtype: map<str, str>

        """
        super().getContent()
        for filename in self.files:
            gz = gzip.open(filename, "rb")
            f = io.BufferedReader(gz)
            docContent = ""
            for line in f:
                line = line.decode("ISO-8859-1")
                if line.startswith("PMID"):
                    # docID = line[6:].strip()
                    self.docID += 1
                elif line.startswith("TI"):
                    docContent = line[6:].strip()
                elif line.startswith("PG"):
                    continue
                elif line.startswith("AD"):
                    self.content[str(self.docID)] = docContent
                    docContent = ""
                    # if limit is non positive, the program will process always 1 document
                    if self.docID >= self.limit:
                        break
                else:
                    if docContent != "":
                        docContent += " "+line[6:].strip()

            gz.close()

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.content = None
        self.files = None
        self.docID = None
        self.limit = None


class LimitedRamFileParser(FileParser):

    def __init__(self, files, limit):
        """
        Class constructor
        """
        super().__init__(files, limit)
        if self.files != []:
            self.gz = gzip.open(self.files.pop(0), "rb")
            self.f = io.BufferedReader(self.gz)

    def getContent(self):
        """
        Implementation of the function defined by the abstract class. Fetches the PMID and the TI.
        Differs from the implementation in GZipFileParser as it reads each line in the input file separately for memory usage reduction purposes.

        :returns: dictionary where the key is the sequential ID of the document and the value the TI
        :rtype: map<str, str>

        """
        docContent = ""

        for line in self.f:
            line = line.decode("ISO-8859-1")
            if line.startswith("PMID"):
                self.docID += 1
            elif line.startswith("TI"):
                docContent = line[6:].strip()
            elif line.startswith("PG"):
                    continue
            elif line.startswith("AD"):
                if self.docID >= self.limit:
                    self.gz.close()
                    return None
                if docContent == "":
                    break
                return {str(self.docID): docContent}
            else:
                if docContent != "":
                    docContent += " "+line[6:].strip()

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
        self.docID = None
        self.limit = None
        self.gz = None
        self.f = None
