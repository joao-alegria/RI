
# Authors: Filipe Pires [85122] & João Alegria [85048]

import re
from abc import ABC, abstractmethod
import gzip
import io

# Abstract class for the several types of FileParser


class FileParser(ABC):
    def __init__(self, files, limit):
        self.content = {}
        self.files = files
        self.limit = limit

    @abstractmethod
    def getContent(self):
        print("Reading...")
        pass

# Class responsible for parsing input files


class GZipFileParser(FileParser):
    def getContent(self):
        super().getContent()
        if self.limit == None:
            for filename in self.files:
                gz = gzip.open(filename, "rb")
                f = io.BufferedReader(gz)
                docContent = ""
                for line in f:
                    line = line.decode("ISO-8859-1")
                    if line.startswith("PMID"):
                        docID = line[6:].strip()
                    elif line.startswith("TI"):
                        docContent = line[6:].strip()
                    elif line.startswith("      "):
                        if docContent != "":
                            docContent += " "+line[6:].strip()
                    else:
                        if docContent != "":
                            self.content[docID] = docContent
                            docContent = ""

                gz.close()
        else:
            numDocs = 0
            for filename in self.files:
                gz = gzip.open(filename, "rb")
                f = io.BufferedReader(gz)
                docContent = ""
                for line in f:
                    line = line.decode("ISO-8859-1")
                    if line.startswith("PMID"):
                        docID = line[6:].strip()
                    elif line.startswith("TI"):
                        docContent = line[6:].strip()
                    elif line.startswith("      "):
                        if docContent != "":
                            docContent += " "+line[6:].strip()
                    else:
                        if docContent != "":
                            self.content[docID] = docContent
                            docContent = ""
                            numDocs += 1
                            if numDocs >= self.limit:
                                break

                gz.close()

        return self.content
