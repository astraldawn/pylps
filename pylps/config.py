from pylps.constants import *
from pylps.exceptions import *

VALID_OPTIONS = {
    'debug': set([False, True]),
    'experimental': set([False, True]),
    'single_clause': set([False, True]),

    'obs': set([OBS_AFTER, OBS_BEFORE]),
    'solution_preference': set([SOLN_PREF_FIRST, SOLN_PREF_MAX]),
    'strategy': set([
        STRATEGY_DEFAULT, STRATEGY_COMB, STRATEGY_GREEDY,
        STRATEGY_GREEDY_FAST,
    ]),
}

VALID_OPTIONS_TYPE = {
    'n_solutions': int,
}


class _CONFIG(object):

    def __init__(self):
        self._options = {}
        self._n_solutions = 1

        # Counter for reactive ID
        self.reactive_id = 0

    @property
    def options(self):
        return self._options

    def set_options(self, options_dict):
        for (k, v) in options_dict.items():
            if v in VALID_OPTIONS.get(k, []):
                self._options[k] = v
                continue

            if VALID_OPTIONS_TYPE.get(k):
                if isinstance(v, VALID_OPTIONS_TYPE[k]):
                    self._options[k] = v
                    continue

            raise ConfigError(k, v)

    @property
    def debug(self):
        return self._options['debug']

    @property
    def strategy(self):
        return self._options['strategy']

    @property
    def experimental(self):
        return self._options['experimental']

    @property
    def n_solutions(self):
        return self._options['n_solutions']

    @property
    def obs(self):
        return self._options['obs']

    @property
    def single_clause(self):
        return self._options['single_clause']

    @property
    def solution_preference(self):
        return self._options['solution_preference']


CONFIG = _CONFIG()
