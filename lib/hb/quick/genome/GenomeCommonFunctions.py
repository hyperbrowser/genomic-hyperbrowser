import os
import shutil
from collections import OrderedDict
from datetime import datetime

from config.Config import NONSTANDARD_DATA_PATH, ORIG_DATA_PATH, PARSING_ERROR_DATA_PATH, \
    NMER_CHAIN_DATA_PATH
from gold.util.CustomExceptions import InvalidFormatError
from quick.extra.GenomeImporter import GenomeImporter
from quick.util.CommonFunctions import createDirPath, ensurePathExists
from quick.util.GenomeInfo import GenomeInfo

TRACKS_WITH_OVERLAPS = 'preProcessedTracks (withOverlaps)'
TRACKS_NO_OVERLAPS = 'preProcessedTracks (noOverlaps)'
NMER_CHAINS = 'nmerChains'
PARSING_ERROR_TRACKS = 'parsingErrorTracks'
STANDARDIZED_TRACKS = 'standardizedTracks'
COLLECTED_TRACKS = 'collectedTracks'

GENOME_PATHS = OrderedDict([(COLLECTED_TRACKS, NONSTANDARD_DATA_PATH),
                            (STANDARDIZED_TRACKS, ORIG_DATA_PATH),
                            (PARSING_ERROR_TRACKS, PARSING_ERROR_DATA_PATH),
                            (NMER_CHAINS, NMER_CHAIN_DATA_PATH),
                            (TRACKS_NO_OVERLAPS, createDirPath('', '', allowOverlaps=False)),
                            (TRACKS_WITH_OVERLAPS, createDirPath('', '', allowOverlaps=True))])

TRASH_FOLDER = '.trash'


def removeGenomeData(genome, trackFolder, removeFromShelve=False):
    path = os.path.join(GENOME_PATHS[trackFolder], genome)
    trashPath = os.path.join(GENOME_PATHS[trackFolder], TRASH_FOLDER, genome)

    if os.path.exists(path):
        print 'Moving ' + genome + ' to' + TRASH_FOLDER + 'in folder: ' + trashPath
        if os.path.exists(trashPath):
            shutil.rmtree(trashPath)
        ensurePathExists(trashPath)
        shutil.move(path, trashPath)

    if removeFromShelve:
        gi = GenomeInfo(genome)
        if gi.isInstalled():
            print 'Removing from shelve'
            gi.removeEntryFromShelve()


def storeGenomeProperties(gi, fullName, username, buildSource, buildName, species, taxonomyUrl, assembly, accessList, isPrivate, isExperimental, ucscClade, uscsGenome, ucscAssssmbly):
    gi.fullName = fullName
    gi.installedBy = username
    gi.genomeBuildSource = buildSource
    gi.genomeBuildName = buildName
    gi.species = species
    gi.speciesTaxonomyUrl = taxonomyUrl
    gi.assemblyDetails = assembly
    gi.privateAccessList = accessList
    gi.isPrivate = isPrivate
    gi.isExperimental = isExperimental
    gi.ucscClade = ucscClade
    gi.ucscGenome = uscsGenome
    gi.ucscAssembly = ucscAssssmbly
    gi.store()


def downloadGenomeFromUrls(gi, urls):
    gi.sourceUrls = urls
    for url in urls:
        try:
            GenomeImporter.downloadGenomeSequence(gi.genome, url)
        except InvalidFormatError:
            return

def downloadGenomeGffFileFromUrls(gi, urls):
    gi.sourceUrls = urls
    for url in urls:
        try:
            GenomeImporter.downloadGffFile(gi.genome, url)
        except InvalidFormatError:
            return


def installGenome(abbrv, renamedChrsDict, selectedStandardChrs, username):
    gi = GenomeInfo(abbrv)
    GenomeImporter.createGenome(abbrv, renamedChrsDict, selectedStandardChrs)

    gi.installedBy = username
    gi.timeOfInstallation = datetime.now()
    gi.store()
