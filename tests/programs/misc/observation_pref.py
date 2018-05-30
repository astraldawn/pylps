from pylps.core import *

initialise(max_time=5)

create_actions('say(_)')
create_fluents('f')
create_variables('A', 'B')

observe(say('a').frm(1, 2))

initially(f)

reactive_rule(f.at(T1)).then(
    say('b').frm(T2, T3)
)

say(A).terminates(f)

false_if(say(A), say(B), A != B)

execute(debug=False)

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
