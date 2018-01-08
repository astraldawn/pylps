from pylps.core import *

initialise(max_time=2)

create_facts('country(_)', 'colour(_)', 'adjacent(_, _)')
create_actions('paint(_, _)')
create_variables('X', 'Y', 'C')

country('A')
country('B')
country('C')
country('D')

colour('red')
colour('yellow')
colour('blue')

# adjacent('C', 'A')
# adjacent('C', 'B')
# adjacent('A', 'B')
# adjacent('A', 'D')
# adjacent('B', 'D')

reactive_rule(country(X)).then(
    colour(C),
    paint(X, C).frm(T1, T2)
)

execute()

show_kb_log()


'''
maxTime(5).

actions paint(_,_).

country(iz).
country(oz).
country(az).
country(uz).

colour(red).
colour(yellow).
colour(blue).

adjacent(az,iz).
adjacent(az,oz).
adjacent(iz,oz).
adjacent(iz,uz).
adjacent(oz,uz).

if country(X)
then
    colour(C),
    paint(X,C) from T1 to T2.
'''