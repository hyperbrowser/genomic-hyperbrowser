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
import sys, traceback
from cgi import escape
from urllib import quote, unquote
%>
<%
galaxy = control.galaxy
params = galaxy.params
error = ''
try:
    control.action()
except:
    error = traceback.format_exc()

%>
<%inherit file="base.mako"/>
<%namespace name="functions" file="functions.mako" />


<%def name="title()">Preprocess tracks</%def>
<%def name="head()">
    <script type="text/javascript">
        <%include file="common.js"/>
    </script>
</%def>

<form method="post" action="">
<p>
##    Genome build: ${control.genomeElement.getHTML()} ${control.genomeElement.getScript()}    
    ${functions.genomeChooser(control)}
</p>
${functions.trackChooser(control.track, 0, control.params)}

%if control.userHasFullAccess():

<input id="start" type="button" value="Preprocess" onclick="form.action='${h.url_for("/tool_runner")}';form.submit()">

%else:
        <p>You must be one of us to start preprocessing</p>

%endif

    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="hb_preprocess">
    <INPUT TYPE="HIDDEN" NAME="mako" VALUE="preprocesstracks">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">

</form>
${error}
