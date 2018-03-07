from pylps.core import *
from pylps.lps_data_structures import LPSConstant

initialise(max_time=5)

create_actions('say(_)', 'say_single(_)')
create_events('respond(_)')
create_facts('ask(_)')
create_variables('X', 'Y', 'Rest')

ask(['a', 'b1', 'c', 'd'])
ask(['a', 'b2', 'c', 'd'])

reactive_rule(ask(X)).then(
    respond(X).frm(T1, T2))

goal(
    respond(
        [LPSConstant('a') | [X | [LPSConstant('a') | Rest]]]
    ).frm(T1, T2)
).requires(
    say(X).frm(T1, T2),
)

execute(single_clause=False, debug=True)

show_kb_log()
