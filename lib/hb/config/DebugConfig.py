class DebugModes(object):
    NO_DEBUG = 'No debugging'
    PROFILING = 'Profiling with call graphs'
    UNCHANGED_LOGIC_VERBOSE = 'Debug without changing logic (verbose)'
    UNCHANGED_LOGIC_TRACE_CREATE_VERBOSE = 'Debug without changing logic (tracing statistic creation, verbose)'
    UNCHANGED_LOGIC_TRACE_COMPUTE_VERBOSE = 'Debug without changing logic (tracing statistic compute, verbose)'
    UNCHANGED_LOGIC_FULL_TRACE_VERBOSE = 'Debug without changing logic (tracing statistic creation and compute, verbose)'
    RAISE_HIDDEN_EXCEPTIONS_NO_VERBOSE = 'Debug by raising hidden exceptions'
    RAISE_HIDDEN_EXCEPTIONS_FULL_TRACE_VERBOSE = 'Debug by raising hidden exceptions (tracing statistic creation and compute, verbose)'
    RAISE_HIDDEN_EXCEPTIONS_INCLUDING_NONE_WITH_VERBOSE = 'Debug by raising hidden exceptions incl. stats returning None (only in special cases, verbose)'
    RAISE_HIDDEN_EXCEPTIONS_INCLUDING_NONE_FULL_TRACE_WITH_VERBOSE = 'Debug by raising hidden exceptions incl. stats returning None (special cases, full trace, verbose)'


class DebugConfigMeta(type):
    def __init__(cls, name, bases, d):
        type.__init__(cls, name, bases, d)
        cls._init()

    def _init(cls):
        pass

    def __str__(cls):
        settings = ''
        for constant in ['VERBOSE',
                         'PASS_ON_VALIDSTAT_EXCEPTIONS',
                         'PASS_ON_COMPUTE_EXCEPTIONS',
                         'PASS_ON_BATCH_EXCEPTIONS',
                         'PASS_ON_FIGURE_EXCEPTIONS',
                         'PASS_ON_NONERESULT_EXCEPTIONS',
                         'USE_SLOW_DEFENSIVE_ASSERTS',
                         'USE_PROFILING',
                         'USE_CALLGRAPH',
                         'TRACE_STAT',
                         'TRACE_PRINT_REGIONS',
                         'TRACE_PRINT_TRACK_NAMES']:
            settings += '%s: %s\n' % (constant, getattr(cls, constant))
        return settings


class DebugConfig(object):
    __metaclass__ = DebugConfigMeta

    @classmethod
    def _init(cls):
        cls.VERBOSE = False
        cls.PASS_ON_VALIDSTAT_EXCEPTIONS = False
        cls.PASS_ON_COMPUTE_EXCEPTIONS = False
        cls.PASS_ON_BATCH_EXCEPTIONS = False
        cls.PASS_ON_FIGURE_EXCEPTIONS = False
        cls.PASS_ON_NONERESULT_EXCEPTIONS = False
        cls.USE_SLOW_DEFENSIVE_ASSERTS = False
        cls.USE_PROFILING = False
        cls.USE_CALLGRAPH = False
        cls.TRACE_STAT = {'computeStep': False,
                          'compute': False,
                          '_compute': False,
                          '_combineResults': False,
                          '_createChildren': False,
                          '__init__': False,
                          '_afterComputeCleanup' : False,
                          '_setNotMemoizable' : False,
                          '_updateInMemoDict' : False}
        cls.TRACE_PRINT_REGIONS = False
        cls.TRACE_PRINT_TRACK_NAMES = False

    @classmethod
    def changeMode(cls, debugMode):
        cls._init()

        if debugMode != DebugModes.NO_DEBUG:
            cls.USE_SLOW_DEFENSIVE_ASSERTS = True

        if debugMode not in [DebugModes.NO_DEBUG,
                             DebugModes.PROFILING,
                             DebugModes.RAISE_HIDDEN_EXCEPTIONS_NO_VERBOSE]:
            cls.VERBOSE = True

        if debugMode == DebugModes.PROFILING:
            cls.USE_PROFILING = True
            cls.USE_CALLGRAPH = True

        if debugMode in [DebugModes.RAISE_HIDDEN_EXCEPTIONS_NO_VERBOSE,
                         DebugModes.RAISE_HIDDEN_EXCEPTIONS_FULL_TRACE_VERBOSE,
                         DebugModes.RAISE_HIDDEN_EXCEPTIONS_INCLUDING_NONE_WITH_VERBOSE,
                         DebugModes.RAISE_HIDDEN_EXCEPTIONS_INCLUDING_NONE_FULL_TRACE_WITH_VERBOSE]:
            cls.PASS_ON_VALIDSTAT_EXCEPTIONS = True
            cls.PASS_ON_COMPUTE_EXCEPTIONS = True
            cls.PASS_ON_BATCH_EXCEPTIONS = True
            cls.PASS_ON_FIGURE_EXCEPTIONS = True

        if debugMode in [DebugModes.RAISE_HIDDEN_EXCEPTIONS_INCLUDING_NONE_WITH_VERBOSE,
                         DebugModes.RAISE_HIDDEN_EXCEPTIONS_INCLUDING_NONE_FULL_TRACE_WITH_VERBOSE]:
            cls.PASS_ON_NONERESULT_EXCEPTIONS = True

        if debugMode in [DebugModes.UNCHANGED_LOGIC_TRACE_CREATE_VERBOSE,
                         DebugModes.UNCHANGED_LOGIC_FULL_TRACE_VERBOSE,
                         DebugModes.RAISE_HIDDEN_EXCEPTIONS_FULL_TRACE_VERBOSE,
                         DebugModes.RAISE_HIDDEN_EXCEPTIONS_INCLUDING_NONE_FULL_TRACE_WITH_VERBOSE]:
            cls.TRACE_STAT['_createChildren'] = True
            cls.TRACE_STAT['__init__'] = True

        if debugMode in [DebugModes.UNCHANGED_LOGIC_TRACE_COMPUTE_VERBOSE,
                         DebugModes.UNCHANGED_LOGIC_FULL_TRACE_VERBOSE,
                         DebugModes.RAISE_HIDDEN_EXCEPTIONS_FULL_TRACE_VERBOSE,
                         DebugModes.RAISE_HIDDEN_EXCEPTIONS_INCLUDING_NONE_FULL_TRACE_WITH_VERBOSE]:
            cls.TRACE_STAT['computeStep'] = True
            cls.TRACE_STAT['compute'] = True
            cls.TRACE_STAT['_compute'] = True
            cls.TRACE_STAT['_combineResults'] = True
            cls.TRACE_STAT['_afterComputeCleanup'] = True

        if debugMode in [DebugModes.UNCHANGED_LOGIC_TRACE_CREATE_VERBOSE,
                         DebugModes.UNCHANGED_LOGIC_TRACE_COMPUTE_VERBOSE,
                         DebugModes.UNCHANGED_LOGIC_FULL_TRACE_VERBOSE,
                         DebugModes.RAISE_HIDDEN_EXCEPTIONS_FULL_TRACE_VERBOSE,
                         DebugModes.RAISE_HIDDEN_EXCEPTIONS_INCLUDING_NONE_FULL_TRACE_WITH_VERBOSE]:
            cls.TRACE_STAT['_setNotMemoizable'] = True
            cls.TRACE_STAT['_updateInMemoDict'] = True
            cls.TRACE_PRINT_REGIONS = True
            cls.TRACE_PRINT_TRACK_NAMES = True
