from pylps.core import *

initialise(max_time=10)

create_facts('fib(_, _)')
create_fluents('compute(_)')
create_actions('stop_compute(_)', 'say(_)')
create_events('compute_fib(_, _)')
create_variables('X', 'Res', 'Y', 'Z', 'YRes', 'ZRes')

fib(1, 1)
fib(2, 1)

initially(compute(6))
initially(compute(2))

reactive_rule(compute(X)).then(
    stop_compute(X),
    compute_fib(X, Res).frm(T1, T2),
    say(Res)
)

goal(compute_fib(X, Res).frm(T1, T3)).requires(
    X > 2,
    Y.is_(X - 1),
    Z.is_(X - 2),
    compute_fib(Y, YRes).frm(T1, T2),
    compute_fib(Z, ZRes).frm(T2, T3),
    Res.is_(YRes + ZRes),
)

goal(compute_fib(X, Res).frm(T1, T2)).requires(
    fib(X, Res),
)

stop_compute(X).terminates(compute(X))

execute()

show_kb_log()
'''
maxTime(10).
fluents compute(_).
events compute_fib(_, _).
actions stop_compute(_), show(_).

fib(1, 1).
fib(2, 1).

initially compute(8).

if    compute(X)
then stop_compute(X), compute_fib(X, Res) from T1 to T2, show(Res).

compute_fib(X, Res) from T1 to T3 if
    X > 2,
    Y is X - 1,
    Z is X - 2,
    compute_fib(Y, YRes) from T1 to T2,
    compute_fib(Z, ZRes) from T2 to T3,
    Res is (YRes + ZRes).

compute_fib(X, Res) from T to T if fib(X, Res).

stop_compute(X) terminates compute(X).
'''
