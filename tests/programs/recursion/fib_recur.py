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
