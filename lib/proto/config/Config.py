from proto.config.GalaxyConfigParser import GALAXY_BASE_DIR, GalaxyConfigParser


def getUrlPrefix(config):
    prefix = config.getWithDefault('prefix', '', 'filter:proxy-prefix')
    filterWith = config.getWithDefault('filter-with', '', 'app:main')
    return prefix if filterWith == 'proxy-prefix' else ''


config = GalaxyConfigParser()

if not globals().get('URL_PREFIX'):
    URL_PREFIX = getUrlPrefix(config)

GALAXY_REL_TOOL_CONFIG_FILE = config.getWithDefault('tool_config_file', 'config/tool_conf.xml')
ADMIN_USERS = [username.strip() for username in
               config.getWithDefault('admin_users', '').split(',')]
RESTRICTED_USERS = [username.strip() for username in
                    config.getWithDefault('restricted_users', '', 'galaxy_proto').split(',')]
OUTPUT_PRECISION = int(config.getWithDefault('output_precision', '4', 'galaxy_proto'))
STATIC_DIR = '/static/proto'
STATIC_REL_PATH = URL_PREFIX + STATIC_DIR
STATIC_PATH = GALAXY_BASE_DIR + STATIC_DIR
GALAXY_FILE_PATH = GALAXY_BASE_DIR + '/' + config.getWithDefault('file_path', 'database/files')
PROTO_TOOL_SHELVE_FN = GALAXY_BASE_DIR + '/database/proto-tool-cache.shelve'


def userHasFullAccess(galaxyUserName):
    return galaxyUserName in ADMIN_USERS + RESTRICTED_USERS \
        if galaxyUserName not in [None, ''] else False
