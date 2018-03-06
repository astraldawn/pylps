from pylps.core import *

initialise(max_time=5)

create_actions('show(_, _)')
create_facts('f(_, _)')
create_variables('X')

f(1, 2)
f(1, 3)
f(2, 3)

reactive_rule(True).then(
    f(1, X),
    show('rule 1', X).frm(T1, T2)
)

reactive_rule(True).then(
    f(X, 3),
    show('rule 2', X).frm(T1, T2)
)

execute()

show_kb_log()
