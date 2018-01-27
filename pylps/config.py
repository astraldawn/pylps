from pylps.constants import *
from pylps.exceptions import *

VALID_OPTIONS = {
    'single_clause': set([False, True])
}


class _CONFIG(object):

    def __init__(self):
        self._options = {}

    @property
    def options(self):
        return self._options

    def set_options(self, options_dict):
        for (k, v) in options_dict.items():
            if v in VALID_OPTIONS.get(k, []):
                self._options[k] = v
            else:
                raise ConfigError(k, v)

    @property
    def single_clause(self):
        return self._options['single_clause']


CONFIG = _CONFIG()
