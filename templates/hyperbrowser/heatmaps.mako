<!--
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
-->

<%!
import sys, os
from cgi import escape
from urllib import quote, unquote

import proto.hyperbrowser.hyper_gui as gui
import quick.extra.GoogleMapsInterface as gmi

%>
<%
galaxy = gui.GalaxyWrapper(trans)
%>
<%inherit file="base.mako"/>
<%namespace name="functions" file="functions.mako" />

<%def name="title()">View heatmaps</%def>

%if hyper.userHasFullAccess(galaxy.getUserName()):
    <table border="1">
    %for map in gmi.Map.getMaps():
        <tr><td><b><a href="${map.getUrl()}">${map.getPrettyName()}</a></b></td>
		   <td><a href="${map.getRunDescriptionUrl()}">Run Description</a></td>
		   <td><a href="${map.getCountUrl()}">Counts</a></td>
		   <td><a href="${map.getEffectSizeUrl()}">Effect size</a></td>
		   <td><a href="${map.getPvalUrl()}">P-values</a><br/></td></tr>
    %endfor
    </table>

%else:
    ${functions.accessDenied()}
%endif
