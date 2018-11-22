import quick.gsuite.GuiBasedTsFactory as factory

from gold.application.DataTypes import getSupportedFileSuffixesForPointsAndSegments
from gold.track.trackstructure import TsRandAlgorithmRegistry as TsRandAlgReg
from gold.track.trackstructure.TsRandAlgorithmRegistry import createDefaultTrackViewProvider
from proto.tools.GeneralGuiTool import BoxGroup


class RandAlgorithmMixin(object):
    SELECT_CHOICE_STR = '--- Select ---'
    NO = 'No'
    YES = 'Yes'

    @classmethod
    def getInputBoxNamesForRandAlgSelection(cls):
        """
        Should be added at the natural place in the list in the getUserBinInputBoxNames()
        method in the subclass. E.g.:

        @classmethod
        def getUserBinInputBoxNames(cls):
            return [('First choice', 'first') + \
                    ('Second choice', 'second')] + \
                    cls.getInputBoxNamesForRandAlgSelection()
        """
        return [('Type of randomization', 'randType'),
                ('Randomization algorithm', 'randAlg'),
                ('Avoid segments from a specified track', 'selectExcludedTrack'),
                ('Select track with segments to avoid', 'excludedTrack')]

    @classmethod
    def getInputBoxGroups(cls, choices=None):
        prevBoxGroups = None
        if hasattr(super(RandAlgorithmMixin, cls), 'getInputBoxGroups'):
            prevBoxGroups = super(RandAlgorithmMixin, cls).getInputBoxGroups(choices)

        if cls._showRandAlgorithmChoices(choices) and not choices.isBasic:
            if not prevBoxGroups:
                prevBoxGroups = []
            return prevBoxGroups + \
                   [BoxGroup(label='Randomization algorithm', first='randType', last='excludedTrack')]
        else:
            return prevBoxGroups

    @classmethod
    def _showRandAlgorithmChoices(cls, prevChoices):
        """
        Override this method in the tool if the randomization algorithm option boxes should not be
        shown for certain settings in choices.
        :param: The selected choices selected by the user before the first rand alg option box
        :return: True if the randomization algorithm option boxes should be shown, else False
        """
        return True

    @classmethod
    def getOptionsBoxRandType(cls, prevChoices):
        if cls._showRandAlgorithmChoices(prevChoices):
            if not prevChoices.isBasic:
                return [cls.SELECT_CHOICE_STR] + TsRandAlgReg.getCategories()

    @classmethod
    def getOptionsBoxRandAlg(cls, prevChoices):
        if cls._showRandAlgorithmChoices(prevChoices):
            if not prevChoices.isBasic:
                for definedRandType in TsRandAlgReg.getCategories():
                    if prevChoices.randType == definedRandType:
                        return [cls.SELECT_CHOICE_STR] + \
                               TsRandAlgReg.getAlgorithmList(definedRandType)

    @classmethod
    def getOptionsBoxSelectExcludedTrack(cls, prevChoices):
        if cls._showExcludedTrackSelection(prevChoices):
            return [RandAlgorithmMixin.NO, RandAlgorithmMixin.YES]

    @classmethod
    def _showExcludedTrackSelection(cls, choices):
        randType = choices.randType
        randAlg = choices.randAlg
        return \
            randType in TsRandAlgReg.getCategories() and \
            randAlg in TsRandAlgReg.getAlgorithmList(randType) and \
            TsRandAlgReg.EXCLUDED_TS_ARG in \
               TsRandAlgReg.getRequiredArgsForAlgorithm(randType, randAlg)

    @classmethod
    def getOptionsBoxExcludedTrack(cls, prevChoices):
        if prevChoices.selectExcludedTrack == RandAlgorithmMixin.YES:
            return cls.getHistorySelectionElement(*getSupportedFileSuffixesForPointsAndSegments())

    @classmethod
    def createTrackViewProvider(cls, choices, origTs, binSource, genome):
        if choices.isBasic:
            return createDefaultTrackViewProvider()

        reqArgs = TsRandAlgReg.getRequiredArgsForAlgorithm(choices.randType, choices.randAlg)
        kwArgs = TsRandAlgReg.getKwArgsForAlgorithm(choices.randType, choices.randAlg)

        args = []
        for arg in reqArgs:
            if arg == TsRandAlgReg.EXCLUDED_TS_ARG:
                if choices.selectExcludedTrack == RandAlgorithmMixin.YES:
                    excludedTs = factory.getSingleTrackTS(genome, choices.excludedTrack)
                else:
                    excludedTs = None
                args.append(excludedTs)
            if arg == TsRandAlgReg.BIN_SOURCE_ARG:
                args.append(binSource)

        tvProvider = TsRandAlgReg.createTrackViewProvider(
            choices.randType, choices.randAlg, *args, **kwArgs
        )

        tvProvider.setOrigTrackStructure(origTs)
        tvProvider.setBinSource(binSource)

        return tvProvider

    @classmethod
    def validateRandAlgorithmSelection(cls, choices):
        if cls._showExcludedTrackSelection(choices):
            for requiredParameter in (choices.randType, choices.randAlg):
                if requiredParameter in [None, '', '--- Select ---']:
                    return 'Please select all randomization parameters'

            if choices.selectExcludedTrack == RandAlgorithmMixin.YES:
                if not choices.excludedTrack:
                    return 'Please select a track with the regions to be excluded in the ' \
                           'randomization algorithm.'
