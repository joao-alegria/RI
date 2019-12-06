import sys
import os


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
            truth.remove(p)
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
    for idx, p in enumerate(prediction[:k+1]):
        if p in truth:
            count += 1
            P, R, F1 = calculateP_R_F1(truth, prediction[:idx+1])
            pSum += P
    return pSum/count if count != 0 else 0.0


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
    for f in ourResults:
        truth = queryTrueResults[f]
        trueDocs = [x[0] for x in truth]
        results = loadOurResults(ourResultsFolder+"/"+f)
        P, R, F1 = calculateP_R_F1(trueDocs, results)
        MPat10 = calculateMPatK(trueDocs, results, 10)
        meanPs.append(calculateMPatK(trueDocs, results, len(results)))
        print(f, P, R, F1, MPat10)
    meanAP = calculateMAP(meanPs)


if __name__ == "__main__":
    main(sys.argv[1:])
