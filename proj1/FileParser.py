
# Authors: Filipe Pires [85122] & João Alegria [85048]

import re
from abc import ABC, abstractmethod
import gzip

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
        for filename in self.files:
            f = gzip.open("2004_TREC_ASCII_MEDLINE_1.gz", "r")
            docID = ""
            docContent = ""

            if self.limit == None:
                for line in f:
                    try:
                        line = f.readline()
                    except Exception as e:
                        print(e)
                        docID = ""
                        docContent = ""
                        continue
                    if line == "":
                        break
                    splittedLine = line.decode(
                        "ISO-8859-1").strip().split("-")
                    label = splittedLine[0].strip()
                    if(len(splittedLine) >= 2):
                        content = splittedLine[1].strip()
                        if label == "PMID":
                            docID = content
                        elif label == "TI":
                            if docID != "":
                                docContent = content
                        else:
                            if docContent != "":  # detects the end of titles with 2+ lines
                                self.content[docID] = docContent
                                docID = ""
                                docContent = ""
                            else:
                                continue
                    else:
                        if docContent != "":
                            docContent += " "+label  # in this case label=title content
                f.close()
            else:
                for x in range(self.limit):
                    try:
                        line = f.readline()
                    except Exception as e:
                        print(e)
                        docID = ""
                        docContent = ""
                        continue
                    if line == "":
                        break
                    splittedLine = line.decode(
                        "ISO-8859-1").strip().split("-")
                    label = splittedLine[0].strip()
                    if(len(splittedLine) >= 2):
                        content = splittedLine[1].strip()
                        if label == "PMID":
                            docID = content
                        elif label == "TI":
                            if docID != "":
                                docContent = content
                        else:
                            if docContent != "":
                                # to do: consider that the file already exists and that we are reading it a second time
                                # or leave it this way since we do not allow duplications
                                self.content[docID] = docContent
                                docID = ""
                                docContent = ""
                            else:
                                continue
                    else:
                        if docContent != "":
                            docContent += " "+label
                f.close()

        return self.content
