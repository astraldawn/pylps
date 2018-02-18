import inspect
from pylps.core import *


def simple_fire():
    initialise(max_time=5)  # Assume all time variables created here

    create_fluents('fire')
    create_actions('eliminate', 'escape')
    create_events('deal_with_fire')

    frame = inspect.currentframe()

    print(frame)

    initially(fire)

    reactive_rule(fire.at(T1)).then(
        deal_with_fire.frm(T1, T2))

    goal(deal_with_fire.frm(T1, T2)).requires(
        eliminate.frm(T1, T2))

    goal(deal_with_fire.frm(T1, T2)).requires(
        escape.frm(T1, T2))

    eliminate.terminates(fire)

    execute()

    frame = inspect.currentframe()

    print(frame)

    show_kb_log()


def simple_fire_2():
    initialise(max_time=5)  # Assume all time variables created here

    # create_fluents('fire')
    # create_actions('eliminate', 'escape')
    # create_events('deal_with_fire')

    initially(fire)

    reactive_rule(fire.at(T1)).then(
        deal_with_fire.frm(T1, T2))

    goal(deal_with_fire.frm(T1, T2)).requires(
        eliminate.frm(T1, T2))

    goal(deal_with_fire.frm(T1, T2)).requires(
        escape.frm(T1, T2))

    eliminate.terminates(fire)

    execute()

    show_kb_log()


simple_fire()

simple_fire_2()

print(inspect.getouterframes(inspect.currentframe()))

'''
maxTime(10).
fluents     fire, water.
actions eliminate, ignite(_), escape, refill.

observe     ignite(sofa) from 1 to 2.
observe     ignite(bed) from 4 to 5.
observe     refill from 7 to 8.

initially   water.

flammable(sofa).
flammable(bed).


if    fire at T1
then deal_with_fire from T2 to T3.

deal_with_fire  from T1 to T2
if  eliminate from T1 to T2.

deal_with_fire  from T1 to T2
if  escape from T1 to T2.

ignite(Object)  initiates   fire  if    flammable(Object).

eliminate terminates fire.
eliminate terminates water.
refill initiates water.

false   eliminate, fire, not water.
'''
