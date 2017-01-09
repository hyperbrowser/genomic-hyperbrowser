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

from quick.extra.TrackExtractor import TrackExtractor
from quick.application.UserBinSource import UserBinSource

trackName1 = ['Genes and gene subsets','Genes','Refseq'] #or any other track that are precomputed on the server

#genome regions to extract could be from a bed-file:
#regions = UserBinSource('file','myRegions.bed')
#or implicitly declared, here as 500 regions, 1k long, in the beginning of chr1:
regions = UserBinSource('chr1:1-500000','1k','hg18') #could also have been e.g. genomewide as UserBinSource('*','*','hg18')

#options
globalCoords=False #now gives coordinates relative to each region. Using True would have given global coordinates (chromosome-offsets)
asOriginal=False #gives output in the original format (overrides the fileFormatName attribute if True)
allowOverlaps=False #if set to False, any overlapping segments are merged into "super-segments"

#Generate files. Here only one track, but could have been list of many tracks.
#Either combine track data for all regions in a single file:
TrackExtractor.extractManyToOneDir([trackName1], regions, 'myOutputFolder', 'bed', globalCoords, asOriginal)
#Or one could have created a separate folder with track-data for each region:
#TrackExtractor.extractManyToRegionDirs([trackName1], regions, 'myOutputFolder', 'bed', globalCoords, asOriginal)
