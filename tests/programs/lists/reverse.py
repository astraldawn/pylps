from pylps.core import *

initialise(max_time=5)

create_actions('say(_, _)', 'say_single(_)')
create_events('reverse(_, _)', 'reverse_aux(_, _, _)')
create_facts('inp(_)')
create_variables('Rev', 'List', 'H', 'Tail', 'L', 'SoFar')

inp([])
inp([1, 2, 3, 4, 5])
inp([['a', 'b'], 5, [10, 'd']])

reactive_rule(inp(List)).then(
    reverse(List, Rev),
    say(List, Rev),
)

goal(reverse(List, Rev)).requires(
    reverse_aux(List, Rev, [])
)

goal(reverse_aux([], L, L))

goal(reverse_aux([H | Tail], L, SoFar)).requires(
    reverse_aux(Tail, L, [H | SoFar])
)

execute(debug=False)

show_kb_log()
