from pylps.core import *

initialise(max_time=3)

create_actions('say(_, _)', 'ask(_, _)')
create_events('respond(_, _)', 'path(_, _)', 'ask2(_, _)')
create_facts('arc(_, _)')
create_variables('X', 'Y', 'Z')

arc('a', 'b')
arc('b', 'c')
arc('a', 'd')
arc('d', 'e')
arc('a', 'c')

observe(ask('a', 'c').frm(1, 2))
observe(ask2('a', 'e').frm(1, 2))

reactive_rule(ask(X, Y).frm(T1, T2)).then(
    respond(X, Y).frm(T2, T3),
)

reactive_rule(ask2(X, Y).frm(T1, T2)).then(
    respond(X, Y).frm(T2, T3),
)

goal(respond(X, Y).frm(T1, T2)).requires(
    path(X, Y).frm(T1, T1),
    say(X, Y).frm(T1, T2)
)

goal(path(X, Y).frm(T, T)).requires(
    arc(X, Y),
)

goal(path(X, Y).frm(T, T)).requires(
    arc(X, Z),
    path(Z, Y).frm(T, T),
)

execute(debug=False)

show_kb_log()

'''
maxTime(5).

actions     say(_,_), ask2(_, _).
events       ask(_,_).

observe ask(a, c) from 1 to 2.
observe ask2(a, e) from 1 to 2.

arc(a,b).
arc(b,c).
arc(a,d).
arc(d,e).
arc(a,c).

if     ask(X,Y) from  T1 to T2
then     respond(X,Y) from T2 to T3.

if ask2(X,Y) from T1 to T2
then respond(X,Y) from T2 to T3.

respond(X,Y) from T1 to T2
if         path(X,Y), say(X,Y) from T1 to T2.

path(X,Y) :- arc(X,Y).
path(X,Y):- arc(X,Z), path(Z,Y).
'''
