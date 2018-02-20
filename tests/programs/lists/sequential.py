'''
actions show(_).

if true
then handle_list([a,b,c,d]) from T1 to T2.

handle_list([Single]) from T1 to T2 if show(Single) from T1 to T2.

handle_list([X|Xs]) from T1 to T3 if
    show(X) from T1 to T2,
    handle_list(Xs) from T2 to T3.

show(a) 1 2
show(b) 2 3
show(c) 3 4
show(d) 4 5
'''
