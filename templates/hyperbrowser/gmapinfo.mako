<%!
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

import sys, traceback
from cgi import escape
from urllib import quote, unquote

import quick.extra.GoogleMapsInterface as gmi
import proto.hyperbrowser.hyper_gui as gui

%>
<%
error = ''
try:
    galaxy = gui.GalaxyWrapper(trans)
    params = galaxy.params

    filename = params['map']
    mapId = params['mapid']
    
    info = gmi.MarkInfo(filename, 0, 0, mapId)

    if not info.validMapId():
	error = 'Marker info is not supported until a valid mapId is chosen.'
    else:
        try:
    	    row = int(params['row'])
            col = int(params['col'])
        except:
	    row, col = 0, 0
            error = 'Column and/or row index is not valid. This may be caused by incorrectly specified map coordinates.'

        info = gmi.MarkInfo(filename, col, row, mapId)
        infotext = info.getHtmlText()

except:
    error = traceback.format_exc()

%>
<div style="overflow: auto; height: 200px">
%if error != '':
    ${error}
%else:
    ${infotext}
%endif
</div>
