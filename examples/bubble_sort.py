from pylps.core import *

initialise(max_time=1)

create_fluents('location(_, _)')
create_actions('swap(_, _, _, _)')
create_events('swapped(_, _, _, _)')
create_variables('X', 'Y', 'N1', 'N2')

initially(
    location('d', 1), location('c', 2), location('b', 3), location('a', 4),
)

reactive_rule(
    location(X, N1).at(T1),
    N2.is_(N1 + 1),
    location(Y, N2).at(T1),
    Y < X,
).then(
    swapped(X, N1, Y, N2)
)

execute(debug=True)

show_kb_log()

'''
maxTime(5).
fluents location(_, _).
actions swap(_,_,_,_).

initially   location(d, 1), location(c, 2), location(b, 3),  location(a,4).

if  location(X, N1) at T1, N2 is N1 +1,  location(Y, N2) at T1,  Y@<X
then    swapped(X, N1, Y, N2) from T2 to T3.

% swapped does not work if the order of the two clauses below is
% reversed. Perhaps for good reasons,
% namely in the hope that positions will become swapped in the future
% without the need to swap them explicitly.

swapped(X, N1, Y, N2) from T1 to T2
if  location(X, N1) at T1, location(Y, N2) at T1,
    Y@<X, swap(X, N1, Y, N2) from T1 to T2.

swapped(X, N1, Y, N2) from T to T
if  location(X, N1) at T, location(Y, N2) at T, X@<Y.

swap(X, N1, Y, N2)      initiates   location(X, N2).
swap(X, N1, Y, N2)      initiates   location(Y, N1).

swap(X, N1, Y, N2)      terminates  location(X, N1).
swap(X, N1, Y, N2)      terminates  location(Y, N2).

false   swap(X, N1, Y, N2), swap(Y, N2, Z, N3).
'''