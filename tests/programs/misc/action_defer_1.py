# Example to show actions are deferred to end of cycle
from pylps.core import *

initialise(max_time=2)

create_facts('f(_)', 'g(_)')
create_actions('p1(_)', 'p2(_)')
create_variables('X', 'Y')

f(1)
f(2)
g(1)

reactive_rule(f(X)).then(
    p1(X).frm(T1, T2)
)

reactive_rule(g(X)).then(
    p2(X).frm(T1, T2)
)

false_if(p1(1), p2(1))

execute()

show_kb_log()
