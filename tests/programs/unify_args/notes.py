from pylps.core import *

initialise(max_time=10)

create_actions('say(_)')
create_events('respond(_, _)')
create_facts('arc(_, _)', 'ask(_, _)')
create_variables('X', 'Y', 'Z')

# observe(ask('a', 'b').frm(1, 2))
# observe(ask('a', 'e').frm(4, 5))

arc('a', 'b')
arc('b', 'c')
arc('a', 'd')
arc('d', 'c')
arc('e', 'c')

ask('a', 'b')

reactive_rule(ask(X, Y)).then(
    respond(X, Y).frm(T1, T2))

goal(respond(X, Y).frm(T1, T2)).requires(
    arc(X, Y), say(X).frm(T1, T2))

execute()

# goal(respond(X, Y).frm(T1, T2)).requires(
#     arc(X, Z), respond(Z, Y).frm(T1, T2), say('yes').frm(T1, T2))


'''
# MAP COLOURING

from pylps.core import *

initialise(max_time=10)

create_actions('say(_)', 'ask(_, _)')
create_facts('arc(_, _)')

observe(ask(a, c).frm(1, 2))
observe(ask(a, e).frm(4, 5))

arc('a', 'b')
arc('b', 'c')
arc('a', 'd')
arc('d', 'c')
arc('e', 'c')

reactive_rule(ask(X, Y)).then(
    respond(X, Y).frm(T1, T2))

goal(respond(X, Y).frm(T1, T2)).requires(
    arc(X, Y), say('yes').frm(T1, T2))

goal(respond(X, Y).frm(T1, T2)).requires(
    arc(X, Z), respond(Z, Y).frm(T1, T2), say('yes').frm(T1, T2))


actions say(_), ask(_, _).

observe ask(a, e) from 4 to 5.
observe ask(a, c) from 1 to 2.

arc(a, b).
arc(b, c).
arc(a, d).
arc(d, c).
arc(e, c).

if ask(X, Y) then respond(X, Y) from T1 to T2.

respond(X, Y) from T1 to T2 if arc(X, Y), say(yes) from T1 to T2.
respond(X, Y) from T1 to T2 if arc(X, Z), respond(Z, Y) from T1 to T2, say(yes) from T1 to T2.

create_facts('country(_)', 'colour(_)', 'adjacent(_, _)')
create_fluents('painted(_,_)')
create_actions('paint(_, _)')
create_variables('X', 'Y', 'C')

country('A')
country('B')
country('C')
country('D')

colour('red')
colour('yellow')
colour('blue')

adjacent('C', 'A')
adjacent('C', 'B')
adjacent('A', 'B')
adjacent('A', 'D')
adjacent('B', 'D')

reactive_rule(country(X)).then(
    colour(C),
    paint(X, C).frm(T1, T2)
)

paint(X, C).initiates(painted(X, C))

false_if(paint(X, C), adjacent(X, Y), paint(Y, C))

# uncomment the lines below to solve the problem stepwise
# false_if(paint(X, _), paint(Y, _), X != Y)
# false_if(painted(X, C), adjacent(X, Y), painted(Y, C))

execute()

show_kb_log()
'''
