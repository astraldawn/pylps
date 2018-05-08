'''
TODO: Test member with variables
'''

from pylps.core import *

initialise(max_time=1)

create_actions('say(_, _)', 'say_single(_)')
create_events('member(_, _)')
create_facts('inp(_, _)')
create_variables('X', 'Y', 'F', 'Item', 'List', 'Tail')


inp('a', ['c', 'd', F])
# inp(F, [1, 2])

reactive_rule(inp(Item, List)).then(
    member(Item, List),
    say(Item, List),
)

goal(member(X, [X | _])).requires()

goal(member(X, [Y | Tail])).requires(
    member(X, Tail),
)

execute(debug=False)

show_kb_log()
