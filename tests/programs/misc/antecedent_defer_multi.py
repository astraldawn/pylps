from pylps.core import *

initialise(max_time=8)

create_fluents('f1')
create_events('e1', 'e2')
create_actions('a1', 'a2', 'a3', 'r1')

observe(a1.frm(1, 2))
observe(a2.frm(2, 3))
observe(a2.frm(5, 6))

reactive_rule(a1.frm(T1, T2), a2.frm(T3, T4)).then(
    r1.frm(T4, T5)
)

execute(debug=False)

show_kb_log()

'''
maxTime(8).
actions a1, r1, a2.

observe     a1 from 1 to 2.
observe     a2 from 2 to 3.
observe     a2 from 5 to 6.

if    a1 from T1 to T2, a2 from T3 to T4
then r1 from T4 to T5.
'''
