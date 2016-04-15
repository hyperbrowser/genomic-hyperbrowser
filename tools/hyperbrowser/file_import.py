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

import sys, os, shutil, base64

#from gold.application.GalaxyInterface import *
from config.Config import STATIC_PATH, GALAXY_FILE_PATH

def main():
    input = sys.argv[1]
    if not input.startswith('/'):
        input = base64.urlsafe_b64decode(input)
    input = os.path.abspath(input)
    output = sys.argv[2]
    datatype = sys.argv[3]

    if (input.startswith(STATIC_PATH) or \
        os.path.realpath(input).startswith(os.path.realpath(GALAXY_FILE_PATH))) \
        and input.endswith('.' + datatype):
            shutil.copy(input, output)
    else:
        print input, 'not allowed'

if __name__ == "__main__":
    main()


