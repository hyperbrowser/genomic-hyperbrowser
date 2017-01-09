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


def getSupportedFileSuffixesForBinning():
    return ['gtrack', 'bed', 'point.bed', 'category.bed', 'valued.bed', 'wig', \
            'targetcontrol.bedgraph', 'bedgraph', 'gff', 'gff3', 'category.gff', \
            'narrowpeak', 'broadpeak']


def getSupportedFileSuffixesForPointsAndSegments():
    return getSupportedFileSuffixesForBinning()


def getSupportedFileSuffixesForGSuite():
    return getSupportedFileSuffixesForPointsAndSegments() + \
           ['fasta', 'microarray',
            'tsv', 'vcf', 'maf']
# Last three are temporarily added for supporting GSuite repositories via
# manual manipulation


def getSupportedFileSuffixesForFunction():
    return ['hbfunction']


def getSupportedFileSuffixes():
    return getSupportedFileSuffixesForGSuite() + \
           getSupportedFileSuffixesForFunction()


# Defined to stop searching for GTrackGenomeElementSource subtypes online.
def getUnsupportedFileSuffixes():
    return ['bam', 'bai', 'tab', 'tbi', 'bigwig', 'bw', 'bigbed', 'bb', 'fastq', 'fq', \
            'csfasta', 'csqual', 'doc', 'docx', 'xls', 'xlsx', 'gp', 'gappedPeak', 'peaks', \
            'bedcluster', 'bedlogr', 'bedrnaelement', 'bedrrbs', 'cel', 'matrix', \
            'pdf', 'peptidemapping', 'shortfrags', 'spikeins', 'pair', 'txt', \
            'xml', 'svs', 'gz', 'tar', 'z', 'tgz', 'zip']
#            'xml', 'svs', 'maf', 'gz', 'tar', 'z', 'tgz', 'zip']
