from pylps.core import *

initialise(max_time=1)

create_actions('show(_)')

reactive_rule(True).then(
    show(['a', 'b', 'c', 'd']).frm(T1, T2)
)

execute()

show_kb_log()
'''
actions show(_).

if true
then show([a,b,c,d]) from T1 to T2.

show([a,b,c,d]) from T1 to T2
'''
