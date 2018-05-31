from pylps.core import *

initialise(max_time=5)

create_actions('say(_, _)', 'say_single(_)')
create_events('member(_, _)')
create_facts('inp(_, _)')
create_variables('X', 'Y', 'F', 'Item', 'List', 'Tail')

inp([], [[]])
inp('z', ['a', 'b', 'c', 'd', 'e'])
inp('a', ['b', 'c', 'a'])
inp(['b', 'c'], ['d', ['a', 'c']])
inp(['b', 'c'], ['d', ['a', 'c'], ['b', 'c']])

reactive_rule(inp(Item, List)).then(
    Item.not_in(List),
    say(Item, List),
)

execute(debug=False)

show_kb_log()
