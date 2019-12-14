import os

inputDir = "../extraindex/"
files = os.listdir(inputDir)
limitcache = 3
cache = {}
for file in files:
    for line in open(inputDir+file):
        line = line.strip().split(";")
        token = line[0].split(":")[0]
        for docs in line[1:]:
            docs = docs.split(":")
            doc = docs[0]
            weight = docs[1]
            if docs[0] not in cache:
                cache[doc] = [(token, weight)]
            else:
                if len(cache[doc]) < limitcache:
                    cache[doc].append((token, weight))
                else:
                    for termcache, termweight in cache[doc]:
                        if termweight < weight:
                            cache[doc].remove(
                                (termcache, termweight))
                            cache[doc].append(
                                (token, weight))
                            break


f = open("../docCache", "w")
for key in cache:
    f.write(key+"".join(";"+str(x[0])+":"+str(x[1]) for x in cache[key])+"\n")
