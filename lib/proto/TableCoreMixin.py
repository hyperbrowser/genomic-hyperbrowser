from collections import OrderedDict


class TableCoreMixin(object):
    def tableFromDictionary(self, dataDict, columnNames=None, sortable=True,
                            tableId=None, expandable=False, visibleRows=6,
                            presorted=None, **kwargs):
        """Render a table from data in dataDict. Each key in dataDict is a row title,
        each value is a list of values, each corresponding to the column given with columnNames.

        If presorted is set to a number and tableId != None and sortable == True, that column will be presorted (using a hacky solution using jquery.
        """

        # transform dicts with a single value to a dict of lists for easier
        # sorting and html table generation
        dataDictOfLists = OrderedDict()
        for key, val in dataDict.iteritems():
            if isinstance(val, list):
                dataDictOfLists[key] = val
            elif isinstance(val, tuple):
                dataDictOfLists[key] = list(val)
            else:
                dataDictOfLists[key] = [val]

        if presorted is not None and presorted > -1:
            assert isinstance(presorted, int), 'presorted must be int'
            from quick.util import CommonFunctions
            dataDictOfLists = CommonFunctions.smartSortDictOfLists(
                dataDictOfLists, sortColumnIndex=presorted)

        tableClass = 'colored bordered'
        if expandable:
            assert tableId, 'Table ID must be set for expandable tables.'
            tableClass += ' expandable'

        self.tableHeader(headerRow=columnNames, sortable=sortable,
                         tableId=tableId,
                         tableClass=tableClass, **kwargs)

        for key, val in dataDictOfLists.iteritems():
            if isinstance(val, list):
                self.tableLine([key] + val)
            else:
                self.tableLine([key] + [val])

        self.tableFooter()

        # if tableId != None and sortable and presorted:
        #     # Javascript code for clicking on the column (so that it is sorted client side)
        #     # Hacky solution: Emulates a click on the header with a 500 ms delay so that sorttable.js is done first
        #     self._str += "<script>$(document).ready(function(){ setTimeout(function(){ $('#" + tableId + " .header')[" + str(presorted) + "].click();}, 500) })</script>"

        if expandable and len(dataDict) > visibleRows:
            self.tableExpandButton(tableId, len(dataDict),
                                   visibleRows=visibleRows)

        return self

    def tableFromDictOfDicts(self, dataDict, firstColName='', sortable=True,
                             tableId=None, expandable=False, visibleRows=6,
                             presorted=None, **kwargs):
        """
        # Note: it is assumed that dataDict is a full matrix, i.e. each element in
        # the dict is a dict of the same size.
        """

        assert isinstance(dataDict, OrderedDict) and \
               all(isinstance(x, OrderedDict) for x in dataDict.values()), \
            'dataDict must be an OrderedDict of OrderedDicts'

        colNames = []
        convertedDataDict = OrderedDict()

        for key1, val1 in dataDict.iteritems():
            if not colNames:
                colNames = [firstColName] + val1.keys()
            convertedDataDict[key1] = val1.values()

        self.tableFromDictionary(convertedDataDict,
                                 columnNames=colNames,
                                 sortable=sortable, tableId=tableId,
                                 expandable=expandable,
                                 visibleRows=visibleRows,
                                 presorted=presorted, **kwargs)

        return self

    def tableExpandButton(self, tableId, totalRows, visibleRows=6):
        self.script('''
function expandTable(tableId) {
    tblId = "#" + tableId;
    $(tblId).find("tr").show();
    btnDivId = "#toggle_table_" + tableId;
    $(btnDivId).find("input").toggle();
}

function collapseTable(tableId, visibleRows) {
    tblId = "#" + tableId;
    trScltr = tblId + " tr:nth-child(n + " + visibleRows + ")";
    $(trScltr).hide();
    btnDivId = "#toggle_table_" + tableId;
    $(btnDivId).find("input").toggle();
}

$(document).ready(function(){
    hiddenRowsSlctr = "table.expandable tr:nth-child(n + %s)";
    $(hiddenRowsSlctr).hide();
}
);''' % str(visibleRows + 2))  # '+2' for some reason (one of life's great mysteries)

        self._str += '''
<div id="toggle_table_%s" class="toggle_table_btn">
<input type="button" value="Expand table (now showing %s of %s rows)..." id="expand_table_btn" style="background: #F5F5F5;" onclick="expandTable('%s')"/>
<input type="button" value="Collapse table (now showing %s of %s rows)" id="collapse_table_btn" style="background: #F5F5F5; display: none;" onclick="collapseTable('%s', %s)"/>
''' % (tableId, visibleRows, totalRows, tableId, totalRows, totalRows, tableId, visibleRows + 1)
        return self
