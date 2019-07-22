
import abc
import glob
import importlib
from collections import OrderedDict
from collections import namedtuple
from os.path import dirname, basename, isfile

from gold.track.TrackView import TrackView
from gold.track.TrackFormat import TrackFormatReq
from quick.track_operations.TrackContents import TrackContents


class InvalidArgumentError(Exception):
    pass

class Operator(object):
    __metaclass__ = abc.ABCMeta

    _operationHelp = None
    _trackHelpList = []
    _numTracks = 0
    _resultIsTrack = False
    _nestedOperator = False
    _result = None

    def __init__(self, *args, **kwargs):
        self._tracks = args

        # Load the default kwargs and set any given ones.
        self._kwargs = self._parseKwargs(**kwargs)

        # Generate the resultTrackFormat
        self._setResultTrackFormat()

        # Run the preCalculate (if any)
        # preCalc updates the self._tracks
        self._preCalculation()

        self._checkArgs()

    def _checkArgs(self):

        if len(self._tracks) != self._numTracks:
            raise InvalidArgumentError("Operation requires {} tracks, but {} "
                                       "tracks were given"
                                       .format(self.numTracks, len(self._tracks)))

        for i, track in enumerate(self._tracks):
            if isinstance(track, Operator):
                # Track is another operator
                self._nestedOperator = True
                trackReq = self.trackRequirements[i]
                trackFormat = track.trackFormat

                if not trackReq.isCompatibleWith(trackFormat):
                    raise InvalidArgumentError(
                        ("Operation requires track number {} to follow "
                         "the following requirements: {} "
                         "The format of the supplied track is: {}"
                         .format(i+1, trackReq,trackFormat)))
            else:
                if not isinstance(track, TrackContents):
                    raise InvalidArgumentError(
                        "Operation requires TrackContent objects as arguments")

                trackReq = self.trackRequirements[i]
                trackFormat = track.firstTrackView().trackFormat

                if not trackReq.isCompatibleWith(trackFormat):
                    raise InvalidArgumentError(
                        ("Operation requires track number {} to follow "
                         "the following requirements: {} "
                         "The format of the supplied track is: {}"
                         .format(i+1, trackReq, trackFormat)))

        regionsFirstArg = self.getResultRegion()
        genomeFirstArg = self.getResultGenome()
        self._resultGenome = genomeFirstArg
        for i, track in enumerate(self._tracks[1:]):
            if isinstance(track, Operator):
                if track.getResultRegion() != regionsFirstArg:
                    raise InvalidArgumentError(
                        "Region lists must be the same for all tracks")
                if track.getResultGenome() != genomeFirstArg:
                    raise InvalidArgumentError(
                        "All tracks must have the same genome")
            else:
                if track.regions != regionsFirstArg:
                    raise InvalidArgumentError(
                        "Region lists must be the same for all tracks")
                if track.genome != genomeFirstArg:
                    raise InvalidArgumentError(
                        "All tracks must have the same genome")

    # Kwargs handling methods
    def __getattr__(self, name):
        """
        Dynamically return the given options or default value.
        :param name: Variable name
        :return: The value from the _kwargs dict with name as key
        :raises AttributeError: If name is not a key in _kwargs
        """
        if name is '_options' or name is '_kwargs':
            # The operation is missing the _options and _kwargs variables
            # These need to be set in the __init__ method.
            raise AttributeError("The operations is missing {}".format(name))
        elif name.startswith('_'):
            try:
                # If in kwargs, return it
                return self._kwargs[name[1:]]
            except KeyError:
                raise AttributeError("{} not found in kwarg".format(name))
        else:
            if self._debug:
                raise AttributeError("{} not defined!".format(name))
            else:
                raise AttributeError

    def _parseKwargs(self, **kwargs):
        """
        Get the operations default kwargs. Parse the kwargs combine then into
        one dict that define all off the operations options.

        Kwargs not define are ignored
        :return:
        """
        # Extract the default values

        kw = {k: v.defaultValue for k, v in
              self.__class__.getKwArgumentInfoDict(

        ).iteritems()}

        for k, v in kwargs.iteritems():
            if k in kw:
                kw[k] = v
            else:
                # Maybe remove this at some point. But is is rather nice
                # when debuging
                raise TypeError("{} not defined in the "
                                "KwArgumentInfoDict!".format(k))

        return kw

    @classmethod
    def getKwArgumentInfoDict(cls):
        """
        Return the operations keyword arguments.
        :return:
        """
        kwArgDict = cls._getKwArgumentInfoDict()
        kwArgDict.pop('debug')

        return cls._getKwArgumentInfoDict()

    @classmethod
    def _getKwArgumentInfoDict(cls):
        """
        Overload this in each operation
        :return:
        """
        pass

    @classmethod
    def getInfoDict(cls):
        """
        Return a dict of info about the operation.
        Useful when creating application that use the operations dynamically
        :return: Dict containing basic information about the operation
        """

        return {'name': cls.__name__,
                'operationHelp': cls._operationHelp,
                'numTracks': cls._numTracks,
                'trackHelp': cls._trackHelpList}

    def _setResultTrackFormat(self):
        """
        Overload this method if one wants to define the TrackFormat of the
        result track.
        :return:
        """
        # Set to None if not overloaded
        self._resultTrackFormat = None

    # Calculation methods
    def __call__(self, *args, **kwargs):
        """
        Legacy, remove at a later point.
        :param args:
        :param kwargs:
        :return:
        """
        return self.calculate()

    def calculate(self):
        """
        Run operation. Iterates through all regions in a track.

        :return: The result of the operation as a track or as a ordered dict
        of the result per region.
        """

        if self._result is not None:
            # If we have a result we return it
            return self._result

        self._result = OrderedDict()

        # Compute any nested operations.
        computedTracks = []
        for track in self._tracks:
            if isinstance(track, Operator):
                print("**********")
                print("Computing nesting")
                print("**********")
                computedTracks.append(track.calculate())
            else:
                computedTracks.append(track)

        result = OrderedDict()
        for region in self.getResultRegion():

            trackViewPerArg = [track.getTrackView(region) for track in
                               computedTracks]
            tv = self._calculate(region, *trackViewPerArg)

            if tv is not None:
                result[region] = tv

        if self.resultIsTrack:
            # Result is a track. Create new TrackContent
            self._result = TrackContents(self._resultGenome, result)
        else:
            # The result is not a track.
            self._result = result

        self._postCalculation()
        return self._result

    def _preCalculation(self):
        pass

    def _postCalculation(self):
        pass

    # **** Abstract methods ****
    @abc.abstractmethod
    def _calculate(self, *args):
        """
        Main run method. This will be called one time per region.
        :param args: Arguments of operation (track views, region, ect..)
        :return: Result of operation
        """
        pass

    def _updateTrackFormatRequirements(self):
        """
        Remove?

        Called when we have updated some of the properties that the track
        requirement depend on.

        :return:
        """
        if self._trackFormatReqChangeable:
            # Only update requirements if the operation allows it
            self._trackRequirements = \
                [TrackFormatReq(dense=r.isDense(),
                                allowOverlaps=self._allowOverlap) for r in
                 self._trackRequirements]

    def _updateResultTrackFormatRequirements(self):
        """
        Remove ?
        Equal to _updateTrackFormat but now updating the result track
        requirments (if any)
        :return: None
        """
        if self._resultTrackFormatReqChangeable:
            # Only update requirements if the operation allows it
            if self._resultIsTrack is not None:
                # Result is a track.
                dense = self._resultTrackRequirements.isDense()
                self._resultTrackRequirements = \
                    TrackFormatReq(dense=dense, allowOverlaps=self._allowOverlap)

    def printResult(self):
        """
        Used by GTools.
        Used if the operation returns something other the a new track.
        GTools uses this method to print the result.
        Overload if one wants more complex printing
        :return:
        """

        if isinstance(self._result, TrackContents):
            pass
        else:
            if self._result is not None:
                print(self._out)
            else:
                print("ERROR! Calculation not run!")

    # **** Common properties ***
    # Properties common to all operation
    # Setters are only defined for properties that can be changed without
    # braking the operation.

    @property
    def allowOverlaps(self):
        """
        Define if we allow overlapping segments in the input tracks.
        :return: None
        """
        return self._allowOverlap

    @allowOverlaps.setter
    def allowOverlaps(self, allowOverlap):
        assert isinstance(allowOverlap, bool)
        self._allowOverlap = allowOverlap
        self._updateTrackFormat()

    @property
    def numTracks(self):
        """
        The number of tracks a operation uses as input.
        :return: None
        """
        return self._numTracks

    @property
    def trackRequirements(self):
        """
        The TrackFormatReq of the input tracks
        :return: None
        """
        return self._trackRequirements

    # Properties about the result of the operation
    @property
    def resultAllowOverlaps(self):
        """
        Define if we allow overlapping segments in the result track (if any).
        :return: None
        """
        return self._resultAllowOverlaps

    @resultAllowOverlaps.setter
    def resultAllowOverlaps(self, allowOverlap):
        assert isinstance(allowOverlap, bool)
        # TODO, if result allow overlap and not input
        self._resultAllowOverlaps = allowOverlap
        self._updateResultTrackFormat()

    @property
    def resultIsTrack(self):
        """
        Define if result is a track or not.
        :return: None
        """
        return self._resultIsTrack

    @property
    def resultTrackFormat(self):
        """
        The TrackFormatReq of the result track (if any).
        :return: None
        """
        return self._resultTrackFormat

    @property
    def trackFormat(self):
        """
        Gives the resultTrackFormat
        Called by a higher operation when nested.
        :return:
        """
        return self._resultTrackFormat

    # **** Misc methods ****
    def isNestable(self):
        """
        Check if the operation can be "nested" into another operations.
        Any operation that returns a track can be nested. An operation
        that returns a number can not.

        Made this into a method so it can be expanded later without
        changing the call code.
        :return: True if nestable, false else
        """
        return self.resultIsTrack

    def getResultRegion(self):
        """
        Returns the regions
        :return:
        """
        # TODO: Se paa denne!
        # Use extended genome
        if isinstance(self._tracks[0], Operator):
            return self._tracks[0].getResultRegion()
        else:
            return self._tracks[0].regions

    def getResultGenome(self):
        """
        Returns the genome of the results.
        :return:
        """
        if self.isNestable():
            if isinstance(self._tracks[0], Operator):
                return self._tracks[0].getResultGenome()
            else:
                return self._tracks[0].genome
        else:
            return None

    def _createTrackView(self, region, startList=None, endList=None,
                         valList=None, strandList=None, idList=None,
                         edgesList=None, weightsList=None,
                         extraLists=OrderedDict()):
        """
        TODO move this to a util file?
        Help function used to create a track view.
        :param region:
        :param startList:
        :param endList:
        :param valList:
        :param strandList:
        :param idList:
        :param edgesList:
        :param weightsList:
        :param extraLists:
        :return:
        """
        return TrackView(region, startList, endList, valList, strandList,
                         idList, edgesList, weightsList,
                         borderHandling='crop',
                         allowOverlaps=self.resultAllowOverlaps,
                         extraLists=extraLists)


# Named tuple uses to define the keyword arguments of a operation
KwArgumentInfo = namedtuple('KwArgumentInfo', ['key', 'shortkey', 'help',
                                               'contentType', 'defaultValue'])


def getOperation():
    """
    Returns all defined operations. This method is used to create a dynamic
    cli.

    Works in the normal pythonic way. Will ignore any files starting with a
    underscore.

    TODO: Check that we only add valid operations.

    :return: A list of all operations in the operations folder.
    """

    name = __name__.split('.')[-1]
    files = glob.glob(dirname(__file__)+"/*.py")
    operations = [basename(file)[:-3] for file in files if isfile(file) and
                  not basename(file)[:-3].startswith('_') and basename(
                  file)[:-3] != name]

    module = '.'.join(__name__.split('.')[:-1])

    return module, operations


def importOperations():
    """
    Import all defined operations
    :return: None
    """
    module, operations = getOperation()

    importedOperations = {}

    for operation in operations:
        m = "{0}.{1}".format(module, operation)

        mod = importlib.import_module(m)
        operationClass = getattr(mod, operation)

        # TODO check if class

        importedOperations[operation] = operationClass

    return importedOperations


def getKwArgOperationDict(operations):
    opDict = {}
    kwDict = {}
    for op, opCls in operations.items():
        opDict[op] = opCls.getKwArgumentInfoDict().keys()

    for op, kwArgs in opDict.items():
        for kw in kwArgs:
            kwDict.setdefault(kw, []).append(op)

    kwDict.pop('debug')

    return kwDict



