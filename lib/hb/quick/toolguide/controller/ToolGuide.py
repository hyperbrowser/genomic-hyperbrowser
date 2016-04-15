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
Created on Feb 16, 2015

@author: boris
'''
from collections import OrderedDict
from quick.toolguide.presenter.ToolGuideHtml import ToolGuideHtml
from quick.toolguide.ToolGuideConfig import *

class ToolGuideController():
    
    @staticmethod
    def getHtml(sourceToolId, inputTypeList, isBasicMode):
        guideDataGenerator = ToolGuideDataGenerator(sourceToolId, inputTypeList, isBasicMode)
        guideHtmlBuilder = ToolGuideHtml(guideDataGenerator.getGuideData())
        return guideHtmlBuilder.getContent()

class ToolGuideDataGenerator(object):
    '''
    Generates the guide data dictionary that is to be used by the ToolGuideHtml object.
    Note: not a python generator (maybe the name should be changed to avoid confusion).
    '''

    def __init__(self, sourceToolId, inputTypeList, isBasicMode):
        '''
        Constructor
        inputTypeList: contains a list of input types [GSuite, Track,...], for each a guide entry is to be created
        isBasicMode: flag, true if tools are used in basic mode, false if tools are used in advanced mode
        '''
        self._sourceToolId = sourceToolId
        self._inputTypeList = inputTypeList
        self._isBasicMode = isBasicMode
        self._guideDataDict = OrderedDict()
        self._generateGuideData()
        
    @property
    def isBasicMode(self):
        return self._isBasicMode
        


    def _generateGuideDataCommon(self, inputTypeMapper):
        for inputType in self._inputTypeList:
            assert inputType in inputTypeMapper, "%r is not a supported input type for Basic Mode. Supported types are %r." % (inputType, inputTypeMapper.keys())
            for toolId in inputTypeMapper[inputType]:
                toolUrl = TOOL_ID_TO_TOOL_URL_DICT.get(toolId)
                assert toolUrl, 'The URL for tool with id=%s is not defined in the configuration' % toolId
            #If display name is not configured just use the tool ID in camel case without underscores
                toolDisplayName = TOOL_ID_TO_TOOL_DISPLAY_NAME.get(toolId, toolId.replace('_', ' ').title())
                description = TOOL_ID_TO_TOOL_DESCRIPTION_DICT.get(toolId)
                assert description, 'The description for tool with id=%s is not defined in the configuration' % toolId
                imgUrl = TOOL_ID_TO_IMG_URL.get(toolId)
                helpPageUrl = TOOL_ID_TO_HELP_PAGE_URL.get(toolId)
                guideData = ToolGuideData(toolUrl, toolDisplayName, description, imgUrl=imgUrl, helpPageUrl=helpPageUrl)
                self._addGuideData(inputType, guideData)

    def _generateGuideDataForBasicMode(self, inputTypeMapper):
        self._generateGuideDataCommon(inputTypeMapper)
    
    def _generateGuideDataForAdvancedMode(self, inputTypeMapper):
        self._generateGuideDataCommon(inputTypeMapper)
    
    
    def _generateGuideData(self):
        if self.isBasicMode:
            self._generateGuideDataForBasicMode(TOOL_INPUT_TYPE_TO_TOOL_ID_BASIC_MODE)
        else:
            self._generateGuideDataForAdvancedMode(TOOL_INPUT_TYPE_TO_TOOL_ID_ADVANCED_MODE)
    

    def _getGuideDataForInputType(self, inputType):
        return self._guideDataDict.get(inputType, [])
    
    def _setGuideDataForInputType(self, inputType, validationHelpDataList):
        self._guideDataDict[inputType] = validationHelpDataList
    
    def _addGuideData(self, inputType, guideData):
        guideDataList = self._getGuideDataForInputType(inputType)
        guideDataList.append(guideData)
        self._setGuideDataForInputType(inputType, guideDataList)
        
    def getGuideData(self):
        return self._guideDataDict
    
class ToolGuideData(object):
    
    '''
    Model for the data displayed by the guide in each tool.
    '''
    
    def __init__(self, toolUrl, toolDisplayName, description, imgUrl=None, helpPageUrl = None ):
        self._toolUrl = toolUrl
        self._toolDisplayName = toolDisplayName
        self._description = description
        self._imgUrl = imgUrl
        self._helpPageUrl = helpPageUrl
        
    @property
    def toolUrl(self):
        return self._toolUrl
    
    @property
    def toolDisplayName(self):
        return self._toolDisplayName
    
    @property
    def description(self):
        return self._description
    
    @property
    def imgUrl(self):
        return self._imgUrl
    
    @property
    def helpPageUrl(self):
        return self._helpPageUrl

    