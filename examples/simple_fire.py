from pylps.core import *  # nopep8

initialise(max_time=2)  # Assume all time variables created here

create_fluents('fire(_)')
create_actions('eliminate', 'escape')
create_events('deal_with_fire')

initially(fire('small'))

reactive_rule(fire('small').at(T1)).then(
    deal_with_fire.frm(T1, T2))

goal(deal_with_fire.frm(T1, T2)).requires(
    eliminate.frm(T1, T2))

eliminate.terminates(fire('small'))

execute()

show_kb_log()

'''
maxTime(5).

fluents     fire(_).
actions     eliminate, escape.
events      put_out_fire, run_from_fire.

initially   fire(small).

if      fire(small) at T1
then    put_out_fire from T1 to T2.

put_out_fire from T1 to T2
if      eliminate from T1 to T2.

eliminate  terminates fire(small).
'''
