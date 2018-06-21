from pylps.core import *

initialise(max_time=2)

create_facts('country(_)', 'colour(_)', 'adjacent(_, _)')
create_actions('paint(_, _)')
create_variables('X', 'Y', 'C')

country('A')
country('B')
country('C')
country('D')

# colour('red')
colour('yellow')

adjacent('C', 'A')
adjacent('B', 'A')
adjacent('D', 'A')

reactive_rule(country(X)).then(
    colour(C),
    paint(X, C).frm(T1, T2)
)

false_if(
    paint(X, C),
    adjacent(X, Y),
    paint(Y, C)
)

execute()

show_kb_log()
