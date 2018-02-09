# Example to show actions are deferred to end of cycle
from pylps.core import *

initialise(max_time=2)

create_fluents('a')
create_facts('f(_)', 'g(_)')
create_events('p1(_)', 'p2(_)')
create_variables('X', 'Y')

f(1)
f(2)
g(1)

initially(a)

reactive_rule(a.at(T1)).then(
    p1(X).frm(T1, T2)
)

reactive_rule(a.at(T1)).then(
    p2(X).frm(T1, T2)
)

goal(p1(X).frm(T1, T2)).requires(
    f(X)
)

goal(p2(X).frm(T1, T2)).requires(
    g(X)
)

# false_if(p1(X), p2(Y), X != Y)
# false_if(p1(1), p2(1))

execute()

show_kb_log(show_events=True)
