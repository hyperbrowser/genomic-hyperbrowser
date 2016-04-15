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

import unittest

import psycopg2
import testing.postgresql

from quick.trackaccess.DatabaseTrackAccessModule import DatabaseAdapter

class TestPostgresDatabaseAdapter(unittest.TestCase):
    def setUp(self):
        self.postgresql = testing.postgresql.Postgresql()

    def testCreateTableFromList(self):
        db = DatabaseAdapter(**self.postgresql.dsn())
        db.createTableFromList('testtable', cols = ['a', 'b'], pk = 'b')
        self.assertEquals(['a', 'b'], db.getTableCols('testtable'))

    def runTest(self):
        pass

    def tearDown(self):
        self.postgresql.stop()


if __name__ == "__main__":
    #TestDatabaseTrackAccessModule().run()
    unittest.main()
