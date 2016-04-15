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

#!/usr/bin/env python
import os
import sys
import third_party.safeshelve as safeshelve
from config.Config import DATA_FILES_PATH

commands = safeshelve.open(DATA_FILES_PATH + os.sep +'CommandCatalog.shelve')

if len(sys.argv) == 1:
    print 'syntax: '
    print 'to add: add [name] [command]'
    print 'to remove: rm [name] [command]'
    print 'to print: print [name]'    
    print 'to use: [name]'
    print 'available commands: '
    print ','.join(commands.keys() )
    sys.exit(0)
    
if sys.argv[1] == 'add':
    assert(len(sys.argv) >= 4)
    commands[sys.argv[2]] = ' '.join(sys.argv[3:])
elif sys.argv[1] == 'rm':
    assert(len(sys.argv) == 3)
    del commands[sys.argv[2]]
elif sys.argv[1] == 'print':
    assert(len(sys.argv) == 3)
    print commands[sys.argv[2]] 
else:
    assert(len(sys.argv) == 2)
    command = commands[sys.argv[1]]
    commands.close()
    os.system( command )
    
commands.close()