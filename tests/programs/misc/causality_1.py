from pylps.core import *

initialise(max_time=2)

create_fluents('test(_, _)')
create_actions('hello(_, _)')
create_variables('Person', 'Years', 'NewYears', 'OldYears',)


initially(test('A', 0),)

reactive_rule(True).then(
    hello('A', 5),
)

hello(Person, Years).initiates(test(Person, NewYears)).iff(
    test(Person, OldYears), NewYears.is_(OldYears + Years)
)

hello(Person, Years).terminates(test(Person, OldYears))

execute(debug=False)

show_kb_log()
