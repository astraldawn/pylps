from pylps.core import *

initialise(max_time=10)

create_fluents('available(_)')
create_actions('pickup(_, _)', 'putdown(_, _)')
create_variables('P', 'P1', 'P2', 'F', 'F1', 'F2')
create_facts('philosopher(_)', 'adjacent(_, _, _)')
create_events('dine(_)')

initially(
    available('fork1'), available('fork2'), available('fork3'),
    available('fork4'), available('fork5'),
)

philosopher('socrates')
philosopher('plato')
philosopher('aristotle')
philosopher('hume')
philosopher('kant')

adjacent('fork1', 'socrates', 'fork2')
adjacent('fork2', 'plato', 'fork3')
adjacent('fork3', 'aristotle', 'fork4')
adjacent('fork4', 'hume', 'fork5')
adjacent('fork5', 'kant', 'fork1')

reactive_rule(philosopher(P)).then(
    dine(P).frm(T1, T2),
)

goal(dine(P).frm(T1, T3)).requires(
    adjacent(F1, P, F2),
    pickup(P, F1).frm(T1, T2),
    pickup(P, F2).frm(T1, T2),
    putdown(P, F1).frm(T2, T3),
    putdown(P, F2).frm(T2, T3),
)

pickup(P, F).terminates(available(F))
putdown(P, F).initiates(available(F))

false_if(pickup(P, F), ~available(F), )
false_if(pickup(P1, F), pickup(P2, F), P1 != P2,)

execute(debug=True, solution_preference=SOLN_PREF_MAX)

show_kb_log()

'''
maxTime(7).
fluents     available(_).
actions     pickup(_,_), putdown(_,_).

initially   available(fork1),
        available(fork2),
        available(fork3),
        available(fork4),
        available(fork5).

philosopher(socrates).
philosopher(plato).
philosopher(aristotle).
philosopher(hume).
philosopher(kant).

adjacent(fork1, socrates, fork2).
adjacent(fork2, plato, fork3).
adjacent(fork3, aristotle, fork4).
adjacent(fork4, hume, fork5).
adjacent(fork5, kant, fork1).

if      philosopher(P)
then        dine(P) from T1 to T2.

dine(P) from T1 to T3   if
    adjacent(F1, P, F2),
    pickup(P, F1) from T1 to T2,
    pickup(P, F2) from T1 to T2,
    putdown(P, F1) from T2 to T3,
    putdown(P, F2) from T2 to T3 .

pickup(P, F)    terminates  available(F).
putdown(P, F)   initiates   available(F).

false   pickup(P, F),    not available(F).
false   pickup(P1, F),  pickup(P2, F), P1 \= P2.
'''
