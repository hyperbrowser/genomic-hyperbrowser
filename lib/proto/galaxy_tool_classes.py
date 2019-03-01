import os, urllib, shelve, logging, json
from xml.etree import ElementTree

from galaxy.tools import Tool, DataSourceTool
from galaxy.tools.deps import build_dependency_manager, CondaDependencyResolver, ToolRequirements
from galaxy.tools.deps.conda_util import CondaTarget
from galaxy.tools.deps.resolvers.conda import CONDA_SOURCE_CMD
from galaxy.tools.parser.output_actions import ToolOutputActionGroup
from galaxy.tools.parser.output_objects import ToolOutput
from galaxy.tools.parser.output_collection_def import DEFAULT_DATASET_COLLECTOR_DESCRIPTION
from galaxy.util.odict import odict

log = logging.getLogger( __name__ )


# Helper classes

class ProtoCondaDependencyResolver(CondaDependencyResolver):
    def _get_mulled_environment_name(self, requirements):
        expanded_requirements = ToolRequirements(
            [self._expand_requirement(r) for r in requirements])
        conda_targets = [CondaTarget(r.name, version=r.version) for r in expanded_requirements]
        return self.merged_environment_name(conda_targets)

    def get_conda_activate_source(self, requirements):
        env_name = self._get_mulled_environment_name(requirements)
        environment_path = self.conda_context.env_path(env_name)
        activate_bin_path = self.conda_context.activate
        return CONDA_SOURCE_CMD % (
                    environment_path,
                    activate_bin_path,
                    environment_path
                )


# Proto Tools

class ProtoTool(DataSourceTool):
    tool_type = 'proto'

    @property
    def requires_galaxy_python_environment(self):
        # Setting this to False will enable activation of tool-specific Conda environment by
        # Galaxy, which by design excludes the Galaxy Python environment.
        #
        # The Galaxy Python environment can still be provided for ProTo tools by an
        # adjustment in protoToolExecute.py, which adds the Galaxy "lib" directory to the
        # beginning of PYTHONPATH. However, if the conda environment contains another Python
        # installation, it will override the Galaxy Python environment. Thus this solution only
        # works if the Conda environment does not contain Python.
        #
        # Do to the complicated issues described above, the default value is set to True. A
        # different way of activating a tool-specific Conda environment is described in
        # GeneralGuiTool.py.
        #
        # TODO: If some ProTo tools require this to be set to False, one should implement
        # tool-specific configuration of this option, instead of this global one.
        return True

    def parse_inputs( self, root ):
        Tool.parse_inputs( self, root )
        
    def exec_before_job( self, app, inp_data, out_data, param_dict):
        #morj: odict has lost order, create new odict with output as first output
        out_data2 = odict()
        if out_data.has_key('output'):
            out_data2['output'] = out_data['output']

        for name, data in out_data.items():
            if name == 'output':
                ext = param_dict.get('datatype', param_dict.get('format'))
                if ext:
                    data = app.datatypes_registry.change_datatype(data, ext)
                    param_dict['datatype'] = ext
            job_name = param_dict.get('job_name')
            if job_name:
                if data.name == self.name:
                    data.name = urllib.unquote(job_name)
            out_data2[name] = data
        
        param_dict['file_path'] = os.path.abspath(os.path.join(app.config.root, app.config.file_path))
        # Galaxy removes the tool_id from params, add it back for ProTo
        param_dict['tool_id'] = self.id
        DataSourceTool.exec_before_job(self, app, inp_data, out_data2, param_dict)
        
    def exec_after_process(self, app, inp_data, out_data, param_dict, job = None):
        job_info = param_dict.get('job_info')
        if job_info:
            for name, data in out_data.items():
                data.info = urllib.unquote(job_info)
            self.sa_session.flush()


class ProtoGenericTool(ProtoTool):
    tool_type = 'proto_generic'
    proto_mako = 'generictool'
    proto_action = '/proto'
    proto_command = '$GALAXY_ROOT_DIR/lib/proto/protoToolExecute.py $output'

    def parse( self, tool_source, guid=None ):
        root = tool_source.root
        tool_id = root.get('id')
        proto_module = root.get('proto_tool_module')
        proto_class = root.get('proto_tool_class')

        requirements = tool_source.parse_requirements_and_containers()[0]
        if len(requirements) > 0:
            dep_manager = build_dependency_manager(self.app.config)
            conda_dep_resolver = ProtoCondaDependencyResolver(dep_manager)
            conda_activate_source = conda_dep_resolver.get_conda_activate_source(requirements)
        else:
            conda_activate_source = None

        if proto_module and proto_class:
            s = shelve.open('database/proto-tool-cache.shelve')
            s[tool_id] = (proto_module, proto_class, conda_activate_source)
            s.close()

        if root.find('inputs') is None:
            inputs = ElementTree.Element('inputs')
            inputs.append(ElementTree.Element('param', name='mako', type='hidden', value=self.proto_mako))
            inputs.append(ElementTree.Element('param', name='tool_id', type='hidden', value=root.get('id')))
            inputs.append(ElementTree.Element('param', name='tool_name', type='hidden', value=root.get('name')))
            root.append(inputs)
        if root.find('outputs') is None:
            outputs = ElementTree.Element('outputs')
            outputs.append(ElementTree.Element('data', format='html', name='output'))
            root.append(outputs)
        super(ProtoGenericTool, self).parse(tool_source, guid)
        #self.command = '$GALAXY_ROOT_DIR/lib/proto/protoToolExecute.py $output'
        self.command = self.proto_command
        self.interpreter = 'python'
        self.options['sanitize'] = False
        self.action = self.proto_action
        self.check_values = False
        self.method = 'post'

    def execute( self, trans, incoming={}, set_output_hid=True, history=None, **kwargs ):
        """
        Overrides Tool.execute() to dynamically add more output elements
        """

        if incoming.has_key('extra_output'):
            try:
                extra_output = json.loads(urllib.unquote(incoming['extra_output']))
                if isinstance(extra_output, list):
                    
                    if len(self.outputs) > 1:
                        for k in self.outputs.keys():
                            if k != 'output':
                                del self.outputs[k]
                    
                    for item in extra_output:
                        output = ToolOutput(item[0])
                        output.format = item[1]
                        output.change_format = None
                        output.format_source = None
                        output.metadata_source = ""
                        output.parent = None
                        output.label = item[2] if len(item) > 2 and item[2] != None else item[0] 
                        output.count = 1
                        output.filters = []
                        output.from_work_dir = None
                        output.hidden = item[3] if len(item) > 3 else False
                        output.tool = self
                        output.actions = ToolOutputActionGroup( output, None )
                        output.dataset_collector_descriptions = [DEFAULT_DATASET_COLLECTOR_DESCRIPTION]
                        self.outputs[ output.name ] = output

            except:
                log.exception('Could not add extra output elements')

        return self.tool_action.execute( self, trans, incoming=incoming, set_output_hid=set_output_hid, history=history, **kwargs )


proto_tool_types = {'proto': ProtoTool,
                    'proto_generic': ProtoGenericTool}

