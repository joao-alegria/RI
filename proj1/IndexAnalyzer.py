import sys

content = {}
highestFrequency = 0

# reads output file and builds dictionary with terms as keys and number of occurrences as values
def buildDict(outputFileName):
    global highestFrequency
    outputFile = open(outputFileName,"r") 
    for line in outputFile:
        elements = line.split(",")
        count = 0
        for e in elements[1:]:
            count += int(e.split(":")[1])
        content[elements[0]] = count
        if highestFrequency < count:
            highestFrequency = count

# returns fraction of the 'content' dictionary where the values are equal to 'n'
def filterByOccur(n):
    retdict = {}
    for key in content:
        if content[key] == int(n):
            retdict[key] = content[key]
    return retdict

# aux method for the quicksort
def partition(terms,low,high): 
    i = (low-1) 
    pivot = terms[high]

    for j in range(low , high): 
        if terms[j] <= pivot:
            i += 1
            terms[i],terms[j] = terms[j],terms[i] 

    terms[i+1],terms[high] = terms[high],terms[i+1] 
    return (i+1) 

# quicksort implementation to order the terms alphabetically
def quicksortAlphabetical(terms,low,high):
    if low < high: 
        pi = partition(terms,low,high)  # partitioning index
        quicksortAlphabetical(terms, low, pi-1) 
        quicksortAlphabetical(terms, pi+1, high) 

# main function to answer to some of the assignment's questions
def main(args):
    if len(args) == 0:
        print("Please insert output file name as first argument.")
        return

    outputFileName = args[0]
    documentFrequency = 1 if len(args)==1 else args[1]

    buildDict(outputFileName)
    print("\nThe given file contains " + str(len(content.keys())) + " unique terms.") # just count the keys to calculate the vocabulary size

    terms = list(filterByOccur(documentFrequency).keys()) # retrieve only the keys with the desired document frequency
    quicksortAlphabetical(terms,0,len(terms)-1) # sort them alphabetically
    firstTerms = terms[0:10]
    print("\nThe " + str(len(firstTerms)) + " first terms with document frequency of " + str(documentFrequency) + " (ordered alphabetically):")
    print(firstTerms[0:10]) # print a maximum of 10 terms

    highestTerms = []
    auxFrequency = highestFrequency
    while len(highestTerms) < 10 and auxFrequency != 0: # decrease auxFrequency as long as the list of terms with highest frequency isn't long enough (while possible)
        auxList = list(filterByOccur(auxFrequency).keys())
        for element in auxList:
            highestTerms += [(element,auxFrequency)]
        if len(highestTerms) < 10:
            auxFrequency -= 1
    if len(highestTerms) < 10:
        print("\nThe " + str(len(highestTerms)) + " terms with highest document frequency:")
    else:
        print("\nThe 10 terms with highest document frequency:")
    print(highestTerms[0:10]) # print a maximum of 10 terms
    print()

main(sys.argv[1:])