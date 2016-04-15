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

import inspect
import os
import gold.statistic
import quick.statistic
from gold.statistic.MagicStatFactory import MagicStatFactory

def importStats(branch):
    statFiles = [fn for fn in os.listdir(globals()[branch].__dict__['statistic'].__path__[0]) \
                 if fn.endswith('Stat.py')]
    
    for statFile in statFiles:
        statName = os.path.splitext(statFile)[0]
#        print statName
        module = __import__('.'.join([branch, 'statistic', statName]), globals(), locals(), ['*'])
        globals().update(module.__dict__)
        
importStats('gold')
importStats('quick')

STAT_CLASS_DICT = dict([cls.__name__, cls] for cls in globals().values() \
                  if inspect.isclass(cls) and issubclass(cls, MagicStatFactory) and cls!=MagicStatFactory)
