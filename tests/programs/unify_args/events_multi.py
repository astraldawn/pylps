from pylps.core import *

initialise(max_time=5)

create_actions('say(_, _)')
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

ask('a', 'c')

reactive_rule(ask(X, Y)).then(
    respond(X, Y).frm(T1, T2))

goal(respond(X, Y).frm(T1, T2)).requires(
    arc(X, Y), say(X, Y).frm(T1, T2))

goal(respond(X, Y).frm(T1, T3)).requires(
    arc(X, Z),
    respond(Z, Y).frm(T1, T2),
    say(X, Z).frm(T2, T3))

execute(single_clause=False, debug=True, n_solutions=10)

show_kb_log()

'''
actions say(_, _).

arc(a, b).
arc(b, c).
arc(a, d).
arc(d, c).
arc(e, c).

ask(a, c).

if ask(X, Y) then respond(X, Y) from T1 to T2.

respond(X, Y) from T1 to T2 if arc(X, Y), say(X, Y) from T1 to T2.
respond(X, Y) from T1 to T3 if
    arc(X, Z),
    respond(Z, Y) from T1 to T2,
    say(X, Z) from T2 to T3.

1 - 2: say(b, c), say(d, c)
2 - 3: say(a, b), say(a, d)
'''
