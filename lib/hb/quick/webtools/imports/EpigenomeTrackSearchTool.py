from quick.webtools.imports.TrackSearchTool import TrackSearchTool
from quick.trackaccess.DatabaseTrackAccessModule import DatabaseTrackAccessModule
from quick.webtools.GeneralGuiTool import GeneralGuiTool

class EpigenomeTrackSearchTool(TrackSearchTool):
#    DATABASE_TRACK_ACCESS_MODULE_CLS = EncodeDatabaseTrackAccessModule
    def __new__(cls, *args, **kwArgs):
        return TrackSearchTool.__new__(EpigenomeTrackSearchTool, *args, **kwArgs)
    
    @staticmethod
    def getToolName():
        return "Roadmap Epigenomics (old version)"
    
    @classmethod
    def _getTableName(cls):
        return 'file_epigenome'
    
    @classmethod
    def _getClassAttributes(cls, db):
        attributes = []
        
        colList = db._db.getTableCols(cls.TABLE_NAME)   
        for col in colList:
            attributes.append(col)
        attributes.remove('url')
        attributes.remove('hb_datatype')        
        return attributes

    @classmethod
    def getColListString(cls):
        cols = cls.DB._db.correctColumNames\
        (cls.DB._db.getTableCols(cls.TABLE_NAME))
        colListString = ''
        cols.insert(0, cols.pop(cols.index('"url"')))
        cols.insert(1, cols.pop(cols.index('"hb_datatype"')))
        for col in cols:
            colListString += col+','
        
        return cols,colListString.strip(',')
