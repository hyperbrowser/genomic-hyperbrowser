from proto.hyperbrowser.HtmlCore import HtmlCore
class Legend():

    def __init__(cls):
        pass

    @classmethod
    def _depth(cls, l):
        if isinstance(l, list):
            return 1 + max(cls._depth(item) for item in l)
        else:
            return 0

    @classmethod
    def createDescription(cls, toolDescription=None, stepsToRunTool=None, toolResult=None,
                          limitation=None, exampleDescription=None, notice=None):
        core = HtmlCore()

        if toolDescription != None or stepsToRunTool != None or toolResult != None or limitation != None:
            core.divBegin(style='margin: 0px -5px; text-align: justify; color: #66635b;border: solid 1px #66635b; border-radius: 5px; background-color: #ffffff;')
            core.divBegin(style='padding: 5px;')
            core.header('Description')

            # small description of tool (The resaon of creating the tool)
            if toolDescription != None:
                core.divBegin(style='background-color: #efefee; padding: 10px;')
                core.paragraph(toolDescription)
                core.divEnd()

            # how to use tool
            if stepsToRunTool != None:
                core.paragraph('To run the tool, follow these steps:')
                core.orderedList(stepsToRunTool)

            # what is the result of tool
            if toolDescription != None:
                core.divBegin(style='background-color: #efefee; padding: 10px;')
                core.paragraph(toolResult)
                core.divEnd()

            if exampleDescription != None:
                cls.createExample(core, exampleDescription)

            if notice != None:
                core.paragraph('<b>Notice:</b>')
                core.line('<p style="padding-left:30px;color:#53982d;">' + str(notice) + '</p>')

                # what are the limitation for tool
                #         if limitation:
                #             limits...

            core.divEnd()
            core.divEnd()

        return str(core)

    @classmethod
    def createExample(cls, core, exampleDescriptionDict):

        if len(exampleDescriptionDict.items ()) > 0:


            js = """
            jQuery(function(){
                jQuery('.targetDiv').hide();
                jQuery('.hideDiv').hide();
                
                jQuery('.showDiv').click(function()
                {
                    jQuery('.targetDiv').hide();
                    
                    jQuery('#div'+$(this).attr('target')).show();
    
                    $('.hideDiv').each(function(i, obj) {
                        if (obj.id == '#showDiv'+$(this).attr('target'))
                        {
                        }
                        else
                        {
                            jQuery('#showDiv'+$(this).attr('target')).show();
                            jQuery('#hideDiv'+$(this).attr('target')).hide();
                        }
                    });
                    jQuery('#showDiv'+$(this).attr('target')).hide();
                    jQuery('#hideDiv'+$(this).attr('target')).show();                
                });
                jQuery('.hideDiv').click(function()
                {
                    jQuery('#div'+$(this).attr('target')).hide();
                    jQuery('#hideDiv'+$(this).attr('target')).hide();
                    jQuery('#showDiv'+$(this).attr('target')).show();
                });
            });   
            """
            core.script(js);
            scriptDiv = ""
            i=0

            keysExampleDescriptionDict = sorted(exampleDescriptionDict.keys())

            for key in keysExampleDescriptionDict:

                exampleDescription = exampleDescriptionDict[key]

                scriptDiv += '<a style="text-decoration:none" href="#' + 'page' + str(i)  + '"><div id="showDiv' + str(i) + '" target="' + str(i) + '" class="showDiv" style="width:100%; padding: 10px;border: 1px solid #efefee; background-color:#fff7db;color:#565656; margin:10px 0px;">Show ' + str(key) + '</div></a>'
                scriptDiv += '<a name="page' + str(i) + '"><div id="hideDiv' + str(i) + '" target="' + str(i) + '" class="hideDiv" style="cursor:pointer;width:100%; padding: 10px;border: 1px solid #efefee; background-color:#565656; color:#fff7db; margin:10px 0px;">Hide ' + str(key) + '</div>'
                scriptDiv += '<div id="div' + str(i) + '" class="targetDiv" style="position: relative;border: 1px solid #efefee; background-color:#fff7db; padding: 25px;">'

                if len(exampleDescription) == 4:
                    for edNum, ed in enumerate(exampleDescription):
                        #core.line(str(len(exampleDescription)) + str(edNum) + str(len(ed)))
                        if len(exampleDescription) >= 1 and edNum == 0:
                            edText = 'Description:'
                        elif len(exampleDescription) >= 2 and edNum == 1:
                            edText = 'Input:'
                        elif len(exampleDescription) >= 3 and edNum == 2:
                            edText = 'Options:'
                        elif len(exampleDescription) >= 4 and edNum == 3:
                            edText = 'Output:'

                        if (len(ed) > 0 and edNum >= 1) or (ed != '' and edNum == 0):
                            scriptDiv += '<p><b style="color:#000000;">' + edText + '</b></p>'
                        if len(ed) > 0 and (edNum == 0):
                            scriptDiv += '<p>' + str(ed) + '</p>'
                        if len(ed) > 0 and (edNum == 2):
                            for edNum1, ed1 in enumerate(ed):
                                scriptDiv += '<p style="text-align:left;">' + ed1[0] + ': ' + '<b>' + ed1[1] + '</b>' + '</p>'
                        if len(ed) > 0 and (edNum == 1 or edNum == 3):
                            for edNum1, ed1 in enumerate(ed):
                                if cls._depth(ed1) == 0:
                                    scriptDiv += '<p><div style="clear:both;border:1px solid #8f8f8e;background-color:#fbfbfb;"><pre><code>' + str(
                                            ed1) + '</code></pre></div></p>'
                                if cls._depth(ed1) == 1:
                                    for edNum2, ed2 in enumerate(ed1):
                                        scriptDiv += '<p><div style="clear:both;border:1px solid #8f8f8e;background-color:#fbfbfb;"><pre><code>' + str(
                                                ed2) + '</code></pre></div></p>'
                        if len(ed) > 0 and edNum >= 1 and edNum <=2:
                            scriptDiv += '<p><hr style="border: 1px dotted #000;" /></p>'
                    scriptDiv += '</a></div>'
                    i+=1
                else:
                    scriptDiv = ""
            core.line(scriptDiv)