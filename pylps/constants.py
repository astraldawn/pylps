# Objects
CONSTANT = 'constant'
VARIABLE = 'variable'
TEMPORAL_VARIABLE = 'temporal_var'

# LPS Objects
ACTION = 'action'
CLAUSE = 'clause'
EVENT = 'event'
CAUSALITY = 'causality'
FACT = 'fact'
FLUENT = 'fluent'
FLUENTS = 'fluents'
OBS = 'obs'
RULE = 'rule'
LPS_OBJECTS = ['ACTION', 'EVENT', 'FLUENT', 'RULE']

# Actions
A_TERMINATE = 'terminate'
A_INITIATE = 'initiate'
F_INITIATE = 'fluent_initiate'
F_TERMINATE = 'fluent_terminate'

# Goal related stuff
G_DISCARD = 'goal_discard'
G_SOLVED = 'goal_solved'
G_UNSOLVED = 'goal_unsolved'
G_CLAUSE_FAIL = 'goal_clause_fail'
G_SINGLE_SOLVED = 'goal_single_solved'
G_SINGLE_UNSOLVED = 'goal_single_unsolved'
NO_SUBS = None

VALID_GOAL_RESPONSES = set(
    [G_DISCARD, G_UNSOLVED, G_UNSOLVED, G_CLAUSE_FAIL, G_SINGLE_SOLVED,
     G_SINGLE_UNSOLVED, NO_SUBS])
