from pylps.core import *
from pylps.lps_data_structures import LPSConstant

initialise(max_time=5)

create_actions('say(_)', 'say_single(_)')
create_events('respond(_)')
create_facts('ask(_)')
create_variables('X', 'Y', 'Rest')

ask(['a', 'b1', 'c', 'd', 'e'])
ask(['a', 'b2', 'c', 'd'])

reactive_rule(ask(X)).then(
    respond(X).frm(T1, T2))

goal(
    respond(
        [LPSConstant('a') | [X | [LPSConstant('c') | Rest]]]
    ).frm(T1, T2)
).requires(
    say(X).frm(T1, T2),
    say(Rest).frm(T1, T2),
)

execute(single_clause=False)

show_kb_log()

'''
actions say(_).

ask([a,b1,c,d,e]).
ask([a,b2,c,d]).

if ask(X) then respond(X) from T1 to T2.

respond(['a'|[X|['c'|Rest]]]) from T1 to T2 if
        say(X) from T1 to T2,
        say(Rest) from T1 to T2.
'''
