from pylps.core import *

initialise(max_time=3)

create_actions('say(_)', 'respond(_)')
create_variables('X')

observe(say('a').frm(1, 2))

reactive_rule(say(X).frm(T1, T2)).then(
    respond(X).frm(T2, T3)
)

execute(debug=True)

show_kb_log()

'''
actions say(_).
fluents f.

observe say(a) from 1 to 2.

initially f.

if f at T1 then say(b) from T2 to T3.

say(A) terminates f.

false say(A), say(B), A \= B.

1,2 - say(A)
2,3 - say(B)??
'''
