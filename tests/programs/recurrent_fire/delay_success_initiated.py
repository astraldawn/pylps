from pylps.core import *


initialise(max_time=10)  # Assume all time variables created here

create_fluents('fire', 'water', 'p')
create_actions('eliminate', 'escape', 'refill', 'ignite(_)',
               'delay', 'delay_more')
create_events('deal_with_fire')
create_variables('X')
create_facts('flammable(_)')

observe(ignite('sofa').frm(1, 2))
observe(ignite('bed').frm(4, 5))
observe(refill.frm(7, 8))

initially(water)

flammable('sofa')
flammable('bed')

reactive_rule(fire.at(T1)).then(
    deal_with_fire.frm(T2, T3))

goal(deal_with_fire.frm(T1, T2)).requires(
    eliminate.frm(T1, T2),
    delay.frm(T1, T2),
    delay_more.frm(T1, T2))

ignite(X).initiates(fire).iff(flammable(X))

eliminate.terminates(fire)
eliminate.terminates(water)
eliminate.initiates(p)
refill.initiates(water)

false_if(eliminate, fire, ~water)
false_if(delay, p)

execute(debug=False)
show_kb_log()


'''
maxTime(10).
fluents     fire, water, p.
actions eliminate, ignite(_), escape, refill, delay, delay_more.

observe     ignite(sofa) from 1 to 2.
observe     ignite(bed) from 4 to 5.
observe     refill from 7 to 8.

initially   water.

flammable(sofa).
flammable(bed).


if    fire at T1
then deal_with_fire from T2 to T3.

deal_with_fire  from T1 to T2
if  eliminate from T1 to T2, delay from T1 to T2, delay_more from T1 to T2.

ignite(Object)  initiates   fire  if    flammable(Object).

eliminate terminates fire.
eliminate terminates water.
eliminate initiates p.
refill initiates water.

false   eliminate, fire, not water.
false   delay, p.
'''
