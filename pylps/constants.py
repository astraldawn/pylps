# Objects
CONSTANT = 'constant'
EXPR = 'expr'
VARIABLE = 'variable'
TEMPORAL_VARIABLE = 'temporal_var'
VAR_SEPARATOR = '_._'

# LPS Objects
ACTION = 'action'
CLAUSE = 'clause'
EVENT = 'event'
CAUSALITY = 'causality'
CAUSALITY_OUTCOME = 'causality_outcome'
CONSTRAINT = 'constraint'
FACT = 'fact'
FLUENT = 'fluent'
FLUENTS = 'fluents'
OBS = 'obs'
RULE = 'rule'
LPS_OBJECTS = ['ACTION', 'EVENT', 'FLUENT', 'RULE']

# Data structure constants
LIST = 'list'
TUPLE = 'tuple'
MATCH_LIST_HEAD = 'MATCH_LIST_HEAD'

# Solver objects
SOLVER_GOAL = 'solver_goal'
TREE_GOAL = 'TREE_GOAL'
REACTIVE_TREE_GOAL = 'REACTIVE_TREE_GOAL'
SOLVER_TREE_GOAL = 'SOLVER_TREE_GOAL'
REACTIVE = 'REACTIVE'

# Actions
A_TERMINATE = 'terminate'
A_INITIATE = 'initiate'
F_INITIATE = 'fluent_initiate'
F_TERMINATE = 'fluent_terminate'

# Goal related stuff
G_NPROCESSED = 'goal_not_processed'
G_DISCARD = 'goal_discard'
G_SOLVED = 'goal_solved'
G_UNSOLVED = 'goal_unsolved'
G_FAIL_NO_SUBS = 'GOAL_FAIL_NO_SUBS'
G_CLAUSE_FAIL = 'goal_clause_fail'
G_SINGLE_SOLVED = 'goal_single_solved'
G_SINGLE_UNSOLVED = 'goal_single_unsolved'
G_DEFER = 'goal_defer'
NO_SUBS = None

VALID_GOAL_RESPONSES = set(
    [G_DISCARD, G_UNSOLVED, G_UNSOLVED, G_CLAUSE_FAIL, G_SINGLE_SOLVED,
     G_SINGLE_UNSOLVED, NO_SUBS, G_NPROCESSED])

SOLVED_RESPONSES = set([G_SOLVED, G_SINGLE_SOLVED])

# OPERATORS
OP_ASSIGN = 'OP_ASSIGN'

# ERROR CONSTANTS
ERROR_NO_SUB_OPTIONS = 'ERROR_NO_SUB_OPTIONS'

# REJECTIONS
WARNING_REJECTED_OBSERVATION = 'Rejected observation'

# CONFIG
CONFIG_DEFAULT_N_SOLUTIONS = 1
SOLN_PREF_FIRST = 'first'
SOLN_PREF_MAX = 'maximum'
