from conglomerate.methods.interface import RestrictedThroughInclusion
from conglomerate.methods.stereogene.stereogene import StereoGene

import pkg_resources

from conglomerate.tools.method_compatibility import getCompatibleMethodObjects
from conglomerate.tools.runner import runAllMethodsInSequence
from conglomerate.tools.constants import VERBOSE_RUNNING
from proto.StaticFile import GalaxyRunSpecificFile
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.webtools.misc.CongloProtoTool import ALL_METHOD_CLASSES
#ALL_METHOD_CLASSES = [StereoGene]
#WORKING: selections = {'setGenomeName': [('setGenomeName', u'Human (hg19)')], 'setChromLenFileName': [('setChromLenFileName', '/software/galaxy/personal/geirksa/galaxy_dev/lib/tests/resources/chrom_lengths.tabular')], 'preserveClumping': [('preserveClumping', False), ('preserveClumping', True)]}
selections =  {'setGenomeName': [('setGenomeName', u'Human (hg19)')], 'setChromLenFileName': [('setChromLenFileName', '/software/galaxy/personal/geirksa/galaxy_dev/lib/tests/resources/chrom_lengths.tabular')]}
#OK: selections['setRestrictedAnalysisUniverse'] = [('setRestrictedAnalysisUniverse', RestrictedThroughInclusion(pkg_resources.resource_filename('tests.resources', 'H3K4me1_no_overlaps.bed')))]
#Not Working: selections['setRestrictedAnalysisUniverse'] = [('setRestrictedAnalysisUniverse', RestrictedThroughInclusion(pkg_resources.resource_filename('tests.resources', 'Ensembl_Genes_cropped.bed.gz')))]
selections['setRestrictedAnalysisUniverse'] = [('setRestrictedAnalysisUniverse',None), ('setRestrictedAnalysisUniverse', RestrictedThroughInclusion(pkg_resources.resource_filename('tests.resources', 'H3K4me3_no_overlaps.bed')))]

#selections['preserveClumping'] = [('preserveClumping', False), ('preserveClumping', True)]

selections['setChromLenFileName'] = [('setChromLenFileName',pkg_resources.resource_filename('tests.resources', 'chrom_lengths.tabular') )]
galaxyFn = '/software/galaxy/personal/geirksa/galaxy_dev/database/files/000/dataset_635.dat'
queryTrack = [pkg_resources.resource_filename('tests.resources', 'H3K4me1_no_overlaps_cropped.bed')]
#queryTrack = [pkg_resources.resource_filename('tests.resources', 'Refseq_Genes_cropped.bed.gz')]

#refTracks = [pkg_resources.resource_filename('tests.resources', 'H3K4me1_with_overlaps.bed'), pkg_resources.resource_filename('tests.resources', 'H3K4me3_with_overlaps.bed')]
refTracks = [pkg_resources.resource_filename('tests.resources', 'H3K4me3_no_overlaps_cropped.bed'), pkg_resources.resource_filename('tests.resources', 'H3K4me1_no_overlaps.bed')]
#refTracks = [pkg_resources.resource_filename('tests.resources', 'H3K4me3_no_overlaps.bed.gz'), pkg_resources.resource_filename('tests.resources', 'H3K4me1_no_overlaps.bed.gz')]


wmos = getCompatibleMethodObjects(selections.values(), queryTrack, refTracks, ALL_METHOD_CLASSES)
keptWmos = wmos#[-1:]

if VERBOSE_RUNNING:
    print 'Working methods:'
    print [wmo._methodCls.__name__ for wmo in keptWmos]
    for wmo in keptWmos:
        print '**', wmo._methodCls.__name__, '**'
        print wmo._methods[0]._params
        print '****'


runAllMethodsInSequence(keptWmos)

unionOfParamKeys = set([paramKey for wmo in keptWmos for paramKey in wmo.annotatedChoices.keys()])
# print(unionOfParamKeys)
keysWithVariation = []
for key in unionOfParamKeys:
    numDifferentKeyValues = len(set([wmo.annotatedChoices.get(key) \
                                         if not isinstance(wmo.annotatedChoices.get(key), list) \
                                         else tuple(wmo.annotatedChoices.get(key)) \
                                     for wmo in keptWmos]))
    if numDifferentKeyValues > 1:
        keysWithVariation.append(key)
keysWithVariation.sort()

core = HtmlCore()
core.tableHeader(
    ['Method name', 'Query track', 'reference track'] + keysWithVariation + ['P-value', 'Test statistic',
                                                                             'Detailed results'])
for i, wmo in enumerate(keptWmos):
    if not wmo.ranSuccessfully():
        continue

    allPvals = wmo.getPValue()
    allTestStats = wmo.getTestStatistic()
    # print 'TEMP18: ', wmo._methodCls.__name__, allTestStats
    allFullResults = wmo.getFullResults()
    # assert len(allPvals)>0, allPvals
    assert len(allPvals) == len(allTestStats), (allPvals, allTestStats)
    for j, trackCombination in enumerate(allPvals.keys()):
        fullResultStaticFile = GalaxyRunSpecificFile(['details' + str(i) + '_' + str(j) + '.html'], galaxyFn)
        fullResult = allFullResults[trackCombination]
        fullResultStaticFile.writeTextToFile(fullResult)
        pval = allPvals[trackCombination]
        ts = allTestStats[trackCombination]
        # prettyTrackComb = '-'.join([track.split('/')[-1] for track in trackCombination])
        prettyTracks = [track.split('/')[-1] for track in trackCombination]
        # print 'TEMP14', [wmo._methodCls.__name__, prettyTrackComb] + [wmo.annotatedChoices.get(key) for key in keysWithVariation] + [str(pval), str(ts), fullResultStaticFile.getLink('Full results')]
        core.tableLine(
            [wmo._methodCls.__name__] + prettyTracks + [wmo.annotatedChoices.get(key) for key in
                                                        keysWithVariation] + [str(pval), str(ts),
                                                                              fullResultStaticFile.getLink(
                                                                                  'Full results')])
core.tableFooter()

# not wmo.ranSuccessfully()
if not all(wmo.ranSuccessfully() for wmo in keptWmos):
    core.tableHeader(['Method name', 'Tool error'])
    for i, wmo in enumerate(keptWmos):
        if wmo.ranSuccessfully():
            continue
        errorStaticFile = GalaxyRunSpecificFile(['errors' + str(i) + '.html'], galaxyFn)
        errorStaticFile.writeTextToFile(wmo.getErrorDetails())
        # print 'TEMP18: ', wmo.getErrorDetails()
        core.tableLine([wmo._methodCls.__name__, errorStaticFile.getLink('Tool error output')])
    core.tableFooter()

print core