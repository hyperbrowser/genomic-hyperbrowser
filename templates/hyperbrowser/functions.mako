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

import hyperbrowser.hyper_gui as gui
%>

<%def name="staticInfoBox(name, info)">
    %if info:
        <img class="showInfo" onclick="$('#infobox_${name}').toggle()" title="Information" alt="(i)" src="${h.url_for('/static/style/info_small.png')}">
        <div class="infomessage" id="infobox_${name}" style="display:none">${info}</div>
    %endif
</%def>

<%def name="select(name, opts, value, label = None, info = None)">
    <p><label>${label if label else name}
    <select name="${name}" onchange="reloadForm(form, this)">
        %for o in range(len(opts)):
            <option value="${opts[o]}" ${'selected' if value == opts[o] else ''}>${opts[o]}</option>
        %endfor
    </select>
    </label>
    ${staticInfoBox(name, info)}
    </p>
</%def>

<%def name="history_select(control, name, opts, value, label = None, info = None)">
    <p><label>${label if label else name}
    <select name="${name}" onchange="reloadForm(form, this)">
        ${opts[0]}
    </select>
    </label>
        ${staticInfoBox(name, info)}
    </p>
</%def>

<%def name="checkbox(name, opts, value, label = None, info = None)">
    <p><label><input onchange="reloadForm(form, this)" id="${name}" name="${name}" type="checkbox" value="True" ${'checked=checked' if value else ''}> ${label}</label>
    ${staticInfoBox(name, info)}
    </p>
</%def>

<%def name="multichoice(name, opts, values, label = None, info = None)">
    <fieldset><legend>${label}</legend>
        <a href="javascript:;" id="${name}_check" onclick="$('input.${name}').attr('checked',true);reloadForm(null, this);">Check all</a>
        <a href="javascript:;" id="${name}_uncheck" onclick="$('input.${name}').removeAttr('checked');reloadForm(null, this)">Uncheck all</a><br/>
        %for key,value in opts.items():
            <label><input onchange="reloadForm(form, this)" class="${name}" id="${name + '|' + key}" name="${name + '|' + key}" type="checkbox" value="True" ${'checked=checked' if values and values[key] else 'checked=checked' if value and not values else ''}> ${key}</label><br/>
        %endfor
        <input type="hidden" name="${name}" value="${len(opts)}">
    </fieldset>
</%def>

<%def name="multihistory(name, opts, values, label = None, info = None)">
    <fieldset><legend>${label}</legend>
        <a href="javascript:;" id="${name}_check" onclick="$('input.${name}').attr('checked',true);reloadForm(null, this);">Check all</a>
        <a href="javascript:;" id="${name}_uncheck" onclick="$('input.${name}').removeAttr('checked');reloadForm(null, this)">Uncheck all</a><br/>
        %for key,value in opts.items():
            <label><input onchange="reloadForm(form, this)" class="${name}" id="${name + '|' + key}" name="${name + '|' + key}" type="checkbox" value="${value}" ${'checked=checked' if values and values[key] else 'checked=checked' if value and not values else ''}> ${unquote(value.split(':')[3])}</label><br/>
        %endfor
        <input type="hidden" name="${name}" value="${len(opts)}">
    </fieldset>
</%def>


<%def name="rawStr(name, value = '', label = None)">
    <div>${value}</div>
</%def>

<%def name="text(name, value = '', label = None, rows = 5, readonly = False, reload = False, info = None)">
    <div style="margin: 1em 0px">
    %if label:
        <label for="${name}">${label}</label>
    %endif
    %if rows > 1:
        <textarea ${"onchange=\"reloadForm(form, this)\"" if reload else ''} rows="${rows}" name="${name}" id="${name}" wrap="off"
            style="max-width:100%;width:100%;overflow:auto;" ${"readonly=\"readonly\"" if readonly else ""}>${value}</textarea>
    %else:
        <input type="text" ${"onchange=\"reloadForm(form, this)\"" if reload else ''} name="${name}" id="${name}"
            style="max-width:100%;width:100%;overflow:auto;" ${"readonly=\"readonly\"" if readonly else ""} value="${value}">
    %endif
    ${staticInfoBox(name, info)}
    </div>
</%def>

<!-- <textarea ${"" if not value else "onchange=\"reloadForm(form, this)\""} rows="${rows}" name="${name}" id="${name}" wrap="off" -->

<%def name="password(name, value='', label=None, reload=False, info = None)">
    %if label:
        <label for="${name}">${label}</label>
    %endif
    <p><label>${label if label else name}<br>
        <input type="password" name="${name}" value="${value}" autocomplete="off" style="max-width:100%;width:100%" ${"onchange=\"reloadForm(form, this)\"" if reload else ''}>
    </p>
</%def>

<%def name="trackChooser(track, i, params, do_reset=True, readonly=False)">
    <%
        galaxy = gui.GalaxyWrapper(trans)
        genome = params.get('dbkey')
    %>
    <fieldset><legend>${track.legend}</legend>

  %if not readonly:
    <%
    typeElement = gui.TrackSelectElement(track, 0)

    # reset stats parameter when changing track
    if do_reset:
        typeElement.onChange = "if ($('#_stats')){$('#_stats').val('');$('#stats').val('');}" + typeElement.onChange
    %>
    ${typeElement.getHTML()} ${typeElement.getScript()}

    %if track.valueLevel(0) == 'galaxy':
            <select name="${track.nameFile}" onchange="form.action='?';form.submit()">
                ${track.optionsFromHistory(params.get(track.nameFile))}
##                ${galaxy.optionsFromHistory(hyper.getSupportedGalaxyFileFormats(), params.get(track.nameFile))}
            </select>

##    %elif track.valueLevel(0) == '__recent_tracks':
##            <select name="${track.nameRecent}" onchange="setTrackToRecent('${track.nameMain}', this, form)">
##                <option value=""> -- Select -- </option>
##                %for t in track.recentTracks:
##                    <option value="${t}">${t}</option>
##                %endfor
##            </select>
    %else:
        %for j in range(1, 10):
            %if track.getTracksForLevel(j):
                %if track.valueLevel(j - 1) == 'K-mers':
                    <div style="margin-left:${j}em">|_
                    <input type="text" size="25" name="${track.nameLevel(j)}" value="${track.valueLevel(j) if track.valueLevel(j) != None else ''}" onblur="checkNmerReload(event, this)" onkeypress="checkNmerReload(event, this)">
                    </div>
                %else:
                    <%
                    levelElement = gui.TrackSelectElement(track, j)
                    %>
                    <div style="margin-left:${j}em">|_ ${levelElement.getHTML()} ${levelElement.getScript()}</div>
                %endif
            %endif
        %endfor
    %endif

  %endif

    %if track.main and track.valueLevel(0) != 'galaxy' and track.selected():
        <%
        sti_val = params.get('show_info_'+track.nameMain, '0')
        if sti_val == '1':
            sti_class = 'hideInfo'
            sti_display = ''
        else:
            sti_class = 'showInfo'
            sti_display = 'display:none'

        %>
        <img class="${sti_class}" src="${h.url_for('/static/style/info_small.png')}" alt="Track information" title="Track information" onclick="getInfo(document.forms[0], this, '${track.nameMain}')"/>
        <div id="info_${track.nameMain}" class="infomessagesmall" style="${sti_display}"> ${hyper.getTrackInfo(genome, track.definition())} </div>
        <input type="hidden" name="show_info_${track.nameMain}" id="show_info_${track.nameMain}" value="${sti_val}">

    %endif

        <input type="hidden" name="${track.nameMain}" id="${track.nameMain}" value="${track.asString()}">

        <input type="hidden" name="${track.nameState}" id="${track.nameState}" value="${track.getState()}">

    %if i == 0:
        ${self.help(track.nameMain, 'What is a genomic track?')}
    %else:
        <br>&nbsp;<br>
    %endif

    <%
##    if track.selected():
##        valid = hyper.trackValid(genome, track.definition())
##    else:
##        valid = True
    %>
    %if track.valid != True:
        <div class="errormessagesmall">${track.valid}</div>
    %endif

    </fieldset>

</%def>



<%def name="trackChooserTest(track, i, params, do_reset=True)">
    <%
        galaxy = gui.GalaxyWrapper(trans)
        genome = params.get('dbkey')
    %>
    <fieldset><legend>${track.legend}</legend>

    <%
    typeElement = gui.TrackSelectElement(track, 0)

    # reset stats parameter when changing track
    if do_reset:
        typeElement.onChange = "if ($('#_stats')){$('#_stats').val('');$('#stats').val('');}" + typeElement.onChange
    %>
    ${typeElement.getHTML()} ${typeElement.getScript()}

    %if track.valueLevel(0) == 'galaxy':
            <select name="${track.nameFile}" onchange="form.action='?';form.submit()">
                ${galaxy.optionsFromHistory(hyper.getSupportedGalaxyFileFormats(), params.get(track.nameFile))}
            </select>

    %else:
        %for j in range(1, 10):
            %if track.getTracksForLevel(j):
                %if track.valueLevel(j - 1) == 'K-mers':
                    <div style="margin-left:${j}em">|_
                    <input type="text" size="25" name="${track.nameLevel(j)}" value="${track.valueLevel(j) if track.valueLevel(j) != None else ''}" onblur="checkNmerReload(event, this)" onkeypress="checkNmerReload(event, this)">
                    </div>
                %else:
                    <%
                    levelElement = gui.TrackSelectElement(track, j)
                    %>
                    <div style="margin-left:${j}em">|_ ${levelElement.getHTML()} ${levelElement.getScript()}</div>
                %endif
            %endif
        %endfor
    %endif


    %if track.main and track.valueLevel(0) != 'galaxy' and track.selected():
        <%
        sti_val = params.get('show_info_'+track.nameMain, '0')
        if sti_val == '1':
            sti_class = 'hideInfo'
            sti_display = ''
        else:
            sti_class = 'showInfo'
            sti_display = 'display:none'

        %>
        <img class="${sti_class}" src="${h.url_for('/static/style/info_small.png')}" alt="Track information" title="Track information" onclick="getInfo(document.forms[0], this, '${track.nameMain}')"/>
        <div id="info_${track.nameMain}" class="infomessagesmall" style="${sti_display}"> ${hyper.getTrackInfo(genome, track.definition())} </div>
        <input type="hidden" name="show_info_${track.nameMain}" id="show_info_${track.nameMain}" value="${sti_val}">
    %endif

        <input type="hidden" name="${track.nameState}" id="${track.nameState}" value="${track.getState()}">

        ${self.help(track.nameMain, 'What is a genomic track?')}

        <input type="text" name="${track.nameMain}" id="${track.nameMain}" value="${track.asString()}" style="min-width:75%">

    </fieldset>


</%def>





<%def name="help(what, text)">
    <div style="text-align:right">
            <a href="#help_${what}" title="Help" onclick="getHelp('${what}')">${text}</a>
    </div>
    <div id="help_${what}" class="infomessagesmall help">help</div>
</%def>


<%def name="__trackChooser2(track, i, params)">
    <%
        genome = params.get('dbkey')
    %>
    <fieldset><legend>${track.legend}</legend>

    <%
    typeElement = gui.TrackSelectElement(track, 0)
    # reset stats parameter when changing track
    typeElement.onChange = "if ($('#_stats')){$('#_stats').val('');$('#stats').val('');}" + typeElement.onChange
    %>
    ${typeElement.getHTML()} ${typeElement.getScript()}

    %if track.valueLevel(0) == 'galaxy':
            <select name="${track.nameFile}" onchange="form.action='';form.submit()">
                ${galaxy.optionsFromHistory(gui.defaultFileTypes, params.get(track.nameFile))}
            </select>

    %else:
        %for j in range(1, 10):
            %if track.getTracksForLevel(j):
                <%
                levelElement = gui.TrackSelectElement(track, j)
                #print levelElement.getHTML()
                %>
                <div style="margin-left:${j}em">|_ ${levelElement.getHTML()} ${levelElement.getScript()}</div>
            %endif
        %endfor
    %endif
    %if track.main and track.valueLevel(0) != 'galaxy':
        <%
        sti_val = params.get('showtrackinfo'+str(i), '0')
        if sti_val == '1':
            sti_class = 'hideInfo'
            sti_display = ''
        else:
            sti_class = 'showInfo'
            sti_display = 'display:none'
        %>
        <img class="${sti_class}" src="${h.url_for('/static/style/info_small.png')}" alt="Track information" title="Track information" onclick="getInfo(document.forms[0], this, '#trackInfo${i}', '${i}')"/>
        <div id="trackInfo${i}" class="infomessagesmall" style="${sti_display}"> ${hyper.getTrackInfo(genome, track.definition())} </div>
        <input type="hidden" name="showtrackinfo${i}" id="showtrackinfo${i}" value="${sti_val}">
    %endif

        <input type="hidden" id="${track.nameMain}" name="${track.nameMain}" value="${track.asString()}">

    </fieldset>

</%def>

<%def name="genomeChooser(control, genomeElement = None, genome = None)">
    <%
    if genomeElement == None:
        genomeElement = control.getGenomeElement()
    if genome == None:
        genome = control.getGenome()
    %>

    Genome build: ${genomeElement.getHTML()} ${genomeElement.getScript()}
    <%
        sti_val = control.params.get('show_genome_info', '0')
        if sti_val == '1':
            sti_class = 'hideInfo'
            sti_display = ''
        else:
            sti_class = 'showInfo'
            sti_display = 'display:none'
        genomeInfo = hyper.getGenomeInfo(genome)

    %>
    %if genomeInfo:
        <img class="${sti_class}" src="${h.url_for('/static/style/info_small.png')}" alt="Genome info" title="Genome information" onclick="getGenomeInfo(document.forms[0], this, '${genome}')"/>
        <div id="genome_info" class="infomessagesmall" style="${sti_display}"> ${genomeInfo} </div>
        <input type="hidden" name="show_genome_info" id="show_genome_info" value="${sti_val}">
    %elif genome:
        %if genome != '?':
            <div class="errormessagesmall">
            ${genome} is not yet supported by HyperBrowser.<br>
        %else:
            <div class="warningmessagesmall">
        %endif
            Please select a genome build from the list above to continue.
            </div>
    %endif
</%def>

<%def name="accessDenied()">
    <div class="warningmessage">This functionality is only available to specific users. <br>Contact us if you need access.</div>
</%def>
