import os
import re
import shelve
import sys
import traceback
from importlib import import_module

from proto.config.Config import SOURCE_CODE_BASE_DIR, PROTO_TOOL_DIR, PROTO_TOOL_SHELVE_FN
from proto.tools.GeneralGuiTool import GeneralGuiTool, MultiGeneralGuiTool


EXCEPT_MODULE_NAMES = ['proto.tools.ExploreToolsTool',
                       'proto.tools.InstallToolsTool',
                       'proto.tools.ToolTemplate',
                       'proto.tools.ToolTemplateMinimal']


def getInstalledProtoTools():
    tool_shelve = shelve.open(PROTO_TOOL_SHELVE_FN, 'r')
    installed_classes = [tool_shelve.get(t)[1] for t in tool_shelve.keys() if os.path.exists(
        os.path.join(SOURCE_CODE_BASE_DIR,
                     tool_shelve.get(t)[0].replace('.', os.path.sep))
        + '.py')]
    tool_shelve.close()
    return installed_classes


def getProtoToolList(exceptClassNames=[], toolDir=PROTO_TOOL_DIR):
    tmp_tools = {}
    tools = {}
    tool_classes = []
    all_installed_sub_classes = set()
    pys = []
    for d in os.walk(toolDir, followlinks=True):
        if d[0].find('.svn') == -1:
            pys += [os.path.join(d[0], f) for f in d[2] if f.endswith('.py') and
                    not any(f.startswith(x) for x in ['.', '#'])]

    # To fix import issue if there are modules in /lib and /lib/proto with the
    # same name (e.g. 'config').
    tmpSysPath = sys.path
    if sys.path[0].endswith('/proto'):
        sys.path = tmpSysPath[1:]

    # print 'Num py', len(wpys)
    for fn in pys:
        with open(fn) as f:
            for line in f:
                m = re.match(r'class +(\w+) *\(([\w ,]+)\)', line)
                if m:
                    class_name = m.group(1)
                    module_name = os.path.splitext(os.path.relpath(
                        os.path.abspath(fn), SOURCE_CODE_BASE_DIR))[0].replace(os.path.sep, '.')
                    try:
                        if module_name not in EXCEPT_MODULE_NAMES:
                            module = import_module(module_name)
                            prototype_cls = getattr(module, class_name)
                            if issubclass(prototype_cls, GeneralGuiTool):
                                if issubclass(prototype_cls, MultiGeneralGuiTool):
                                    if class_name in exceptClassNames and \
                                            prototype_cls.getSubToolClasses():
                                        for sub_cls in prototype_cls.getSubToolClasses():
                                            all_installed_sub_classes.add(sub_cls)
                                elif hasattr(prototype_cls, 'getToolName'):
                                    if class_name not in exceptClassNames:
                                        toolDirLen = len(toolDir.split(os.path.sep)) - \
                                            len(SOURCE_CODE_BASE_DIR.split(os.path.sep))
                                        tool_module = module_name.split('.')[toolDirLen:]
                                        if class_name != tool_module[-1]:
                                            tool_selection_name = '.'.join(tool_module) + \
                                                                  ' [' + class_name + ']'
                                        else:
                                            tool_selection_name = '.'.join(tool_module)

                                        # print (fn, m.group(2), prototype_cls, module_name)
                                        tmp_tools[tool_selection_name] = \
                                            (fn, m.group(2), prototype_cls, module_name)
                    except Exception as e:
                        traceback.print_exc()
                        # break
    # print 'Num protopy', len(tools)

    for tool_selection_name, tool_info in tmp_tools.iteritems():
        prototype_cls = tool_info[2]
        if prototype_cls not in all_installed_sub_classes:
            tools[tool_selection_name] = tool_info
            tool_classes.append(prototype_cls)

    sys.path = tmpSysPath
    return tools, tool_classes


def getToolPrototype(toolId):
    tool_shelve = None
    try:
        tool_shelve = shelve.open(PROTO_TOOL_SHELVE_FN, 'r')
        module_name, class_name = tool_shelve[str(toolId)]
        module = __import__(module_name, fromlist=[class_name])
        # print module, class_name, toolId
        prototype = getattr(module, class_name)(toolId)
        # print "Loaded proto tool:", class_name
    #except KeyError:
    #    prototype = None
    finally:
        if tool_shelve:
            tool_shelve.close()
    return prototype
