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
<%inherit file="/base.mako"/>

<%def name="title()">
    ${self.title()}
</%def>

<%def name="stylesheets()">
    ${h.css('base')}
    ${h.css('proto')}
</%def>

<%def name="javascripts()">
    ${h.js( "libs/jquery/jquery")}
    ${self.head()}
</%def>

<%def name="javascript_app()"></%def>

<%def name="head()"></%def>
<%def name="action()"></%def>
<%def name="toolHelp()"></%def>
<%def name="help(what)">
    <a href="#help_${what}" title="Help" onclick="getHelp('${what}')" class="help">?</a>
    <div id="help_${what}" class="infomessagesmall help">help</div>
</%def>

    
    <div id="__disabled"></div>
    <div class="toolForm">
    <div class="toolFormTitle">${self.title()}</div>
        <div class="toolFormBody">
            ${self.body()}
        </div>
    </div>
    <div class="toolHelp">
        <div class="toolHelpBody">
            ${self.toolHelp()}
        </div>
    </div>

