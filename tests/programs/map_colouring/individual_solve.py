from pylps.core import *

initialise(max_time=10)

create_facts('country(_)', 'colour(_)', 'adjacent(_, _)')
create_fluents('painted(_,_)')
create_actions('paint(_, _)')
create_variables('X', 'Y', 'C')

country('A')
country('B')
country('C')
country('D')

colour('red')
colour('yellow')
colour('blue')

adjacent('C', 'A')
adjacent('C', 'B')
adjacent('A', 'B')
adjacent('A', 'D')
adjacent('B', 'D')

reactive_rule(country(X)).then(
    colour(C),
    paint(X, C).frm(T1, T2)
)

paint(X, C).initiates(painted(X, C))

false_if(paint(X, C), adjacent(X, Y), paint(Y, C))
false_if(paint(X, _), paint(Y, _), X != Y)
false_if(painted(X, C), adjacent(X, Y), painted(Y, C))

execute(debug=True)

show_kb_log()

'''
maxTime(5).

fluents painted(_,_).
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
then colour(C), paint(X,C) from T1 to T2.

paint(X,C) initiates painted(X,C).

false paint(X,C), adjacent(X,Y), paint(Y,C).
false painted(X,C), adjacent(X,Y), painted(Y,C).
false paint(X,_), paint(Y,_), X\=Y.
'''
