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

#note cannot import HB.GalaxyInterface here due to rpy threading issue

from urllib import quote, unquote
from collections import OrderedDict
from galaxy.util.json import from_json_string, to_json_string
import os

def getDataFilePath(root, id):
    hashDir = '/%03d/' % (int(id) / 1000)
    return root + hashDir + 'dataset_' + str(id) + '.dat'

def load_input_parameters( filename, erase_file = False ):
    datasource_params = {}
    try:
        json_params = from_json_string( open( filename, 'r' ).read() )
        datasource_params = json_params.get( 'param_dict' )
    except:
        json_params = None
        for line in open( filename, 'r' ):
            try:
                line = line.strip()
                fields = line.split( '\t' )
                datasource_params[ fields[0] ] = unquote(fields[1]).replace('\r','')
            except:
                continue
    if erase_file:
        open( filename, 'w' ).close() #open file for writing, then close, removes params from file
    return json_params, datasource_params

def fileToParams(filename):
    return load_input_parameters( filename, False )[1]
#    params = {}
#    for line in open(filename, 'r'):
#        try:
#            #print line
#            line = line.strip()
#            fields = line.split('\t')
#            params[fields[0]] = unquote(fields[1]).replace('\r','')
#        except:
#            continue
#    return params

def getJobFromDataset(job_hda):
    # mojo: copied from tool_runner.py
    # Get the associated job, if any. If this hda was copied from another,
    # we need to find the job that created the origial hda
    while job_hda.copied_from_history_dataset_association:#should this check library datasets as well?
        job_hda = job_hda.copied_from_history_dataset_association
    if not job_hda.creating_job_associations:
        print "Could not find the job for this dataset hid %d" % job_hda.hid
        return None
    # Get the job object
    job = None
    for assoc in job_hda.creating_job_associations:
        job = assoc.job
        break   
    if not job:
        print "Failed to get job information for dataset hid %d" % job_hda.hid
    return job


class GalaxyWrapper:
    _data_file_root = None
    trans = None
    params = {}
    
    def __init__(self, trans):
        self.trans = trans
        #self.setDataFileRoot(trans.environ['paste.config']['here'] + '/' + trans.app.config.file_path)
        self.setDataFileRoot(os.path.abspath(os.path.join(trans.app.config.root, trans.app.config.file_path)))
        params = trans.request.rerun_job_params if hasattr(trans.request, 'rerun_job_params') else trans.request.params
        for key in params.keys():
            try:
                self.params[key] = str(params[key]) if params[key] != None else None
            except:
                self.params[key] = params[key]

    def setDataFileRoot(self, root):
        self._data_file_root = root

    def getDataFilePath(self, id):
        hashDir = '/%03d/' % (int(id) / 1000)
        return self._data_file_root + hashDir + 'dataset_' + str(id) + '.dat'

    def getHistory(self, ext, dbkey = None):
        datasets = []
        for dataset in self.trans.get_history().active_datasets:
            if dataset.visible and dataset.state == 'ok':
                if dataset.extension in ext and (dbkey == None or dataset.dbkey == dbkey):
                    datasets.append(dataset)
        return datasets

    def getValidRScripts(self):
        datasets = []
        try:
            for dataset in self.getHistory(['R']):
                rfilename = self.getDataFilePath(dataset.dataset_id)
                qid = '[scriptFn:=' + rfilename.encode('hex_codec') + ':] -> CustomRStat'
                #if hyper.isRScriptValid(tracks[0].definition(), tracks[1].definition(), qid):
                datasets.append(dataset)
        except AttributeError:
            pass
        return datasets

    def optionsFromHistory(self, exts, sel = None):
        html = ''
        for dataset in self.trans.get_history().active_datasets:
            if exts == None or dataset.extension in exts:
                name = dataset.name.replace('[', '(')
                name = name.replace(']', ')')
                val = 'galaxy,' + str(dataset.dataset_id) + ',' + dataset.extension + ',' + str(dataset.hid) + quote(' - ' + name, safe='')
                html += '<option value="%s" %s>%d - %s</option>\n' % (val, selected(val, sel), dataset.hid, name)
        return html

    def optionsFromHistoryFn(self, exts = None, tools = None, select = None):
        #html = ''
        #vals = []
        html = '<option value=""> --- Select --- </option>\n'
        vals = [None]
        for dataset in self.trans.get_history().active_datasets:
            if tools:
                job = getJobFromDataset(dataset)
                tool_id = job.tool_id if job else None
            if dataset.visible and dataset.state == 'ok':
                if exts == None or dataset.extension in exts or any([isinstance(dataset.datatype, ext) for ext in exts if isinstance(ext, type)]):
                    if tools == None or tool_id in tools:
                        name = dataset.name.replace('[', '(')
                        name = name.replace(']', ')')
                        val = ':'.join(['galaxy', dataset.extension, self.getDataFilePath(dataset.dataset_id), str(dataset.hid) + quote(' - ' + name, safe='')])
                        vals.append(val)
                        html += '<option value="%s" %s>%d - %s</option>\n' % (val, selected(val, select), dataset.hid, name)
        return html, vals

    def itemsFromHistoryFn(self, exts = None):
        items = OrderedDict()
        for dataset in self.trans.get_history().active_datasets:
            if exts == None or dataset.extension in exts:
                name = dataset.name.replace('[', '(')
                name = name.replace(']', ')')
                val = ':'.join(['galaxy', dataset.extension, self.getDataFilePath(dataset.dataset_id), str(dataset.hid) + quote(' - ' + name, safe='')])
                #vals.append(val)
                #html += '<option value="%s" %s>%d - %s</option>\n' % (val, selected(val, sel), dataset.hid, name)
                items[str(dataset.dataset_id)] = val
        return items

    def getUserName(self):
        user = self.trans.get_user()
        return user.email if user else ''

    def getUserIP(self):
        return self.trans.environ['REMOTE_ADDR']
        
    def getSessionKey(self):
        session = self.trans.get_galaxy_session()
#        key = session.session_key if session.is_valid and session.user_id else None
        key = session.session_key if session.is_valid else None
        return key
    
    def hasSessionParam(self, param):
        user = self.trans.get_user()
        if user and user.preferences.has_key('hb_' + param):
#            hbdict = from_json_string(user.preferences['hyperbrowser'])
#            if hbdict.has_key(param):
            return True
        return False

    def getSessionParam(self, param):
        prefs = self.trans.get_user().preferences
        value = from_json_string(prefs['hb_'+param])
        return value

    def setSessionParam(self, param, value):
        if self.trans.get_user():
            prefs = self.trans.get_user().preferences
            #hbdict = dict()
            #hbdict[param] = value
            prefs['hb_'+param] = to_json_string(value)
            self.trans.sa_session.flush()


trackListCache = {}

class TrackWrapper:
    has_subtrack = False
    def __init__(self, name, api, preTracks, galaxy, datasets, genome = '', ucscTracks = True):
        params = galaxy.params
        self.api = api
        self.galaxy = galaxy
        self.datasets = datasets
        self.nameMain = name
        self.nameFile = self.nameMain + 'file'
        self.nameState = self.nameMain + '_state'
#        self.nameRecent = self.nameMain + '_recent'
        self.state = params.get(self.nameState)
        if self.state != None:
            self.state = unquote(self.state)

#        if params.has_key(name) and (not params.has_key(self.nameLevel(0)) or params.get(self.nameRecent)):
        if params.has_key(name) and (not params.has_key(self.nameLevel(0))):
            parts = params[name].split(':')
            if len(parts) == 4 and parts[0] == 'galaxy':
                dataset_id = int(parts[2].split('/dataset_')[-1].split('.dat')[0]) if not parts[2].isdigit() else int(parts[2])
                params[self.nameFile] = ','.join([parts[0],str(dataset_id),parts[1],parts[3]])
                self.setValueLevel(0, parts[0])
            else:
                for i in range(len(parts)):
                    self.setValueLevel(i, parts[i])
        
        #if self.valueLevel(0) == '__recent_tracks' and params.get(self.nameRecent):
        #    #raise Exception(params[self.nameRecent])
        #    parts = params[self.nameRecent].split(':')
        #    for i in range(len(parts)):
        #        self.setValueLevel(i, parts[i])
            
        
        #self.preTracks = preTracks
        self.preTracks = []
        self.extraTracks = []
#        self.recentTracks = []
#        self.extraTracks.append(('UCSC tracks', 'ucsc', False))
        if len(datasets) > 0:
            self.extraTracks.append(('-- From history (bed, wig, ...) --', 'galaxy', False))
        self.extraTracks += preTracks

#        if self.galaxy.hasSessionParam('recent_tracks'):
#            self.extraTracks.append(('-- Recently selected tracks --', '__recent_tracks', False))
#            self.recentTracks = self.galaxy.getSessionParam('recent_tracks')

        #self.main = params.get(self.nameMain)
        #if self.main == '-':
        #    self.main = None
        self.main = self.valueLevel(0)
        self.file = params.get(self.nameFile)
        if not self.file and len(self.datasets) > 0:
            self.file = self._makeHistoryOption(self.datasets[0])[1]
            
        self.tracks = []
        self.ucscTracks = ucscTracks
        self.genome = genome
        self.numLevels = len(self.asList())
        self.valid = True

    def _makeHistoryOption(self, dataset, sel = None):
        name = dataset.name.replace('[', '(')
        name = name.replace(']', ')')
        sel_id = int(sel.split(',')[1]) if sel else 0
        val = 'galaxy,' + str(dataset.dataset_id) + ',' + dataset.extension + ',' + str(dataset.hid) + quote(' - ' + name, safe='')
        html = '<option value="%s" %s>%d: %s [%s]</option>\n' % (val, 'selected' if dataset.dataset_id == sel_id else '', dataset.hid, name, dataset.dbkey)
        return (html, val)

    def optionsFromHistory(self, sel = None, exts = None):
        html = ''
        for dataset in self.datasets:
            if exts == None or dataset.extension in exts:
                option = self._makeHistoryOption(dataset, sel)
                html += option[0]
        return html

    def getState(self, q = True):
        return quote(self.state) if self.state and q else self.state if self.state else ''

    def fetchTracks(self):
        for i in range(0, self.numLevels + 1):
            self.getTracksForLevel(i)
        self.numLevels = len(self.tracks)
   
    def hasSubtrack(self):
        #sub = self.valueLevel(self.numLevels - 1)
        #print self.has_subtrack, sub, len(self.tracks), self.numLevels, self.valueLevel(self.numLevels - 1)
        ldef = len(self.definition())
        if len(self.tracks) > ldef:
            if len(self.tracks[ldef]) > 0:
                return True
        return False

    def nameLevel(self, level):
        return self.nameMain + '_' + str(level)

    def valueLevel(self, level):
        val = self.galaxy.params.get(self.nameLevel(level))
        if val == '-':
            return None
        return val

    def setValueLevel(self, level, val):
        self.galaxy.params[self.nameLevel(level)] = val

    def asList(self):
        vals = []
        for i in range(0, 10):
            val = self.valueLevel(i)
            if val != None and val != '-':
                vals.append(val)
            else:
            #    vals.append(None)
                break
        return vals

    def asString(self):
        vals = self.definition(False)
        return ':'.join(vals)

    def selected(self):
        #self.hasSubtrack()
        #print len(self.tracks[len(self.definition())]), self.hasSubtrack()
#        if self.valueLevel(0) == '__recent_tracks':
#            return False
        if (len(self.definition()) >= 1 and not self.hasSubtrack()) or self.valueLevel(0) == '':
            #if self.galaxy.hasSessionParam('recent_tracks'):
            #    recent = self.galaxy.getSessionParam('recent_tracks')
            #    if not isinstance(recent, list):
            #        recent = []
            #else:
            #    recent = []
            #if not self.asString() in recent:
            #    recent.append(self.asString())
            #if len(recent) > 5:
            #    recent = recent[len(recent)-5:]
            #self.galaxy.setSessionParam('recent_tracks', recent)
            self.valid = self.api.trackValid(self.genome, self.definition())
            if self.valid == True:
                return True
        return False

    def definition(self, unquotehistoryelementname = True):
        #if self._definition:
        #    return self._definition
        arr = [self.main]
        if self.main == 'galaxy' and self.file:
            f = self.file.split(',')
            path = self.galaxy.getDataFilePath(f[1])
            #print path
            arr.append(str(f[2]))
            arr.append(str(path))
            if unquotehistoryelementname:
                arr.append(str(unquote(f[3])))
            else:
                arr.append(str(f[3]))
        elif self.valueLevel(0) == '':
            arr = []
        else:
            arr = self.asList()
        return arr

    def getTracksForLevel(self, level):
        if not self.genome:
            return []
        if level < len(self.tracks):
            return self.tracks[level]
        self.has_subtrack = False
        tracks = None
        if level == 0:
            tracks = self.mainTracks()
            val = self.valueLevel(0)
            if val != None:
                ok = False
                for t in tracks:
                    if val == t[1]:
                        ok = True
                if not ok:
                    self.setValueLevel(0, None)
        else:
            trk = []
            for i in range(0, level):
                val = self.valueLevel(i)
                if val != None and val != 'galaxy':
                    trk.append(val)
                else:
                    trk = []
                    break
            if len(trk) > 0 and val not in ['', '-']:
                try:
                    tracks, self.state = self.api.getSubTrackNames(self.genome, trk, False, self.galaxy.getUserName(), self.state)
                except OSError, e:
                    #print e, level, i
                    self.setValueLevel(i, None)
                    self.has_subtrack = False
                    if e.errno != 2:
                        raise e
                if tracks and len(tracks) > 0:
                    self.has_subtrack = True
                    #tracks = None
                #if tracks and len(tracks) == 1 and not tracks[0][1]:
                #    tracks = None
        if tracks == None:
            self.setValueLevel(level, None)
        else:
            self.tracks.append(tracks)
        return tracks

    def mainTracks(self):
        tracks = self.api.getMainTrackNames(self.genome, self.preTracks, self.extraTracks, self.galaxy.getUserName(), self.ucscTracks)
#        for i in range(len(tracks)):
#            if tracks[i][1] == self.main:
#                tracks[i] = (tracks[i][0], tracks[i][1], True)
        return tracks

    #return self.api.getMainTrackNames(self.preTracks, [('-- From history (bed-file) --', 'bed', False), ('-- From history (wig-file) --', 'wig', False)])



def selected(opt, sel):
    return ' selected="selected" ' if opt == sel else ''

def checked(opt, sel):
    return ' checked="checked" ' if opt == sel else ''

def disabled(opt, sel):
    return ' disabled="disabled" ' if opt == sel else ''

def _disabled(opt, sel):
    return ' disabled="disabled" ' if opt != sel else ''

def optionListFromDatasets(datasets, exts = None, sel = None):
    list = []
    for dataset in datasets:
        if exts == None or dataset.extension in exts:
            val = 'galaxy,' + str(dataset.dataset_id) + ',' + dataset.extension
            txt = '%d: %s [%s]' % (dataset.hid, dataset.name, val)
            tup = (txt, val, False)
            list.append(tup)
    return list

def optionsFromDatasets(datasets, exts = None, sel = None):
    html = ''
    for dataset in datasets:
        if exts == None or dataset.extension in exts:
            val = 'galaxy,' + str(dataset.dataset_id) + ',' + dataset.extension
            html += '<option value="%s" %s>%d: %s [%s]</option>\n' % (val, selected(val, sel), dataset.hid, dataset.name, val)
    return html

def optionLinksFromDatasets(rel, datasets, exts = None, sel = None):
    html = ''
    for dataset in datasets:
        if exts == None or dataset.extension in exts:
            val = 'galaxy,' + str(dataset.dataset_id) + ',' + dataset.extension
            html += '<a href="javascript:;" rel="%s" rev="%s" class="%s option">%d: %s [%s]</a>\n' % (rel, val, selected(val, sel), dataset.hid, dataset.name, val)
            #html += '<label class="option"><input type="radio" name="%s" value="%s" %s>%d: %s [%s]</label>\n' % (rel, val, checked(val, sel), dataset.hid, dataset.name, val)
    return html


def joinAttrs(attrs):
    str = ''
    for k, v in attrs.items():
        str += k + '="' + v + '" '
    return str

class Element:
    def __init__(self):
        pass
    def setHTML(self, html):
        self.html = html
    def getHTML(self):
        self.make()
        return self.html;
    def make(self):
        pass


class SelectElement(Element):
    def __init__(self, id = None, options = [], selected = None):
        Element.__init__(self)
        self.id = id
        self.options = options
        self.attrs = {}
        if self.id:
            self.attrs['id'] = self.id
            self.attrs['name'] = self.id    
        self.selectedOption = selected
        self.hasSelection = False
        #self.onChange = "this.form.action = ''; this.form.submit();"
        self.onChange = "reloadForm(this.form, this);"

    def make(self):
        html = '<select ' + joinAttrs(self.attrs) + '>'
        for opt in self.options:
#            if opt[1] == '':
#                val = '*'
            selected = ''
            if (opt[2] and not self.hasSelection) or (self.selectedOption != None and opt[1] == self.selectedOption):
                selected = 'selected'
                self.hasSelection = True
            html += '<option value="%s" %s>%s</option>' % (opt[1], selected, opt[0])
        html += '</select>\n'
        self.setHTML(html)

    def getScript(self):
        self.script = '<script type="text/javascript">\n $(document).ready(function () {'
        self.script += "$('#%s').change(function (){%s})" % (self.attrs['id'], self.onChange)
        self.script += '}); \n</script>\n'
        return self.script


class TrackSelectElement(SelectElement):
    def __init__(self, track, level):
        SelectElement.__init__(self)
        self.id = track.nameLevel(level)
        self.attrs['id'] = self.id
        self.attrs['name'] = self.id
        self.options = [('----- Select ----- ', '-', False)]
        self.selectedOption = track.valueLevel(level)
        self.onChange = "try{$('#" + track.nameLevel(level + 1) + "').val('')} catch(e){} " + self.onChange
        opts = track.getTracksForLevel(level)
        if opts:
            self.options.extend(opts)


