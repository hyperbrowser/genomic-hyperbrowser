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

from gold.application.GalaxyInterface import GalaxyInterface
#GalaxyInterface.run(['HCNE','density_mm8_90pc_50col'], ['genes','refseq'], '[altHyp:=ha1:]a -> PointPositioningPValStat','chr1','10m')

print GalaxyInterface.getTrackInfoRecord('hg18',['Regulation','CpG islands'])
GalaxyInterface.setTrackInfoRecord('hg18',['Regulation','CpG islands'], {'description':'Test'}, False)
print GalaxyInterface.getTrackInfoRecord('hg18',['Regulation','CpG islands'])
GalaxyInterface.setTrackInfoRecord('hg18',['Regulation','CpG islands'], {'private':True}, False)
print GalaxyInterface.getTrackInfoRecord('hg18',['Regulation','CpG islands'])
GalaxyInterface.setTrackInfoRecord('hg18',['Regulation','CpG islands'], {'description':''}, False)
GalaxyInterface.setTrackInfoRecord('hg18',['Regulation','CpG islands'], {'private':False}, False)
print GalaxyInterface.getTrackInfoRecord('hg18',['Regulation','CpG islands'])
