class Cube():

    @classmethod
    def addSelectList(cls, fileNameList, optionsToUniqueList):
        js = """<form name="classic">"""
        for index, fileName in enumerate(fileNameList):
            js += cls._addOptionToSelectList(fileName, index)
            js += "<br \><br \>"
        js += """</form>"""
        js += """<script type = "text/javascript" >"""

        for index, fileName in enumerate(fileNameList):
            js += cls._addOptionsToUniqueSelectOptionList(index, optionsToUniqueList[index])

        js += """var chocieslistRowColumn=document.classic.choicesRowColumn"""

        for index, fileName in enumerate(fileNameList):
            js += cls._fillSecondSelectOption(index, 'fV'+str(index)+'U')
        for index, fileName in enumerate(fileNameList):
            js += cls._updateChoices(index)

        js += cls._addExtraJS(len(fileNameList))

        js += cls._summarizeTable()

        return js

    @classmethod
    def _addOptionToSelectList(cls, fieldName, index):
        js = cls._fillFirstSelect("How to treat " + str(fieldName), index)
        js += cls._fillSecondSelect(index)
        return js

    @classmethod
    def _fillFirstSelect(cls, firstSelectTitle, idNum):
        js = firstSelectTitle + '''
        <select name="dimensions''' + str(idNum) + '''" id="dimensions''' + str(
            idNum) + '''" size="1" onClick="onClickChoices()" onChange="updateChoices''' + str(
            idNum) + '''(this.selectedIndex)" style="width: 150px">
        <option value="0">---Select---</option>
        <option value="1">Select one value</option>
        <option value="-2">Show results for each value</option>
        <option value="-1">Sum across this dimension</option>
        </select>
        '''
        return js

    @classmethod
    def _fillSecondSelect(cls, idNum):
        js = '''
        <select name="choices''' + str(idNum) + '''" id="choices''' + str(idNum) + '''" size="1" style="width: 100px"  onClick="onClickChoices()">
        </select>'''
        return js


    @classmethod
    def _addOptionsToUniqueSelectOptionList(cls, index, optionsToUniqueList):

        js = ''
        js += cls._addSecondSelectInfo(index)
        js += """ folderValue"""+str(index)+"""Unique =""" + str(optionsToUniqueList) + ";"
        js += """
            var fV"""+str(index)+"""U = new Array(folderValue"""+str(index)+"""Unique.length)
            fV"""+str(index)+"""U[0] = "Select value|0"
            for(i=0;i<folderValue"""+str(index)+"""Unique.length;i++)
            {
                j=i+1
                fV"""+str(index)+"""U[j] = folderValue"""+str(index)+"""Unique[i] +'|' + folderValue"""+str(index)+"""Unique[i]
            }
            j=j+1
            """
        return js

    @classmethod
    def _addSecondSelectInfo(cls, idNum):
        js = '''document.getElementById("choices''' + str(idNum) + '''").style.visibility = "hidden";
        var dimensionslist''' + str(idNum) + '''=document.classic.dimensions''' + str(idNum) + ''';
        var choiceslist''' + str(idNum) + '''=document.classic.choices''' + str(idNum) + ''';

        '''
        return js

    @classmethod
    def _fillSecondSelectOption(cls, idNum, data):
        js = '''
        var choices''' + str(idNum) + '''=new Array()
        choices''' + str(idNum) + '''[1]=''' + data
        return js

    @classmethod
    def _updateChoices(cls, idNum):
        js = '''
        function updateChoices''' + str(idNum) + '''(selectedChoicesGroup)
        {
            hideTable()
            document.getElementById("choices''' + str(idNum) + '''").style.visibility = "hidden";        
            if(selectedChoicesGroup  == 1)
            {
                document.getElementById("choices''' + str(idNum) + '''").style.visibility = "visible";       

                choiceslist''' + str(idNum) + '''.options.length=0
                if (selectedChoicesGroup>0)
                {
                    for (i=0; i<choices''' + str(idNum) + '''[selectedChoicesGroup].length; i++)
                    {
                        choiceslist''' + str(idNum) + '''.options[choiceslist''' + str(
            idNum) + '''.options.length]=new Option(choices''' + str(
            idNum) + '''[selectedChoicesGroup][i].split("|")[0], choices''' + str(idNum) + '''[selectedChoicesGroup][i].split("|")[1])
                    }
                }
                var dimensions''' + str(
            idNum) + ''' = document.getElementById("dimensions''' + str(idNum) + '''");
                dimensions''' + str(idNum) + '''.options[selectedChoicesGroup].setAttribute("selected", "selected");
            }
        }
        '''
        return js

    @classmethod
    def _addExtraJS(cls, indexLen):
        js = ''
        js += """
            function updateChoicesRowColumn(selectedChoicesGroupRowColumn, selDim)
            {
                hideTable()

                var ch = document.getElementById("choices1");
                var selCh = ch.selectedIndex
                selDim=selDim-1

                if(selCh != 0 && selCh != 3)
                {
                    document.getElementById("choicesRowColumn").style.visibility = "visible";

                    chocieslistRowColumn.options.length=0
                    if (selectedChoicesGroupRowColumn>0)
                    {
                        for (j=0; j<choicesRowColumn.length; j++)
                        {
                            if(j == selDim)
                            {
                                for (i=0; i<choicesRowColumn[selDim][selectedChoicesGroupRowColumn].length; i++)
                                {
                                    chocieslistRowColumn.options[chocieslistRowColumn.options.length]=new Option(choicesRowColumn[j][selectedChoicesGroupRowColumn][i].split("|")[0], choicesRowColumn[j][selectedChoicesGroupRowColumn][i].split("|")[1])
                                }
                            }
                        }
                    }
                }
                else
                {
                    document.getElementById("choicesRowColumn").style.visibility = "hidden";
                    if(selCh == 3)
                    {
                        showAllTables(selDim)
                    }
                }
            }

            function hideTable()
            {
                var childDivs = document.getElementById('results').getElementsByTagName('div');
                for( i=0; i< childDivs.length; i++ )
                {
                    var childDiv = childDivs[i];
                    var resultsDiv = document.getElementById(childDiv.id);
                    resultsDiv.setAttribute('class', 'hidden');
                }
            }
            function showAllTables(selDim)
            {
                selDim = selDim +1
                var childDivs = document.getElementById('results').getElementsByTagName('div');
                for( i=0; i< childDivs.length; i++ )
                {
                    var childDiv = childDivs[i];
                    temp = childDiv.id
                    temp = temp.replace("[", "");
                    temp = temp.replace("]", "");
                    var tab = new Array();
                    tab = temp.split(",");

                    if(tab[0] == selDim)
                    {
                        var resultsDiv = document.getElementById(childDiv.id);
                        resultsDiv.setAttribute('class', 'visible');
                    }
                }
            }
            """

        js += """
            function onClickChoices()
            {
                //hideTable();

                """
        for index in range(0, indexLen):
            js += cls._addSelectedIndex(index)

        for index in range(0, indexLen):
            js += cls._addSelectedDimension(index)

        js+= """ if (  """
        for index in range(0, indexLen):
            js += """selDim"""+str(index)+""" !=0  """
            if indexLen -1 != index:
                js += " && "
        js += """ )
                {
                """
        js += """var divName = []; """
        for index in range(0, indexLen):
            js += """ divName.push(selDim"""+str(index) + """);"""

        js += """
        
                tab = summarizeTable(data, divName);
                tab = changeDataIntoProperTable(tab);
                console.log('tab', tab);
                generateTable(tab);
              }
              """

        js += """
                console.log(divName);
                //var resultsDiv = document.getElementById(divName);
                //resultsDiv.setAttribute('class', 'visible');
            }

            

            </script>
            """
        return js

    @classmethod
    def _addSelectedIndex(cls, index):
        return """
                var ch"""+str(index)+""" = document.getElementById('choices"""+str(index)+"""');
                var selCh"""+str(index)+""" = ch"""+str(index)+""".value
                """

    @classmethod
    def _addSelectedDimension(cls, index):
        js = """var dim"""+str(index)+""" = document.getElementById('dimensions"""+str(index)+"""');
                var selDim"""+str(index)+""" = dim"""+str(index)+""".value"""
        js+= """
                if (selDim"""+str(index)+""" == -2 || selDim"""+str(index)+""" == -1) 
                {
                	selDim"""+str(index)+""" = parseInt(selDim"""+str(index)+""");
                }
                else if (selDim"""+str(index)+""" == 1)
                {
                	if(selCh"""+str(index)+""" != 0)
                	{
                		selDim"""+str(index)+""" = """ + """selCh"""+str(index) + """;
                	}
                }
        """
        return js

    @classmethod
    def _summarizeTable(cls):
        js = """
        <script type = "text/javascript" >
        var data = [['ata', '1 - 243-2--eta-.bed--TG', 863], ['ata', '1 - 243-2--eta-.bed--TA', 781]];
        console.log(data);
        
        function changeDataIntoProperTable(data)
       {
       	   res = {};
       	   for (var d in data)
       	   {
                if not d[0] in res.keys():
                    res[d[0]] = OrderedDict()
                if not d[1] in res[d[0]].keys():
                    res[d[0]][d[1]] = 0
                res[d[0]][d[1]] = d[2]
            }
       }
        
       function generateTable(tab) 
       {
		  var body = document.getElementsByTagName("body")[0];
		  var div = document.createElement("div");
		  div.setAttribute('id', 'results');
		  body.appendChild(div);
 		  var tbl = document.createElement("table");
  		  var tblBody = document.createElement("tbody");
 	      
 	      for (var i = 0; i < tab.length; i++) 
  			{
    			var row = document.createElement("tr");
	    		for (var j = 0; j < tab[i].length; j++) 
    			{
     			   var cell = document.createElement("td");
      		   	   var cellText = document.createTextNode(tab[i][j]);
      			   cell.appendChild(cellText);
      		   	   row.appendChild(cell);
    		     }
		       tblBody.appendChild(row);
  			}
 
  			tbl.appendChild(tblBody);
  	
  			body.appendChild(tbl);

		}
		
        function summarizeTable(flat, operations)
        {
        	var operationsReverse = operations.reverse()
        	
        	var i = operationsReverse.length-1;
        	for (var k = 0; k < operationsReverse.length; k++) 
        	{	
        		var op = operationsReverse[k];
        		
        		if ((op >= 0) || (op.length >= 0))
        		{	
        			var partFlat = [];
        			for (j = 0; j < flat.length; j++) 
        			{
        				if(flat[j][i] == op)
        				{
        					var part = (flat[j].slice(0,i)).concat(flat[j].slice(i+1,flat.length));	
        					partFlat.push(part);
        				}
        			}
        			flat = partFlat;
        		}
        		else if(op == -1)
        		{
        			var partFlat = [];
        			for (var j = 0; j < flat.length; j++) 
        			{
        				partFlat[j]= flat[j].slice(0,i).concat(flat[j].slice(i+1,flat.length+1));
        			}
        			flat = partFlat;
        			
        			var myDict = {};
        			for (var x in flat) 
        			{
        				var value = parseFloat(flat[x][flat[x].length-1]);
        				var key = flat[x].slice(0,flat[x].length-1);
        				if (myDict[ key ] == undefined)
        				{
        					myDict[ key ] = 0;
        				}
	        			myDict[ key ] += value;
        			}
        			
        			partFlat = [];
        			var c = 0;
        			
        			for (var x in myDict)
        			{
        				if ( x == "")
        				{
        					partFlat[c] = [myDict[x]];
        				}
        				else
        				{
        					partFlat[c] = x.split(',');
        					partFlat[c].push(myDict[x]);
        				}
        				c = c+1;
        			}
        			flat = partFlat;
        			
        		}
        		i = i - 1;
        	}
        	return flat;
        }
        
        </script>
        
        """
        return js