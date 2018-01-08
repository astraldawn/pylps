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

reactive_rule(country(X)).then(
    colour(C),
    paint(X, C).frm(T1, T2)
)

execute()

# show_kb_rules()

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

if country(X)
then
    colour(C),
    paint(X,C) from T1 to T2.
'''
