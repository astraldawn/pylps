from pylps.core import *

initialise(max_time=5)

create_fluents('total_years_in_jail(_, _)')
create_actions('sort(_)', 'say(_)')
create_variables('X', 'Y')

observe(sort(['1', '2', '3', '4']).frm(1, 2))


def python_sort(iterable):
    return sorted(iterable)


reactive_rule(sort(X)).then(
    Y.is_(python_sort(X)),
    say(Y).frm(T2, T3),
)

execute(debug=True)

show_kb_log()
