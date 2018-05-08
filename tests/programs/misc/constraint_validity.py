from pylps.core import *

initialise(max_time=10)

create_actions('show(_)', 'valid(_)', 'say(_, _)')
create_events('river(_, _, _, _)', 'member(_, _)')
create_facts('inp(_', 'crossing(_, _, _)')
create_variables(
    'A', 'B', 'C', 'P', 'V', 'X', 'Y', 'Z', 'Tail',
    'Action', 'Start', 'End', 'Plan',
)

inp(['l', 'l', 'l', 'l'])
inp(['r', 'l', 'l', 'l'])
inp(['r', 'l', 'r', 'l'])
inp(['l', 'l', 'r', 'r'])

reactive_rule(inp(Start)).then(
    valid(Start),
)

false_if(valid([A, B, B, C]), A != B)
false_if(valid([A, C, B, B]), A != B)

execute(debug=False)

show_kb_log()
