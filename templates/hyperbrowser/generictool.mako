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

import sys, os, traceback, json
from cgi import escape
from urllib import quote, unquote

import hyperbrowser.hyper_gui as gui

%>
<%
params = control.params

if control.isRedirectTool() or not control.prototype.isHistoryTool():
    formAction = '?'
else:
    formAction = h.url_for('/tool_runner')

%>
<%namespace name="functions" file="functions.mako" />
<%inherit file="base.mako" />
<%def name="title()">${control.prototype.getToolName()}</%def>
<%def name="head()">
    %if control.doRedirect():
        <meta http-equiv="Refresh" content="0; url=${control.getRedirectURL()}" />
    %endif
    <script type="text/javascript">
        <%include file="common.js"/>
    </script>
    ${h.js('sorttable')}
</%def>

%if control.userHasFullAccess():

    <form method="post" action="${formAction}">

    <INPUT TYPE="HIDDEN" NAME="old_values" VALUE="${quote(json.dumps(control.oldValues))}">
    <INPUT TYPE="HIDDEN" NAME="datatype" VALUE="${control.prototype.getOutputFormat(control.choices)}">
    <INPUT TYPE="HIDDEN" NAME="mako" VALUE="generictool">
    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="${control.toolId}">
    <INPUT TYPE="HIDDEN" NAME="tool_name" VALUE="${control.toolId}">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">
    <INPUT TYPE="HIDDEN" NAME="extra_output" VALUE="${quote(json.dumps(control.extra_output))}">

    %if len(control.subClasses) > 0:
        ${functions.select('sub_class_id', control.subClasses.keys(), control.subClassId, control.subToolSelectionTitle)}
    %endif

    %for i in control.inputOrder:
        %if i in control.inputGroup[0]:
            %for label in control.inputGroup[0][i]:
            <fieldset><legend>${label}</legend>
            %endfor
        %endif

        %if control.inputTypes[i] == 'select':
            ${functions.select(control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i], info=control.inputInfo[i])}
        %elif control.inputTypes[i] == 'multi':
            ${functions.multichoice(control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i], info=control.inputInfo[i])}
        %elif control.inputTypes[i] == 'checkbox':
            ${functions.checkbox(control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i], info=control.inputInfo[i])}
        %elif control.inputTypes[i] == 'text':
            ${functions.text(control.inputIds[i], control.displayValues[i], control.inputNames[i], control.options[i][1], readonly=False, reload=control.prototype.isDynamic(), info=control.inputInfo[i])}
        %elif control.inputTypes[i] == 'text_readonly':
            ${functions.text(control.inputIds[i], control.displayValues[i], control.inputNames[i], control.options[i][1], readonly=True)}
        %elif control.inputTypes[i] == '__rawstr__':
            ${functions.rawStr(control.inputIds[i], control.displayValues[i], control.inputNames[i])}
        %elif control.inputTypes[i] == '__password__':
            ${functions.password(control.inputIds[i], control.displayValues[i], control.inputNames[i], reload=control.prototype.isDynamic(), info=control.inputInfo[i])}
        %elif control.inputTypes[i] == '__genome__':
            ${functions.genomeChooser(control)}
        %elif control.inputTypes[i] == '__track__':        
            ${functions.trackChooser(control.trackElements[control.inputIds[i]], i, params, False)}
        %elif control.inputTypes[i] == '__history__':
            ${functions.history_select(control, control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i], info=control.inputInfo[i])}
        %elif control.inputTypes[i] == '__toolhistory__':
            ${functions.history_select(control, control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i], info=control.inputInfo[i])}
        %elif control.inputTypes[i] == '__multihistory__':
            ${functions.multihistory(control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i], info=control.inputInfo[i])}
        %elif control.inputTypes[i] == '__hidden__':
            <input type="hidden" name="${control.inputIds[i]}" id="${control.inputIds[i]}" value="${control.displayValues[i]}">
        %elif control.inputTypes[i] == 'table':
            ${control.displayValues[i]}
        %endif

        %if i in control.inputGroup[1]:
            %for j in range(0, control.inputGroup[1].count(i)):
            </fieldset>
            %endfor
        %endif
        
    %endfor
    
    <p><input id="start" type="submit" name="start" value="Execute" ${'disabled' if not control.isValid() else ''}></p>

    </form>

    %if control.hasErrorMessage():
        <div class="errormessage">${control.errorMessage}</div>
    %endif

    %if control.params.get('start') and not control.prototype.isHistoryTool() and control.isValid():
        <p class="infomessage">${control.executeNoHistory()}</p>
    %endif


    %if control.prototype.isBatchTool() and control.isValid() and control.userIsOneOfUs():
    <p class="infomessage" onclick="$('#batchline').toggle()">
        <a href="#batchline" title="Click to show/hide">Corresponding batch command line:</a>
        <span id="batchline" style="display:none"><br>
        ${control.getBatchLine()}
        </span>
    </p>
    <br/>
    
    <p class="infomessage" onclick="$('#testform').toggle()">
        <a href="#testform" title="Click to show/hide">Add run to test repository:</a>
        <!--<button id="testsubmit" type="button" style="display:none" >Click Me!</button>-->
        <form id="testform" style="display:none">
        set test name: <input type="text" name="testname"><br>
        <input type="submit" name="testsubmit" value="Add test">
        </form>
    </p>
    <script type="text/javascript">
        $( "#testform" ).bind( "submit", function( event ) {
        //$( "#testsubmit" ).click(function() {
        //var c = $("[name='add_test']:checked").val();
        if(1)
        	 {var datastring = $("form").serialize();
            var lastChar = datastring.indexOf('&testname=');
            var b = datastring.slice (0,lastChar).replace(/&/g,"\n").replace(/=/g, ":");
            var c = '&box2='+ $("[name='testname']").val();
            var testData = "old_values=%7B%7D&datatype=html&mako=generictool&tool_id=hb_add_test_tool&tool_name=hb_add_test_tool&URL=http://dummy&start=Execute&box1=" + b + c
            
            $.post("/dev2/tool_runner",  testData);
            alert('Added test to test-repository..');
            event.preventDefault();
            }});
    </script>
    %endif

%else:
    ${functions.accessDenied()}
%endif

<%def name="toolHelp()">
    %if control.hasDemoURL():
        <button onclick="location.href='${control.getDemoURL()}'">Fill out demo selections</button>
        <hr>
    %endif

    ${control.prototype.getToolDescription()}

    %if control.getIllustrationImage():
        %if os.path.exists(control.getIllustrationImage().getDiskPath()):
            <p><hr><img width="100%" style="max-width: 640px; width: expression(this.width > 640 ? 640: true);" src="${control.getIllustrationImage().getURL()}"></p>
        %elif control.isDebugging():
            <p class="warningmessage">No imagefile exists at: ${control.getIllustrationImage().getDiskPath()}</p>
        %endif
    %endif

    %if control.hasFullExampleURL():
        %if control.prototype.getToolDescription() not in [None, '']:
            <hr>
        %endif
        <b>Example</b>
        <p><a href="${control.getFullExampleURL()}" target=_top>See full example</a> of how to use this tool.</p>
    %endif
</%def>

