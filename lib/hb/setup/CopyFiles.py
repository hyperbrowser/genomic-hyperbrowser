from ModFiles import ModFiles
from config.Config import GALAXY_BASE_DIR, HB_GALAXY_SOURCE_CODE_BASE_DIR
from subprocess import PIPE, Popen
import sys
import os

class CopyFiles(ModFiles):
    RSYNC_CMD = "rsync -rpEic --exclude='.*' --exclude='*~' --exclude='#*' --exclude='*.orig' --exclude='*.old'"
    def __init__(self, modListFn):
        ModFiles.__init__(self, modListFn, numCols=2)

    def _getFns(self, hbFn, galaxyFn):
        fromFn = self._fixIfDir(os.sep.join([HB_GALAXY_SOURCE_CODE_BASE_DIR, hbFn]))
        toFn = self._fixIfDir(os.sep.join([GALAXY_BASE_DIR, galaxyFn]))
        toFn = self._getUnlocalizedFnIfExists(toFn)
        return fromFn, toFn

    def _getFnFromRsyncOut(self, text):
        return [' '.join(x.strip().split()[1:]) for x in text]

    def _copy(self, fromFn, toFn, shortFromFn, rsyncCmd, renameFunc):
        if not self._filesExist([fromFn], printError=True):
            return False

        process = Popen([rsyncCmd + ' -c --dry-run %s %s' % (fromFn, toFn)], shell=True, stdout=PIPE)
#        print os.linesep.join([x for x in process.stdout])
        filesToCopy = self._getFnFromRsyncOut(process.stdout)
        if len(filesToCopy) == 0:
            print 'UNCHANGED: %s -> %s (File/directory has already been copied)' % (shortFromFn, toFn)
            return True

        for fn in filesToCopy:
            if fn == 'non-regular':
                print 'FAILED: %s (File is symlink)' % toFn
                return False
            galaxyFn = os.sep.join([os.path.dirname(toFn), fn])
            if not os.path.isdir(galaxyFn):
                galaxyFn = self._getUnlocalizedFnIfExists(galaxyFn)
                if self._filesExist([galaxyFn]):
                    self._copyFile(galaxyFn, renameFunc(galaxyFn))
                
        process = Popen([rsyncCmd + ' -c %s %s' % (fromFn, toFn)], shell=True, stdout=PIPE)
        filesCopied = self._getFnFromRsyncOut(process.stdout)
        for fn in filesCopied:
            hbFn = os.sep.join([os.path.dirname(shortFromFn), fn])
            galaxyFn = os.sep.join([os.path.dirname(toFn), fn])
            if not os.path.isdir(fromFn):
                galaxyFn = self._getUnlocalizedFnIfExists(galaxyFn)
            print 'COPIED: %s -> %s' % (hbFn, galaxyFn)

        return True

    def update(self):
        for hbFn, galaxyFn in self._modList:
            toFn, fromFn = self._getFns(hbFn, galaxyFn)
            self._copy(fromFn, toFn, hbFn, self.RSYNC_CMD + ' --existing', self._oldFn)

    def apply(self):
        for hbFn, galaxyFn in self._modList:
            fromFn, toFn = self._getFns(hbFn, galaxyFn)
            ok = self._copy(fromFn, toFn, hbFn, self.RSYNC_CMD, self._origOrOldFn)
            if not ok:
                sys.exit(1)
        return True

    def cleanup(self):
        for hbFn, galaxyFn in self._modList:
            fromFn, toFn = self._getFns(hbFn, galaxyFn)
            self._cleanUpFile(fromFn)

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ['update', 'apply', 'cleanup']:
        print '''
Usage: python CopyFiles.py update|apply|cleanup patchListFn
        
update:  Copies original Galaxy files to the HyperBrowser file tree. Only
         copies files that exist in the HyperBrowser tree and are different.
         N.B. This overwrites the HyperBrowser files (but a copy is stored
         as <filename>.old).

apply:   Copies HyperBrowser files to the Galaxy file tree. Only copies files
         that are different. Works recursively for directories.
         N.B. This overwrites the Galaxy files (but a copy is stored as
         <filename>.orig).

         If an unlocalized version of the Galaxy file is present,
         this is the file that is overwritten (and a copy is stored as <filename>.old).
         N.B. This does not work recursively for directories.
         
cleanup: Removes old files from the HyperBrowser file tree. This is typically
         called prior to svn commit.
'''
        sys.exit(0)

    command = sys.argv[1]
    copyFiles = CopyFiles(sys.argv[2])

    if command == 'update':
        copyFiles.update()
    elif command == 'apply':
        copyFiles.apply()
    elif command == 'cleanup':
        copyFiles.cleanup()
    else:
        print 'Nothing done. Should not be possible'

