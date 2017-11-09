from pylps.core import *  # nopep8

initialise(max_time=5)  # Assume all time variables created here

create_fluents('fire(_)')
create_actions('eliminate', 'escape')
create_events('deal_with_fire')

initially(fire('small'))

reactive_rule(fire('small').at(T1)).then(
    deal_with_fire.frm(T1, T2))

goal(deal_with_fire.frm(T1, T2)).requires(eliminate.frm(T1, T2))

eliminate.terminates(fire('small'))

show_kb_rules()
show_kb_fluents()

# execute()

'''
maxTime(5).

fluents     fire(_).
actions     eliminate, escape.
events      put_out_fire, run_from_fire.

initially   fire(big).

if      fire(small) at T1
then    put_out_fire from T1 to T2.

if      fire(big) at T1
then    run_from_fire from T1 to T2.

put_out_fire from T1 to T2
if      eliminate from T1 to T2.

run_from_fire from T1 to T2
if       escape from T1 to T2.

eliminate  terminates fire(small).
'''
