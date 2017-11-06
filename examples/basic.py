import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from pylps.core import *  # nopep8


initialise(max_time=5)  # Assume all time variables created here

create_fluents('fire')
create_actions('eliminate', 'escape')
create_events('deal_with_fire')

initially(fire)

reactive_rule(fire.at(T1)).then(deal_with_fire.frm(T1, T2))

# print(reactive_rule(fire.at(T1)))

goal(deal_with_fire.frm(T1, T2)).requires(eliminate.frm(T1, T2))

# goal(deal_with_fire.frm(T1, T2)).requires(escape.frm(T1, T2))

eliminate.terminates(fire)

show_reactive_rules()

execute()


'''
maxTime(5).

fluents     fire.
actions     eliminate, escape.
events      deal_with_fire.

initially   fire.

if      fire at T1
then    deal_with_fire from T1 to T2.

deal_with_fire from T1 to T2
if      eliminate from T1 to T2.

deal_with_fire from T1 to T2
if       escape from T1 to T2.

eliminate  terminates fire.
'''
