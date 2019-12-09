import sys
import os
import math


def loadQueryTruth(queryTruth):
    f = open(queryTruth, "r")

    queryResults = {}

    for line in f:
        processedLine = line.strip().split("\t")
        if processedLine[0] not in queryResults:
            queryResults[processedLine[0]] = [processedLine[1:]]
        else:
            queryResults[processedLine[0]].append(processedLine[1:])
    return queryResults


def loadOurResults(ourQuery):
    f = open(ourQuery, "r")

    ourResults = []

    for line in f:
        processedLine = line.strip().split(",")[0]
        if processedLine not in ourResults:
            ourResults.append(processedLine)

    return ourResults


def calculateP_R_F1(truth, prediction):
    tp = 0
    fp = 0
    fn = 0
    for p in prediction:
        if p in truth:
            tp += 1
        else:
            fp += 1
    for t in truth:
        fn += 1

    P = tp/(tp+fp) if (tp+fp) != 0 else 0.0
    R = tp/(tp+fn) if (tp+fn) != 0 else 0.0
    F1 = (2*R*P)/(R+P) if (R+P) != 0 else 0.0

    return P, R, F1


def calculateMAP(meanAPs):
    return sum(meanAPs)/len(meanAPs)


def calculateMPatK(truth, prediction, k):
    pSum = 0
    count = 0
    for idx, p in enumerate(prediction[:k]):
        if p in truth:
            count += 1
            P, R, F1 = calculateP_R_F1(truth, prediction[:idx])
            pSum += P
    return pSum/count if count != 0 else 0.0


def calculateNDCG(truth, prediction):
    ideal = 0
    actual = 0
    predictionRelevance = []
    for p in prediction:
        for t, tv in truth:
            if p == t:
                predictionRelevance.append(tv)
            else:
                predictionRelevance.append(0)

    idealRelevance = [x[1] for x in truth]
    idealRelevance.sort(reverse=True)
    for idx in range(max(len(predictionRelevance), len(idealRelevance))):
        denominator = math.log2(idx+1) if idx+1 > 1 else 1
        if idx < len(predictionRelevance):
            actual += predictionRelevance[idx]/denominator
        if idx < len(idealRelevance):
            ideal += idealRelevance[idx]/denominator
    return actual/ideal if ideal != 0 else 0.0


def main(argv):
    if len(argv) != 2:
        print("""USAGE:
        python3 QueryAnalyzer.py queryTruth queryResultFolder
        """)
        sys.exit(0)
    queryTruth = argv[0]
    ourResultsFolder = argv[1]

    queryTrueResults = loadQueryTruth(queryTruth)

    ourResults = os.listdir(ourResultsFolder)
    meanPs = []
    precisions = []
    recalls = []
    f1s = []
    mpat10s = []
    ndcgs = []
    for f in ourResults:
        truth = queryTrueResults[f]
        trueDocs = [x[0] for x in truth]
        results = loadOurResults(ourResultsFolder+"/"+f)
        P, R, F1 = calculateP_R_F1(trueDocs, results)
        mpat10 = calculateMPatK(trueDocs, results, 10)
        ndcg = calculateNDCG([[x[0], 3-int(x[1])] for x in truth], results)
        meanPs.append(calculateMPatK(trueDocs, results, len(results)))
        precisions.append(P)
        recalls.append(R)
        f1s.append(F1)
        mpat10s.append(mpat10)
        ndcgs.append(ndcg)
        print(f, P, R, F1, mpat10, ndcg)
    meanAP = calculateMAP(meanPs)
    print(meanAP)
    print(sum(precisions)/len(precisions))
    print(sum(ndcgs)/len(ndcgs))


if __name__ == "__main__":
    main(sys.argv[1:])
