from pylps.core import *

initialise(max_time=5)

create_fluents('total_years_in_jail(_, _)')
create_actions('sort(_)', 'say(_)')
create_variables('X', 'Y')

observe(sort(['1', '2', '3', '4']).frm(1, 2))


def python_sort(iterable):
    return sorted(iterable)


reactive_rule(sort(X)).then(
    Y.is_(python_sort(X)),
    say(Y).frm(T2, T3),
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
