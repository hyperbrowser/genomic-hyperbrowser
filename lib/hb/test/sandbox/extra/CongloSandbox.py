from conglomerate.methods.interface import RestrictedThroughInclusion
from conglomerate.methods.stereogene.stereogene import StereoGene

import pkg_resources

from conglomerate.tools.method_compatibility import getCompatibleMethodObjects
from conglomerate.tools.runner import runAllMethodsInSequence
from proto.StaticFile import GalaxyRunSpecificFile
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.webtools.misc.CongloProtoTool import ALL_METHOD_CLASSES
#ALL_METHOD_CLASSES = [StereoGene]
#WORKING: selections = {'setGenomeName': [('setGenomeName', u'Human (hg19)')], 'setChromLenFileName': [('setChromLenFileName', '/software/galaxy/personal/geirksa/galaxy_dev/lib/tests/resources/chrom_lengths.tabular')], 'preserveClumping': [('preserveClumping', False), ('preserveClumping', True)]}
selections =  {'setGenomeName': [('setGenomeName', u'Human (hg19)')], 'setChromLenFileName': [('setChromLenFileName', '/software/galaxy/personal/geirksa/galaxy_dev/lib/tests/resources/chrom_lengths.tabular')]}
#OK: selections['setRestrictedAnalysisUniverse'] = [('setRestrictedAnalysisUniverse', RestrictedThroughInclusion(pkg_resources.resource_filename('tests.resources', 'H3K4me1_no_overlaps.bed')))]
#Not Working: selections['setRestrictedAnalysisUniverse'] = [('setRestrictedAnalysisUniverse', RestrictedThroughInclusion(pkg_resources.resource_filename('tests.resources', 'Ensembl_Genes_cropped.bed.gz')))]
selections['setRestrictedAnalysisUniverse'] = [('setRestrictedAnalysisUniverse', RestrictedThroughInclusion(pkg_resources.resource_filename('tests.resources', 'H3K4me3_no_overlaps.bed')))]

selections['preserveClumping'] = [('preserveClumping', False), ('preserveClumping', True)]

selections['setChromLenFileName'] = [('setChromLenFileName',pkg_resources.resource_filename('tests.resources', 'chrom_lengths.tabular') )]
galaxyFn = '/software/galaxy/personal/geirksa/galaxy_dev/database/files/000/dataset_635.dat'
#queryTrack = [pkg_resources.resource_filename('tests.resources', 'H3K4me1_no_overlaps_cropped.bed')]
queryTrack = [pkg_resources.resource_filename('tests.resources', 'Refseq_Genes_cropped.bed.gz')]

#refTracks = [pkg_resources.resource_filename('tests.resources', 'H3K4me1_with_overlaps.bed'), pkg_resources.resource_filename('tests.resources', 'H3K4me3_with_overlaps.bed')]
#refTracks = [pkg_resources.resource_filename('tests.resources', 'H3K4me3_no_overlaps.bed'), pkg_resources.resource_filename('tests.resources', 'H3K4me1_no_overlaps.bed')]
refTracks = [pkg_resources.resource_filename('tests.resources', 'H3K4me3_no_overlaps.bed.gz'), pkg_resources.resource_filename('tests.resources', 'H3K4me1_no_overlaps.bed.gz')]


workingMethodObjects = getCompatibleMethodObjects(selections.values(), queryTrack, refTracks, ALL_METHOD_CLASSES)
keptWmos = workingMethodObjects#[-1:]
print keptWmos
print [wmo._methodCls.__name__ for wmo in keptWmos]
for wmo in keptWmos:
    print '**', wmo._methodCls.__name__, '**'
    print wmo._methods[0]._params
    print '****'

runAllMethodsInSequence(keptWmos)

mocked = keptWmos

unionOfParamKeys = set([paramKey for wmo in mocked for paramKey in wmo.annotatedChoices.keys()])
print(unionOfParamKeys)
keysWithVariation = []
for key in unionOfParamKeys:
    numDifferentKeyValues = len(set([wmo.annotatedChoices.get(key) \
                        if not isinstance(wmo.annotatedChoices.get(key), list) \
                else tuple(wmo.annotatedChoices.get(key)) \
                for wmo in mocked]))
    print(key, numDifferentKeyValues)
    if numDifferentKeyValues > 1:
        keysWithVariation.append(key)
keysWithVariation.sort()

core = HtmlCore()
core.tableHeader(['Method name', 'Query and reference track'] + keysWithVariation + ['P-value', 'Test statistic', 'Detailed results'])
print('TEMPM13: ', len(mocked))
for i, wmo in enumerate(mocked):
    fullResultStaticFile = GalaxyRunSpecificFile(['details' + str(i) + '.html'], galaxyFn)
    #fullResultStaticFile.writeTextToFile(wmo.getFullResults())
    allPvals = wmo.getPValue()
    allTestStats = wmo.getTestStatistic()
    assert len(allPvals)>0, allPvals
    assert len(allPvals) == len(allTestStats)
    for trackCombination in allPvals.keys():
        pval = allPvals[trackCombination]
        ts = allTestStats[trackCombination]
        prettyTrackComb = '-'.join([track.split('/')[-1] for track in trackCombination])
        print 'TEMP14', [wmo._methodCls.__name__, prettyTrackComb] + [wmo.annotatedChoices.get(key) for key in keysWithVariation] + [str(pval), str(ts), fullResultStaticFile.getLink('Full results')]
        core.tableLine(
            [wmo._methodCls.__name__, prettyTrackComb] + [wmo.annotatedChoices.get(key) for key in keysWithVariation] + [str(pval), str(ts), fullResultStaticFile.getLink('Full results')])
core.tableFooter()
print core
