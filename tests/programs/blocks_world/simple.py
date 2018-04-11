'''
                A
A B     -->     B
------------------------
'''
from pylps.core import *
from pylps.lps_data_structures import LPSConstant

initialise(max_time=10)

create_fluents('location(_, _)')
create_actions('move(_, _)', 'say(_)')
create_events(
    'clear(_)', 'make_tower(_)',
    'make_on(_, _)', 'make_clear(_)',
)
create_variables('Block', 'Block1', 'Place', 'Places')

initially(
    location('a', 'floor'), location('b', 'floor'),
)

reactive_rule(True).then(
    make_tower(['a', 'b', 'floor']).frm(T1, T2),
)

goal(
    make_tower([Block | LPSConstant('floor')]).frm(T1, T2)
).requires(
    make_on(Block, 'floor').frm(T1, T2),
)

goal(
    make_tower([Block | [Place | Places]]).frm(T1, T3)
).requires(
    Place != 'floor',
    make_tower([Place | Places]).frm(T1, T2),
    make_on(Block, Place).frm(T2, T3),
)

goal(make_on(Block, Place).frm(T1, T2)).requires(
    say(Block).frm(T1, T2),
    say(Place).frm(T1, T2),
)

move(Block, Place).initiates(location(Block, Place))
move(Block, _).terminates(location(Block, Place))

execute(debug=False)

show_kb_log()
