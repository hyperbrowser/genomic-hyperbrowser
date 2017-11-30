from proto.hyperbrowser.HtmlCore import HtmlCore
class Legend():

    def __init__(cls):
        pass

    @classmethod
    def createDescription(cls, toolDescription=None, stepsToRunTool=None, toolResult=None,
                          limitation=None):
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

                # what are the limitation for tool
                #         if limitation:
                #             limits...

            core.divEnd()
            core.divEnd()

        return str(core)