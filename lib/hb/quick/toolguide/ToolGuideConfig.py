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
'''
Created on Feb 17, 2015

@author: boris

Configuration for the Tool guide.

'''

from quick.util.CommonFunctions import createGalaxyToolURL, createToolURL
from config.Config import STATIC_REL_PATH

GSUITE_INPUT = 'gsuite'
TRACK_INPUT = 'track'
IMG_URL = STATIC_REL_PATH + '/images/tool_guide_images/'
TOOL_GUIDE_HELP_HEADER_TEXT = 'Tool guide'
TOOL_GUIDE_HELP_HEADER_TEXT_TEXT = 'You need to select the input for the analysis. The user guide would help you finding the appropriate tools to run your analysis. The following steps will guide you to upload/generate the input dataset which is needed for the analysis.'

TOOL_INPUT_TYPE_TO_TOOL_ID_BASIC_MODE = dict([(TRACK_INPUT,["upload1"]), (GSUITE_INPUT, ["hb_track_global_search_tool"])])
TOOL_INPUT_TYPE_TO_TOOL_ID_ADVANCED_MODE = dict([(TRACK_INPUT,["upload1"]), (GSUITE_INPUT, ["hb_track_global_search_tool",
                                                                                            "hb_track_source_test_tool",
                                                                                            "hb_create_g_suite_file_from_history_elements_tool",
                                                                                            "hb_extract_subtracks_tool"
                                                                                            ])])

TOOL_ID_TO_TOOL_URL_DICT = dict([
                                ("upload1", createGalaxyToolURL("upload1")),
                                ("hb_track_global_search_tool", createToolURL("hb_track_global_search_tool")),
                                ("hb_track_source_test_tool", createToolURL("hb_track_source_test_tool")),
                                ("hb_create_g_suite_file_from_history_elements_tool", createToolURL("hb_create_g_suite_file_from_history_elements_tool")),
                                ("hb_extract_subtracks_tool", createToolURL("hb_extract_subtracks_tool")),
                                ])

TOOL_ID_TO_TOOL_DESCRIPTION_DICT = dict([
                                        ('upload1', '''
                                        Upload a genomic track to the history pane from disc.
                                        '''),
                                         ('hb_track_global_search_tool', '''
                                         Acquire a dataset collection (GSuite) by browsing a catalog of chromatine tracks.
                                         '''),
                                         ('hb_track_source_test_tool', '''
                                         Acquire a dataset collection (GSuite) from a public database (e.g. ENCODE, CGA, etc.).
                                         '''),
                                         ('hb_create_g_suite_file_from_history_elements_tool', '''
                                         Combine existing datasets from history into a collection (GSuite).
                                         '''),
                                         ('hb_extract_subtracks_tool', '''
                                         Biuld a dataset collection (GSuite) from datasets in the HyperBrowser repository.
                                         ''')
                                        ])

TOOL_ID_TO_TOOL_DISPLAY_NAME  = dict([
                                      ('upload1', 'Upload file'),
                                      ('hb_track_global_search_tool', 'Import collection of tracks from public repositories'),
                                      ('hb_track_source_test_tool', 'Compile GSuite from external database'),
                                      ('hb_create_g_suite_file_from_history_elements_tool', 'Compile GSuite from history elements'),
                                      ('hb_extract_subtracks_tool', 'Compile GSuite from HyperBrowser repository')
                                      ])

TOOL_INPUT_TYPE_TO_TOOL_GUIDE_HELP_HEADER_DICT = dict([
                                (TRACK_INPUT, 'The following list of tools provide the missing input, of type Genomic Track. Follow the link to the tool which fits your requirements.'),
                                (GSUITE_INPUT, 'The following list of tools provide the missing input, of type GSuite. Follow the link to the tool which fits your requirements.')
                                ])


TOOL_ID_TO_IMG_URL = dict([('upload1', IMG_URL + 'icon_genomeTrack.png'),
                           ('hb_track_global_search_tool', IMG_URL + 'icon_gSuite.png'),
                           ('hb_track_source_test_tool', IMG_URL + 'icon_gSuite.png'),
                           ('hb_create_g_suite_file_from_history_elements_tool', IMG_URL + 'icon_gSuite.png'),
                           ('hb_extract_subtracks_tool', IMG_URL + 'icon_gSuite.png'),
                           ])

#('hb_track_global_search_tool', URL_PREFIX + '/u/hb-superuser/p/browse-catalog-of-chromatin-tracks')
TOOL_ID_TO_HELP_PAGE_URL = dict()
