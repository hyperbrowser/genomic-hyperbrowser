from collections import OrderedDict

import numpy

from proto.CommonFunctions import ensurePathExists
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class OperationOnTrackTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Operations on track"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select genome or track', 'trackOrGenome'),
                ('Select track', 'track1'),
                ('Select genome', 'genome'),
                ('Select track2', 'track2'),
                ('Type of operation', 'oper')]

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None

    @classmethod
    def getOptionsBoxTrackOrGenome(cls):
        return ['track', 'genome']

    @classmethod
    def getOptionsBoxTrack1(cls, prevChoices):
        if prevChoices.trackOrGenome == 'track':
            return GeneralGuiTool.getHistorySelectionElement('bed')

    @classmethod
    def getOptionsBoxGenome(cls, prevChoices):
        if prevChoices.trackOrGenome == 'genome':
            return '__genome__'

    @classmethod
    def getOptionsBoxTrack2(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('bed')

    @classmethod
    def getOptionsBoxOper(cls, prevChoices):
        return ['difference', 'intersection']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        if choices.trackOrGenome == 'genome':
            genome = choices.genome
            data = GenomeInfo.getStdChrLengthDict(genome)

            genomeFile = GalaxyRunSpecificFile(['genome.bed'], galaxyFn)
            ensurePathExists(genomeFile.getDiskPath())
            outputFile = open(genomeFile.getDiskPath(), 'w')
            for chr1, d1 in data.iteritems():
                outputFile.write('\t'.join([str(chr1), str(0), str(d1)]) + '\n')
            outputFile.close()
            track1 = genomeFile.getDiskPath()

        if choices.trackOrGenome == 'track':
            track1 = choices.track1
            track1 = ExternalTrackManager.extractFnFromGalaxyTN(track1.split(':'))

        track2 = choices.track2
        track2 = ExternalTrackManager.extractFnFromGalaxyTN(track2.split(':'))

        import os, subprocess

        if choices.oper == "difference":
            command = """ bedtools subtract -a """ + str(track1) + """ -b  """ + str(track2)
        else:
            pass

        if choices.oper == "intersection":
            command = """ bedtools intersect -a """ + str(track1) + """ -b  """ + str(track2)
        else:
            pass

        process = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        results, errors = process.communicate()

        outputFile = open(galaxyFn,'w')
        outputFile.write(results)
        outputFile.close()


    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None
    #
    # @classmethod
    # def isPublic(cls):
    #     return False
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     return []
    #
    # @classmethod
    # def getToolDescription(cls):
    #     return ''
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     return False
    #
    @classmethod
    def getOutputFormat(cls, choices):
        return 'bed'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
