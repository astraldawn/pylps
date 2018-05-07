from pylps.core import *

initialise(max_time=1)

create_actions('show(_)', 'valid(_)', 'say(_, _)')
create_events('river(_, _, _, _)', 'member(_, _)')
create_facts('inp(_, _)', 'crossing(_, _, _)')
create_variables(
    'A', 'B', 'C', 'P', 'V', 'X', 'Y', 'Z', 'Tail',
    'Action', 'Start', 'End', 'Plan',
)

inp(['l', 'l', 'l', 'l'], ['r', 'r', 'r', 'r'])

crossing(['l', X, 'l', Z], ['r', X, 'r', Z], 'goose_cross')
crossing(['r', X, 'r', Z], ['l', X, 'l', Z], 'goose_back')

reactive_rule(inp(Start, End)).then(
    crossing(Start, C, Action),
    say(Action, C).frm(T1, T2),
)

execute(debug=True)

show_kb_log()
