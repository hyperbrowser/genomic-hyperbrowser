# NB: imported by Galaxy (managers.hdas). Should not import other ProTo modules.
# This module will only be loaded once, during startup of Galaxy, and not dynamically by ProTo tools.
# This means changes in the module will not take effect until Galaxy is restarted.

import os
from ConfigParser import SafeConfigParser

GALAXY_BASE_DIR = os.path.abspath(os.path.dirname(__file__) + '/../../../.')


def getUniverseConfigParser():
    config = SafeConfigParser({'here': GALAXY_BASE_DIR})
    configRelFn = os.environ.get('GALAXY_CONFIG_FILE')
    if not configRelFn:
        configRelFn = 'config/galaxy.ini'
    configFn = GALAXY_BASE_DIR + '/' + configRelFn
    if os.path.exists(configFn):
        config.read(configFn)
    else:
        raise Exception('No Galaxy config file found at path: ' + configFn)
    return config


config = getUniverseConfigParser()


def getFromConfig(config, key, default, section='app:main'):
    try:
        return config.get(section, key)
    except:
        return default


def galaxyGetSecurityHelper(config):
    from galaxy.web.security import SecurityHelper

    id_secret = getFromConfig(config, 'proto_id_secret',
                              'USING THE DEFAULT IS ALSO NOT SECURE!',
                              section='galaxy_proto')
    return SecurityHelper(id_secret=id_secret)


try:
    GALAXY_SECURITY_HELPER_OBJ = galaxyGetSecurityHelper(config)
except:
    GALAXY_SECURITY_HELPER_OBJ = None


def galaxySecureEncodeId(plainId):
    return GALAXY_SECURITY_HELPER_OBJ.encode_id(plainId)


def galaxySecureDecodeId(encodedId):
    return GALAXY_SECURITY_HELPER_OBJ.decode_id(str(encodedId))
