from proto.tools.GeneralGuiTool import GeneralGuiTool, MultiGeneralGuiTool
from proto.config.Config import GALAXY_BASE_DIR, GALAXY_REL_TOOL_CONFIG_FILE, URL_PREFIX
import os, re, shelve, shutil, sys, traceback
from importlib import import_module
from collections import OrderedDict
#import xml.etree.ElementTree as ET
from cgi import escape
from urllib import quote

SOURCE_CODE_BASE_DIR = GALAXY_BASE_DIR + '/lib'
#HB_TOOL_DIR = GALAXY_BASE_DIR + '/tools/hyperbrowser/new-xml/'
#PROTO_TOOL_DIR = HB_SOURCE_CODE_BASE_DIR + '/quick/webtools/'
PROTO_TOOL_DIR = GALAXY_BASE_DIR + '/lib/proto/tools/'
TOOL_SHELVE = GALAXY_BASE_DIR + '/database/proto-tool-cache.shelve'
TOOL_CONF = GALAXY_BASE_DIR + '/' + GALAXY_REL_TOOL_CONFIG_FILE
GALAXY_TOOL_XML_PATH = GALAXY_BASE_DIR + '/tools/'
TOOL_XML_REL_PATH = 'hyperbrowser/'


class GalaxyToolConfig:

    tool_xml_template = '''<tool id="%s" name="%s" version="1.0.0"
  tool_type="%s_generic" proto_tool_module="%s" proto_tool_class="%s">
  <description>%s</description>
</tool>\n'''

    def __init__(self, tool_conf_fn=TOOL_CONF):
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
        
    def createToolXml(self, tool_fn, tool_id, tool_name, tool_type, tool_module, tool_cls, tool_descr):
        tool_xml = self.tool_xml_template % (tool_id, tool_name, tool_type,
                                             tool_module, tool_cls, tool_descr)
        return tool_xml


def getProtoToolList(except_class_names=[]):
    except_class_names.append('ToolTemplate')
    except_class_names.append('ToolTemplateMinimal')
    tmp_tools = {}
    tools = {}
    tool_classes = []
    all_sub_classes = set()
    pys = []
    for d in os.walk(PROTO_TOOL_DIR, followlinks=True):
        if d[0].find('.svn') == -1:
            pys += [os.path.join(d[0], f) for f in d[2] if f.endswith('.py') and not any(f.startswith(x) for x in ['.', '#'])]

    # To fix import issue if there are modules in /lib and /lib/proto with the
    # same name (e.g. 'config').
    tmpSysPath = sys.path
    if sys.path[0].endswith('/proto'):
        sys.path = tmpSysPath[1:]

    #print 'Num py', len(pys)
    for fn in pys:
        with open(fn) as f:
            for line in f:
                m = re.match(r'class +(\w+) *\(([\w ,]+)\)', line)
                if m:
                    class_name = m.group(1)
                    module_name = os.path.splitext(os.path.relpath(os.path.abspath(fn), SOURCE_CODE_BASE_DIR))[0].replace(os.path.sep, '.')
                    try:
                        if module_name != __name__:
                            module = import_module(module_name)
                            prototype_cls = getattr(module, class_name)
                            if issubclass(prototype_cls, GeneralGuiTool):
                                if issubclass(prototype_cls, MultiGeneralGuiTool):
                                    if prototype_cls.getSubToolClasses():
                                        for sub_cls in prototype_cls.getSubToolClasses():
                                            all_sub_classes.add(sub_cls)
                                elif hasattr(prototype_cls, 'getToolName'):
                                    if class_name not in except_class_names:
                                        prototype = prototype_cls('hb_no_tool_id_yet')
                                        tool_module = module_name.split('.')[2:]
                                        if class_name != tool_module[-1]:
                                            tool_selection_name = '.'.join(tool_module) + ' [' + class_name + ']'
                                        else:
                                            tool_selection_name = '.'.join(tool_module)

                                        # print (fn, m.group(2), prototype_cls, module_name)
                                        tmp_tools[tool_selection_name] = (fn, m.group(2), prototype_cls, module_name)
                    except Exception as e:
                        traceback.print_exc()
                        #break
    #print 'Num protopy', len(tools)

    for tool_selection_name, tool_info in tmp_tools.iteritems():
        prototype_cls = tool_info[2]
        if prototype_cls not in all_sub_classes:
            tools[tool_selection_name] = tool_info
            tool_classes.append(prototype_cls)

    sys.path = tmpSysPath
    return tools, tool_classes


class ExploreToolsTool(MultiGeneralGuiTool):
    @staticmethod
    def getToolName():
        return "ProTo tool explorer"

    @staticmethod
    def getToolSelectionName():
        return "-----  Select tool -----"

    @staticmethod
    def useSubToolPrefix():
        return True
    
    @classmethod
    def getSubToolClasses(cls):
        tool_shelve = shelve.open(TOOL_SHELVE, 'r')
        installed_classes = [tool_shelve.get(t)[1] for t in tool_shelve.keys()
                             if os.path.exists(os.path.join(SOURCE_CODE_BASE_DIR, tool_shelve.get(t)[0].replace('.', os.path.sep)) + '.py') ]
        tool_shelve.close()
        tool_list = getProtoToolList(installed_classes)[1]
        return sorted(tool_list, key=lambda c: c.__module__)

    @staticmethod
    def getToolDescription():
        from proto.HtmlCore import HtmlCore
        core = HtmlCore()
        core.smallHeader("General description")
        core.paragraph("This tool is used to try out ProTo tools that have "
                       "not been installed as separate tools in the tool "
                       "menu. This is typically used for development "
                       "purposes, so that one can polish the tool until it"
                       "is finished for deployment in the tool menu. "
                       "When a tool is installed into the menu, the tool "
                       "disappears from the tool list in this tool."
                       "The logic for inclusion in the list is that there "
                       "exists a Python module with a class that inherits "
                       "from GeneralGuiTool, without there existing "
                       "a Galaxy xml file for the tool.")
        return str(core)



    #@classmethod
    #def getOptionsBoxInstalled(cls):
    #    cls.existing_tools = cls.get_existing_tool_xml_list()
    #    tool_shelve = shelve.open(TOOL_SHELVE, 'r')
    #    cls.installed_classes = [tool_shelve.get(t)[1] for t in tool_shelve.keys()]
    #    tool_shelve.close()
    #    return sorted(cls.installed_classes)
    #
    #
    #@classmethod
    #def getOptionsBoxProtoTools(cls, choices):
    #    proto_tools = sorted(cls.get_proto_tool_list().keys())
    #    return None
    #
    #@classmethod
    #def getOptionsBoxOrphanTools(cls, choices):
    #    orphans = [t for t in cls.get_proto_tool_list().keys() if t not in cls.installed_classes]
    #    return sorted(orphans)
    
    #@classmethod
    #def get_existing_tool_xml_list(cls):
    #    tools = {}
    #    xmls = [x for x in os.listdir(HB_TOOL_DIR) if x.endswith('.xml')]
    #    for fn in xmls:
    #        tree = ET.parse(HB_TOOL_DIR + fn)
    #        root = tree.getroot()
    #        if root.tag == 'tool' and root.attrib.get('tool_type') == 'hyperbrowser_generic':
    #            tool_id = root.attrib['id']
    #            tools[tool_id] = root.attrib
    #    return tools



class InstallToolsTool(GeneralGuiTool):
    prototype = None

    @classmethod
    def _getToolList(cls):
        tool_shelve = shelve.open(TOOL_SHELVE, 'r')
        tool_IDs = set(tool_shelve.keys())
        installed_classes = [tool_shelve.get(t)[1] for t in tool_IDs]
        tool_shelve.close()
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
    #    #tool_file = TOOL_XML_REL_PATH + tool_cls + '.xml'
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
        txt = ''
        if choices.tool and choices.section:
            txt = 'Install %s into %s' % (choices.tool, choices.section)
        tool_cls = choices.tool
        prototype = cls._getProtoType(choices.tool)
        tool_file = choices.toolXMLPath
        tool_type = choices.toolType
        toolConf = GalaxyToolConfig()
        xml = toolConf.addTool(choices.section, tool_file)
        tool_xml = toolConf.createToolXml(tool_file, choices.toolID,
                                          choices.name, prototype.__module__,
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


class GenerateToolsTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "ProTo tool generator"

    @staticmethod
    def getInputBoxNames():
        return [('Package name', 'packageName'),
                ('Module/class name', 'moduleName'),
                ('Tool name', 'toolName'),
                ('Use template with inline documentation', 'template')]

    #@staticmethod
    #def getResetBoxes():
    #    return ['moduleName']
    
    @staticmethod
    def getOptionsBoxPackageName():
        return ''
    
    @staticmethod
    def getOptionsBoxModuleName(prevchoices):
        return 'ChangeMeTool'
    
    @staticmethod
    def getOptionsBoxToolName(prevchoices):
        return 'Title of tool'

    @staticmethod
    def getOptionsBoxTemplate(prevchoices):
        return ['Yes', 'No']
    
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        packagePath = choices.packageName.split('.')
        packageDir = PROTO_TOOL_DIR + '/'.join(packagePath)
        if not os.path.exists(packageDir):
            os.makedirs(packageDir)

        for i in range(len(packagePath)):
            init_py = PROTO_TOOL_DIR + '/'.join(packagePath[0:i+1]) + '/__init__.py'
            if not os.path.exists(init_py):
                print 'creating ', init_py
                open(init_py, 'a').close()
            
        pyname = packageDir + '/' + choices.moduleName + '.py'
        
        if choices.template == 'Yes':
            templatefn = PROTO_TOOL_DIR + 'ToolTemplate.py'
        else:
            templatefn = PROTO_TOOL_DIR + 'ToolTemplateMinimal.py'
        
        with open(templatefn) as t:
            template = t.read()
        
        #template = re.sub(r'ToolTemplate', choices.moduleName, template)
        template = template.replace('ToolTemplate', choices.moduleName)
        template = template.replace('Tool not yet in use', choices.toolName)

        with open(pyname, 'w') as p:
            p.write(template)
        explore_id = quote(choices.moduleName + ': ' + choices.toolName)
        print 'Tool generated: <a href="%s/proto/?tool_id=proto_ExploreToolsTool&sub_class_id=%s">%s: %s</a>' % (URL_PREFIX, explore_id, choices.moduleName, choices.toolName)
        print 'Tool source path: ', pyname

    @staticmethod
    def getToolDescription():
        from proto.HtmlCore import HtmlCore
        core = HtmlCore()
        core.smallHeader("General description")
        core.paragraph("This tool is used to dynamically generate a Python "
                       "module defining a new ProTo tool. After tool "
                       "execution, The tool will be available from the "
                       "'ProTo tool explorer' tool for development purposes.")
        core.divider()
        core.smallHeader("Parameters")
        core.descriptionLine("Package name",
                             "The name of the package where the new tool "
                             "should be installed. The package path is "
                             "relative to 'proto.tools'. If, for instance, "
                             "the package is set to 'mypackage.core', the full"
                             "package hierarchy is 'proto.tools.mypackage."
                             "core'. Any non-existing directories will be "
                             "created as needed.", emphasize=True)
        core.descriptionLine("Module/class name",
                             "The name of the Python module (filename) and "
                             "class for the new tool. For historical reasons, "
                             "ProTo uses 'MixedCase' naming for both the "
                             "module and the class. By convention, it is "
                             "advised (but not required) to end the name "
                             "with 'Tool', e.g. 'MyNewTool'. This will create "
                             "a Python module 'MyNewTool.py' with the class "
                             "'MyNewTool', inheriting from "
                             "'proto.GeneralGuiTool'.", emphasize=True)
        core.descriptionLine("Tool name",
                             "A string with the name or title of the tool. "
                             "This will appear on the top of the tool GUI "
                             "as well as being the default value for the "
                             "tool name in the menu (which can be changed "
                             "when installing).", emphasize=True)
        core.descriptionLine("Use template with inline documentation",
                             "The new Python module is based upon a template"
                             "file containing a simple example tool with "
                             "two option boxes (one selection box and one "
                             "text box). There are two such template files, "
                             "one that contains inline documentation of the "
                             "methods and possible choices, and one without "
                             "the documentation. Advanced users could select "
                             "the latter to make the tool code itself shorter "
                             "and more readable.", emphasize=True)
        return str(core)
