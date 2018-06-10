from pylps.core import *

initialise(max_time=5)

create_actions('say(_)', 'say2(_)')
create_fluents('f', 'g')
create_variables('A', 'B')

initially(f)
initially(g)

reactive_rule(f.at(T1)).then(
    say('a').frm(T2, T3),
    say2('b').frm(T2, T3)
)

say(A).terminates(f)
say2(A).terminates(g)

false_if(~f, ~g)

execute(debug=False)

show_kb_log()

'''
actions say(_).
fluents f, g.

initially f.
initially g.

if f at T1 then say(a) from T2 to T3, say(b) from T2 to T3.

say(a) terminates f.
say(b) terminates g.

false not f, not g.
'''
