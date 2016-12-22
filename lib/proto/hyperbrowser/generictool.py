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
#
# instance is dynamically imported into namespace of <modulename>.mako template (see web/controllers/hyper.py)

# import sys, os, json
# from collections import namedtuple, OrderedDict, defaultdict
# from urllib import quote, unquote
# from quick.webtools.GeneralGuiTool import HistElement
# from proto.hyperbrowser.StaticFile import StaticImage
# from proto.hyperbrowser.HtmlCore import HtmlCore
# from config.Config import URL_PREFIX
# from gold.application.LogSetup import usageAndErrorLogging
# from gold.util.CommonFunctions import getClassName
from proto.generictool import GenericToolController
from HyperBrowserControllerMixin import HyperBrowserControllerMixin
# from gold.application.GalaxyInterface import GalaxyInterface


class HBGenericToolController(HyperBrowserControllerMixin, GenericToolController):
    def _init(self):
        super(HBGenericToolController, self)._init()

def getController(transaction = None, job = None):
    return HBGenericToolController(transaction, job)
