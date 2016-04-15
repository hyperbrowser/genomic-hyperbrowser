from quick.webtools.imports.TrackSearchTool import TrackSearchTool

class Epigenome2TrackSearchTool(TrackSearchTool):
#    DATABASE_TRACK_ACCESS_MODULE_CLS = EncodeDatabaseTrackAccessModule
    def __new__(cls, *args, **kwArgs):
        return TrackSearchTool.__new__(Epigenome2TrackSearchTool, *args, **kwArgs)

    @staticmethod
    def getToolName():
        return "Roadmap Epigenomics"

    @classmethod
    def _getTableName(cls):
        return 'file_epigenome2'

    @classmethod
    def _getGlobalSQLFilter(cls):
        #return
        return "NOT url LIKE '%consolidatedImputed%'"
    
    @classmethod
    def _getClassAttributes(cls, db):
        attributes = []

        colList = db._db.getTableCols(cls.TABLE_NAME)
        for col in colList:
            attributes.append(col)
        attributes.remove('url')

        return attributes

    @classmethod
    def getColListString(cls):
        cols = cls.DB._db.correctColumNames\
        (cls.DB._db.getTableCols(cls.TABLE_NAME))
        colListString = ''
        cols.insert(0, cols.pop(cols.index('"url"')))
        for col in cols:
            colListString += col+','

        return cols,colListString.strip(',')
