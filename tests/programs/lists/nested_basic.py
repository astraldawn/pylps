from pylps.core import *

initialise(max_time=5)

create_actions('say(_)', 'say_single(_)')
create_events('respond(_)')
create_facts('ask(_)')
create_variables('X', 'Y', 'Rest')

ask([])
ask(['a'])
ask(['b', 'c'])
ask(['d', 'e', 'f', 'g', 'h'])

reactive_rule(ask(X)).then(
    respond(X).frm(T1, T2))

# Match empty
goal(respond([]).frm(T1, T2)).requires(
    say('empty list').frm(T1, T2),
)

# Match single element
goal(respond([X]).frm(T1, T2)).requires(
    say_single(X).frm(T1, T2),
)

# Match multiple elements
goal(respond([X | [Y | Rest]]).frm(T1, T2)).requires(
    say(X).frm(T1, T2),
    say(Y).frm(T1, T2),
    say(Rest).frm(T1, T2),
)

execute(single_clause=False, debug=True)

show_kb_log()
