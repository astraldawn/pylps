initialise(max_time=10, create_variables=False)


create_actions(
    'eliminate', 'escape',
    'refill', 'ignite(_)'
)
create_fluents('fire', 'water')
create_facts('flammable(_)')
create_events('deal_with_fire')

observe(ignite('sofa').frm(1, 2))
observe(ignite('sofa').frm(4, 5))
observe(refill.frm(7, 8))

initially(water)

flammable('sofa')
flammable('bed')

reactive_rule(fire.at(T1)).then(
    deal_with_fire.frm(T2, T3))

goal(deal_with_fire.frm(T1, T2)).requires(
    eliminate.frm(T1, T2))

goal(deal_with_fire.frm(T1, T2)).requires(
    escape.frm(T1, T2))

ignite(X).initiates(fire).iff(flammable(X))

eliminate.terminates(fire)
eliminate.terminates(water)
refill.initiates(water)

false_if(eliminate, fire, ~water)
