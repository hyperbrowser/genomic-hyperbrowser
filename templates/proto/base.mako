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
    ${h.css('proto/base')}
    <style type="text/css">
    .showInfo {
        cursor: pointer;
    }
    .hideInfo {
        cursor: pointer;
    }
    .hidden {
        display: none;
    }
	fieldset {
        padding: 8px;
		margin-top: 6px;
		margin-bottom: 6px;
    }
	textarea {
		margin-top: 6px;
		margin-bottom: 6px;
    }
	input {
		margin-top: 6px;
		margin-bottom: 6px;	
	}
	.genome {
		float:left;
		margin-top:10px;
		margin-bottom:10px
	}
    .option {
    }
    a.help {
        font-weight: bold;
        text-decoration: none;
        font-size: 15px;
    }
    div.help {
        display: none;
        b__order: dashed 1px;
        padding: 2px;
        background-image: none;
    }
    div.toolHelp {
    	margin-top: 15px;
    }
    hr.space {
    	margin-top: 15px;
    	margin-bottom: 15px;
    }
    a.option {
            cursor: pointer;
            display: block;
            text-decoration: none;
            padding: 2px;
            width: 99%;
    }
    a.option:hover {
        background-color: #006;
        color: #fff;
    }
    a.selected {
        border: solid 1px #006;
    }
    div.options {
        width: 90%;
        height: auto;
        overflow: auto;
        display: none;
        position: absolute;
        border: 2px outset;
        background-color: #fff;
    }
	.infomessagesmall {
	    margin: 5px;
	}
    .invisible {
        visibility: hidden;
    }
    .options label {
        display: block;
    }
    #_stats_text {
        font-weight: bold;
    }
	td {
	    padding: 20px;
            white-space: normal;
	}
    table {
        max-width: 100%;
        text-align: center;
        margin-left: auto;
        margin-right: auto;
        table-layout:auto;
        word-wrap:break-word;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    h4 {
        padding-top: 20px;
        text-align: center;
    }
    
    #__disabled
    {
	display:none;
	position:absolute;
	top:0px;
	left:0px;
	width: 100%;
	height: 100%;
	opacity: 0.50;
	filter:alpha(opacity=50);
	z-Index:1000;
        background-color: #EEEEEE;
        background-image: url("static/proto/images/rays.gif");
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center center;
        background-size: 32px;
    }

    </style>
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

