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
        <option value="2">Show results for each value</option>
        <option value="3">Sum across this dimension</option>
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
                fV"""+str(index)+"""U[j] = folderValue"""+str(index)+"""Unique[i] +'|' + j
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
            function showAllRowsColumn(selDim, selCh)
            {
                var childDivs = document.getElementById('results').getElementsByTagName('div');
                for( i=0; i< childDivs.length; i++ )
                {
                    var childDiv = childDivs[i];
                    temp = childDiv.id
                    temp = temp.replace("[", "");
                    temp = temp.replace("]", "");
                    var tab = new Array();
                    tab = temp.split(",");


                    if(tab[0] == selDim && tab[1] == selCh)
                    {
                        var resultsDiv = document.getElementById(childDiv.id);
                        resultsDiv.setAttribute('class', 'visible');
                    }
                }
            }"""

        js += """
            function onClickChoices()
            {
                hideTable();

                """
        for index in range(0, indexLen):
            js += cls._addSelectedIndex(index)

        for index in range(0, indexLen):
            js += cls._addSelectedDimension(index)


        #""" folderValue"""+str(index)+"""Unique[selCh""" folderValue"""+str(index)+"""Unique-1]

        js += """var divName = '[' """
        for index in range(0, indexLen):
            js += """ + selDim"""+str(index)+""" + ', ' + selCh"""+str(index)
            if indexLen-1 != index:
                js += """ + ', ' """
        js += """+ ']';"""

        js += """
                //var divName = '[' + selDim0 + ', ' + selCh0 + ', ' + selDim1 + ', ' + selCh1 +  ']';
                console.log(divName);
                var resultsDiv = document.getElementById(divName);
                resultsDiv.setAttribute('class', 'visible');
            }

            function onClickChoicesRowColumn(dimensions, choices, choicesRowColumnIndex)
            {
                if(choicesRowColumnIndex>0)
                {
                    numEl=choicesRowColumn[dimensions-1][choices].length
                    numEl=numEl-1

                    if(choicesRowColumnIndex!=numEl)
                    {
                        choicesRowColumnIndex = choicesRowColumnIndex - 1
                        var divName = '[' + dimensions + ', ' + choices + ', ' + choicesRowColumnIndex + ']'
                        var resultsDiv = document.getElementById(divName);
                        resultsDiv.setAttribute('class', 'visible');

                        var childDivs = document.getElementById('results').getElementsByTagName('div');
                        for( i=0; i< childDivs.length; i++ )
                        {
                            var childDiv = childDivs[i];
                            if(childDiv.id != divName)
                            {
                                var resultsDiv = document.getElementById(childDiv.id);
                                resultsDiv.setAttribute('class', 'hidden');
                            }          
                        }
                    }
                    else
                    {
                        showAllRowsColumn(dimensions, choices)
                    }
                }
            }

            </script>
            """
        return js

    @classmethod
    def _addSelectedIndex(cls, index):
        return """
                var ch"""+str(index)+""" = document.getElementById('choices"""+str(index)+"""');
                var selCh"""+str(index)+""" = ch"""+str(index)+""".selectedIndex
                """

    @classmethod
    def _addSelectedDimension(cls, index):
        js = """var dim"""+str(index)+""" = document.getElementById('dimensions"""+str(index)+"""');
                var selDim"""+str(index)+""" = dim"""+str(index)+""".selectedIndex"""
        js+= """
                if(selCh"""+str(index)+"""!=-1)
                {
                    selCh"""+str(index)+""" = selCh"""+str(index)+"""-1;
                }
        """
        js+= """
                if (selDim"""+str(index)+""" == 2 || selDim"""+str(index)+""" == 3)
                {
                    selCh"""+str(index)+"""=-1;
                }
        """
        return js

    @classmethod
    def _summarizeTable(cls):
        js = """
        var data = [['ata', '1 - 243-2--eta-.bed--TG', 863], ['ata', '1 - 243-2--eta-.bed--TA', 781]];
        console.log(data);
        
        var flat = data;
        var operations = [-1, -1, -2];
        function summarizeTable(flat, operations)
        {
        	console.log('flat', flat);
        	console.log('operations', operations);
        	
        	var operationsReverse = operations.reverse()
        	console.log('operationsReverse', operationsReverse, operationsReverse.length);
        	
        	var i = operationsReverse.length-1;
        	for (var k = 0; k < operationsReverse.length; k++) 
        	{	
        		var op = operationsReverse[k];
        		
        		console.log('op', op, 'i', i);
        		
        		if (op >= 0)
        		{
        			for (j = 0; j < flat.length; j++) 
        			{
        				if(flat[j] == op)
        				{
        					flat = [flat[j].slice(0,i) + flat[j].slice(i+1,flat.length)];
        				}
        			}
        		}
        		else if(op == -1)
        		{
        			var partFlat = [];
        			console.log('flat.length', flat.length, flat);
        			for (var j = 0; j < flat.length; j++) 
        			{
        				//console.log('flat[j]', flat[j], flat[j].slice(0,i), flat[j].slice(i+1,flat.length+1), 0, i, i+1,flat.length);
        				partFlat[j]= flat[j].slice(0,i).concat(flat[j].slice(i+1,flat.length+1));
        				console.log(i, 'partFlat', partFlat, flat[j].slice(0,i), flat[j].slice(i+1,flat.length+1));
        			}
        			flat = partFlat;
        			console.log('-----', flat, flat.length);
        			
        			
        			var myDict = {};
        			for (var j = 0; j < flat.length; j++) 
        			{
        				//console.log('j-beforeFirst', j, myDict[ key ], key, value);
        				var value = parseFloat(flat[j][flat.length-1]);
        				var key = flat[j].slice(0,flat.length-1);
        				//console.log('j-beforeSecond', j, myDict[ key ], key, value);
        				if (myDict[ key ] == undefined)
        				{
        					myDict[ key ] = 0;
        				}
        				//console.log('j-afterFirst', j, myDict[ key ], key, value);
	        			myDict[ key ] += value;
    	    			//console.log('j-afterSecond', j, myDict[ key ], key, value);
        								
        			}
        			
        			console.log('myDict', myDict, myDict.length);
        			partFlat = [];
        			var c = 0;
        			
        			for (var x in myDict)
        			{
        				console.log('x', x, myDict[x], Array(x, myDict[x]));
        				if ( x == "")
        				{
        					partFlat[c] = [myDict[x]];
        				}
        				else
        				{
        					partFlat[c] = Array(x, myDict[x]);
        				}
        				c = c+1;
        			}
        			flat = partFlat;
        			
        			console.log('i=' ,i, 'flat', flat);
        			
        		}
        		i = i - 1;
        	}
        	return flat;
        }
        
        
        
        aa = summarizeTable(flat, operations);
        console.log('flatAfter', aa);
        """
        return js