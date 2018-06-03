'''
Iterative fibonacci
'''
from pylps.core import *

initialise(max_time=10)

create_facts('fib(_, _, _)')
create_fluents('compute(_)')
create_actions('stop_compute(_)', 'say(_)')
create_events('compute_fib(_, _, _)')
create_variables('X', 'Res', 'Res1', 'Y', 'YRes', 'YRes1')

fib(1, 1, 0)
fib(2, 1, 1)

initially(compute(15))

reactive_rule(compute(X)).then(
    stop_compute(X),
    compute_fib(X, Res, Res1).frm(T1, T2),
    say(Res)
)

goal(compute_fib(X, Res, Res1).frm(T1, T2)).requires(
    X > 2,
    Y.is_(X - 1),
    compute_fib(Y, Res1, YRes1).frm(T1, T2),
    Res.is_(Res1 + YRes1),
)

goal(compute_fib(X, Res, Res1).frm(T1, T2)).requires(
    fib(X, Res, Res1),
)

stop_compute(X).terminates(compute(X))

execute()

show_kb_log()

'''
maxTime(10).
fluents compute(_).
events compute_fib(_, _, _).
actions stop_compute(_), show(_).

fib(1, 1, 0).
fib(2, 1, 1).

initially compute(30).

if    compute(X)
then stop_compute(X), compute_fib(X, Res, Res1) from T1 to T2, show(Res).

compute_fib(X, Res, Res1) from T1 to T2 if
    X > 2,
    Y is X - 1,
    compute_fib(Y, Res1, YRes1) from T1 to T2,
    Res is (Res1 + YRes1).

compute_fib(X, Res, Res1) from T1 to T2 if fib(X, Res, Res1).

stop_compute(X) terminates compute(X).
'''
