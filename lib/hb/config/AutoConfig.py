#from config.LocalOSConfig import *

from proto.config.Config import \
    OUTPUT_PRECISION, GALAXY_BASE_DIR, getUniverseConfigParser, config, getFromConfig, \
    getUrlPrefix, GALAXY_SECURITY_HELPER_OBJ, URL_PREFIX, RESTRICTED_USERS

from ConfigParser import SafeConfigParser
#from gold.application.RSetup import R_VERSION
import os

# GALAXY_BASE_DIR = os.path.abspath(os.path.dirname(__file__) + '/../../.')

# def getUniverseConfigParser():
#     config = SafeConfigParser({'here': GALAXY_BASE_DIR})
#     configFn = GALAXY_BASE_DIR + '/universe_wsgi.ini'
#     if os.path.exists(configFn):
#         config.read(configFn)
#     return config
#
# def getFromConfig(config, key, default, section='app:main'):
#     try:
#         return config.get(section, key)
#     except:
#         return default

# def getGalaxyConfiguration():
#     import galaxy.config
#     configParser = getUniverseConfigParser()
#     configDict = {}
#     for key, value in configParser.items("app:main"):
#         configDict[key] = value
#     return galaxy.config.Configuration(**configDict)

# def getUrlPrefix(config):
#     prefix = getFromConfig(config, 'prefix', '', 'filter:proxy-prefix')
#     filterWith = getFromConfig(config, 'filter-with', '', 'app:main')
#     return prefix if filterWith == 'proxy-prefix' else ''
#
# def galaxyGetSecurityHelper(config):
#     from galaxy import eggs
#     from galaxy.web.security import SecurityHelper
#
#     id_secret = getFromConfig(config, 'id_secret', 'USING THE DEFAULT IS NOT SECURE!')
#     return SecurityHelper(id_secret=id_secret)

# config = getUniverseConfigParser()

# try:
#     GALAXY_SECURITY_HELPER_OBJ = galaxyGetSecurityHelper(config)
# except:
#     GALAXY_SECURITY_HELPER_OBJ = None

# if not 'URL_PREFIX' in globals():
#     URL_PREFIX = getUrlPrefix(config)

# COOKIE_PATH = URL_PREFIX if URL_PREFIX != '' else '/'

HB_SOURCE_CODE_BASE_DIR = GALAXY_BASE_DIR + '/lib/hb'

GALAXY_REL_FILE_PATH = getFromConfig(config, 'file_path', 'database/files')
GALAXY_REL_NEW_FILE_PATH = getFromConfig(config, 'new_file_path', 'database/tmp')
GALAXY_REL_TOOL_CONFIG_FILE = getFromConfig(config, 'tool_config_file', 'config/tool_conf.xml')
GALAXY_REL_TOOL_PATH = getFromConfig(config, 'tool_path', 'tools')
GALAXY_REL_TOOL_DATA_PATH = getFromConfig(config, 'tool_data_path', 'tool-data')
GALAXY_REL_DATATYPES_CONFIG_FILE = getFromConfig(config, 'datatypes_config_file', 'config/datatypes_conf.xml')
GALAXY_REL_JOB_WORKING_DIR = getFromConfig(config, 'job_working_directory', 'database/job_working_directory')
GALAXY_TMP_DIR = getFromConfig(config, 'new_file_path','database/tmp')

EXT_NONSTANDARD_DATA_PATH = getFromConfig(config, 'ext_nonstandard_data_path', '', 'hyperbrowser')
EXT_ORIG_DATA_PATH = getFromConfig(config, 'ext_orig_data_path', '', 'hyperbrowser')
EXT_PARSING_ERROR_DATA_PATH = getFromConfig(config, 'ext_parsing_error_data_path', '', 'hyperbrowser')
EXT_PROCESSED_DATA_PATH = getFromConfig(config, 'ext_processed_data_path', '', 'hyperbrowser')
EXT_MEMOIZED_DATA_PATH = getFromConfig(config, 'ext_memoized_data_path', '', 'hyperbrowser')

EXT_DATA_FILES_PATH = getFromConfig(config, 'ext_data_files_path', '', 'hyperbrowser')
EXT_UPLOAD_FILES_PATH = getFromConfig(config, 'ext_upload_files_path', '', 'hyperbrowser')
EXT_STATIC_FILES_PATH = getFromConfig(config, 'ext_static_files_path', '', 'hyperbrowser')
EXT_TOOL_DATA_PATH = getFromConfig(config, 'ext_tool_data_path', '', 'hyperbrowser')
EXT_NMER_CHAIN_DATA_PATH = getFromConfig(config, 'ext_nmer_chain_data_path', '', 'hyperbrowser')
EXT_MAPS_PATH = getFromConfig(config, 'ext_maps_path', '', 'hyperbrowser')
EXT_LOG_PATH = getFromConfig(config, 'ext_log_path', '', 'hyperbrowser')
EXT_RESULTS_PATH = getFromConfig(config, 'ext_results_path', '', 'hyperbrowser')
EXT_TMP_PATH = getFromConfig(config, 'ext_tmp_path', '', 'hyperbrowser')

#del config

GALAXY_FILE_PATH = GALAXY_BASE_DIR + '/' + GALAXY_REL_FILE_PATH
GALAXY_NEW_FILE_PATH = GALAXY_BASE_DIR + '/' + GALAXY_REL_NEW_FILE_PATH
GALAXY_TOOL_CONFIG_FILE = GALAXY_BASE_DIR + '/' + GALAXY_REL_TOOL_CONFIG_FILE
GALAXY_TOOL_PATH = GALAXY_BASE_DIR + '/' + GALAXY_REL_TOOL_PATH
GALAXY_TOOL_DATA_PATH = GALAXY_BASE_DIR + '/' + GALAXY_REL_TOOL_DATA_PATH
GALAXY_DATATYPES_CONFIG_FILE = GALAXY_BASE_DIR + '/' + GALAXY_REL_DATATYPES_CONFIG_FILE
GALAXY_JOB_WORKING_DIR = GALAXY_BASE_DIR + '/' + GALAXY_REL_JOB_WORKING_DIR

GALAXY_COMPILED_TEMPLATES = GALAXY_BASE_DIR + '/database/compiled_templates'
GALAXY_TEMPLATES_PATH = GALAXY_BASE_DIR + '/templates'
GALAXY_LIB_PATH = GALAXY_BASE_DIR + '/lib'

# HB_GALAXY_SOURCE_CODE_BASE_DIR = HB_SOURCE_CODE_BASE_DIR + '/galaxy_hb'
# HB_CONFIG_BASE_DIR = HB_SOURCE_CODE_BASE_DIR + '/config'
# HB_SETUP_CONFIG_BASE_DIR = HB_CONFIG_BASE_DIR + '/setup'
# HB_SETUP_CONFIG_DEFAULT_FN = HB_SETUP_CONFIG_BASE_DIR + '/default/default.setup'
HB_SOURCE_DATA_BASE_DIR = HB_SOURCE_CODE_BASE_DIR + '/data'
# HB_SRC_STATIC_PATH = HB_SOURCE_CODE_BASE_DIR + '/galaxy_hb/static/hyperbrowser'

STATIC_REL_PATH = URL_PREFIX + '/static/hyperbrowser'
STATIC_PATH = GALAXY_BASE_DIR + '/static/hyperbrowser'

HB_DATA_BASE_DIR = GALAXY_BASE_DIR + '/hyperbrowser'
TRACKS_BASE_DIR = HB_DATA_BASE_DIR + '/tracks'
NONSTANDARD_DATA_PATH = TRACKS_BASE_DIR + '/collectedTracks'
ORIG_DATA_PATH = TRACKS_BASE_DIR + '/standardizedTracks'
PARSING_ERROR_DATA_PATH = TRACKS_BASE_DIR + '/parsingErrorTracks'
PROCESSED_DATA_PATH = TRACKS_BASE_DIR + '/preProcessedTracks'
NMER_CHAIN_DATA_PATH = TRACKS_BASE_DIR + '/nmerChains'

DATA_FILES_PATH = HB_DATA_BASE_DIR + '/data'
UPLOAD_FILES_PATH = HB_DATA_BASE_DIR + '/upload'
LOG_PATH = HB_DATA_BASE_DIR + '/logs'
SRC_PATH = HB_DATA_BASE_DIR + '/src'
# SRC_STATIC_PATH = SRC_PATH + '/galaxy_hb/static/hyperbrowser'
# HB_EGGS_FILE_PATH = SRC_PATH + '/galaxy_hb/hb_eggs.ini'

RESULTS_PATH = HB_DATA_BASE_DIR + '/results'
RESULTS_FILES_PATH = RESULTS_PATH + '/files'
RESULTS_JOB_WORKING_DIR = RESULTS_PATH + '/job_working_directory'
MEMOIZED_DATA_PATH = RESULTS_PATH + '/memoizedData'
RESULTS_STATIC_PATH = RESULTS_PATH + '/static'
MAPS_PATH = RESULTS_STATIC_PATH + '/maps'
MAPS_COMMON_PATH = MAPS_PATH + '/common'
MAPS_TEMPLATE_PATH = GALAXY_TEMPLATES_PATH + '/hyperbrowser/gmap'
# HB_LIB_PATH = HB_DATA_BASE_DIR + '/lib'
# HB_R_LIBS_DIR = HB_LIB_PATH + '/R/library'

# def CreateWebServerCfgText():
#     txt = ''
#     for i in range(int(GALAXY_ADDITIONAL_WEB_SERVER_COUNT)):
#         txt += '''
# [server:web%d]
# use = egg:Paste#http
# port = %d
# host = 0.0.0.0
# use_threadpool = True
# threadpool_workers = %d
# ''' % (i + 1, int(GALAXY_WEB_SERVER_PORT) + i + 1, int(GALAXY_WEB_SERVER_THREADPOOL_WORKERS))
#     return txt
#
# if globals().has_key('GALAXY_ADDITIONAL_WEB_SERVER_COUNT'):
#     GALAXY_ADDITIONAL_WEB_SERVERS = CreateWebServerCfgText()
