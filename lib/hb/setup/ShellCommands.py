from ModFiles import ModFiles
from subprocess import Popen
import sys

class ShellCommands(ModFiles):
    def __init__(self, modListFn, configDict=None):
        ModFiles.__init__(self, modListFn, numCols=1, configDict=configDict)       

    def apply(self):
        for command in self._modList:
            command = command[0]
            process = Popen(['%s' % (command)], shell=True)
            if process.wait() == 0:
                print 'OK: %s' % (command)
            else:
                print 'FAILED: %s' % (command)
                sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ['apply']:
        print '''
Usage: python ShellCommands.py apply shellCommandListFn
        
apply:   Carries out a set of shell commands as specified in the shellCommandListFn file.
'''
        sys.exit(0)

    command = sys.argv[1]
    shellCommands = ShellCommands(sys.argv[2])

    if command == 'apply':
        shellCommands.apply()
    else:
        print 'Nothing done. Should not be possible'

