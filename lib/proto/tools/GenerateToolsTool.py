import os
from urllib import quote

from proto.config.Config import URL_PREFIX, PROTO_TOOL_DIR
from proto.tools.GeneralGuiTool import GeneralGuiTool


class GenerateToolsTool(GeneralGuiTool):
    MAX_DIR_LEVELS = 5
    NO_SELECTION = '--- Select a tool directory ---'
    NEW_DIR = '-- Create a new directory --'

    @staticmethod
    def getToolName():
        return "ProTo tool generator"

    @classmethod
    def getInputBoxNames(cls):
        return [('', 'hidden')] + \
               [('  ' * i + ('|_' if i > 0 else '') +
                'Choose directory for new tool (level %s)' % (i+1), 'dirLevel%s' % i)
                for i in range(cls.MAX_DIR_LEVELS)] + \
               [('    ' * i + 'Name of new directory', 'newName%s' % i)
                for i in range(cls.MAX_DIR_LEVELS)] + \
               [('Package name', 'packageName'),
                ('Module/class name', 'moduleName'),
                ('Tool name', 'toolName'),
                ('Use template with inline documentation', 'template')]

    #@staticmethod
    #def getResetBoxes():
    #    return ['moduleName']

    @staticmethod
    def getOptionsBoxHidden():
        return '__hidden__'

    @classmethod
    def _getSelectedDir(cls, prevChoices, index=MAX_DIR_LEVELS):
        dirs = []
        for i in range(index):
            dirSelection = getattr(prevChoices, 'dirLevel' + i)

            if dirSelection == cls.NEW_DIR:
                dirSelection = getattr(prevChoices, 'newDir' + i).strip()

            if dirSelection != cls.NO_SELECTION:
                dirs.append(dirSelection)
            else:
                break

        return os.path.sep.join([PROTO_TOOL_DIR] + dirs)

    @classmethod
    def _getOptionsBoxDirLevel(cls, prevChoices, index):
        from gold.application.LogSetup import logMessage
        logMessage(repr(prevChoices))
        if index == 0 or getattr(prevChoices, 'dirLevel' + (index - 1)) != cls.NO_SELECTION:
            selectedDir = cls._getSelectedDir(prevChoices, index)
            subDirs = [x for x in os.listdir(selectedDir) if
                       os.path.isdir(os.sep.join(selectedDir, x))]
            return [cls.NO_SELECTION] + subDirs + [cls.NEW_DIR]

    @classmethod
    def _getOptionsBoxNewDir(cls, prevChoices, index):
        curDirChoice = getattr(prevChoices, 'dirLevel' + index)
        if curDirChoice == cls.NEW_DIR:
            return '', 1

    @classmethod
    def setupExtraBoxMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_DIR_LEVELS):
            setattr(cls, 'getOptionsBoxDirLevel%s' % i,
                    partial(cls._getOptionsBoxDirLevel, index=i))
            setattr(cls, 'getOptionsBoxNewDir%s' % i,
                    partial(cls._getOptionsBoxNewDir, index=i))

        from gold.application.LogSetup import logMessage

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

GenerateToolsTool.setupExtraBoxMethods()
