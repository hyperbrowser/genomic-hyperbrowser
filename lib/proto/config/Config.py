from ConfigParser import SafeConfigParser
import os


GALAXY_BASE_DIR = os.path.abspath(os.path.dirname(__file__) + '/../../../.')

OUTPUT_PRECISION = 4


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


def getFromConfig(config, key, default, section='app:main'):
    try:
        return config.get(section, key)
    except:
        return default


def getUrlPrefix(config):
    prefix = getFromConfig(config, 'prefix', '', 'filter:proxy-prefix')
    filterWith = getFromConfig(config, 'filter-with', '', 'app:main')
    return prefix if filterWith == 'proxy-prefix' else ''


config = getUniverseConfigParser()

if not globals().get('URL_PREFIX'):
    URL_PREFIX = getUrlPrefix(config)


GALAXY_REL_TOOL_CONFIG_FILE = getFromConfig(config, 'tool_config_file', 'config/tool_conf.xml')
ADMIN_USERS = [username.strip() for username in
               getFromConfig(config, 'admin_users', '').split(',')]
RESTRICTED_USERS = [username.strip() for username in
                    getFromConfig(config, 'restricted_users', '', 'galaxy_proto').split(',')]
STATIC_REL_PATH = URL_PREFIX + '/static/proto'
STATIC_PATH = GALAXY_BASE_DIR + '/' + STATIC_REL_PATH
GALAXY_URL = URL_PREFIX
GALAXY_FILE_PATH = GALAXY_BASE_DIR + '/' + getFromConfig(config, 'file_path', 'database/files')


def userHasFullAccess(galaxyUserName):
    return galaxyUserName in ADMIN_USERS + RESTRICTED_USERS if galaxyUserName not in [None, ''] else False


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
