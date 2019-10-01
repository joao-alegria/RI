
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
        numDocs = 0
        for filename in self.files:
            f = gzip.open(filename, "r")
            docContent = ""
            chunk = f.read(2000000000).decode("ISO-8859-1")
            while chunk != "":
                for line in chunk.split("\n"):
                    if re.match("^PMID( )*-", line):
                        docID = re.sub("^PMID( )*-( )*", "", line)
                    elif re.match("^TI( )*-", line):
                        docContent = re.sub(
                            "^TI( )*-( )*", "", line)
                    elif re.match("^PG( )*-", line):
                        self.content[docID] = docContent
                        docContent = ""
                        # numDocs += 1
                        # if self.limit != None and numDocs >= self.limit:
                        #     break
                        #print(numDocs, end="\r", flush=True)
                    elif docContent != "":
                        docContent += " "+re.sub("^( )+", "", line).strip()
                chunk = f.read(2000000000).decode("ISO-8859-1")
            f.close()

        return self.content
