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
    map = params['map']
    mapId = params['mapid']
    query = params['query']
    info = gmi.MarkInfo(map, 0, 0, mapId)
    if info.validMapId():
        rows = info.getIndexesFromRowName(query)
    	cols = info.getIndexesFromColName(query)
    else:
	error = 'Searching is not supported until a valid mapId is chosen.'

except:
    error = traceback.format_exc()

%>
%if error != '':
    ${error}
%else:
    %for (name,index) in cols:
        <a href="javascript:;" onclick="gotoColRow(${index}, -1)">${name} (col: ${index})</a><br/>
    %endfor
    %for (name,index) in rows:
        <a href="javascript:;" onclick="gotoColRow(-1, ${index})">${name} (row: ${index})</a><br/>
    %endfor
%endif
