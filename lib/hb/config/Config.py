# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.

#from config.LocalOSConfig import *

from config.DebugConfig import DebugConfig, DebugModes
from proto.config.Config import (config, URL_PREFIX, RESTRICTED_USERS,
                                 GALAXY_BASE_DIR, OUTPUT_PRECISION)

#
# Version information
#

HB_VERSION = 'v2.0'

#
# Functionality settings
#
IS_EXPERIMENTAL_INSTALLATION = True
USE_MEMORY_MEMOIZATION = True
LOAD_DISK_MEMOIZATION = IS_EXPERIMENTAL_INSTALLATION
STORE_DISK_MEMOIZATION = IS_EXPERIMENTAL_INSTALLATION
PRINT_PROGRESS = True
CFG_ALLOW_COMP_BIN_SPLITTING = False
ALLOW_GSUITE_FILE_PROTOCOL = True

#
# Optimization and limits
#

COMP_BIN_SIZE = 100000
MEMMAP_BIN_SIZE = 1024 * 1024
MAX_NUM_USER_BINS = 330000
MAX_LOCAL_RESULTS_IN_TABLE = 100000
TEST_DEBUG = False
USE_PARALLEL = False
BATCH_COL_SEPARATOR = '|'
MULTIPLE_EXTRA_TRACKS_SEPARATOR = '&'
MAX_CONCAT_LEN_FOR_OVERLAPPING_ELS = 20

#
# Paths
#

GALAXY_REL_FILE_PATH = config.getWithDefault('file_path', 'database/files')
GALAXY_REL_NEW_FILE_PATH = config.getWithDefault('new_file_path', 'database/tmp')
GALAXY_REL_TOOL_CONFIG_FILE = config.getWithDefault('tool_config_file', 'config/tool_conf.xml')
GALAXY_REL_TOOL_PATH = config.getWithDefault('tool_path', 'tools')
GALAXY_REL_TOOL_DATA_PATH = config.getWithDefault('tool_data_path', 'tool-data')
GALAXY_REL_DATATYPES_CONFIG_FILE = config.getWithDefault('datatypes_config_file', 'config/datatypes_conf.xml')
GALAXY_REL_JOB_WORKING_DIR = config.getWithDefault('job_working_directory', 'database/job_working_directory')
GALAXY_TMP_DIR = config.getWithDefault('new_file_path','database/tmp')

EXT_NONSTANDARD_DATA_PATH = config.getWithDefault('ext_nonstandard_data_path', '', 'hyperbrowser')
EXT_ORIG_DATA_PATH = config.getWithDefault('ext_orig_data_path', '', 'hyperbrowser')
EXT_PARSING_ERROR_DATA_PATH = config.getWithDefault('ext_parsing_error_data_path', '', 'hyperbrowser')
EXT_PROCESSED_DATA_PATH = config.getWithDefault('ext_processed_data_path', '', 'hyperbrowser')
EXT_MEMOIZED_DATA_PATH = config.getWithDefault('ext_memoized_data_path', '', 'hyperbrowser')

EXT_DATA_FILES_PATH = config.getWithDefault('ext_data_files_path', '', 'hyperbrowser')
EXT_UPLOAD_FILES_PATH = config.getWithDefault('ext_upload_files_path', '', 'hyperbrowser')
EXT_STATIC_FILES_PATH = config.getWithDefault('ext_static_files_path', '', 'hyperbrowser')
EXT_TOOL_DATA_PATH = config.getWithDefault('ext_tool_data_path', '', 'hyperbrowser')
EXT_NMER_CHAIN_DATA_PATH = config.getWithDefault('ext_nmer_chain_data_path', '', 'hyperbrowser')
EXT_MAPS_PATH = config.getWithDefault('ext_maps_path', '', 'hyperbrowser')
EXT_LOG_PATH = config.getWithDefault('ext_log_path', '', 'hyperbrowser')
EXT_RESULTS_PATH = config.getWithDefault('ext_results_path', '', 'hyperbrowser')
EXT_TMP_PATH = config.getWithDefault('ext_tmp_path', '', 'hyperbrowser')

#
# Dependent constants
#

# COOKIE_PATH = URL_PREFIX if URL_PREFIX != '' else '/'

HB_SOURCE_CODE_BASE_DIR = GALAXY_BASE_DIR + '/lib/hb'

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

#
# To be removed
#

DEFAULT_GENOME = 'hg18'
