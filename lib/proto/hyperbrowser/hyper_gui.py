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


from proto.hyper_gui import *
from proto.hyper_gui import _disabled


class TrackWrapper:
    has_subtrack = False

    def __init__(self, name, api, preTracks, galaxy, datasets, genome='', ucscTracks=True):
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
        enc_dataset_id = self.galaxy.encode_id(dataset.dataset_id)
        sel_id = sel.split(',')[1] if sel else None
        val = 'galaxy,' + enc_dataset_id + ',' + dataset.extension + ',' + str(dataset.hid) + quote(' - ' + name, safe='')
        html = '<option value="%s" %s>%d: %s [%s]</option>\n' % (val, 'selected' if enc_dataset_id == sel_id else '', dataset.hid, name, dataset.dbkey)
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
        if (len(self.definition()) >= 1 and not self.hasSubtrack()) or self.valueLevel(0) == '':
            self.valid = self.api.trackValid(self.genome, self.definition())
            if self.valid == True:
                return True
        print self.valid
        return False

    def definition(self, unquotehistoryelementname=True, use_path=False):
        arr = [self.main]
        if self.main == 'galaxy' and self.file:
            f = self.file.split(',')
#            path = self.galaxy.getDataFilePath(f[1])
            if not use_path:
                dataset_id = self.galaxy.encode_id(f[1]) if len(f[1]) < 16 and f[1].isdigit() else f[1]
            else:
                dataset_id = self.galaxy.getDataFilePath(f[1])

            arr.append(str(f[2]))
            arr.append(str(dataset_id))
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

