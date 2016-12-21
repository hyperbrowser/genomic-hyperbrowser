# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import

import sys, os

from galaxy.web.base.controller import web, error, BaseUIController
import logging

log = logging.getLogger( __name__ )

import traceback
from multiprocessing import Process, Pipe, Queue
from importlib import import_module

#from sqlalchemy import create_engine, event, exc
#from sqlalchemy.orm.session import Session, sessionmaker
#from sqlalchemy.orm.scoping import scoped_session



class ProtoController( BaseUIController ):

    def run_fork(self, response, trans, mako):
        # this can close active connections in parent threads, since db server endpoint closes
        #trans.sa_session.get_bind().dispose()

        # don't know why this has no effect
        #engine = create_engine(trans.app.config.database_connection, pool_size=1)
        #trans.app.model.context = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=True))

        # logging locks and/or atexit handlers may be cause of deadlocks in a fork from thread
        # attempt to fix by shutting down and reloading logging module and clear exit handlers
        # logging.shutdown()
        # import atexit
        # for handler in atexit._exithandlers:
        #    print repr(handler)
        #    try:
        #        handler[0]()
        #    except Exception, e:
        #        print e
        #
        # atexit._exithandlers = []
        # reload(logging)
        # log.warning('fork log test')
        
        exc_info = None
        html = ''
        #response.send_bytes('ping')

        try:
            html, exc_info = self.run_tool(mako, trans)
        except Exception, e:
            html = '<html><body><pre>\n'
            if exc_info:
               html += str(e) + ':\n' + exc_info + '\n\n'
#               html += str(e) + ':\n' + ''.join(traceback.format_exception(exc_info[0],exc_info[1],exc_info[2])) + '\n\n'
            html += str(e) + ':\n' + traceback.format_exc() + '\n</pre></body></html>'

        response.send_bytes(html)
        response.close()

        #trans.sa_session.flush()
        #engine.dispose()

    def run_tool(self, mako, trans):
        toolController = None
        exc_info = None
        try:
            toolModule = import_module('proto.' + mako)
            toolController = toolModule.getController(trans)
        except Exception, e:
            #                print e
            exc_info = sys.exc_info()
        if mako.startswith('/'):
            template_mako = mako + '.mako'
            html = trans.fill_template(template_mako, trans=trans, control=toolController)
        else:
            template_mako = '/proto/' + mako + '.mako'
            html = trans.fill_template(template_mako, trans=trans, control=toolController)
        return html, exc_info

    @web.expose
    def index(self, trans, mako = 'generictool', **kwd):

        if kwd.has_key('rerun_hda_id'):
            self._import_job_params(trans, kwd['rerun_hda_id'])
                    
        if isinstance(mako, list):
            mako = mako[0]

        timeout = 30
        retry = 3
        while retry > 0:
            retry -= 1

            my_end, your_end = Pipe()
            proc = Process(target=self.run_fork, args=(your_end,trans,str(mako)))

            #trans.sa_session.flush()

            # this avoids database exceptions in fork, but defies the point of having a
            # connection pool
            #trans.sa_session.get_bind().dispose()

            # attempt to fully load history/dataset objects to avoid "lazy" loading from
            # database in forked process
            if trans.get_history():
                for hda in trans.get_history().active_datasets:
                    _ = hda.visible, hda.state, hda.dbkey, hda.extension, hda.datatype

            proc.start()
            html = ''
            if proc.is_alive():
                if my_end.poll(timeout):
                    #ping = my_end.recv_bytes()
                    html = my_end.recv_bytes()
                    my_end.close()
                    break
                else:
                    log.warn('Fork timed out after %d sec. Retrying...' % (timeout,))
            else:
                log.warn('Fork died on startup.')
                break

            proc.join(1)
            if proc.is_alive():
                proc.terminate()
                log.warn('Fork did not exit, terminated.')

        return html


    @web.json
    def json(self, trans, module = None, **kwd):
        response = Queue()
        proc = Process(target=self.__json, args=(response,trans,module,kwd))
        proc.start()
        dict = response.get(True, 120)
        proc.join(30)
        if proc.is_alive():
            proc.terminate()
            print 'json fork did not join; terminated.'
        response = None
        return dict

    @web.json
    def check_job(self, trans, pid = None, filename = None):
        # Avoid caching
        trans.response.headers['Pragma'] = 'no-cache'
        trans.response.headers['Expires'] = '0'
        rval = {'running': True}
        try:
            os.kill(int(pid), 0)
        except OSError:
            rval['running'] = False
        
        return rval


    def _import_job_params(self, trans, id=None):
        """
        Copied from ToolController.rerun()
        Given a HistoryDatasetAssociation id, find the job and that created
        the dataset, extract the parameters.
        """
        if not id:
            error( "'id' parameter is required" );
        try:
            id = int( id )
        except:
            error( "Invalid value for 'id' parameter" )
        # Get the dataset object
        data = trans.sa_session.query( trans.app.model.HistoryDatasetAssociation ).get( id )
        #only allow rerunning if user is allowed access to the dataset.
        if not trans.app.security_agent.can_access_dataset( trans.get_current_user_roles(), data.dataset ):
            error( "You are not allowed to access this dataset" )
        # Get the associated job, if any. If this hda was copied from another,
        # we need to find the job that created the origial hda
        job_hda = data
        while job_hda.copied_from_history_dataset_association:#should this check library datasets as well?
            job_hda = job_hda.copied_from_history_dataset_association
        if not job_hda.creating_job_associations:
            error( "Could not find the job for this dataset" )
        # Get the job object
        job = None
        for assoc in job_hda.creating_job_associations:
            job = assoc.job
            break   
        if not job:
            raise Exception("Failed to get job information for dataset hid %d" % data.hid)
        ## Get the job's parameters
        try:
            trans.request.rerun_job_params = job.get_param_values( trans.app, ignore_errors = True )
            trans.request.rerun_job_params['tool_id'] = job.tool_id
        except:
            raise Exception( "Failed to get parameters for dataset id %d " % data.id )
