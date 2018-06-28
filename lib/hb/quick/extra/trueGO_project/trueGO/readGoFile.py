from collections import defaultdict
from itertools import combinations
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import plotly.plotly as ply
import plotly
import plotly.graph_objs as go

class ReadGoFile:

    def __init__(self, goFn):
        self._goContent = ''
        self._readGoFile(goFn)

    def _readGoFile(self, goFn):
        self._goFn = goFn
        with open(self._goFn) as gofile:
            self._goContent = gofile.readlines()
        return self._goContent

class GoTerms:
    def __init__(self):
        self._goTerms = []

    def getGoTerms(self, goContent):
        self._goContent = goContent
        self._goTerms = [go_line.strip("\n").split("\t")[4] for go_line in goContent if
                        not go_line.startswith("!")]
        return self._goTerms

class Genes:
    def __init__(self):
        self._genes=[]
        self._geneUniverse = []

    def getGenes(self,goContent):
        self._goContent = goContent
        self._genes = [go_line.strip("\n").split("\t")[2] for go_line in self._goContent if not go_line.startswith("!")]
        return self._genes

    def getGeneUniverse(self):
        self._geneUniverse_temp = sorted(set(self._genes))
        self._geneUniverse = list(filter(None, self._geneUniverse_temp))
        return self._geneUniverse

class GoGeneMapping:
    def getGoGeneMapping(self,goTerms,genes):
        self._goTerms = goTerms
        self._genes = genes
        self._gotermGenes = defaultdict(set)
        for (key, value) in list(zip(self._goTerms, self._genes)):
            self._gotermGenes[key].add(value)
        return self._gotermGenes


class GoGeneMatrix:

    def isGeneIncludedInGo(self, gene, go, gotermgenes):
        return gene in gotermgenes[go]

    def getGeneListForGo(self, go, gotermgenes):
        return gotermgenes[go]

    def getGoTermKappaCoeff(self,goterm1,goterm2,gotermgenes,geneuniversesize):
        term1genes = gotermgenes[goterm1]
        term2genes = gotermgenes[goterm2]
        bothpresent = len(set.intersection(term1genes,term2genes))
        present_in_onlyterm1 = len(set.difference(term1genes,term2genes))
        present_in_onlyterm2 = len(set.difference(term2genes, term1genes))
        bothabsent = geneuniversesize-len(set.union(term1genes,term2genes))
        totalcol1 = bothpresent+present_in_onlyterm1
        totalcol2 = bothabsent+present_in_onlyterm2
        totalrow1 = bothpresent+present_in_onlyterm2
        totalrow2 = bothabsent+present_in_onlyterm1
        totalgenes = totalcol1+totalcol2
        observed_cooccurrence = (bothpresent+bothabsent)/totalgenes
        chance_cooccurrence = ((totalcol1 * totalrow1) + (totalcol2 * totalrow2)) / (totalgenes * totalgenes)
        try:
            kappa_coeff = (observed_cooccurrence - chance_cooccurrence) / (1 - chance_cooccurrence)
        except ZeroDivisionError:
            chance_cooccurrence += 0.001
            kappa_coeff = (observed_cooccurrence - chance_cooccurrence) / (1 - chance_cooccurrence)
        return kappa_coeff

    def computeKappaforGoTerms(self,goterms,gotermgenes,geneuniversesize):
        gopairs = list(combinations(goterms, 2))
        return {pair : self.getGoTermKappaCoeff(*pair,gotermgenes,geneuniversesize) for pair in gopairs}

# class GoGeneMatrix:
#
#     def __init__(self, goFn):
#         self._goContent = ''
#         self._genes = []
#         self._goTerm = []
#         self._gotermGenes = {}
#         self._geneUniverse = []
#         self._readGoFile(goFn)
#
#     def _readGoFile(self, GoFile):
#         self._GoFile = GoFile
#         with open(self._GoFile) as gofile:
#             self._goContent = gofile.readlines()
#             self._genes = [go_line.strip("\n").split("\t")[2] for go_line in self._goContent if not go_line.startswith("!")]
#             self._goTerm = [go_line.strip("\n").split("\t")[4] for go_line in self._goContent if not go_line.startswith("!")]
#             self._gotermGenes = defaultdict(set)
#             for (key,value) in list(zip(self._goTerm,self._genes)):
#                 self._gotermGenes[key].add(value)
#             self._geneUniverse_temp = sorted(set(self._genes))
#             self._geneUniverse = list(filter(None, self._geneUniverse_temp))
#
#
#     def getGenes(self):
#         return self._genes
#
#     def getGoTerms(self):
#         return self._goTerm
#
#     def getGoGeneMapping(self):
#         return self._gotermGenes
#
#     def getGeneUniverse(self):
#         return self._geneUniverse
#
#     def isGeneIncludedinGo(self,gene,go):
#         return gene in self._gotermGenes[go]
#
#     def getGeneListForGo(self,go):
#         return self._gotermGenes[go]
#
#     def getGoTermKappaCoeff(self,goterm1,goterm2):
#         assert False

if __name__ == "__main__":
    import os
    os.chdir('/Users/chakravarthikanduri/Documents/PostDoc_Projs/trueGO_data/')
    myObj=GoGeneMatrix()
    myObj._readGoFile("goa_human.gaf")
    golist = myObj.getGoGeneMapping()
    print(golist)

if __name__ == "__main__":
    from userdata import readUserGoList
    import os
    os.chdir('/Users/chakravarthikanduri/Documents/PostDoc_Projs/trueGO_data/')
    gofile=ReadGoFile(goFn="goa_human.gaf")
    goterms = GoTerms()
    genes = Genes()
    gogenemap = GoGeneMapping()
    gogenemat = GoGeneMatrix()
    gocontent = gofile._readGoFile(goFn="goa_human.gaf")
    gotermlist = goterms.getGoTerms(gocontent)
    genelist = genes.getGenes(gocontent)
    geneuniverselist = genes.getGeneUniverse()
    gogenemapping= gogenemap.getGoGeneMapping(gotermlist,genelist)
    #temp = gogenemat.getGoTermKappaCoeff("GO:0007269","GO:0007269",gogenemapping,len(geneuniverselist))
    userdata = readUserGoList("user_testdata.txt")
    kappa = gogenemat.computeKappaforGoTerms(userdata,gogenemapping,len(geneuniverselist))
    kappa_values = list(kappa.values())
    x_axis = [i for i in range(len(kappa_values))]
    # trace = go.Scatter(
    #     x=x_axis,
    #     y=kappa_values,
    #     mode='markers'
    # )
    # plotly_data = [trace]
    # plotly.offline.plot(plotly_data)
    plt.scatter(x_axis,kappa_values)
    plt.show()
    #print(len(kappa))
