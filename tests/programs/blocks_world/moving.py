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

goal(clear(Block).at(T)).requires(
    Block != 'floor',
    ~location(_, Block).at(T),
)

goal(clear('floor').at(_))

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

goal(make_on(Block, Place).frm(T1, T4)).requires(
    ~location(Block, Place).at(T1),
    make_clear(Place).frm(T1, T2),
    make_clear(Block).frm(T2, T3),
    move(Block, Place).frm(T3, T4),
)

goal(make_on(Block, Place).frm(T, T)).requires(
    location(Block, Place).at(T),
)

goal(make_clear(Place).frm(T, T)).requires(
    clear(Place).at(T),
)

goal(make_clear(Block).frm(T1, T2)).requires(
    location(Block1, Block).at(T1),
    make_on(Block1, 'floor').frm(T1, T2),
)

move(Block, Place).initiates(location(Block, Place))
move(Block, _).terminates(location(Block, Place))

execute(strategy=STRATEGY_GREEDY)

show_kb_log()
