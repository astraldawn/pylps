from pylps.core import *

initialise(max_time=3)

create_actions('say(_)', 'respond(_)')
create_variables('X')

observe(say('a').frm(1, 2))

reactive_rule(say(X).frm(T1, T2)).then(
    respond(X).frm(T2, T3)
)

execute(debug=False)

show_kb_log()
