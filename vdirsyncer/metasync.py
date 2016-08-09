import logging

from . import exceptions
from .storage.base import normalize_meta_value

logger = logging.getLogger(__name__)


class MetaSyncError(exceptions.Error):
    pass


class MetaSyncConflict(MetaSyncError):
    key = None


def metasync(storage_a, storage_b, status, keys, conflict_resolution=None):
    def _a_to_b():
        logger.info(u'Copying {} to {}'.format(key, storage_b))
        storage_b.set_meta(key, a)
        status[key] = a

    def _b_to_a():
        logger.info(u'Copying {} to {}'.format(key, storage_a))
        storage_a.set_meta(key, b)
        status[key] = b

    def _resolve_conflict():
        if a == b:
            status[key] = a
        elif conflict_resolution is None:
            raise MetaSyncConflict(key=key)
        elif conflict_resolution == 'a wins':
            _a_to_b()
        elif conflict_resolution == 'b wins':
            _b_to_a()

    for key in keys:
        a = storage_a.get_meta(key)
        b = storage_b.get_meta(key)
        s = normalize_meta_value(status.get(key))
        logger.debug(u'Key: {}'.format(key))
        logger.debug(u'A: {}'.format(a))
        logger.debug(u'B: {}'.format(b))
        logger.debug(u'S: {}'.format(s))

        if a != s and b != s:
            _resolve_conflict()
        elif a != s and b == s:
            _a_to_b()
        elif a == s and b != s:
            _b_to_a()
        else:
            assert a == b

    for key in set(status) - set(keys):
        del status[key]
