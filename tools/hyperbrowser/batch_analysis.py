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

import sys, os, getopt,types

from gold.application.GalaxyInterface import *

os.environ['DISPLAY'] = ':9.0'

def main():
    #print "running"
    input = sys.argv[1]
    output = sys.argv[2]
    genome = sys.argv[3]
    sys.stdout = open(output, "w", 0)
    # galaxy separates the lines by XX
    lines = input.split("XX")
    try:
        print '''<script type="text/javascript" src="/static/scripts/jquery.js"></script>
            <script type="text/javascript">
                var done = false;
                var job = { filename: "%s", pid: %d };

                var dead = document.cookie.indexOf("dead=" + job.pid) >= 0 ? true : false;
                                        
                function check_job() {
                    if (!done) {
                        if (!dead) {
                            $.getJSON("/hyper/check_job", job, function (status) {
                                    if (status.running) {
                                        location.reload(true);
                                    } else {
                                        document.cookie = "dead=" + job.pid;
                                        location.reload(true);
                                    }
                                }
                            );
                        } else {
                            alert("This job did not finish successfully: " + job.filename);
                        }
                    }
                }
                
                setTimeout("if (!done) check_job();", 2000);
            </script>
        ''' % (output, os.getpid())

        GalaxyInterface.runBatchLines(lines, output, genome)

    finally:
        print '<script type="text/javascript">done = true;</script>'
    
if __name__ == "__main__":
    main()
