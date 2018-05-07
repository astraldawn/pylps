from pylps.core import *

initialise(max_time=1)

create_actions('say(_)')
create_facts('inp(_, _)')
create_variables('X', 'Item', 'List')

inp([], [[]])
inp('a', ['b', 'c', 'a'])
inp(['b', 'c'], ['d', ['a', 'c'], ['b', 'c']])

reactive_rule(inp(Item, List)).then(
    X.is_([Item | List]),
    say(X),
)
execute(debug=False)

show_kb_log()
