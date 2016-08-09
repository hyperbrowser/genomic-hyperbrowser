import sys, traceback
from importlib import import_module

from galaxy.web.base.controller import web, log
from galaxy.webapps.galaxy.controllers import proto


class HyperController(proto.ProtoController):

    # @staticmethod
    # def __index_pipe_old(response, trans, tool):
    #
    #     exc_info = None
    #     html = ''
    #     try:
    #         from gold.application.GalaxyInterface import GalaxyInterface
    #         template_mako = '/hyperbrowser/' + tool + '.mako'
    #         toolController = None
    #         try:
    #             toolModule = import_module('proto.hyperbrowser.' + tool)
    #             toolController = toolModule.getController(trans)
    #         except Exception, e:
    #             print e
    #             exc_info = sys.exc_info()
    #             pass
    #
    #         html = trans.fill_template(template_mako, trans=trans, hyper=GalaxyInterface, control=toolController)
    #     except Exception, e:
    #         html = '<html><body><pre>\n'
    #         if exc_info:
    #             html += str(e) + ':\n' + ''.join(traceback.format_exception(exc_info[0],exc_info[1],exc_info[2])) + '\n\n'
    #         html += str(e) + ':\n' + traceback.format_exc() + '\n</pre></body></html>'
    #
    #     response.send_bytes(html)
    #     response.close()

    def run_tool(self, mako, trans):
        toolController = None
        exc_info = None
        try:
            toolModule = import_module('proto.hyperbrowser.' + mako.split('/')[-1])
        except ImportError:
            toolModule = None

        if toolModule:
            toolController = toolModule.getController(trans)

        if mako.startswith('/'):
            from gold.application.GalaxyInterface import GalaxyInterface
            template_mako = mako + '.mako'
            #print mako, template_mako
            html = trans.fill_template(template_mako, trans=trans, hyper=GalaxyInterface, control=toolController)
        elif toolController:
            template_mako = '/hyperbrowser/' + mako + '.mako'
            html = trans.fill_template(template_mako, trans=trans, control=toolController)
        return html, exc_info



    @web.expose
    def index(self, trans, mako='/hyperbrowser/analyze', **kwd):
        #print mako
        if isinstance(mako, list):
            mako = mako[0]
        if mako[0] != '/':
            mako = '/hyperbrowser/' + mako
            # print mako
        return super(HyperController, self).index(trans, mako, **kwd)

