from pylps.core import *
from pylps.lps_data_structures import LPSFunction

initialise(max_time=10)

create_actions('sort(_)', 'say(_)')
create_variables('X', 'Y')

observe(sort([5, 4, 3, 2, 1, 10]).frm(1, 2))


class python_sort(LPSFunction):
    def func(self, iterable):
        return sorted(iterable)


reactive_rule(sort(X)).then(
    Y.is_(python_sort(X)),
    say(Y).frm(T2, T3),
)

execute(debug=False)

show_kb_log()
