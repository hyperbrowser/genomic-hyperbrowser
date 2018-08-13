class Cube():

    @classmethod
    def addSelectList(cls, fileNameList, optionsToUniqueList, data, divId, statNum):

        js = ''

        if statNum == 0:
            js += cls._visualizeResultsAddLib()

        #create form
        js += """<form id='""" + str(divId) + 'form' +  """' name="classic">"""
        for index, fileName in enumerate(fileNameList):
            js += cls._addOptionToSelectList(fileName, index, data, divId, statNum)
            js += "<br \><br \>"
        js += """</form>"""
        js += """<script type = "text/javascript" >"""

        #fill the form
        for index, fileName in enumerate(fileNameList):
            js += cls._addOptionsToUniqueSelectOptionList(index, optionsToUniqueList[index], statNum)

        js += """var chocieslistRowColumn"""+str(statNum)+"""=document.classic.choicesRowColumn"""+str(statNum)

        # fill the form
        for index, fileName in enumerate(fileNameList):
            js += cls._fillSecondSelectOption(index, 'fV'+str(statNum)+str(index)+'U', statNum)


        #update choices
        if statNum == 0:
            js += cls._addExtraJS(len(fileNameList))

        js += "</script>"
        js += """
        <div>
        <b>Options for presenting results: </b>
        </div>
        <div>
        """

        js += '''<input onchange="readDataFromTable(''' + str(divId) + ''', ''' + str(statNum) + ''', trans = true)" type="checkbox" id ="transpose''' + str(statNum) + '''" name="transpose''' + str(statNum) + '''" value="yes" \>Transpose tables and plots'''
        js += """</div><div>"""
        js += '''<input onchange="readDataFromTable(''' + str(divId) + ''', ''' + str(statNum) + ''')" type="checkbox" id ="series''' + str(statNum) + '''" name="series''' + str(statNum) + '''" value="yes" \>Show all series as one in the plots'''
        js += """</div>"""
        js += '''<div id="zerosDiv''' + str(statNum) + '''" style="display:none">'''
        js += '''<input onchange="readDataFromTable(''' + str(divId) + ''', ''' + str(statNum) + ''')" type="checkbox" id ="zeros''' + str(statNum) + '''" name="zeros''' + str(statNum) + '''" value="yes" \>Remove zeros from plots'''
        js += """</div>"""

        js += cls._addTransposePossibility(statNum)

        if statNum == 0:
            js += cls._addTransposePossibilityFunctions(statNum)
            js += cls._allScripts()
            js += cls._updateChoices()

        return js

    @classmethod
    def _addOptionToSelectList(cls, fieldName, index, data, divId, statNum):
        js, idNumFS = cls._fillFirstSelect("How to treat " + str(fieldName) + ": ", index, data, divId, statNum)
        js += cls._fillSecondSelect(index, data, divId, idNumFS, statNum)
        return js

    @classmethod
    def _fillFirstSelect(cls, firstSelectTitle, idNum, data, divId, statNum):
        js = firstSelectTitle
        js += '<select class="dimension" name="dimensions' + str(statNum) + str(idNum) + '" id="dimensions' + str(statNum) + str(idNum) + '" size="1" onClick="onClickChoices(' + str(statNum) + ',' + str(idNum) + ',' + str(data) + ',' + "'" + str(divId) + "'" + ')" onChange="updateChoices(' + str(statNum) + ',' + str(idNum) + ', this.selectedIndex, ' + "'" + str(divId) + "'" + ')" style="width: 150px">'
        js += '''
        <option value="0">---Select---</option>
        <option value="1">Select one value</option>
        <option value="-2">Show results for each value</option>
        <option value="-1">Sum across this dimension</option>
        </select>
        '''
        return js, idNum

    @classmethod
    def _fillSecondSelect(cls, idNum, data, divId, idNumFS, statNum):
        js = '<select class="dimension" name="choices' + str(statNum) + '' + str(idNum) + '" id="choices' + str(statNum) + str(idNum) + '" size="1" style="width: 100px"  onClick="onClickChoices(' + str(statNum) + ',' + str(idNumFS) + ',' + str(data) + ',' + "'" + str(divId) + "'" + ')"></select>'
        return js


    @classmethod
    def _addOptionsToUniqueSelectOptionList(cls, index, optionsToUniqueList, statNum):

        js = ''
        js += cls._addSecondSelectInfo(index, statNum)
        js += """ folderValue"""+str(statNum)+str(index)+"""Unique =""" + str(optionsToUniqueList) + ";"
        js += """
            var fV"""+str(statNum)+str(index)+"""U = new Array(folderValue"""+str(statNum)+str(index)+"""Unique.length)
            fV"""+str(statNum)+str(index)+"""U[0] = "Select value|0"
            for(i=0;i<folderValue"""+str(statNum)+str(index)+"""Unique.length;i++)
            {
                j=i+1
                fV"""+str(statNum)+str(index)+"""U[j] = folderValue"""+str(statNum)+str(index)+"""Unique[i] +'|' + folderValue"""+str(statNum)+str(index)+"""Unique[i]
            }
            j=j+1
            """
        return js

    @classmethod
    def _addSecondSelectInfo(cls, idNum, statNum):
        js = '''document.getElementById("choices''' + str(statNum) + str(idNum) + '''").style.visibility = "hidden";
        var dimensionslist''' + str(statNum) + str(idNum) + '''= document.getElementById("dimensions''' + str(statNum) + str(idNum) + '''");
        var choiceslist''' + str(statNum) + str(idNum) + '''= document.getElementById("choices''' + str(statNum) + str(idNum) + '''");

        '''
        return js

    @classmethod
    def _fillSecondSelectOption(cls, idNum, data, statNum):
        js = '''
        var choices'''+ str(statNum) + str(idNum) + '''=new Array()
        choices'''+ str(statNum) + str(idNum) + '''[1]=''' + data

        return js

    @classmethod
    def _updateChoices(cls):
        js = '''
        <script>
        function updateChoices(statNum, idNum, selectedChoicesGroup, divId)
        {
            hideTable(statNum)
            
            document.getElementById("choices"+statNum+idNum).style.visibility = "hidden";        
            if(selectedChoicesGroup  == 1)
            {
                document.getElementById("choices"+statNum+idNum).style.visibility = "visible";    
                var choiceslist = eval("choiceslist"+statNum+idNum);   

                choiceslist.options.length=0
                if (selectedChoicesGroup>0)
                {
                    var choices = eval("choices"+statNum+idNum);
                    for (i=0; i<choices[selectedChoicesGroup].length; i++)
                    {
                        choiceslist.options[choiceslist.options.length]=new Option(choices[selectedChoicesGroup][i].split("|")[0], choices[selectedChoicesGroup][i].split("|")[1])
                    }
                }
                var dimensions = document.getElementById("dimensions"+statNum+idNum);
                dimensions.options[selectedChoicesGroup].setAttribute("selected", "selected");
            }
        }
        </script>
        '''
        return js

    @classmethod
    def _addExtraJS(cls, indexLen):
        js = ''
        js += """
            

            function removeElement(el) 
            {
    			el.parentNode.removeChild(el);
			}

            function hideTable(statNum)
            {
            	var tab = document.getElementById('results'+statNum);
            	
            	if (tab == null)
            	{
            	}
            	else
            	{
            		removeElement(tab);
            	}
				
            }
            
           
            """

        js += """
            function onClickChoices(statNum, idNumFS, data, divId)
            {
                hideTable(statNum);

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
                //console.log('data', data);
                //console.log('divName', divName);
                tab = summarizeTable(data, divName);
                var dv = changeDivName(divName);
                changeDataIntoProperDict(tab, dv, divId, statNum);
              }
              """

        js += """}"""

        return js

    @classmethod
    def _addSelectedIndex(cls, index):
        return """
                var ch"""+str(index)+""" = document.getElementById('choices'+statNum+'"""+str(index)+"""');
                var selCh"""+str(index)+""" = ch"""+str(index)+""".value
                """

    @classmethod
    def _addSelectedDimension(cls, index):
        js = """var dim"""+str(index)+""" = document.getElementById('dimensions'+statNum+'"""+str(index)+"""');
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
    def _allScripts(cls):
        js = """
       
        
        function changeDivName(divName)
        {
        
        	var dv = [];
        	for (var i = 0; i<divName.length; i++)
        	{
        		x = divName[i];
        		if (x == -1)
        		{
        			dv.push('Sum');
        		}
        		else if (x == -2)
        		{
        			//dv.push('');
        		}
        		else
        		{
        			dv.push(x);
        		}
        	}
        	return dv;
        }
        
        function changeDataIntoProperDict(data, dv, divId, statNum)
       {
       	   var res = {};
       	   if (data[0] == undefined)
       	   {
       	   }
       	   else
       	   {
               var dataLen = data[0].length;
               //console.log('dataLen', dataLen);
               for (var i=0; i < data.length; i++)
               {
                    var value = data[i].slice(data[i].length-3, data[i].length);
                    var key = data[i].slice(0,data[i].length-3);
                    if (res[ key ] == undefined)
                    {
                        res[ key ] = [];
                    }
                    res[ key ].push([value[0], value[1], value[2]]);
                }
                //console.log(res);
                generateListsOutOfDict(res, dataLen, dv, divId, statNum);
            }
       }
       
       
       
       Array.prototype.alphanumSort = function(caseInsensitive) {
          for (var z = 0, t; t = this[z]; z++) {
            this[z] = [];
            var x = 0, y = -1, n = 0, i, j;
        
            while (i = (j = t.charAt(x++)).charCodeAt(0)) {
              var m = (i == 46 || (i >=48 && i <= 57));
              if (m !== n) {
                this[z][++y] = "";
                n = m;
              }
              this[z][y] += j;
            }
          }
        
          this.sort(function(a, b) {
            for (var x = 0, aa, bb; (aa = a[x]) && (bb = b[x]); x++) {
              if (caseInsensitive) {
                aa = aa.toLowerCase();
                bb = bb.toLowerCase();
              }
              if (aa !== bb) {
                var c = Number(aa), d = Number(bb);
                if (c == aa && d == bb) {
                  return c - d;
                } else return (aa > bb) ? 1 : -1;
              }
            }
            return a.length - b.length;
          });
        
          for (var z = 0; z < this.length; z++)
            this[z] = this[z].join("");
        }
       
       function generateListsOutOfDict(res, dataLen, dv, divId, statNum)
       {
       		var body = document.getElementById(divId);
		    var div = document.createElement("div");
		    div.setAttribute('id', 'results'+statNum);
		    body.appendChild(div);
		    
		    //console.log('res',res);
		    //console.log('dataLenv', dataLen);
		    //console.log('dv', dv);
		  	
		  	var kNum = 0;
		  	var r = true;
		  	var iNum = 0;
       		for (var i in res)
       		{
       			
       			var trRes = transpose(res[i]);
       			//console.log( '***','i', i, 'tr',  res[i], trRes);
       			
       			
       			if (trRes[1] == undefined)
       			{
       				if (kNum == 0)
       				{
       				    var h = '';
       					var rows = [];
       					
       					if (dv.length == 0)
       					{
       						var header = [dv];
       					}
       					else
       					{
       						var header = dv;
       					}
       					
       					rows.push(header);
       					kNum = kNum+1;
       				}
       				var row = [i].concat(trRes[0]);
       				rows.push(row);
       			}
       			else
       			{
       				var h = '';
       				if (i == '')
       				{
       				}
       				else
       				{	
       					h = 'Results for: '.concat(i);
       				}
       				var rows = [];
       				var header = ['Data'].concat(trRes[0]);	
       				rows.push(header);
       				kNum=0;
       			}
       			
       			
       			//console.log('header', header);
       			//console.log('column', trRes[1]);
       			
       			
       			var row = [];
       			
       			//console.log('res[i]',  res[i], res[i]);
       			
       			var tempD = {};
       			for (var j in res[i])
       			{
       			    //console.log('--1--', j, res[i][j][0], res[i][j][2], res[i][j][2]);
       			    if (j == 'alphanumSort')
       			    {
       			    }
       			    else
       			    {
       			        var k1 = res[i][j][0];
                        if ( k1 in tempD)
                        {
                        }
                        else
                        {
                            tempD[k1] = {};
                        }
                        //console.log('j', j, typeof(j), 'res[i][j]', res[i][j]);
                        
                        var k2 = res[i][j][1];
                        if (k2 in tempD[k1])
                        {
                        }
                        else
                        {
                            var v = res[i][j][2];
                            
                            //console.log('====', 'k1', k1, 'k2', k2, 'v', v);
                             
                            tempD[k1][k2] = v;
                        }
                    }
       			}
       			//console.log('tempD', tempD);
       			
       			for (var j in trRes[1])
       			{
       			    if (j == 'alphanumSort')
       			    {
       			    }
       			    else
       			    {
                        row = [trRes[1][j]]
                        for (var k = 1; k < header.length; k++)
                        {
                            //console.log('i', i, 'j', j, 'k', k, 'header', header);
                        
                            if (tempD[header[k]][trRes[1][j]] == undefined)
                            {
                                tempD[header[k]][trRes[1][j]] = 0;
                            }
                            row.push(tempD[header[k]][trRes[1][j]]);
                        }
                        //console.log('row', row);
                        rows.push(row);
                    }
       			}
       			
       			if (kNum == 0)
       			{
       				var divExtra = document.createElement("div");
       				divExtra.setAttribute('class', 'description');
       				divExtra.setAttribute('id', 'description'+statNum+iNum);
		    		
		    		
		    		if (rows.length == 2)
                    {
                        //console.log('rows', rows);
                        if (rows[0].length == rows[1].length)
                        {
                        }
                        else
                        {
                            var st = 1;
                            var end = rows[0].length;
                            var r = rows[0][0];
                            rows[0] = rows[0].slice(st, end);
                            if (rows[1].length == 2)
                            {
                                rows[1] = [r, rows[1][1]]
                            }
                        }
                    }
		    		
		    		div.appendChild(divExtra);
       				tbl = generateTable(rows, iNum, divId);
       				div.appendChild(tbl);
       				
       				generateVis(statNum, rows, div, iNum)
       				
       				document.getElementById('description'+statNum+iNum).innerHTML = h;
       				iNum = iNum + 1
       			}
       			else
       			{
       				r = false;
       			}
       			
       			
       			//console.log('rows', rows);
       			
       		}
       		if (r == false)
       		{
       			var divExtra = document.createElement("div");
       			divExtra.setAttribute('class', 'description');
       			divExtra.setAttribute('id', 'description'+statNum+iNum);
		    	div.appendChild(divExtra);
       			
       			if (rows.length == 2)
       			{
       				//console.log('rows', rows);
       				if (rows[0].length == rows[1].length)
       				{
       				}
       				else
       				{
       					var st = 1;
       					var end = rows[0].length;
       					var r = rows[0][0];
       					rows[0] = rows[0].slice(st, end);
       					if (rows[1].length == 2)
       					{
       						rows[1] = [r, rows[1][1]]
       					}
       				}
       			}
       			tbl = generateTable(rows, iNum, divId);
                div.appendChild(tbl);
                
                generateVis(statNum, rows, div, iNum)
                
                document.getElementById('description'+statNum+iNum).innerHTML = h;
                iNum = iNum + 1
       		}
       		
       		
       }
       
       function transpose(original)
       {
        var copy = [];
        var k = 0;
        var l = 0;
    	for (var i = 0; i < original.length; i++) 
    	{
        	for (var j = 0; j < original[i].length-1; j++) 
        	{
        		k = j;
        		if (copy[k] === undefined)
        		{
        			l = 0;
        		}
        		else
        		{
            		l = copy[k].length//i;
            	}
            	
            	if (original[i][j] === undefined) continue;
            	if (copy[k] === undefined) copy[k] = [];
            	
            	if (copy[k].includes(original[i][j]))
            	{
            		
            	}
            	else
            	{
            		copy[k][l] = original[i][j];
            	}
        	}
   		 }
   		//console.log('copy', copy);
    	return copy;
       }
    
       
               
       function generateTable(tab, inx, divId) 
       {
          console.log('tab-generateTable', tab);
 		  var tbl = document.createElement("table");
  		  var tblBody = document.createElement("tbody");
 	      
 	      for (var i = 0; i < tab.length; i++) 
  		  {
    			var row = document.createElement("tr");
    			
    			if (tab[i].length == 0)
    			{
    				var cell1 = document.createElement("th");
    				var cellText1 = document.createTextNode('Data');
    				cell1.appendChild(cellText1);
      		   	    row.appendChild(cell1);
      		   	    
      		   	    var cell1 = document.createElement("th");
    				var cellText1 = document.createTextNode('Value');
    				cell1.appendChild(cellText1);
      		   	    row.appendChild(cell1);
    			}
    			else
    			{
    			
                    for (var j = 0; j < tab[1].length; j++) 
                    {
                        if (i == 0)
                        {
                            var cell = document.createElement("th");
                        }
                        else
                        {
                            var cell = document.createElement("td");
                        }
                        //console.log('tab[i][j]', tab[i][j], tab[i][j].length, tab[i].length);
                        
                        if (tab[i][j] == undefined)
                        {    
                            var cellText = document.createTextNode('Value');
                        }
                        else
                        {
                            if (tab[i][j].length == 0)
                            {
                                if (tab[i].length == 1)
                                {
                                    var cell1 = document.createElement("th");
                                    var cellText1 = document.createTextNode('Data');
                                    cell1.appendChild(cellText1);
                                    row.appendChild(cell1);
                                    
                                    var cellText = document.createTextNode('Value');
                                }
                            }
                            else
                            {
                                var cellText = document.createTextNode(tab[i][j]);
                            }
                        }
                        cell.appendChild(cellText);
                        row.appendChild(cell);
                    }
                }
		        tblBody.appendChild(row);
  			}
  			tbl.setAttribute('class', 'table');
  			tbl.setAttribute('id', divId+inx);
  			tbl.appendChild(tblBody);
  	
  			return tbl;

		}
		
	   function generateVisAsOneSeries(statNum, divId, tab, div, inx, zeros) 
       {
          //console.log('tab-generateTable', tab);
          
          var container = 'container'+statNum+inx;
          
		  var divVis = document.createElement("div");
		  divVis.setAttribute('id', container);
		  div.appendChild(divVis);
 		  
 		  //<div id="container" style="min-width: 310px; height: 400px; margin: 0 auto"></div>
  		  
 	      var categories = [];
 	      var c = [];
 	      var s = '';
 	      var el = '';
 	      var plotLines = ''
 	      
 	      //console.log('tab', tab);
 	      var howManyPlotLines = 0;
 	      var ifLineHaveZeros = 0;
 	      for (var i = 0; i < tab.length; i++) 
  		  {
    			for (var j = 0; j < tab[i].length; j++) 
    			{
    			    el = tab[i][j];
    			    
    			    if (el == 'Data')
    			    {
    			    }
    			    else
    			    {
    					if (i == 0)
    					{
    						categories.push('"'+el+'",');
    						var catLen = categories.length;
    					}
    					else
    					{
    				    	if (j == 0)
    				    	{   
    				    	    var elHeader = el;
    				    	    var numElHeader = j;
    				    	}
    				    	else
    				    	{
    							if (j == tab[i].length-1)
    				        	{
    				        	    if (zeros == true)
                                    {
                                        if (parseFloat(el) == 0)
                                        {
                                            ifLineHaveZeros += 0;
                                        }
                                        else
                                        {
    				        		        s += el + ",";
    				        		        c += categories[j-1];
    				        		        howManyPlotLines += 1;
    				        		        ifLineHaveZeros += 1;
    				        		    }
    				        		}
    				        		else
    				        		{
    				        		    s += el + ",";
    				        		    c += categories[j-1];
    				        		    howManyPlotLines += 1;
    				        		    ifLineHaveZeros = 1;
    				        		}
    				        		if (ifLineHaveZeros > 0)
    				        		{
    				        		    var numDist = 0.25 + howManyPlotLines - 1;
    				        		    plotLines += "{ id: '"+i+"', color: '#3d70b2', dashStyle: 'solid', value: "+numDist+", width: 1, label: { y: 20, textAlign: 'left', text: '"+elHeader+"', style: { color:'#3d70b2' }} },"
    				        		    ifLineHaveZeros = 0;
    				        	    }
    				        	}
    				        	else
    				        	{
    				        		if (s == undefined)
    								{
    								}
    								else
    								{
    								    if (zeros == true)
    								    {
    								        if (parseFloat(el) == 0)
    								        {
    								            ifLineHaveZeros += 0; 
    								        }
    								        else
    								        {
    								            s += el + ",";
    								            c += categories[j-1];
    								            howManyPlotLines += 1;
    								            ifLineHaveZeros += 1
    								        }
    								    }
    								    else
    								    {
    				        			    s += el + ",";
    				        			    c += categories[j-1];
    				        			    howManyPlotLines += 1;
    				        			    ifLineHaveZeros +=1
    				        			}
    				        		}
    				        	}
    				    	}
    					}
    				}
    			}
  		  }
  		  vis = createPLotWithOneSeries(statNum, container, c, s, plotLines, inx);
  		  eval(vis); 
		}
		
	   function createPLotWithOneSeries(statNum, container, categories, series, plotLines, inx)
	   {
	      //console.log('container', container);
  		   //console.log('categories', categories);
  		   //console.log('series', series);
  		  
		    js  = " \
		    Highcharts.chart('"+container+"', { \
                    chart: { \
                        type:  'column', \
                        zoomType: 'x' \
                    }, \
                    title: { \
                        text: '' \
                    }, \
                    subtitle: { \
                        text: '' \
                    }, \
                    xAxis: { \
                        categories: [" + categories + "], \
                        crosshair: true, \
                        min:0, \
                        plotLines: [" + plotLines + "], \
                        labels: { rotation: 90, } \
                    }, \
                    yAxis: { \
                        min: 0, \
                        title: { \
                            text: '' \
                        } \
                    }, \
                    tooltip: { \
                        shared: true, \
                        useHTML: true \
                    }, \
                    plotOptions: { \
                        column: { \
                            pointPadding: 0.2, \
                            borderWidth: 0 \
                        } \
                    }, \
                    series: [ { name: '" + document.getElementById('description'+statNum+inx).innerHTML  + "', type:'column' , data: [" + series + "] } ] \
                });"
			
			//console.log(js);
		    return js;
		}
		
	   function generateVis(statNum, tab, div, inx) 
       {
          //console.log('tab-generateTable', tab);
          
          var container = 'container'+statNum+inx;
          
		  var divVis = document.createElement("div");
		  divVis.setAttribute('id', container);
		  div.appendChild(divVis);
 		  
 		  //<div id="container" style="min-width: 310px; height: 400px; margin: 0 auto"></div>
  		  
 	      var categories = [];
 	      var c = [];
 	      var s = '';
 	      var el = '';
 	      
 	      //console.log('tab', tab);
 	      for (var i = 0; i < tab.length; i++) 
  		  {
    			for (var j = 0; j < tab[i].length; j++) 
    			{
    			    el = tab[i][j];
    			    //console.log('i', i,'j', j, el);
    			    
    			    if (el == 'Data')
    			    {
    			    }
    			    else
    			    {
    					if (i == 0)
    					{
    						categories.push('"'+el+'",');
    					}
    					else
    					{
    				    	if (j == 0)
    				    	{
    				        	s = s + "{ name: "+ '"'+el+'"' + ", data: [";
    				        	c += categories[j];  				    	}
    				    	else
    				    	{
    							if (j == tab[i].length-1)
    				        	{
    				        		s = s + el + "] }, ";
    				        	}
    				        	else
    				        	{
    				        		if (s == undefined)
    								{
    								}
    								else
    								{
    				        			s = s + el + ",";
    				        			c += categories[j];
    				        		}
    				        	}
    				    	}
    					}
    				}
    			}
  		  }
  		  vis = createPLot(container, c, s);
  		  eval(vis); 
		}
		
		function createPLot(container, categories, series)
		{
			//console.log('container', container);
  		  //console.log('categories', categories);
  		  //console.log('series', series);
  		  
  		  	
  		  
		    js  = " \
		    Highcharts.chart('"+container+"', { \
                    chart: { \
                        type:  'column', \
                        zoomType: 'x' \
                    }, \
                    title: { \
                        text: '' \
                    }, \
                    subtitle: { \
                        text: '' \
                    }, \
                    xAxis: { \
                        categories: [" + categories + "], \
                        crosshair: true, \
                        labels: { rotation: 90, } \
                    }, \
                    yAxis: { \
                        min: 0, \
                        title: { \
                            text: '' \
                        } \
                    }, \
                    tooltip: { \
                        shared: true, \
                        useHTML: true \
                    }, \
                    plotOptions: { \
                        column: { \
                            pointPadding: 0.2, \
                            borderWidth: 0 \
                        } \
                    }, \
                    series: [" + series + "] \
                });"
			
			//console.log(js);
		    return js;
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
        					//console.log('>=0', flat[j].slice(0,i), flat[j].slice(i+1,flat[j].length));
        					var part = (flat[j].slice(0,i)).concat(flat[j].slice(i+1,flat[j].length));	
        					partFlat.push(part);
        				}
        			}
        			flat = partFlat;
        			//console.log('op', op, 'op>=0', flat);
        		}
        		else if(op == -1)
        		{
        			var partFlat = [];
        			for (var j = 0; j < flat.length; j++) 
        			{
        				partFlat[j]= flat[j].slice(0,i).concat(flat[j].slice(i+1,flat[j].length));
        			}
        			flat = partFlat;
        			
        			var myDict = {};
        			for (var x in flat) 
        			{
        				if (x == 'alphanumSort')
        				{
        				}
        				else
        				{
        					//console.log('x', x, flat[x], flat[x].length-1);
        					var value = parseFloat(flat[x][flat[x].length-1]);
        					var key = flat[x].slice(0,flat[x].length-1);
        				
        					//console.log('value', value, 'key', key);
        					if (myDict[ key ] == undefined)
        					{
        						myDict[ key ] = 0;
        					}
	        				myDict[ key ] += value;
	        			}
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

    @classmethod
    def _visualizeResultsAddLib(cls):
        return """ 
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
                <script src="https://code.highcharts.com/highcharts.js"></script>
                <script src="https://code.highcharts.com/modules/data.js"></script>
                <script src="https://code.highcharts.com/modules/heatmap.js"></script>
                <script src="https://code.highcharts.com/modules/exporting.js"></script>
                <script src="https://raw.github.com/briancray/tooltipsy/master/tooltipsy.min.js"></script>
                <script src="https://code.highcharts.com/highcharts-more.js"></script>
                """
    @classmethod
    def _addTransposePossibility(cls, statNum):

        js = """
        <script type = "text/javascript" >
        $('[name="series""" + str(statNum) + """"]').change(function()
          {
          	if ($(this).is(':checked')) 
            {
                $('#zerosDiv""" + str(statNum) + """').css('display', 'block');
            }
            else
            {
                $('#zerosDiv""" + str(statNum) + """').css('display', 'none');
                document.getElementById('zeros""" + str(statNum) + """').checked = false;
            }
        });
        </script>
        """
        return js

    @classmethod
    def _addTransposePossibilityFunctions(cls, statNum):

        js = """
        <script>
        function transposeDataFromTable(newTable) {
        
            var newTableTranspose = [];
            for (var i = 0; i < newTable[0].length; i++) 
            {
                var nt = [];
                for (var j = 0; j< newTable.length; j++) 
                {
                    nt.push(newTable[j][i]);
                }
                newTableTranspose.push(nt);
            }
            return newTableTranspose;
        }
        
        function readDataFromTable (divId, statNum, trans = false)
        {    
        
            console.log('a', statNum);
            var tt = document.getElementsByClassName("table");
            var t = []
            for (var i = 0; i < tt.length; ++i) 
            {
    			var item = tt[i];
    			console.log('----', item.id, divId.id, item.id.indexOf(divId.id));
    			if (item.id.indexOf(divId.id) >= 0)
    			{
    				t.push(item);
    			}
			} 
    		
    		console.log(t);
    		var y = '';
    		
    		var allTabs = []
    		var numEl = t.length;
    		
    		var desc = [];
    		for (var x = 0; x < numEl; x++) 
    		{
    			desc.push(document.getElementById('description'+statNum+x).innerHTML);
    			var xx = t[x];
    			//console.log('xx', xx, 'xx.rows[i]', xx.rows.length);
    			var newTable = [];
				for (var i = 0; i < xx.rows.length; i++) 
				{
					var row = xx.rows[i];
					var nt = [];
   					for (var j = 0; j< row.cells.length; j++) 
   					{
   						var cell = row.cells[j];
   						nt.push(cell.innerText);
   					}
   					newTable.push(nt);
   				}
   				
   				if (trans == true)
   				{
                    newTableTranspose = transposeDataFromTable(newTable);
                    //console.log(newTableTranspose);
                    allTabs.push(newTableTranspose);
                }
                else
                {
                    allTabs.push(newTable);
                }
   				
			}
			hideTable(statNum);
			
			console.log('divId', divId);
			var body = divId;
		    var div = document.createElement("div");
		    div.setAttribute('id', 'results'+statNum);
		    body.appendChild(div);
       			
            for (var iNum = 0; iNum < numEl; iNum++) 
            {
            
                var divExtra = document.createElement("div");
                divExtra.setAttribute('class', 'description');
                divExtra.setAttribute('id', 'description'+statNum+iNum);
                div.appendChild(divExtra);
                var rows = allTabs[iNum];
            
                if (rows.length == 2)
                {
                    //console.log('rows', rows);
                    if (rows[0].length == rows[1].length)
                    {
                    }
                    else
                    {
                        var st = 1;
                        var end = rows[0].length;
                        var r = rows[0][0];
                        rows[0] = rows[0].slice(st, end);
                        if (rows[1].length == 2)
                        {
                            rows[1] = [r, rows[1][1]]
                        }
                    }
                }
                tbl = generateTable(rows, iNum, divId.id);
                div.appendChild(tbl);
                document.getElementById('description'+statNum+iNum).innerHTML = desc[iNum];
                
                if (document.getElementById('series'+statNum).checked == false)
                {
                    generateVis(statNum, rows, div, iNum);
                }
                else
                {
                    if (document.getElementById('series'+statNum).checked == true)
                    {
                        if (document.getElementById('zeros'+statNum).checked == true)
                        {
                            var zeros = true;
                        }
                        else
                        {
                            var zeros = false;
                        }
                        generateVisAsOneSeries(statNum, divId.id, rows, div, iNum, zeros);
                    }
                }
            
            }
        }
        """
        #js += """$('[name="zeros""" + str(statNum) + """"]').change(function(){ readDataFromTable(divId, """ + str(statNum) + """)});"""
        #js += """$('[name="transpose""" + str(statNum) + """"]').change(function(){ readDataFromTable(divId, """ + str(statNum) + """, transpose = true) }); """
        #js += """$('[name="series""" + str(statNum) + """"]').change(function(){ readDataFromTable(divId, """ + str(statNum) + """) });"""

        return js