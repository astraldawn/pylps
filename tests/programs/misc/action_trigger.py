from pylps.core import *

initialise(max_time=5)

create_actions('hello(_, _)', 'say(_, _)', 'say2(_, _)')
create_variables('X', 'Y')

reactive_rule(True).then(
    hello('A', 5),
)

reactive_rule(hello(X, Y).frm(T1, T2)).then(
    say(X, Y).frm(T2, T3)
)

reactive_rule(hello(X, Y).frm(T1, T2)).then(
    say2(X, Y).frm(T1, T2)
)

execute(debug=False)

show_kb_log()
