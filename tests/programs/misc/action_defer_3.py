# Example to show actions are deferred to end of cycle
from pylps.core import *

initialise(max_time=3)

create_fluents('a')
create_facts('f(_)', 'g(_)')
create_events('p1(_)', 'p2(_)')
create_actions('p1a(_)', 'p2a(_)')
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
    f(X),
    p1a(X).frm(T1, T2)
)

goal(p2(X).frm(T1, T2)).requires(
    g(X),
    p2a(X).frm(T1, T2)
)

false_if(p1a(1), p2a(1))

execute(debug=False, strategy=STRATEGY_GREEDY)

show_kb_log()

'''
maxTime(3).
fluents     a.
events  p1(_), p2(_).
actions p1a(_), p2a(_).

f(1).
f(2).
g(1).

initially   a.

if a at T1
then p1(X) from T1 to T2.

if a at T1
then p2(X) from T1 to T2.

p1(X) from T1 to T2 if f(X), p1a(X) from T1 to T2.
p2(X) from T1 to T2 if g(X), p2a(X) from T1 to T2.

false p1a(1), p2a(1).

1-2: p1a(2), p2a(1)
2-3: p1a(2), p2a(1)
'''
