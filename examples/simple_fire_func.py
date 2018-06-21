from pylps.core import *


def run_pylps_program():

    initialise(max_time=5, create_vars=False)

    fire = create_fluents('fire', return_obj=True)
    eliminate, escape = create_actions('eliminate', 'escape', return_obj=True)
    deal_with_fire = create_events('deal_with_fire', return_obj=True)
    T1, T2 = create_variables('T1', 'T2', return_obj=True)

    initially(fire)

    reactive_rule(fire.at(T1)).then(
        deal_with_fire.frm(T1, T2))

    goal(deal_with_fire.frm(T1, T2)).requires(
        eliminate.frm(T1, T2))

    eliminate.terminates(fire)

    execute()
    show_kb_log()


run_pylps_program()
