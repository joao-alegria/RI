"""
.. module:: FileParser
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & João Alegria [85048]
"""

import re
from abc import ABC, abstractmethod
import gzip
import io


class FileParser(ABC):
    """
    Abstract class that serves as template and interface for future instances and implementations.

    :param files: list of file names to be processed
    :type name: list<str>
    :param limit: limit number of documents to have in consideration, None if no limit
    :type limit: int

    """

    def __init__(self, files, limit):
        """
        Class constructor
        """
        self.content = {}
        self.files = files
        self.limit = limit

    @abstractmethod
    def getContent(self):
        """
        Function that processes the files passed to the object during it's creation.
        """
        print("Reading...")
        pass


class GZipFileParser(FileParser):
    """
    Implementation of a file parser dedicated to the current context of RI. Processing of one or varios zip files.
    """

    def getContent(self):
        """
        Implementation of the function defined by the abstract class. Fetches the PMID and the TI.

        :returns: dictionary where the key is the PMID of the document and the value the TI
        :rtype: map<str, str>

        """
        super().getContent()
        docID = 0
        # if the limit is None it means that the entirity of the corpus must be read, all the files
        if self.limit == None:
            for filename in self.files:
                gz = gzip.open(filename, "rb")
                f = io.BufferedReader(gz)
                docContent = ""
                for line in f:
                    line = line.decode("ISO-8859-1")
                    if line.startswith("PMID"):
                        # docID = line[6:].strip()
                        docID += 1
                    elif line.startswith("TI"):
                        docContent = line[6:].strip()
                    elif line.startswith("PG"):
                        self.content[str(docID)] = docContent
                        docContent = ""
                    else:
                        if docContent != "":
                            docContent += " "+line[6:].strip()

                gz.close()
        else:
            # if limit is defined the program will only process until the number of documents is reached
            numDocs = 0
            for filename in self.files:
                gz = gzip.open(filename, "rb")
                f = io.BufferedReader(gz)
                docContent = ""
                for line in f:
                    line = line.decode("ISO-8859-1")
                    if line.startswith("PMID"):
                        # docID = line[6:].strip()
                        docID += 1
                    elif line.startswith("TI"):
                        docContent = line[6:].strip()
                    elif line.startswith("PG"):
                        self.content[str(docID)] = docContent
                        docContent = ""
                        numDocs += 1
                        # if limit is non positive, the program will process always 1 document
                        if numDocs >= self.limit:
                            break
                    else:
                        if docContent != "":
                            docContent += " "+line[6:].strip()

                gz.close()

        return self.content


class LimitedRamFileParser(FileParser):

    def __init__(self, files, limit):
        super().__init__(files, limit)
        self.numDocs = 0
        if files != []:
            self.gz = gzip.open(self.files.pop(0), "rb")
            self.f = io.BufferedReader(gz)

    def getContent(self):
        docID = 0
        docContent = ""
        for line in self.f:
            line = line.decode("ISO-8859-1")
            if line.startswith("PMID"):
                docID += 1
            elif line.startswith("TI"):
                docContent = line[6:].strip()
            elif line.startswith("PG"):
                numDocs += 1
                if numDocs >= self.limit:
                    return None
                return {str(docID): docContent}
            else:
                if docContent != "":
                    docContent += " "+line[6:].strip()

            self.gz.close()

        if files != []:
            self.gz = gzip.open(self.files.pop(0), "rb")
            self.f = io.BufferedReader(gz)
        else:
            return None
