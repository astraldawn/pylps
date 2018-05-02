'''
Success:
    append([1,2],L2,[1,2,3,4]). (gives L2=[3,4]).
    append([1,B],L2,[A,2,3,4]). (gives B=2 L2=[3,4] A=1).
    append([1,2],L2,L3).        (gives L2=L2 L3=[1,2|L2]).
    append([1],[2,3],L3).     (gives L3=[1,2,3]).

Fail:
    append(L1,[3],[1,2,3,4]).
    append(1,L2,[1,2]).
'''

from pylps.core import *

initialise(max_time=1)

create_actions('say(_, _, _)', 'say_single(_)')
create_events('append(_, _, _)')
create_facts('lists(_, _)')
create_variables('X', 'Y', 'Z', 'L1', 'L2', 'L3')

lists([], [])
lists([], ['a'])
lists(['a'], ['b'])
lists(['a', 'b'], ['a', 'b', 'c', 'd'])
lists(
    ['a', 'b', ['1', '2', ['3']]],
    ['a', 'b', ['1', '2', ['3']], 'c', ['d']]
)

reactive_rule(lists(X, Y)).then(
    append(X, Z, Y),
    say(X, Z, Y),
)

goal(append([], X, X)).requires()

goal(append([X | L1], L2, [X | L3])).requires(
    append(L1, L2, L3)
)

execute(debug=False)

show_kb_log()

'''
actions say(_, _, _).
maxTime(5).
lists([], [b]).
lists([a], [b]).

if lists(X, Y) then
custom_append(X, Z, Y) from T1 to T2,
say(X, Z, Y) from T1 to T2.

custom_append([], X, X) from T1 to T2 if true.

custom_append([X|L1], L2, [X|L3]) from T1 to T2 if
custom_append(L1, L2, L3) from T1 to T2.
'''
