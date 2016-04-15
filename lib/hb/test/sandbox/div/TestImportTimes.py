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

print '.'
import functools
import os
from urllib import unquote, quote
from config.Config import DEFAULT_GENOME#, brk
print '.'
from gold.application.StatRunner import StatRunner
print '.'
from gold.track.Track import Track
from gold.util.CommonFunctions import insertTrackNames, smartStrLower, getClassName, prettyPrintTrackName, createOrigPath
from quick.application.ProcTrackOptions import ProcTrackOptions
from quick.application.UserBinSource import UserBinSource
print ','
from quick.extra.CustomTrackCreator import CustomTrackCreator
from quick.extra.TrackExtractor import TrackExtractor
from gold.result.Results import Results
from quick.extra.FunctionCategorizer import FunctionCategorizer
from gold.statistic.ResultsMemoizer import ResultsMemoizer
print '.'
from gold.description.AnalysisDefHandler import AnalysisDefHandler
print '0'
#from gold.description.AnalysisManager import AnalysisManager
print '.5'
from quick.application.ExternalTrackManager import ExternalTrackManager
from gold.description.TrackInfo import TrackInfo
print 1
from tempfile import NamedTemporaryFile
import re
from gold.util.CustomExceptions import ShouldNotOccurError
from quick.util.CommonFunctions import extractIdFromGalaxyFn
print '2'
from gold.origdata.GenomeElementSource import GenomeElementSource
from quick.extra.OrigFormatConverter import OrigFormatConverter
from quick.util.GenomeInfo import GenomeInfo
import traceback
import shutil
from copy import copy
from gold.application.LogSetup import logging, HB_LOGGER, USAGE_LOGGER, usageAndErrorLogging, logException, detailedJobRunHandler
print '3'
