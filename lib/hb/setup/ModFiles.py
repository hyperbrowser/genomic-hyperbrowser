from subprocess import Popen
import os
import urllib

class ModFiles(object):
    BASIS_SUFFIX = '.basis'
    OLD_SUFFIX = '.old'
    ORIG_SUFFIX = '.orig'
    CONFLICT_SUFFIX = '.conflict'
    UNLOCALIZED_SUFFIX = '.unlocalized'

    def __init__(self, modListFn, numCols, configDict=None):
        if configDict:
            self._cfgDict = configDict
        else:
            self._cfgDict = self._createConfigDictFromGlobalConfig()

        self._modList = []

        for line in open(modListFn):
            if line.startswith('#') or line.strip() == '':
                continue

            if numCols > 1:
                cols = line.strip().split()
            else:
                cols = [line.strip()]

            assert len(cols) <= numCols, "Line have more than maximum number "\
                "of allowed columns (%d > %d): %s" % (len(cols), numCols, line.strip())
            for i in range(numCols - len(cols)):
                cols.append(cols[0])
            self._modList.append([self._applyLocalization(cols[i]) for i in range(numCols)])

    def _createConfigDictFromGlobalConfig(self):
        import config.Config as Config
        cfgList =  [x for x in dir(Config) if type(Config.__dict__[x]) in [bool, str] and x[0] != '_']
        cfgDict = dict((x, Config.__dict__[x]) for x in cfgList)

        #To remove R dependency from normal Config use
        from gold.application.RSetup import getRVersion
        cfgDict['R_VERSION'] = getRVersion(includePatch=False)
        return cfgDict

    def _applyLocalization(self, contents):
        for cfg in self._cfgDict:
            value = self._cfgDict[cfg]
            if not isinstance(value, str):
                value = repr(value)
            contents = contents.replace('$' + cfg, value)
            contents = contents.replace('$%' + cfg, urllib.quote(value))
        return contents

    def _fixIfDir(self, fn):
        if os.path.isdir(fn) and fn[-1] != os.sep:
            fn += os.sep
        return fn

    def _copyFile(self, fromFn, toFn):
        process = Popen(['cp %s %s' % (fromFn, toFn)], shell=True)
        return process.wait() == 0

    def _isLocalizedFn(self, fn):
        return fn.endswith(self.UNLOCALIZED_SUFFIX)

    def _localizedFn(self, fn):
        if self._isLocalizedFn(fn):
            return fn[:-len(self.UNLOCALIZED_SUFFIX)]
        return fn

    def _oldFn(self, fn):
        return fn + self.OLD_SUFFIX

    def _basisFn(self, fn):
        return fn + self.BASIS_SUFFIX

    def _origFn(self, fn):
        return self._localizedFn(fn) + self.ORIG_SUFFIX

    def _conflictFn(self, fn):
        return fn + self.CONFLICT_SUFFIX

    def _origOrOldFn(self, fn):
        if self._isLocalizedFn(fn):
            return fn + self.OLD_SUFFIX
        return fn + self.ORIG_SUFFIX

    def _getUnlocalizedFnIfExists(self, fn):
        if os.path.exists(self._unlocalizedFn(fn)):
            return self._unlocalizedFn(fn)
        return fn

    def _unlocalizedFn(self, fn):
        return fn + self.UNLOCALIZED_SUFFIX

    def _cleanUpFile(self, fn):
        if os.path.isdir(fn):
            for subFn in os.listdir(fn):
                self._cleanUpFile(os.sep.join([fn, subFn]))

        if not self._filesExist([self._oldFn(fn)]):
            return False

        os.remove(self._oldFn(fn))
        print 'REMOVED: %s' % self._oldFn(fn)
        return True

    def _filesExist(self, fnList, printError=False):
        for fn in fnList:
            if not os.path.exists(fn):
                if printError:
                    print 'FAILED: %s (File does not exist)' % fn
                return False
        return True
