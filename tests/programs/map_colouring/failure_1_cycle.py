from pylps.core import *

initialise(max_time=2)

create_facts('node(_)', 'colour(_)', 'adjacent(_, _)')
create_actions('paint(_, _)')
create_variables('X', 'Y', 'C')

node('A')
node('B')
node('C')
node('D')
node('E')

colour('red')
colour('yellow')
# colour('blue')

adjacent('A', 'B')
adjacent('A', 'C')
adjacent('A', 'D')
adjacent('A', 'E')
adjacent('B', 'C')
adjacent('B', 'E')

reactive_rule(node(X)).then(
    colour(C),
    paint(X, C).frm(T1, T2)
)

false_if(
    paint(X, C),
    adjacent(X, Y),
    paint(Y, C)
)

execute(strategy=STRATEGY_DEFAULT, solution_preference=SOLN_PREF_MAX)
show_kb_log()

execute(strategy=STRATEGY_GREEDY_FAST)
show_kb_log()
