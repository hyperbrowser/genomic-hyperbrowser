from ModFiles import ModFiles
from config.Config import GALAXY_BASE_DIR, HB_GALAXY_SOURCE_CODE_BASE_DIR
from subprocess import PIPE, Popen
import sys
import os

class PatchFiles(ModFiles):
    def __init__(self, modListFn):
        ModFiles.__init__(self, modListFn, numCols=3)

    def _getFns(self, hbFn, galaxyFn, patchedFn):
        patchFn = self._fixIfDir(os.sep.join([HB_GALAXY_SOURCE_CODE_BASE_DIR, hbFn]))
        targetFn = self._fixIfDir(os.sep.join([GALAXY_BASE_DIR, galaxyFn]))
        patchedFn = self._fixIfDir(os.sep.join([GALAXY_BASE_DIR, patchedFn]))

        if os.path.basename(hbFn) == os.path.basename(targetFn) or \
            os.path.basename(targetFn) == os.path.basename(patchedFn):
            patchBasisFn = self._basisFn(patchFn)
        else:
            patchBasisFn = self._fixIfDir(os.sep.join([HB_GALAXY_SOURCE_CODE_BASE_DIR, \
                                                   os.path.dirname(galaxyFn), \
                                                   os.path.basename(targetFn)]))

        targetFn = self._getUnlocalizedFnIfExists(targetFn)
        patchedFn = self._getUnlocalizedFnIfExists(patchedFn)

        return patchFn, patchBasisFn, targetFn, patchedFn

    def _isDifferent(self, fn1, fn2):
        if not self._filesExist([fn1, fn2]):
            return True

        process = Popen(['diff %s %s | wc -l' % (fn1, fn2)], shell=True, stdout=PIPE)
        return int(process.stdout.readline().strip()) != 0

    def _updateFile(self, fromFn, toFn):
        if not self._filesExist([fromFn], printError=True):
            return False

        if not self._isDifferent(fromFn, toFn):
            print 'UNCHANGED: %s -> %s (Nothing to update)' % (fromFn, toFn)
        else:
            if self._filesExist([toFn]):
                self._copyFile(toFn, self._oldFn(toFn))

            self._copyFile(fromFn, toFn)
            print 'UPDATED: %s -> %s' % (fromFn, toFn)
        return True

    def update(self):
        for hbFn, galaxyFn, patchedFn in self._modList:
            patchFn, patchBasisFn, targetFn, patchedFn = self._getFns(hbFn, galaxyFn, patchedFn)

            if targetFn == patchedFn:
                if self._filesExist([self._origFn(targetFn)]):
                    self._updateFile(fromFn = self._origFn(targetFn), toFn = patchBasisFn)
                    self._updateFile(fromFn = patchedFn, toFn = patchFn)
                else:
                    #The target file and the patch file have the same name, but there is no target.orig file,
                    # i.e. no patches have been applied.
                    self._updateFile(fromFn = targetFn, toFn = patchBasisFn)

            elif self._filesExist([targetFn]):
                    self._updateFile(fromFn = targetFn, toFn = patchBasisFn)
                    self._updateFile(fromFn = patchedFn, toFn = patchFn)

    def _getCorrectTargetFn(self, targetFn, patchedFn):
        if targetFn == patchedFn and os.path.exists(self._origFn(targetFn)):
            return self._origFn(targetFn)
        return targetFn

    def apply(self):
        ok = True
        for hbFn, galaxyFn, patchedFn in self._modList:
            patchFn, patchBasisFn, targetFn, patchedFn = self._getFns(hbFn, galaxyFn, patchedFn)
            if not self._filesExist([patchFn, patchBasisFn, targetFn], printError=True):
                continue

            if self._filesExist([patchedFn]):
                process = Popen(['diff3 -m -E %s %s %s | diff - %s | wc -l' % \
                                 (patchFn, patchBasisFn, self._getCorrectTargetFn(targetFn, patchedFn), patchedFn)], \
                                shell=True, stdout=PIPE)
                if int(process.stdout.readline().strip()) == 0:
                    print 'UNCHANGED: %s -> %s (Patch has already been applied)' % (hbFn, patchedFn)
                    continue

            #if os.path.basename(hbFn) == os.path.basename(galaxyFn) and not self._filesExist([self._origFn(targetFn)]):
            #    self._copyFile(targetFn, self._origFn(targetFn))
            #elif self._filesExist([patchedFn]):
            #    self._copyFile(patchedFn, self._oldFn(patchedFn))

            if targetFn == patchedFn and not self._filesExist([self._origFn(targetFn)]):
                self._copyFile(targetFn, self._origFn(targetFn))

            if self._filesExist([patchedFn]):
                self._copyFile(patchedFn, self._oldFn(patchedFn))

            process = Popen(['diff3 -x %s %s %s | wc -l' % \
                             (patchFn, patchBasisFn, self._getCorrectTargetFn(targetFn, patchedFn))], \
                             shell=True, stdout=PIPE)
            if int(process.stdout.readline().strip()) != 0:
                print 'CONFLICT: %s -> %s' % (hbFn, patchedFn)
                ok = False
                patchedFn = self._conflictFn(patchedFn)

            process = Popen(['diff3 -m -E %s %s %s > %s' % \
                             (patchFn, patchBasisFn, self._getCorrectTargetFn(targetFn, patchedFn), patchedFn)], \
                            shell=True)
            print 'PATCHED: %s -> %s' % (hbFn, patchedFn)
            if not ok:
                sys.exit(1)

    def cleanup(self):
        for hbFn, galaxyFn, patchedFn in self._modList:
            patchFn, patchBasisFn, targetFn, patchedFn = self._getFns(hbFn, galaxyFn, patchedFn)

            self._cleanUpFile(patchFn)
            self._cleanUpFile(patchBasisFn)

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ['update', 'apply', 'cleanup']:
        print '''
Usage: python PatchFiles.py update|apply|cleanup patchListFn

update:  Copies original and patched Galaxy files to the HyperBrowser file tree.
         This is done to create the patch files or update them with the latest
         Galaxy changes.
         N.B.: Make sure that there is no unresolved conflicts in the patched files.

apply:   Applies the HyperBrowser patches to the Galaxy files. Also includes any
         additional changes made after the patch was last updated.
         If an unlocalized version of the Galaxy file is present,
         this is the file that is patched.

         N.B.: Conflicts may occur. In that case, manually edit the patched files.
         Also, if the HyperBrowser file and the Galaxy file have the same name,
         the original Galaxy file is renamed <filename>.orig before patching.

cleanup: Removes old files from the HyperBrowser file tree. This is typically
         called prior to svn commit.
'''
        sys.exit(0)

    command = sys.argv[1]
    patchFiles = PatchFiles(sys.argv[2])

    if command == 'update':
        patchFiles.update()
    elif command == 'apply':
        patchFiles.apply()
    elif command == 'cleanup':
        patchFiles.cleanup()
    else:
        print 'Nothing done. Should not be possible'
