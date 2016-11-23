from proto.config.Security import GALAXY_SECURITY_HELPER_OBJ, GALAXY_BASE_DIR, getFromConfig, getUniverseConfigParser


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
OUTPUT_PRECISION = int(getFromConfig(config, 'output_precision', '4', 'galaxy_proto'))
STATIC_REL_PATH = URL_PREFIX + '/static/proto'
STATIC_PATH = GALAXY_BASE_DIR + '/' + STATIC_REL_PATH
GALAXY_URL = URL_PREFIX
GALAXY_FILE_PATH = GALAXY_BASE_DIR + '/' + getFromConfig(config, 'file_path', 'database/files')


def userHasFullAccess(galaxyUserName):
    return galaxyUserName in ADMIN_USERS + RESTRICTED_USERS if galaxyUserName not in [None, ''] else False
