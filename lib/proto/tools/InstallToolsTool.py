import os
import re
import shutil
from cgi import escape

from proto.ProtoToolRegister import getProtoToolList, getInstalledProtoTools
from proto.config.Config import (GALAXY_TOOL_CONFIG_FILE,
                                 GALAXY_TOOL_XML_PATH)
from proto.tools.GeneralGuiTool import GeneralGuiTool


class InstallToolsTool(GeneralGuiTool):
    prototype = None

    @classmethod
    def _getToolList(cls):
        installed_classes = getInstalledProtoTools()
        return getProtoToolList(installed_classes)[0]

    @classmethod
    def _getProtoType(cls, tool):
        try:
            prototype = cls._getToolList()[tool][2]()
        except:
            prototype = None
        return prototype


    @staticmethod
    def getToolName():
        return "ProTo tool installer"

    @staticmethod
    def getInputBoxNames():
        return [('Select tool', 'tool'),
                ('Tool type', 'toolType'),
                ('Tool ID', 'toolID'),
                ('Tool name', 'name'),
                ('Tool description', 'description'),
                ('Tool XML file', 'toolXMLPath'),
                ('Select section', 'section')]

    @staticmethod
    def getResetBoxes():
        return [1, 2]

#    @staticmethod
#    def isHistoryTool():
#        return False

    @staticmethod
    def useSubToolPrefix():
        return True

    @classmethod
    def getOptionsBoxTool(cls):
        tool_list = cls._getToolList()
        return ['-- Select tool --'] + sorted(tool_list)

    @classmethod
    def getOptionsBoxToolType(cls, prevchoices):
        return ['proto']

    @classmethod
    def getOptionsBoxToolID(cls, prevchoices):
        import inflection
        if prevchoices.tool is None or prevchoices.tool.startswith('--'):
            return ''
        tool_list = cls._getToolList()
        module_name = tool_list[prevchoices.tool][2].__name__
        return prevchoices.toolType + '_' + inflection.underscore(module_name)


    @classmethod
    def getOptionsBoxName(cls, prevchoices):
        prototype = cls._getProtoType(prevchoices.tool)
        if prototype is not None:
            return prototype.getToolName()

    @classmethod
    def getOptionsBoxDescription(cls, prevchoices):
        return ''

    @classmethod
    def getOptionsBoxToolXMLPath(cls, prevchoices):
        prototype = cls._getProtoType(prevchoices.tool)
        if prototype is not None:
            package = prototype.__module__.split('.')
            package_dir = '/'.join(package[2:-1]) + '/' if len(package) > 3 else ''
            return 'proto/' + package_dir + prototype.__class__.__name__ + '.xml'

    @classmethod
    def getOptionsBoxSection(cls, prevchoices):
        toolConf = GalaxyToolConfig()
        return toolConf.getSections()

    #@classmethod
    #def getOptionsBoxInfo(cls, prevchoices):
    #    txt = ''
    #    if prevchoices.tool and prevchoices.section:
    #        txt = 'Install %s into %s' % (prevchoices.tool, prevchoices.section)
    #    tool_cls = prevchoices.tool
    #    prototype = cls.prototype
    #    tool_file = prevchoices.toolXMLPath
    #    xml = cls.toolConf.addTool(prevchoices.section, tool_file)
    #    tool_xml = cls.toolConf.createToolXml(tool_file, prevchoices.toolID, prevchoices.name, prototype.__module__, prototype.__class__.__name__, prevchoices.description)
    #    return 'rawstr', '<pre>' + escape(xml) + '</pre>' + '<pre>' + escape(tool_xml) + '</pre>'

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if not choices.toolID or len(choices.toolID) < 6 or not re.match(r'^[a-zA-Z0-9_]+$', choices.toolID):
            return 'Tool ID must be at least 6 characters and not contain special chars'
        return None

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        # txt = ''
        # if choices.tool and choices.section:
        #     txt = 'Install %s into %s' % (choices.tool, choices.section)
        # tool_cls = choices.tool

        prototype = cls._getProtoType(choices.tool)
        tool_file = choices.toolXMLPath
        tool_type = choices.toolType
        toolConf = GalaxyToolConfig()
        xml = toolConf.addTool(choices.section, tool_file)
        tool_xml = toolConf.createToolXml(choices.toolID,
                                          choices.name, tool_type,
                                          prototype.__module__,
                                          prototype.__class__.__name__,
                                          choices.description)

        abs_tool_xml_path = GALAXY_TOOL_XML_PATH + choices.toolXMLPath
        try:
            os.makedirs(os.path.dirname(abs_tool_xml_path))
        except:
            pass
        with open(abs_tool_xml_path, 'w') as tf:
            tf.write(tool_xml)

        toolConf.write()

        from proto.HtmlCore import HtmlCore
        core = HtmlCore()

        extraJavaScriptCode = '''
                <script type="text/javascript">
                    $().ready(function() {
                        $("#reload_toolbox").click(function(){
                            $.ajax({
                            url: "/api/configuration/toolbox",
                            type: 'PUT'
                            }).done(function() {
                                    top.location.reload();
                                }
                            );
                        });
                    });
                </script>
                '''
        core.begin(extraJavaScriptCode=extraJavaScriptCode)
        core.link('Reload toolbox/menu', url='#', args='id="reload_toolbox"')
        core.preformatted(escape(xml))
        core.preformatted(escape(tool_xml))
        core.end()
        print>>open(galaxyFn, 'w'), core

    @staticmethod
    def getToolDescription():
        from proto.HtmlCore import HtmlCore
        core = HtmlCore()
        core.smallHeader("General description")
        core.paragraph(
            "This tool is used to install ProTo tools into the tool menu. "
            "The installation process creates a Galaxy tool XML file and "
            "adds the tool to the tool menu (in the 'tool_conf.xml' file). "
            "After execution, the XML file has been generated and added "
            "to the tool configuration file, but Galaxy needs to reload "
            "the tool menu for it to become visible. This is done by a "
            "Galaxy administrator, either from the Admin menu, or from a "
            "link in the output history element from this tool.")
        core.paragraph("Note that the after this tool has been executed "
                       "but before a Galaxy administrator has reloaded the "
                       "tool menu, the tool is not available from neither "
                       "of the 'ProTo tool explorer' tool or from the "
                       "Galaxy menu.")
        core.divider()
        core.smallHeader("Parameters")

        core.descriptionLine("Select tool", "The tool to install.",
                             emphasize=True)
        core.descriptionLine("Tool ID",
                             "The Galaxy tool id for the new tool to be "
                             "created. This is the 'id' argument to the "
                             "<tool> tag in the tool XML file.",
                             emphasize=True)
        core.descriptionLine("Tool name",
                             "The name of the tool as it will appear in the "
                             "tool menu. The tool name will appear as a HTML "
                             "link.", emphasize=True)
        core.descriptionLine("Tool description",
                             "The description of the tool as it will appear "
                             "in the tool menu. The tool description will "
                             "appear directly after the tool name as "
                             "normal text.", emphasize=True)
        core.descriptionLine("Tool XML file",
                             "The path (relative to 'tools/proto/') and name "
                             "of the Galaxy tool XML file to be created. "
                             "The tool file can be named anything and be "
                             "placed anywhere (as the 'tool_conf.xml' file"
                             "contains the path to the tool XML file). "
                             "However, we encourage the practice of placing "
                             "the Galaxy tool XML file together with the "
                             "Python module, in the same directory and "
                             "with the same name as tool module (with e.g. "
                             "'ABCTool.xml' instead of 'AbcTool.py').",
                             emphasize=True)
        core.descriptionLine("Select section in tool_conf.xml file",
                             "The section in the tool_conf.xml file where"
                             "the tool should be placed in the menu. "
                             "This corresponds to the first level in the"
                             "tool hierarchy.", emphasize=True)
        return str(core)

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'


class GalaxyToolConfig(object):
    tool_xml_template = '''<tool id="%s" name="%s" version="1.0.0"
  tool_type="%s_generic" proto_tool_module="%s" proto_tool_class="%s">
  <description>%s</description>
</tool>\n'''

    def __init__(self, tool_conf_fn=GALAXY_TOOL_CONFIG_FILE):
        self.tool_conf_fn = tool_conf_fn
        with open(self.tool_conf_fn, 'r') as tcf:
            self.tool_conf_data = tcf.read()

    def getSections(self):
        self.sectionPos = {}
        section_names = []
        for m in re.finditer(r'<section ([^>]+)>', self.tool_conf_data):
            attrib = {}
            for a in re.findall(r'([^ =]+)="([^"]+)"', m.group(1)):
                attrib[a[0]] = a[1]
            self.sectionPos[attrib['name']] = m.end(0)
            section_names.append(attrib['name'])
        return section_names

    def addTool(self, section_name, tool_file):
        self.getSections()
        tool_tag = '\n\t<tool file="%s" />' % (tool_file,)
        pos = self.sectionPos[section_name]
        self.tool_conf_data = self.tool_conf_data[:pos] + tool_tag + self.tool_conf_data[pos:]
        return self.tool_conf_data

    def write(self):
        shutil.copy(self.tool_conf_fn, self.tool_conf_fn + '.bak')
        with open(self.tool_conf_fn, 'w') as f:
            f.write(self.tool_conf_data)

    def createToolXml(self, tool_id, tool_name, tool_type, tool_module, tool_cls, tool_descr):
        tool_xml = self.tool_xml_template % (tool_id, tool_name, tool_type,
                                             tool_module, tool_cls, tool_descr)
        return tool_xml
