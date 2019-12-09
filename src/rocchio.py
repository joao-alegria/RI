
import os
import sys
import psutil
import gc
import getopt

import Tokenizer
import Searcher


positionCalc = False
tokenizer = Tokenizer.ComplexTokenizer()
limit = 100
inputFolder = "../index"
maximumRAM = None
feedback = None
N = [5,10,20]
k = 100
rocchioWeights = []

for n in N:
    queriesFile = open("../small_queries.txt","r")
    pseudoFeedbackFile = open("../pseudoFeedback/"+str(n)+".txt", "w")
    userFeedbackFile = open("../userFeedback/"+str(n)+".txt", "w")

    for line in queriesFile:
        # process each query
        query = line.split("\t")
        searcher = Searcher.IndexSearcher(positionCalc, tokenizer, limit, inputFolder, maximumRAM, feedback, n, k, rocchioWeights)
        searcher.retrieveRequiredFiles(query[1])
        while not searcher.calculateScores():
            pass
        Scores = sorted(searcher.Scores.items(), key=lambda kv: kv[1], reverse=True)

        # prepare doc relevance for pseudo feedback
        relevantDocs = ""
        irrelevantDocs = ""
        for i,element in enumerate(Scores):
            if i<n:
                relevantDocs += str(element[0]) + ","
        pseudoFeedbackFile.write(str(query[0]) + ":" + relevantDocs + "\n")

        # prepare doc relevance for user feedback
        relevantDocs = ""
        irrelevantDocs = ""
        
        i=0
        for element in Scores:
            contains = False
            goldStandardFile = open("../queries.relevance.txt", "r")
            for l in goldStandardFile:
                content = l.split("\t")
                if int(content[0])==int(query[0]): # if current line in gold standard regards current query
                    if int(content[1])==int(element[0]): # if current score element
                        relevantDocs += str(element[0]) + ","
                        i += 1
                        contains = True
                        break
            if not contains:
                irrelevantDocs += str(element[0]) + ","
                i += 1
            if i>=n:
                break
        userFeedbackFile.write(str(query[0]) + ":" + relevantDocs + ":" + irrelevantDocs + "\n")

    pseudoFeedbackFile.close()
    userFeedbackFile.close()

