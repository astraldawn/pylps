from pylps.core import *

initialise(max_time=5)

create_actions('say(_, _)', 'say_single(_)')
create_events('member(_, _)')
create_facts('inp(_, _, _)')
create_variables('X', 'Y', 'F', 'Item', 'List', 'Tail', 'ListH', 'ListT')

inp(['b', 'c'], ['a', 'b'], [['b', 'c'], ['d', 'f']])
inp(['d', 'f'], ['a', 'b'], [['b', 'c'], ['d', 'f']])
inp(['q', 'z'], ['a', 'b'], [['b', 'c'], ['d', 'f']])

reactive_rule(inp(Item, ListH, ListT)).then(
    List.is_([ListH | [ListH | ListT]]),
    Item.is_in(List),
    say(Item, List),
)

execute(debug=False)

show_kb_log()
