from collections import OrderedDict


# Adapted from https://stackoverflow.com/a/4127426, which is available for use through the
# CC BY-SA 4.0 licence (https://creativecommons.org/licenses/by-sa/4.0/), which is again
# one-way compatible with GPLv3, under which the current source code is licenced,
# see: https://wiki.creativecommons.org/wiki/ShareAlike_compatibility:_GPLv3
class OrderedDefaultDict(OrderedDict):
    """ A defaultdict with OrderedDict as its base class. """

    def __init__(self, default_factory=None, *args, **kwargs):
        if not (default_factory is None or callable(default_factory)):
            raise TypeError('first argument must be callable or None')
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory  # called by __missing__()

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key,)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):  # Optional, for pickle support.
        args = (self.default_factory,) if self.default_factory else tuple()
        return self.__class__, args, None, None, iter(self.items())

    def __repr__(self):  # Optional.
        return '%s(%r, %r)' % (self.__class__.__name__, self.default_factory, self.items())
