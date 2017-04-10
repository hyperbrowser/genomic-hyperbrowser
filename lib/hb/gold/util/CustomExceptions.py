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

class Warning(Exception):
    pass

class InvalidFormatWarning(Warning):
    pass

class InvalidFormatError(Exception):
    pass

class IncompatibleTracksError(Exception):
    pass

class AbstractClassError(Exception):
    pass

class SplittableStatNotAvailableError(Exception):
    pass

class NotSupportedError(Exception):
    pass

class ShouldNotOccurError(Exception):
    pass

class NotValidGESequence(Exception):
    pass

class EmptyGESourceError(Exception):
    pass

class InvalidRunSpecException(Exception):
    pass

class CentromerError(Exception):
    pass

class TooLargeBinError(Exception):
    pass

class TooSmallBinError(Exception):
    pass

class IncompatibleAssumptionsError(Exception):
    pass

class NoneResultError(Exception):
    pass
    
class FileLockError(Exception):
    pass

class NoMoreUniqueValsError(Exception):
    pass

class ArgumentValueError(Exception):
    pass

class MissingEntryError(Exception):
    pass

class ExecuteError(Exception):
    pass

class SilentError(Exception):
    pass

class IdenticalTrackNamesError(Exception):
    pass
    
class NotIteratedYetError(Exception):
    pass
    
class OutsideBoundingRegionError(Exception):
    pass
    
class BoundingRegionsNotAvailableError(Exception):
    pass

class LackingTsResultsError(Exception):
    pass

class InvalidStatArgumentError(Exception):
    pass