'''
D B             A D
A C     -->     B C
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
    location('a', 'floor'), location('c', 'floor'),
    location('d', 'a'), location('b', 'c')

)

reactive_rule(True).then(
    make_tower(['a', 'b', 'floor']).frm(T1, T2),
)

reactive_rule(True).then(
    make_tower(['c', 'd', 'floor']).frm(T1, T2),
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

execute(debug=False)

show_kb_log()

'''
maxTime(10).
fluents location(_,_).

actions move(_,_).

initially location(a, floor), location(c, floor),
location(b, c), location(d, a).

if true
then make_tower([a,b,floor]) from T1 to T2.

if true
then make_tower([c,d,floor]) from T1 to T2.

clear(Block) at T if Block \= floor,
    not location(_,Block) at T.

clear(floor) at _.

make_tower([Block,floor]) from T1 to T2 if
    make_on(Block,floor) from T1 to T2.

make_tower([Block,Place|Places]) from T1 to T3 if
    Place \= floor,
    make_tower([Place|Places]) from T1 to T2,
    make_on(Block,Place) from T2 to T3.

make_on(Block,Place) from T1 to T4 if
    not location(Block,Place) at T1,
    make_clear(Place) from T1 to T2,
    make_clear(Block) from T2 to T3,
    move(Block,Place) from T3 to T4.

make_on(Block,Place) from T to T if
    location(Block,Place) at T.

make_clear(Place) from T to T if
    clear(Place) at T.

make_clear(Block) from T1 to T2 if
    location(Block1,Block) at T1,
    make_on(Block1,floor) from T1 to T2.

move(Block,Place)  initiates location(Block,Place).
move(Block,_)  terminates location(Block,Place).
'''