from pylps.core import *

initialise(max_time=4)

create_actions('sort(_)', 'say(_)', 'show(_, _, _, _)')
create_variables(
    'X', 'Y', 'Xs', 'Ys', 'Left', 'Right', 'Ls', 'Rs',
    'L1', 'L2', 'L3', 'T6'
)
create_events('quicksort(_, _)', 'split(_, _, _, _)', 'append(_, _, _)')

observe(sort([3, 5, 4, 1, 6, 2]).frm(1, 2))

reactive_rule(sort(X).frm(T1, T2)).then(
    quicksort(X, Y).frm(T2, T3),
    say(Y).frm(T3, T4),
)

goal(append([], X, X)).requires()

goal(append([X | L1], L2, [X | L3])).requires(
    append(L1, L2, L3)
)

goal(quicksort([], []).frm(T1, T1))

goal(quicksort([X | Xs], Ys).frm(T1, T5)).requires(
    split(Xs, X, Left, Right).frm(T2, T3),
    quicksort(Left, Ls).frm(T3, T4),
    quicksort(Right, Rs).frm(T4, T5),
    append(Ls, [X | Rs], Ys)
)

goal(split([], Y, [], []).frm(T1, T1))

goal(split([X | Xs], Y, [X | Ls], Rs).frm(T1, T3)).requires(
    X <= Y,
    split(Xs, Y, Ls, Rs).frm(T2, T3),
)

goal(split([X | Xs], Y, Ls, [X | Rs]).frm(T1, T3)).requires(
    X > Y,
    split(Xs, Y, Ls, Rs).frm(T2, T3),
)

execute(debug=True)

show_kb_log()

'''
maxTime(10).
events  request(_).
actions announce(_).

observe  request(sort([2,1,4,3])) from 1 to 2.

if  request(sort(X)) from T1 to T2
then    quicksort(X, Y) from T2 to T3, announce(Y) from T3 to T4.

quicksort([], []) from T1 to T1.

quicksort([X|Xs], Ys) from T1 to T5 if
    split(Xs, X, Left, Right) from T2 to T3,
    quicksort(Left, Ls) from T3 to T4,
    quicksort(Right, Rs) from T4 to T5,
    append(Ls, [X|Rs], Ys).


split([], Y, [], []) from T1 to T1.

split([X|Xs], Y, [X|Ls], Rs) from T1 to T3 if
    X @=< Y, split(Xs, Y, Ls, Rs) from T2 to T3.

split([X|Xs], Y, Ls, [X|Rs]) from T1 to T3 if
    X @> Y, split(Xs, Y, Ls, Rs) from T2 to T3.



/*
quicksort([X|Xs],Ys) :-
    partition(Xs,X,Left,Right),
    quicksort(Left,Ls),
    quicksort(Right,Rs),
    append(Ls,[X|Rs],Ys). % for XSB use instead basics:append(Ls,[X|Rs],Ys)

quicksort([],[]).


partition([X|Xs],Y,[X|Ls],Rs) :-
    X =< Y, partition(Xs,Y,Ls,Rs).

partition([X|Xs],Y,Ls,[X|Rs]) :-
    X > Y, partition(Xs,Y,Ls,Rs).

partition([],Y,[],[]).
*/
'''
