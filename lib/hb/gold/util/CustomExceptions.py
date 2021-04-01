class Warning(Exception):
    pass

class InvalidFormatWarning(Warning):
    pass

class InvalidFormatError(Exception):
    pass

class IncompatibleTracksError(Exception):
    pass

class AbstractClassError(Exception):
    pass

class SplittableStatNotAvailableError(Exception):
    pass

class NotSupportedError(Exception):
    pass

class ShouldNotOccurError(Exception):
    pass

class NotValidGESequence(Exception):
    pass

class EmptyGESourceError(Exception):
    pass

class InvalidRunSpecException(Exception):
    pass

class CentromerError(Exception):
    pass

class TooLargeBinError(Exception):
    pass

class TooSmallBinError(Exception):
    pass

class IncompatibleAssumptionsError(Exception):
    pass

class NoneResultError(Exception):
    pass
    
class FileLockError(Exception):
    pass

class NoMoreUniqueValsError(Exception):
    pass

class ArgumentValueError(Exception):
    pass

class MissingEntryError(Exception):
    pass

class ExecuteError(Exception):
    pass

class SilentError(Exception):
    pass

class IdenticalTrackNamesError(Exception):
    pass
    
class NotIteratedYetError(Exception):
    pass
    
class OutsideBoundingRegionError(Exception):
    pass
    
class BoundingRegionsNotAvailableError(Exception):
    pass

class ContextException(Exception):
    def __str__(self):
        import traceback

        # From https://chezsoi.org/lucas/blog/displaying-chained-exceptions-stacktraces-in-python-2.html
        out = Exception.__str__(self)
        if hasattr(self, '__cause__') and self.__cause__ and hasattr(self.__cause__, '__traceback__') and self.__cause__.__traceback__:
            out += '\n\nThe above exception was caused by the following exception:\n\n'
            out += ''.join(traceback.format_tb(self.__cause__.__traceback__) + ['{}: {}'.format(self.__cause__.__class__.__name__, self.__cause__)])
        return out

class PreprocessError(ContextException):
    pass

class PreprocessWarning(ContextException):
    pass