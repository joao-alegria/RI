
import os
import sys
import psutil
import gc
import getopt

import Tokenizer
import Searcher

inputFolder = "../index/"
inputFiles = os.listdir(inputFolder)
positionCalc = False
tokenizer = Tokenizer.ComplexTokenizer()
limit = 100
maximumRAM = None
feedback = None
N = [5]#,10,20]
k = 10000
rocchioWeights = []

for n in N:
    queriesFile = open("../queries.txt","r")
    pseudoFeedbackFile = open("../pseudoFeedback/"+str(n)+".txt", "w")
    userFeedbackFile = open("../userFeedback/"+str(n)+".txt", "w")

    for line in queriesFile:
        # process each query
        query = line.split("\t")
        searcher = Searcher.IndexSearcher(positionCalc, tokenizer, limit, inputFolder, maximumRAM, feedback, n, k, rocchioWeights)
        searcher.retrieveRequiredFiles(query[1])

        searcher.calculateScores()
        scores = sorted(searcher.scores.items(), key=lambda kv: kv[1], reverse=True)

        requiredFiles = []
        for term in searcher.tokenizer.tokens:
            for f in inputFiles:
                aux = f.split("_")
                if term > aux[0] and term < aux[1]:
                    if f not in requiredFiles:
                        requiredFiles.append(f)
                        break
        
        # pseudo feedback
        relevantDocs = []
        relevantSumDj = 0.0
        for element in scores[:n]:
            relevantDocs.append(str(element[0]))
        # irrelevantDocs = []
        # irrelevantSumDj = 0.0
        # for element in scores[n:]:
        #    irrelevantDocs.append(str(element[0]))

        for file in requiredFiles:
            f = open(inputFolder+file, "r")
            for l in f:
                if l.split(":")[0] in searcher.tokenizer.tokens:
                    content = l.strip().split(";")[1:]
                    for i in range(0,len(content)):
                        content[i] = content[i].split(":")
                        if content[i][0] in relevantDocs:
                            relevantSumDj += float(content[i][1])
                        # elif content[i][0] in irrelevantDocs:
                        #     irrelevantSumDj += float(content[i][1])
            f.close()
        relevantSumDj = round(relevantSumDj, 2)
        #irrelevantSumDj = round(irrelevantSumDj, 2)
        pseudoFeedbackFile.write(str(query[0]) + ":" + str(len(relevantDocs)) + ":" + str(relevantSumDj) + "\n") #+ ":" + str(len(irrelevantDocs)) + ":" + str(irrelevantSumDj) + "\n")

        # user feedback
        relevantDocs = []
        relevantSumDj = 0.0
        irrelevantDocs = []
        irrelevantSumDj = 0.0
        i=0
        for element in scores:
            contains = False
            goldStandardFile = open("../queries.relevance.txt", "r")
            for l in goldStandardFile:
                content = l.split("\t")
                if int(content[0])==int(query[0]): # if current line in gold standard regards current query
                    if int(content[1])==int(element[0]): # if current score element
                        relevantDocs.append(str(element[0]))
                        i += 1
                        contains = True
                        break
            if not contains:
                irrelevantDocs.append(str(element[0]))
                i += 1
            if i>=n:
                break

        for file in requiredFiles:
            f = open(inputFolder+file, "r")
            for l in f:
                if l.split(":")[0] in searcher.tokenizer.tokens:
                    content = l.strip().split(";")[1:]
                    for i in range(0,len(content)):
                        content[i] = content[i].split(":")
                        if content[i][0] in relevantDocs:
                            relevantSumDj += float(content[i][1])
                        elif content[i][0] in irrelevantDocs:
                            irrelevantSumDj += float(content[i][1])
            f.close()
        relevantSumDj = round(relevantSumDj, 2)
        irrelevantSumDj = round(irrelevantSumDj, 2)
        userFeedbackFile.write(str(query[0]) + ":" + str(len(relevantDocs)) + ":" + str(relevantSumDj) + ":" + str(len(irrelevantDocs)) + ":" + str(irrelevantSumDj) + "\n")

        # relevantDocs = ""
        # irrelevantDocs = ""
        # for element in scores[:n]:
        #     relevantDocs += str(element[0]) + ","
        # pseudoFeedbackFile.write(str(query[0]) + ":" + str(n) + ":" + relevantDocs + "\n")

        # relevantDocs = ""
        # irrelevantDocs = ""
        # i=0
        # for element in scores:
        #     contains = False
        #     goldStandardFile = open("../queries.relevance.txt", "r")
        #     for l in goldStandardFile:
        #         content = l.split("\t")
        #         if int(content[0])==int(query[0]): # if current line in gold standard regards current query
        #             if int(content[1])==int(element[0]): # if current score element
        #                 relevantDocs += str(element[0]) + ","
        #                 i += 1
        #                 contains = True
        #                 break
        #     if not contains:
        #         irrelevantDocs += str(element[0]) + ","
        #         i += 1
        #     if i>=n:
        #         break
        # userFeedbackFile.write(str(query[0]) + ":" + relevantDocs + ":" + irrelevantDocs + "\n")

    pseudoFeedbackFile.close()
    userFeedbackFile.close()

