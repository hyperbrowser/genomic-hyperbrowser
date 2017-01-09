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
import sys
from cgi import escape
from urllib import quote, unquote

import proto.hyperbrowser.hyper_gui as gui


def selected(opt, sel):
    return ' selected="selected" ' if opt == sel else ''

def disabled(opt, sel):
    return ' disabled="disabled" ' if opt == sel else ''

def _disabled(opt, sel):
    return ' disabled="disabled" ' if opt != sel else ''

%>
<%
#reload(gui)

#print vars(trans.get_user().email)

galaxy = gui.GalaxyWrapper(trans)

params = galaxy.params
#print params


genomes = hyper.getAllGenomes(galaxy.getUserName())
genome = params.get('dbkey', genomes[0][1])
genomeElement = gui.SelectElement('dbkey', genomes, genome)


#datasets = galaxy.getHistory(['bed','wig'])
datasets = []

#track = gui.TrackWrapper('track1', hyper, [], galaxy, datasets, genome)
#track.fetchTracks()


formAction = ''

%>
<%inherit file="base.mako"/>

<%def name="title()">Preprocess tracks</%def>
<%def name="head()">
    <script type="text/javascript">
        <%include file="common.js"/>
    </script>
</%def>

<form method="post" action="${formAction}">
<p>
    Genome build: ${genomeElement.getHTML()} ${genomeElement.getScript()}    
</p>

%if hyper.userHasFullAccess(galaxy.getUserName()):

<input id="start" type="button" value="Preprocess" onclick="form.action='/tool_runner';form.submit()">

%else:
        <p>You must be one of us to start preprocessing</p>

%endif

    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="hb_preprocess">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">

</form>
