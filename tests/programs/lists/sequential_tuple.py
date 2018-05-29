from pylps.core import *
from pylps.lps_data_structures import LPSTuple

initialise(max_time=5)

create_actions('show(_)', 'show_tuple(_, _)')
create_events('handle_list(_)')
create_variables('X', 'Y', 'XS')

reactive_rule(True).then(
    handle_list([
        ('a', 1),
        ('b', 2),
        ('c', 3),
        ('d', 4),
    ]).frm(T1, T2)
)

goal(handle_list([LPSTuple((X, Y))]).frm(T1, T2)).requires(
    show(X).frm(T1, T2),
    show(Y).frm(T1, T2)
)

goal(handle_list([LPSTuple((X, Y)) | XS]).frm(T1, T3)).requires(
    show_tuple(X, Y).frm(T1, T2),
    handle_list(XS).frm(T2, T3)
)

execute(single_clause=False)

show_kb_log()

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
