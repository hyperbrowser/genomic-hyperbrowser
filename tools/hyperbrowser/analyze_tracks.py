# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.

#from dbgp.client import brkOnExcept
#brkOnExcept(host='localhost', port=9000, idekey='galaxy')

import sys, os, getopt, types
from urllib import quote, unquote

import galaxy.eggs
from galaxy.util import restore_text

from gold.application.GalaxyInterface import *
from config.Config import URL_PREFIX
import proto.hyperbrowser.hyper_gui as hg


def getDataFilePath(root, id):
    hashDir = '/%03d/' % (int(id) / 1000)
    return root + hashDir + 'dataset_' + str(id) + '.dat'

def main():
    filename = sys.argv[1]
    tool = None
    if len(sys.argv) > 2:
        tool = sys.argv[2]

    job_params,params = hg.load_input_parameters(filename)
#    print job_params, params

    file_path = None

    trackName1 = ""
    trackName2 = ""
    intensityTrackName = None
    subName1 = ""
    subName2 = ""
    track1File = None
    track1FileType = None
    track1FileDescr = None
    track1State = None
    track2File = None
    track2FileType = None
    track2FileDescr = None
    track2State = None
    intensityTrackFile = None
    intensityTrackFileType = None
    statClassName = ""
    binSize = "*"
    region = "*"
    userBins = None
    output = filename
    extractFile = None
    customFile = None
    statsFile = None
    method = None
    segLength = 0
    overlaps = None
    genome = 'hg18'
    #genomes = {'NCBI36': 'hg18'} #,'hg17': 'NCBI35','hg16': 'NCBI34','hg15': 'NCBI33'}
    username = None

    for o, a in params.items():
        if a == "":
            continue
        a = str(a)
        if o == "dbkey":
            genome = a
        elif o == "tool":
            tool = a
        elif o == "track1":
            trackName1 = a
        elif o == "track2":
            trackName2 = a
        elif o == "trackIntensity":
            intensityTrackName = a
        elif o == "grptrack1":
            grpName1 = a
        elif o == "grptrack2":
            grpName2 = a
        elif o == "subtrack1":
            subName1 = a
        elif o == "subtrack2":
            subName2 = a
        elif o == "stats":
            statClassName = a
        elif o == "binsize":
            binSize = a
        elif o == "seglength":
            segLength = int(a)
        elif o == "region":
            region = a
        elif o == "method":
            method = a
        elif o == "output":
            output = a
#            sys.stdout = open(a, "w", 0)
        elif o == "extract":
            extractFile = a
        elif o == "custom":
            sys.stdout = open(a, "w", 0)
            customFile = a
        elif o == "binfile":
            region = "bed"
            userBins = a
        elif o == "track1file":
            dummy, track1File, track1FileType, track1FileDescr = a.split(',')
        elif o == "track2file":
            dummy, track2File, track2FileType, track2FileDescr = a.split(',')
        elif o == "trackIntensityfile":
            dummy, intensityTrackFile, intensityTrackFileType, intensityTrackFileDescr = a.split(',')
        elif o == 'track1type':
            track1FileType = a
        elif o == 'track2type':
            track2FileType = a
        elif o == 'track1_state':
            track1State = unquote(a)
        elif o == 'track2_state':
            track2State = unquote(a)
        elif o == "statsfile":
            statsFile = a
        elif o == "file_path":
            file_path = a
        elif o == "overlaps":
            overlaps = unquote(a)
        elif o == "userEmail":
            username = a

#
#    binFiles = {'chrom': '/data1/rrresearch/standardizedTracks/hg18/Mapping and Sequencing Tracks/_Chromosomes/chromosomes.bed',
#       'arms': '/data1/rrresearch/standardizedTracks/hg18/Mapping and Sequencing Tracks/Chromosome arms/ucscChrArms.bed',
#        'bands': '/data1/rrresearch/standardizedTracks/hg18/Mapping and Sequencing Tracks/Chromosome bands/ucscChrBands.bed'
#       }
#
#    if method in binFiles.keys():
#        region = 'file'
#        binSize = binFiles[method]

    if method in ['__chrs__', '__chrBands__', '__chrArms__', '__genes__']:
        region = method
        binSize = params[method]
    elif method == '__brs__':
        region = method
        binSize = '*'

    if userBins and userBins.startswith('galaxy'):
        binSize = getDataFilePath(file_path, userBins.split(',')[1])
        region = userBins.split(',')[2]

#    if track1File != None:
#        tracks1 = ['galaxy', track1FileType, getDataFilePath(file_path, track1File), unquote(track1FileDescr)]
#    else:
    tracks1 = trackName1.split(':')

#    if track2File != None:
#        tracks2 = ['galaxy', track2FileType, getDataFilePath(file_path, track2File), unquote(track2FileDescr)]
#    else:
    tracks2 = trackName2.split(':')

#    if intensityTrackFile != None:
#        intensityTracks = ['galaxy', intensityTrackFileType, getDataFilePath(file_path, intensityTrackFile), unquote(intensityTrackFileDescr)]
    if intensityTrackName != None:
        intensityTracks = intensityTrackName.split(':')
    else:
        intensityTracks = []

    if statClassName.startswith('galaxy'):
        statsFileId = statClassName.split(',')[1]
        statsFile = getDataFilePath(file_path, statsFileId)
        #hashDir = '/%03d/' % (int(statsFileId) / 1000)
        #statsFile = file_path + hashDir + 'dataset_' + statsFileId + '.dat'
        statClassName = '[scriptFn:=' + statsFile.encode('hex_codec') + ':] -> CustomRStat'

    #print tracks1, tracks2, statClassName, statsFile

    if tool == 'extract':
        #print 'GalaxyInterface.parseExtFormatAndExtractTrackManyBins*', (genome, tracks1, region, binSize, True, overlaps, output)
        if output != None:
            sys.stdout = open(output, "w", 0)
        if params.has_key('sepFilePrRegion'):
            GalaxyInterface.parseExtFormatAndExtractTrackManyBinsToRegionDirsInZipFile(genome, tracks1, region, binSize, True, overlaps, output)
        else:
            GalaxyInterface.parseExtFormatAndExtractTrackManyBins(genome, tracks1, region, binSize, True, overlaps, output)

    else: #run analysis
# already validated
#        validation = GalaxyInterface.runValid(tracks1, tracks2, statClassName, region, binSize)
        validation = True
        if validation == True:
            if output != None:
                sys.stdout = open(output, "w", 0)
            #print params
            demoID = params['demoID'] if params.has_key('demoID') else None
            GalaxyInterface.run(tracks1, tracks2, statClassName, region, binSize, genome, output, intensityTracks, username, track1State, track2State, demoID)
        else:
            print validation


if __name__ == "__main__":
    main()
