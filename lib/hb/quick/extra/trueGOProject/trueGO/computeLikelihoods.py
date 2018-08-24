from itertools import combinations
from collections import defaultdict

def computeMaximumLikelihood(probablityOfBeingIncludedInCategory, numberOfItemsInCategory, numberOfItemsInUniverse):
    numberOfItemsNotInCategory = numberOfItemsInUniverse - numberOfItemsInCategory
    probablityOfNotBeingIncludedInCategory = 1 - probablityOfBeingIncludedInCategory
    maximumLikelihood = (probablityOfBeingIncludedInCategory ** numberOfItemsInCategory) * (probablityOfNotBeingIncludedInCategory ** numberOfItemsNotInCategory)
    return maximumLikelihood

def computeProbabilityOfBeingIncludedInCategory(usergeneslist,goterm1,gotermgenes,geneuniversesize):
    term1genes = gotermgenes[goterm1]
    numberofusergenesingoterm = len(set.intersection(usergeneslist, term1genes))
    fractionOfGeneUniverseIncludedInCategory = float(numberofusergenesingoterm)/geneuniversesize
    return [fractionOfGeneUniverseIncludedInCategory,numberofusergenesingoterm]

def computeProbabilityOfBeingIncludedInBothCategories(usergeneslist,goterm1,goterm2,gotermgenes,geneuniversesize):
    term1genes = gotermgenes[goterm1]
    term2genes = gotermgenes[goterm2]
    bothpresent = set.intersection(term1genes, term2genes)
    numberofusergenesinbothterms = len(set.intersection(usergeneslist, bothpresent))
    fractionOfGeneUniverseIncludedInBothCategories = float(numberofusergenesinbothterms)/geneuniversesize
    return [fractionOfGeneUniverseIncludedInBothCategories,numberofusergenesinbothterms]

def computeLikelihoodsForUserGoTerms(usergoterms,usergeneslist,gotermgenes,geneuniversesize):
    gopairs = list(combinations(usergoterms, 2))
    likelihoodsDict = defaultdict(list)
    for pair in gopairs:
        bothProbability = computeProbabilityOfBeingIncludedInBothCategories(usergeneslist, pair[0], pair[1], gotermgenes,geneuniversesize)
        if bothProbability > 0:
            term1Probability = computeProbabilityOfBeingIncludedInCategory(usergeneslist, pair[0],gotermgenes,geneuniversesize)
            term2Probability = computeProbabilityOfBeingIncludedInCategory(usergeneslist, pair[1],gotermgenes,geneuniversesize)
            maxlikelihood_both = computeMaximumLikelihood(bothProbability[0],bothProbability[1],geneuniversesize)
            maxlikelihood_term1 = computeMaximumLikelihood(term1Probability[0],term1Probability[1],geneuniversesize)
            maxlikelihood_term2 = computeMaximumLikelihood(term2Probability[0],term2Probability[1],geneuniversesize)
            try:
                bothVersusTerm1 = maxlikelihood_both/maxlikelihood_term1
            except ZeroDivisionError:
                bothVersusTerm1 = "zero division"
            try:
                bothVersusTerm2 = maxlikelihood_both/maxlikelihood_term2
            except ZeroDivisionError:
                bothVersusTerm2 = "zero division"
            #likelihoodRatios = [bothVersusTerm1,bothVersusTerm2]
            likelihoodsDict[pair].append(bothVersusTerm1)
            likelihoodsDict[pair].append(bothVersusTerm2)
    return likelihoodsDict
