# Example to show actions are deferred to end of cycle
from pylps.core import *

initialise(max_time=10)

create_facts('f(_)', 'g(_)')
create_action('p1(_)', 'p2(_)')
create_variables('X', 'Y')

reactive_rule(f(X)).then(
    p1(X).frm(T1, T2)
)

reactive_rule(g(X)).then(
    p2(X).frm(T1, T2)
)


false_if(p1(X), p2(Y), X != Y)

execute()

show_kb_log()
