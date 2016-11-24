# NB: imported by Galaxy (managers.hdas). Should not import other ProTo modules.
# This module will only be loaded once, during startup of Galaxy, and not dynamically by ProTo
# tools. This means changes in the module will not take effect until Galaxy is restarted.

import os
from ConfigParser import SafeConfigParser


GALAXY_BASE_DIR = os.path.abspath(os.path.dirname(__file__) + '/../../../.')


class GalaxyConfigParser(SafeConfigParser):
    def __init__(self):
        SafeConfigParser.__init__(self, {'here': GALAXY_BASE_DIR})

        for configRelFn in [os.environ.get('GALAXY_CONFIG_FILE'),
                            'config/galaxy.ini',
                            'config/galaxy.ini.sample']:
            if configRelFn:
                configFn = GALAXY_BASE_DIR + '/' + configRelFn
                if os.path.exists(configFn):
                    self.read(configFn)
                    break
        else:
            raise Exception('No Galaxy config file found at path: ' + configFn)

    def getWithDefault(self, key, default, section='app:main'):
        try:
            return self.get(section, key)
        except:
            return default
