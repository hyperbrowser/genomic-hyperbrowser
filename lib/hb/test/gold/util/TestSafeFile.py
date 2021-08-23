from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed, wait
from contextlib import closing
from copy import copy
import pytest

from gold.util.SafeFile import SafePickleFile, SafeJsonFile
from gold.util.CustomExceptions import NotDictLikeError, NotSyncedError, SyncConflictError
from gold.util.RandomUtil import random


def _test_readwrite_single(safe_file_factory_func):
    my_str = "And now the end is near"

    with closing(safe_file_factory_func()) as sf:
        sf.object = my_str
        assert sf.object == my_str


def _test_openclose(safe_file_factory_func):
    # Testing reading object before close
    with closing(safe_file_factory_func()) as sf:
        sf.object = {'0': "So I face the final curtain",
                     '1': "My friend, I'll say it clear"}
        obj = sf.object

    # Testing reading object or other operations after close

    with pytest.raises(ValueError):
        sf.object = "I'll state my case of which I'm certain"

    with pytest.raises(ValueError):
        obj = sf.object

    with pytest.raises(ValueError):
        sf.sync()

    with pytest.raises(ValueError):
        sf[0]

    with pytest.raises(ValueError):
        sf[0] = "I've lived a life that's full"

    with pytest.raises(ValueError):
        del sf[0]

    with pytest.raises(ValueError):
        sf.get(0)

    with pytest.raises(ValueError):
        0 in sf

    with pytest.raises(ValueError):
        sf.sync()


def _test_readwrite_sequential(safe_file_factory_func):
    my_str = "I've traveled each and every highway"

    with closing(safe_file_factory_func()) as sf_write:
        sf_write.object = my_str

    with closing(safe_file_factory_func()) as sf_read:
        assert sf_read.object == my_str


def _test_readwrite_parallel_oneway(safe_file_factory_func):
    my_str_1 = "And more, much more than this"
    my_str_2 = "I did it my way"

    with closing(safe_file_factory_func()) as sf_2:
        # Testing state before sync

        sf_1 = safe_file_factory_func()
        sf_1.object = my_str_1
        assert sf_1.object == my_str_1
        assert sf_2.object is None

        # Testing state after sync, including auto-sync if local state is empty (sf_2)

        sf_1.sync()
        assert sf_1.object == my_str_1
        assert sf_2.object == my_str_1

        # Testing state after update, before sync

        sf_1.object = my_str_2
        assert sf_1.object == my_str_2
        assert sf_2.object == my_str_1

        # Testing closing and syncing

        sf_1.close()  # Calls sync() if dirty
        assert sf_2.object == my_str_1
        sf_2.sync()
        assert sf_2.object == my_str_2


def _test_readwrite_parallel_conflict(safe_file_factory_func):
    my_str_1 = "Regrets, I've had a few"
    my_str_2 = "But then again, too few to mention"
    my_str_3 = "I did what I had to do"
    my_str_4 = "And saw it through without exception"

    with closing(safe_file_factory_func()) as sf_1, closing(safe_file_factory_func()) as sf_2:
        # Testing conflictResolution='raise'

        sf_1.object = my_str_1
        sf_1.sync()
        sf_2.object = my_str_2

        with pytest.raises(SyncConflictError):
            sf_2.sync(conflictResolution='raise')
        with pytest.raises(SyncConflictError):
            sf_2.sync()  # conflictResolution='raise' by default

        # Testing conflictResolution='remote'. sf_1.sync() not needed for full sync.

        sf_2.sync(conflictResolution='remote')
        assert sf_1.object == sf_2.object == my_str_1 == "Regrets, I've had a few"

        # Testing that remote syncing sp_1 edit into sp_2 does not mess with the next sync of sp_1

        sf_1.object = my_str_2
        sf_1.sync()
        assert sf_1.object == my_str_2 == "But then again, too few to mention"
        assert sf_2.object == my_str_1 == "Regrets, I've had a few"

        # Testing conflictResolution='local'. sf_1.sync() needed for full sync()

        sf_2.object = my_str_3
        with pytest.raises(SyncConflictError):
            sf_2.sync()
        sf_2.sync(conflictResolution='local')
        assert sf_1.object == my_str_2 == "But then again, too few to mention"
        assert sf_2.object == my_str_3 == "I did what I had to do"

        # Testing full sync

        sf_1.object = my_str_4
        with pytest.raises(SyncConflictError):
            sf_1.sync()
        sf_1.sync(conflictResolution='local')
        sf_2.sync()

        assert sf_1.object == sf_2.object == my_str_4 == "And saw it through without exception"


def _test_readwrite_parallel_conflict_readonly(safe_file_factory_func):
    my_str_1 = "I planned each charted course"
    my_str_2 = "Each careful step along the byway"
    my_str_3 = "Oh, and more, much more than this"
    my_str_4 = "I did it my way"

    with closing(safe_file_factory_func()) as sf_1, closing(safe_file_factory_func()) as sf_2:
        # Testing readOnly sync with conflictResolution='local'

        sf_1.object = my_str_1
        sf_2.object = my_str_2
        sf_1.sync()
        with pytest.raises(SyncConflictError):
            sf_2.sync()
        sf_2.sync(conflictResolution='local', readOnly=True)  # Resolves conflict to my_str_2, but only locally
        sf_1.sync()  # Does nothing due to readOnly sync from sf_2
        assert sf_1.object == my_str_1 == "I planned each charted course"
        assert sf_2.object == my_str_2 == "Each careful step along the byway"

        # Testing readOnly sync with conflictResolution='remote'. Readonly has no effect here for non-dictlike objects

        sf_2.sync()  # Conflict has already been resolved for sf_2. Now writes my_str_2
        sf_1.object = my_str_1
        with pytest.raises(SyncConflictError):
            sf_1.sync()
        sf_1.sync(conflictResolution='remote', readOnly=True)  # no effect of readOnly=True
        assert sf_1.object == sf_2.object == my_str_2 == "Each careful step along the byway"

        sf_2.object = my_str_3
        sf_2.sync()
        sf_1.sync()  # Nothing to write
        assert sf_1.object == sf_2.object == my_str_3 == "Oh, and more, much more than this"

        sf_2.object = my_str_4
        sf_2.sync()
        sf_1.object = my_str_1
        with pytest.raises(SyncConflictError):
            sf_1.sync()
        sf_1.sync(conflictResolution='remote')  # same effect as readOnly=True above
        assert sf_1.object == sf_2.object == my_str_4 == "I did it my way"


def _test_readwrite_notdictlike(safe_file_factory_func):
    with closing(safe_file_factory_func()) as sf_1:
        sf_1.object = 'Do-Re-Mi'

        # Testing that operations for dict-line objects does not work for other object types

        with pytest.raises(NotDictLikeError):
            sf_1['by']
        with pytest.raises(NotDictLikeError):
            sf_1.get('by')
        with pytest.raises(NotDictLikeError):
            'by' in sf_1
        with pytest.raises(NotDictLikeError):
            sf_1['by'] = "Rogers and Hammerstein"
        with pytest.raises(NotDictLikeError):
            del sf_1['by']


def _test_readwrite_dict_parallel_basic(safe_file_factory_func):
    my_orig_dict = {'do': "Doe, a deer, a female deer",
                    're': "Ray, a drop of golden sun"}
    my_dict_1 = copy(my_orig_dict)

    with closing(safe_file_factory_func()) as sf_1, closing(safe_file_factory_func()) as sf_2:
        # Testing state before sync, including exceptions for item-level operations

        sf_1.object = my_dict_1
        with pytest.raises(NotSyncedError):
            sf_1['do']
        with pytest.raises(NotSyncedError):
            sf_1.get('do')
        with pytest.raises(NotSyncedError):
            'do' in sf_1
        with pytest.raises(NotSyncedError):
            sf_1['do'] = 'Do nothing'
        with pytest.raises(NotSyncedError):
            del sf_1['do']
        assert sf_1.object == my_dict_1
        assert id(sf_1.object) == id(my_dict_1)
        assert sf_2.object is None

        # Testing state after sync, including auto-sync if local state is empty (sf_2)

        sf_1.sync()
        my_dict_2 = sf_2.object
        assert sf_1.object == my_dict_1 == sf_2.object == my_dict_2 == my_orig_dict
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object) == id(my_dict_2) != id(my_orig_dict)

        # Testing state after update of single dict item and syncing

        sf_1['mi'] = "Me, a name I call myself"
        sf_1.sync()
        sf_2.sync()
        assert sf_1.object == my_dict_1 == sf_2.object == my_dict_2 != my_orig_dict
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object) == id(my_dict_2) != id(my_orig_dict)
        assert set(sf_1.object.keys()) == set(sf_2.object.keys()) == set(('do', 're', 'mi'))
        assert sf_2['mi'] == sf_2.get('mi') == my_dict_2['mi'] == "Me, a name I call myself"

        with pytest.raises(KeyError):
            sf_2['fa']
        assert sf_2.get('fa') is None
        assert 'fa' not in sf_2

        # Testing no conflicts when updating different dict items from different instances

        sf_1['fa'] = "Far, a long, long way to run"
        sf_2['so'] = "Sew, a needle pulling thread"
        sf_1.sync()
        sf_2.sync()
        sf_1.sync()
        print sf_1.object, my_dict_1, sf_2.object, my_dict_2, my_orig_dict
        assert sf_1.object == my_dict_1 == sf_2.object == my_dict_2 != my_orig_dict
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object) == id(my_dict_2) != id(my_orig_dict)
        assert set(sf_1.object.keys()) == set(sf_2.object.keys()) == set(('do', 're', 'mi', 'fa', 'so'))
        assert sf_1['so'] == sf_1.get('so') == sf_2['so'] == sf_2.get('so') == \
               my_dict_1['so'] == my_dict_2['so'] == "Sew, a needle pulling thread"
        assert sf_1['fa'] == sf_1.get('fa') == sf_2['fa'] == sf_2.get('fa') == \
               my_dict_1['fa'] == my_dict_2['fa'] == "Far, a long, long way to run"


def _test_readwrite_dict_parallel_conflict_basic(safe_file_factory_func):
    my_dict_1 = {'do': "Doe, a deer, a female deer",
                 're': "Ray, a drop of golden sun"}

    with closing(safe_file_factory_func()) as sf_1, closing(safe_file_factory_func()) as sf_2:
        sf_1.object = my_dict_1
        sf_1.sync()
        sf_2.sync()

        # Testing conflict when updating same dict item from different instances
        # conflictResolutions: "raise" and "local"

        sf_1['mi'] = "Me, a name I call myself"
        sf_1.sync()
        sf_2['mi'] = "You, a name you call yourself"
        with pytest.raises(SyncConflictError):
            sf_2.sync()
        sf_2.sync(conflictResolution='local')
        sf_1.sync()
        assert sf_1.object == my_dict_1 == sf_2.object
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object)
        assert set(sf_1.object.keys()) == set(my_dict_1.keys()) == set(sf_2.object.keys()) == set(('do', 're', 'mi'))
        assert sf_1['mi'] == sf_1.get('mi') == sf_1.object['mi'] == my_dict_1['mi'] == \
               sf_2['mi'] == sf_2.get('mi') == sf_2.object['mi'] == "You, a name you call yourself"

        # Testing conflict when updating same dict item from different instances
        # conflictResolutions: "raise" and "remote"

        sf_1['fa'] = "Far, a long, long way to run"
        sf_2['fa'] = "Near, a short, short way to run"
        sf_1.sync()
        with pytest.raises(SyncConflictError):
            sf_2.sync()
        sf_2.sync(conflictResolution='remote')
        assert sf_1.object == my_dict_1 == sf_2.object
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object)
        assert set(sf_1.object.keys()) == set(my_dict_1.keys()) == set(sf_2.object.keys()) == \
               set(('do', 're', 'mi', 'fa'))
        assert sf_1['fa'] == sf_1.get('fa') == sf_1.object['fa'] == my_dict_1['fa'] == \
               sf_2['fa'] == sf_2.get('fa') == sf_2.object['fa'] == "Far, a long, long way to run"

        # Testing that remote syncing sp_1 edit into sp_2 does not mess with the next sync of sp_1

        sf_1['fa'] = "Near, a short, short way to run"
        sf_1.sync()
        assert sf_1.object == my_dict_1 != sf_2.object
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object)
        assert set(sf_1.object.keys()) == set(my_dict_1.keys()) == set(sf_2.object.keys()) == \
               set(('do', 're', 'mi', 'fa'))
        assert sf_1['fa'] == sf_1.get('fa') == sf_1.object['fa'] == my_dict_1['fa'] == "Near, a short, short way to run"
        assert sf_2['fa'] == sf_2.get('fa') == sf_2.object['fa'] == "Far, a long, long way to run"

        # Testing no conflict when updating same dict item from different instances, but with the same result

        sf_1['so'] = sf_2['so'] = "Sew, a needle pulling thread"
        sf_1.sync()
        sf_2.sync()
        assert sf_1.object == my_dict_1 == sf_2.object
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object)
        assert set(sf_1.object.keys()) == set(my_dict_1.keys()) == set(sf_2.object.keys()) == \
               set(('do', 're', 'mi', 'fa', 'so'))
        assert sf_1['so'] == sf_1.get('so') == sf_1.object['so'] == my_dict_1['so'] == \
               sf_2['so'] == sf_2.get('so') == sf_2.object['so'] == "Sew, a needle pulling thread"

        # Testing no conflicts when updating different dict items from different instances, including deletes

        del sf_1['re']
        sf_2['la'] = "La, a note to follow Sew"
        sf_1.sync()
        sf_2.sync()
        sf_1.sync()
        assert sf_1.object == my_dict_1 == sf_2.object
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object)
        assert set(sf_1.object.keys()) == set(my_dict_1.keys()) == set(sf_2.object.keys()) == \
               set(('do', 'mi', 'fa', 'so', 'la'))
        assert sf_1['la'] == sf_1.get('la') == sf_1.object['la'] == my_dict_1['la'] == \
               sf_2['la'] == sf_2.get('la') == sf_2.object['la'] == "La, a note to follow Sew"


def _test_readwrite_dict_parallel_conflict_advanced(safe_file_factory_func):
    my_dict_1 = {'do': "Doe, a deer, a female deer",
                 're': "Ray, a drop of golden sun"}

    with closing(safe_file_factory_func()) as sf_1, closing(safe_file_factory_func()) as sf_2:
        # Testing changing object from string to dict

        sf_1.object = "Do-Re-Mi"
        sf_1.sync()
        sf_2.sync()

        sf_1.object = my_dict_1
        sf_1.sync()
        sf_2.sync()
        my_dict_2 = sf_2.object

        # Testing set of dict item conflicts, not fully synced both ways

        sf_1['do'] = "Deer, a deer, a male deer"
        del sf_2['do']
        del sf_1['re']
        sf_2['re'] = "Ray, a drop of silver moon"
        sf_1['mi'] = "Me, a name I call myself"
        sf_2['mi'] = "You, a name you call yourself"
        sf_1['fa'] = "Far, a long, long way to run"
        sf_2['fa'] = "Near, a short, short way to run"
        sf_2['so'] = "Sew, a needle pulling thread"
        sf_1.sync()
        with pytest.raises(SyncConflictError):
            sf_2.sync()
        sf_2.sync(conflictResolution='local')
        assert sf_1.object == my_dict_1 != sf_2.object == my_dict_2
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object) == id(my_dict_2)
        assert set(sf_1.object.keys()) == set(my_dict_1.keys()) == set(('do', 'mi', 'fa'))
        assert set(sf_2.object.keys()) == set(my_dict_2.keys()) == set(('re', 'mi', 'fa', 'so'))
        assert sf_1['mi'] == sf_1.get('mi') == sf_1.object['mi'] == my_dict_1['mi'] == "Me, a name I call myself"
        assert sf_2['mi'] == sf_2.get('mi') == sf_2.object['mi'] == my_dict_2['mi'] == "You, a name you call yourself"
        assert sf_1.get('re') is None
        assert sf_2.get('do') is None
        assert 're' not in sf_1
        assert 'do' not in sf_2

        # Testing delete and restore dict item as a conflict-triggering event

        del sf_1['fa']
        sf_1['fa'] = "Far, a long, long way to run"
        with pytest.raises(SyncConflictError):
            sf_1.sync()
        sf_1.sync(conflictResolution='local')
        sf_2.sync()
        assert sf_1.object == my_dict_1 == sf_2.object == my_dict_2
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object) == id(my_dict_2)
        assert set(sf_1.object.keys()) == set(my_dict_1.keys()) == \
               set(sf_2.object.keys()) == set(my_dict_2.keys()) == \
               set(('re', 'mi', 'fa', 'so'))
        assert sf_1['fa'] == sf_1.get('fa') == sf_1.object['fa'] == my_dict_1['fa'] == \
               sf_2['fa'] == sf_2.get('fa') == sf_2.object['fa'] == my_dict_2['fa'] == \
               "Far, a long, long way to run"

        # Testing that conflicting events on referenced dict do not register as events to be synced

        del my_dict_1['so']
        my_dict_1['la'] = "La, a note to follow Sew"
        my_dict_2['so'] = "Sew, a needle pushing thread"
        my_dict_2['ti'] = "Tea, a drink with jam and bread"
        sf_1.sync()
        sf_2.sync()
        sf_1.sync()
        assert sf_1.object == my_dict_1 != sf_2.object == my_dict_2
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object) == id(my_dict_2)
        assert set(sf_1.object.keys()) == set(my_dict_1.keys()) == set(('re', 'mi', 'fa', 'la'))
        assert set(sf_2.object.keys()) == set(my_dict_2.keys()) == set(('re', 'mi', 'fa', 'so', 'ti'))
        assert sf_1.get('so') is None
        assert 'so' not in sf_1

        # Testing that resetting the referenced dict triggers an object-replace event, with no support for
        # item-level conflicts

        sf_1.object = my_dict_1
        sf_2.object = my_dict_2
        sf_1.sync()
        with pytest.raises(SyncConflictError):
            sf_2.sync()
        sf_2.sync(conflictResolution='remote')
        sf_1.sync()
        assert sf_1.object == my_dict_1 == sf_2.object != my_dict_2
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object) != id(my_dict_2)
        assert set(sf_1.object.keys()) == set(my_dict_1.keys()) == set(sf_2.object.keys()) == \
               set(('re', 'mi', 'fa', 'la'))
        assert sf_1['la'] == sf_1.get('la') == sf_1.object['la'] == my_dict_1['la'] == \
               sf_2['la'] == sf_2.get('la') == sf_2.object['la'] == "La, a note to follow Sew"

        # Testing reset to empty dict

        sf_1.object = dict()
        sf_1.sync()
        sf_2.sync()
        assert sf_1.object == sf_2.object == dict()
        assert id(sf_1.object) != id(sf_2.object)
        assert set(sf_1.object.keys()) == set(sf_2.object.keys()) == set()


def _test_readwrite_dict_parallel_conflict_readonly(safe_file_factory_func):
    my_dict_1 = {'do': "Doe, a deer, a female deer",
                 're': "Ray, a drop of golden sun"}

    with closing(safe_file_factory_func()) as sf_1, closing(safe_file_factory_func()) as sf_2:
        # Testing readOnly sync with conflictResolution='local'

        sf_1.object = my_dict_1
        sf_1.sync()
        sf_2.sync()
        my_dict_2 = sf_2.object

        sf_1['mi'] = "Me, a name I call myself"
        sf_1['fa'] = "Far, a long, long way to run"
        sf_1.sync()
        sf_2['mi'] = "You, a name you call yourself"
        sf_2['so'] = "Sew, a needle pulling thread"
        with pytest.raises(SyncConflictError):
            sf_2.sync()
        sf_2.sync(conflictResolution='local', readOnly=True)  # Resolves conflict locally, but does not write result
        assert sf_1.object == my_dict_1 != sf_2.object == my_dict_2
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object) == id(my_dict_2)
        assert set(sf_1.object.keys()) == set(my_dict_1.keys()) == set(('do', 're', 'mi', 'fa'))
        assert set(sf_2.object.keys()) == set(my_dict_2.keys()) == set(('do', 're', 'mi', 'fa', 'so'))
        assert sf_1['mi'] == sf_1.get('mi') == sf_1.object['mi'] == my_dict_1['mi'] == "Me, a name I call myself"
        assert sf_2['mi'] == sf_2.get('mi') == sf_2.object['mi'] == my_dict_2['mi'] == "You, a name you call yourself"

        # Testing readOnly sync with conflictResolution='local'

        sf_2.sync()  # Conflict has already been resolved for sf_2. Now writes resolution
        sf_1['mi'] = "Him, a name he call himself"
        sf_1['la'] = "La, a note to follow Sew"
        with pytest.raises(SyncConflictError):
            sf_1.sync()
        sf_1.sync(conflictResolution='remote', readOnly=True)  # Resolves conflict locally, but does not write result
        sf_2.sync()  # Does nothing due to readOnly sync from sf_1
        assert sf_1.object == my_dict_1 != sf_2.object == my_dict_2
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object) == id(my_dict_2)
        assert set(sf_1.object.keys()) == set(my_dict_1.keys()) == set(('do', 're', 'mi', 'fa', 'so', 'la'))
        assert set(sf_2.object.keys()) == set(my_dict_2.keys()) == set(('do', 're', 'mi', 'fa', 'so'))
        assert sf_1['mi'] == sf_1.get('mi') == sf_1.object['mi'] == my_dict_1['mi'] == \
               sf_2['mi'] == sf_2.get('mi') == sf_2.object['mi'] == my_dict_2['mi'] == "You, a name you call yourself"

        # Testing full sync after readOnly=True

        sf_1.sync()  # Conflict has already been resolved for sf_1. Now writes resolution
        sf_2['la'] = "La, a tone to follow Sew"
        with pytest.raises(SyncConflictError):
            sf_2.sync()
        sf_2.sync(conflictResolution='remote')
        sf_1.sync()
        assert sf_1.object == my_dict_1 == sf_2.object == my_dict_2
        assert id(sf_1.object) == id(my_dict_1) != id(sf_2.object) == id(my_dict_2)
        assert set(sf_1.object.keys()) == set(my_dict_1.keys()) == \
               set(sf_2.object.keys()) == set(my_dict_2.keys()) == set(('do', 're', 'mi', 'fa', 'so', 'la'))
        assert sf_1['la'] == sf_1.get('la') == sf_1.object['la'] == my_dict_1['la'] == \
               sf_2['la'] == sf_2.get('la') == sf_2.object['la'] == my_dict_2['la'] == "La, a note to follow Sew"


def string_worker(index, num_keys, seed, safe_file, verbose):
    random.setManualSeed(seed)
    if verbose:
        print "Starting worker {}...".format(index)

    with closing(safe_file) as sf:
        sf.object = "String generated by worker {}".format(index)

        random_resolution = random.choice(['local', 'remote'])
        if verbose:
            print "Worker {}: random_resolution={}".format(index, random_resolution)

        sf.sync(conflictResolution=random_resolution)
        if verbose:
            print "Worker {}: object: {}".format(index, sf.object)


def dict_worker(index, num_keys, seed, safe_file, verbose):
    random.setManualSeed(seed)
    if verbose:
        print "Starting worker {}...".format(index)

    with closing(safe_file) as sf:
        keys = [str(i) for i in range(num_keys)]
        sf.object = dict((key, 'Default string') for key in keys)
        sf.sync(conflictResolution='remote')

        random_key = random.choice(keys)
        random_resolution = random.choice(['local', 'remote'])
        if verbose:
            print "Worker {}: random_key={}, random_resolution={}".format(index, random_key, random_resolution)

        sf[random.choice(keys)] = "String generated by worker {}".format(index)
        sf.sync(conflictResolution=random.choice(['local', 'remote']))
        if verbose:
            print "Worker {}: object: {}".format(index, sf.object)


def _run_parallel_workers_with_randomness(executorClass, func, num_workers, num_keys,
                                          safe_file_factory_func):
    from config.DebugConfig import DebugConfig
    verbose = DebugConfig.VERBOSE

    with executorClass() as executor:
        jobs = [executor.submit(func, i, num_keys, random.createRandomSeed(), safe_file_factory_func(), verbose)
                for i in range(num_workers)]
        wait(jobs)

        with closing(safe_file_factory_func()) as sf:
            sf.sync()
            print '\n{}: {}'.format(sf.__class__.__name__, sf.object)


def _test_concurrency_threads_string(safe_file_factory_func):
    _run_parallel_workers_with_randomness(ThreadPoolExecutor, string_worker, 5, None, safe_file_factory_func)


def _test_concurrency_processes_string(safe_file_factory_func):
    _run_parallel_workers_with_randomness(ProcessPoolExecutor, string_worker, 5, None, safe_file_factory_func)


def _test_concurrency_threads_dict(safe_file_factory_func):
    _run_parallel_workers_with_randomness(ThreadPoolExecutor, dict_worker, 5, 3, safe_file_factory_func)


def _test_concurrency_processed_dict(safe_file_factory_func):
    _run_parallel_workers_with_randomness(ProcessPoolExecutor, dict_worker, 5, 3, safe_file_factory_func)


@pytest.fixture
def get_safe_pickle_file(tmp_path):
    def _get_safe_pickle_file():
        pickle_path = str(tmp_path.resolve() / 'myobj.pickle')
        return SafePickleFile(pickle_path)
    return _get_safe_pickle_file


@pytest.fixture
def get_safe_json_file(tmp_path):
    def _get_safe_json_file():
        pickle_path = str(tmp_path.resolve() / 'myobj.json')
        return SafeJsonFile(pickle_path)
    return _get_safe_json_file


# SafePickleFile tests


def test_readwrite_single_pickle(get_safe_pickle_file):
    _test_readwrite_single(get_safe_pickle_file)


def test_openclose_pickle(get_safe_pickle_file):
    _test_openclose(get_safe_pickle_file)


def test_readwrite_sequential_pickle(get_safe_pickle_file):
    _test_readwrite_sequential(get_safe_pickle_file)


def test_readwrite_parallel_oneway_pickle(get_safe_pickle_file):
    _test_readwrite_parallel_oneway(get_safe_pickle_file)


def test_readwrite_parallel_conflict_pickle(get_safe_pickle_file):
    _test_readwrite_parallel_conflict(get_safe_pickle_file)


def test_readwrite_parallel_conflict_readonly(get_safe_pickle_file):
    _test_readwrite_parallel_conflict_readonly(get_safe_pickle_file)


def test_readwrite_notdictlike_pickle(get_safe_pickle_file):
    _test_readwrite_notdictlike(get_safe_pickle_file)


def test_readwrite_dict_parallel_basic_pickle(get_safe_pickle_file):
    _test_readwrite_dict_parallel_basic(get_safe_pickle_file)


def test_readwrite_dict_parallel_conflict_basic_pickle(get_safe_pickle_file):
    _test_readwrite_dict_parallel_conflict_basic(get_safe_pickle_file)


def test_readwrite_dict_parallel_conflict_advanced_pickle(get_safe_pickle_file):
    _test_readwrite_dict_parallel_conflict_advanced(get_safe_pickle_file)


def test_readwrite_dict_parallel_conflict_readonly(get_safe_pickle_file):
    _test_readwrite_dict_parallel_conflict_readonly(get_safe_pickle_file)


def test_concurrency_threads_string_pickle(get_safe_pickle_file):
    _test_concurrency_threads_string(get_safe_pickle_file)


def test_concurrency_processes_string_pickle(get_safe_pickle_file):
    _test_concurrency_processes_string(get_safe_pickle_file)


def test_concurrency_threads_dict_pickle(get_safe_pickle_file):
    _test_concurrency_threads_dict(get_safe_pickle_file)


def test_concurrency_processed_dict_pickle(get_safe_pickle_file):
    _test_concurrency_processed_dict(get_safe_pickle_file)


# SafeJsonFile tests


def test_readwrite_single_json(get_safe_json_file):
    _test_readwrite_single(get_safe_json_file)


def test_openclose_json(get_safe_json_file):
    _test_openclose(get_safe_json_file)


def test_readwrite_sequential_json(get_safe_json_file):
    _test_readwrite_sequential(get_safe_json_file)


def test_readwrite_parallel_oneway_json(get_safe_json_file):
    _test_readwrite_parallel_oneway(get_safe_json_file)


def test_readwrite_parallel_conflict_json(get_safe_json_file):
    _test_readwrite_parallel_conflict(get_safe_json_file)


def test_readwrite_parallel_conflict_readonly(get_safe_json_file):
    _test_readwrite_parallel_conflict_readonly(get_safe_json_file)


def test_readwrite_notdictlike_json(get_safe_json_file):
    _test_readwrite_notdictlike(get_safe_json_file)


def test_readwrite_dict_parallel_basic_json(get_safe_json_file):
    _test_readwrite_dict_parallel_basic(get_safe_json_file)


def test_readwrite_dict_parallel_conflict_basic_json(get_safe_json_file):
    _test_readwrite_dict_parallel_conflict_basic(get_safe_json_file)


def test_readwrite_dict_parallel_conflict_advanced_json(get_safe_json_file):
    _test_readwrite_dict_parallel_conflict_advanced(get_safe_json_file)


def test_readwrite_dict_parallel_conflict_readonly(get_safe_json_file):
    _test_readwrite_dict_parallel_conflict_readonly(get_safe_json_file)


def test_concurrency_threads_string_json(get_safe_json_file):
    _test_concurrency_threads_string(get_safe_json_file)


def test_concurrency_processes_string_json(get_safe_json_file):
    _test_concurrency_processes_string(get_safe_json_file)


def test_concurrency_threads_dict_json(get_safe_json_file):
    _test_concurrency_threads_dict(get_safe_json_file)


def test_concurrency_processed_dict_json(get_safe_json_file):
    _test_concurrency_processed_dict(get_safe_json_file)
