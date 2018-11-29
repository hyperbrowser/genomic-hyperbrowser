import os
import random
from config.Config import DATA_FILES_PATH

def getGeneUniverseOfGivenSize(filename, size):
    with open(filename) as genefile:
        txt = genefile.read()
        words = txt.splitlines()
        geneuniverse_list = random.sample(words,size)
        geneuniverse = set(geneuniverse_list)
    return geneuniverse

def getSubsetTerms(geneUniverseset, isRelevant, size):
    geneUniverse = list(geneUniverseset)
    if isRelevant:
        assert size <= len(geneUniverse) / 2, "subset size should be less than half the size of gene universe"
        subsetTerm = random.sample(geneUniverse[0:(len(geneUniverse)/2)],size)
    else:
        assert size <= len(geneUniverse), "subset size should be less than the size of gene universe"
        subsetTerm = random.sample(geneUniverse,size)
    subsettermset = set(subsetTerm)
    return subsettermset

def returnsyntheticdata(numberOfRelevantterms,numberOfOtherterms, geneuniversesize):
    fn = os.path.join(DATA_FILES_PATH, 'trueGO_data', 'words.txt')
    syntheticData = dict()
    universe = getGeneUniverseOfGivenSize(filename=fn,size=geneuniversesize)
    syntheticData["universe"] = universe
    syntheticData["usergene_list"] = getSubsetTerms(geneUniverseset=syntheticData["universe"], isRelevant=True, size=random.randint((geneuniversesize/2)/2,geneuniversesize/2))
    sizesofrelevantterms = [random.randint((geneuniversesize/2)/2,geneuniversesize/2) for num in range(numberOfRelevantterms)]
    sizesofotherterms = [random.randint((geneuniversesize/2)/2, geneuniversesize/ 2) for num in range(numberOfOtherterms)]
    for i in sizesofrelevantterms:
        syntheticData["relterm%s" %i]=getSubsetTerms(geneUniverseset=universe,isRelevant=True,size=i)
    for i in sizesofotherterms:
        syntheticData["otherterm%s" % i] = getSubsetTerms(geneUniverseset=universe, isRelevant=True, size=i)
    return syntheticData