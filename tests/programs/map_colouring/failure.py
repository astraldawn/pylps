from pylps.core import *

initialise(max_time=3)

create_facts('country(_)', 'colour(_)', 'adjacent(_, _)')
create_actions('paint(_, _)')
create_variables('X', 'Y', 'C')

country('A')
country('B')
country('C')
country('D')

colour('red')
colour('yellow')

adjacent('C', 'A')
adjacent('C', 'B')
adjacent('A', 'B')
adjacent('A', 'D')
adjacent('B', 'D')

reactive_rule(country(X)).then(
    colour(C),
    paint(X, C).frm(T1, T2)
)

false_if(
    paint(X, C),
    adjacent(X, Y),
    adjacent(Y, X),
    paint(Y, C)
)

execute()

show_kb_log()
