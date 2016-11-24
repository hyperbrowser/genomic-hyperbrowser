from ModFiles import ModFiles
from config.Config import GALAXY_BASE_DIR, HB_GALAXY_SOURCE_CODE_BASE_DIR
import shutil
import sys
import os

class LocalizeFiles(ModFiles):
    def __init__(self, modListFn):
        ModFiles.__init__(self, modListFn, numCols=1)
        
    def _getFn(self, galaxyFn):
        return self._fixIfDir(os.sep.join([GALAXY_BASE_DIR, galaxyFn]))

    def _doLocalization(self, fn):
        self._writeContentsToFile(fn, self._getLocalizedContents(fn))

    def _getLocalizedContents(self, fn):
        inFile = open(fn, 'r')
        contents = inFile.read()
        inFile.close()

        return self._applyLocalization(contents)

    def _areContentsEqual(self, fn, contents):
        inFile = open(fn, 'r')
        fileContents = inFile.read()
        inFile.close()

        return fileContents == contents

    def _writeContentsToFile(self, fn, contents):
        outFile = open(fn, 'w')
        outFile.write(contents)
        outFile.close()

    def apply(self):
        for galaxyFn in self._modList:
            galaxyFn = galaxyFn[0]
            origFn = self._getFn(galaxyFn)
            if not self._filesExist([origFn], printError=True):
                continue
            
            if not self._filesExist([self._unlocalizedFn(origFn)]):
                shutil.move(origFn, self._unlocalizedFn(origFn))

            localizedContents = self._getLocalizedContents(self._unlocalizedFn(origFn))
            if self._filesExist([origFn]):
                if self._areContentsEqual(origFn, localizedContents):
                    print 'UNCHANGED: %s (File has already been localized)' % origFn
                    continue
                shutil.move(origFn, self._oldFn(origFn))
            
            self._writeContentsToFile(origFn, localizedContents)
            print 'LOCALIZED: -> %s' % origFn

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ['update', 'apply', 'cleanup']:
        print '''
Usage: python LocalizeFiles.py apply patchListFn

apply:   Localizes HyperBrowser files in the Galaxy file tree. Replaces
         $CONSTANT with respective value from Config.py, LocalOSConfig.py
         or AutoConfig. Also replaces $%CONSTANT with the respective
         URL-encoded string. 

         N.B. The unlocalized versions of the Galaxy files is stored as
         <filename>.unlocalized). Any old localized versions of the Galaxy
         files are stored as <filename>.old.

         Note that the files also should previously be either copied or
         patched (by CopyFiles or PatchFiles, respectively).
'''
        sys.exit(0)

    command = sys.argv[1]
    localizeFiles = LocalizeFiles(sys.argv[2])

    if command == 'apply':
        localizeFiles.apply()
    else:
        print 'Nothing done. Should not be possible'

