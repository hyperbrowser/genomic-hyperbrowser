import sys, traceback
from importlib import import_module

from galaxy.web.base.controller import web, log
from galaxy.webapps.galaxy.controllers import proto


class HyperController(proto.ProtoController):
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

