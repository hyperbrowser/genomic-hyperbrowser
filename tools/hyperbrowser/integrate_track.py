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

import sys, os, getopt,types

from gold.application.GalaxyInterface import *
from hyperbrowser.hyper_gui import getDataFilePath,fileToParams

def trackNameForHistoryItem(field, params):
    item = params[field]
    file_path = params['file_path']
    gal,id,type,name = item.split(',')
    filename = getDataFilePath(file_path, id)
    return [gal, type, filename, name]

def main():
    os.umask(0002)
    filename = sys.argv[1]
    params = fileToParams(filename)

    username = params['userEmail'] if params.has_key('userEmail') else ''
    genome = params['dbkey']
    integratedTrackName = params['integratedname'].split(':')
    private = not params['access_public'] if params.has_key('access_public') else True
    
    historyTrackName = trackNameForHistoryItem('historyitem', params)
    
    sys.stdout = open(filename, "w", 0)
    #print 'GalaxyInterface.integrateTrackFromHistory',(genome, historyTrackName, integratedTrackName, private, username)
    GalaxyInterface.integrateTrackFromHistory(genome, historyTrackName, integratedTrackName, privateAccess=private, username=username)
    
if __name__ == "__main__":
    main()
