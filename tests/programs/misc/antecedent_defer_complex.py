from pylps.core import *

initialise(max_time=12)

create_fluents('f1')
create_events('e1', 'e2')
create_actions('a1', 'a2', 'a3', 'r1')

observe(a1.frm(1, 2))
observe(a2.frm(2, 3))
observe(e2.frm(3, 6))
observe(a3.frm(8, 9))

reactive_rule(a1.frm(T1, T2), e1.frm(T2, T3)).then(
    r1.frm(T3, T4)
)

goal(e1.frm(T1, T4)).requires(
    a2.frm(T1, T2),
    e2.frm(T3, T4),
)

goal(e2.frm(T1, T2)).requires(
    a3.frm(T3, T4)
)

e1.initiates(f1)

execute(debug=False)

show_kb_log()

'''
maxTime(10).
actions a1, r1, a2, a3.
events e2.
fluents f1.

observe     a1 from 1 to 2.
observe     a2 from 2 to 3.
observe     e2 from 3 to 6.
observe     a3 from 8 to 9.


if    a1 from T1 to T2, e1 from T2 to T3
then r1 from T3 to T4.

e1 from T1 to T4 if a2 from T1 to T2, e2 from T3 to T4.
e2 from T1 to T2 if a3 from T3 to T4.

e1 initiates f1.
'''
