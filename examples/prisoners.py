from pylps.core import *

initialise(max_time=6)

create_fluents('total_years_in_jail(_, _)')
create_actions('refuses(_)', 'bears_witness(_)', 'gets(_, _)')
create_facts('other(_, _)')
create_variables('P', 'Q', 'O', 'I', 'Prisoner', 'Years', 'NewYears',
                 'OldYears',)

initially(total_years_in_jail('me', 0), total_years_in_jail('you', 0),)
observe(refuses('you').frm(1, 2))
# observe(refuses('me').frm(1, 2))
observe(bears_witness('me').frm(1, 2))
# observe(bears_witness('you').frm(1, 2))

other('me', 'you')
other('you', 'me')

reactive_rule(bears_witness(P), refuses(Q)).then(
    gets(P, 0).frm(T2, T3), gets(Q, 3).frm(T2, T3)
)

reactive_rule(bears_witness(P), bears_witness(Q), other(P, Q)).then(
    gets(P, 2).frm(T2, T3)
)

reactive_rule(refuses(P), refuses(Q), other(P, Q)).then(
    gets(P, 1).frm(T2, T3)
)

reactive_rule(refuses(O), other(I, O)).then(
    refuses(I).frm(T2, T3))

reactive_rule(bears_witness(O), other(I, O)).then(
    bears_witness(I).frm(T2, T3))

gets(Prisoner, Years).initiates(total_years_in_jail(Prisoner, NewYears)).iff(
    total_years_in_jail(Prisoner, OldYears), NewYears.is_(OldYears + Years))

gets(Prisoner, Years).terminates(total_years_in_jail(Prisoner, OldYears))

execute(debug=False)

show_kb_log()

'''
maxTime(5).
fluents     total_years_in_jail(_,_).
actions     refuses(_), bears_witness(_), gets(_,_).

initially   total_years_in_jail(me,0),  total_years_in_jail(you,0).
observe     refuses(you) from 1 to 2.
observe     bears_witness(me) from 1 to 2.

other(me,you).
other(you,me).

if      bears_witness(P) from T1 to T2, refuses(Q) from T1 to T2
then    gets(P,0) from T2 to T3,    gets(Q,3) from T2 to T3.

if      bears_witness(P) from T1 to T2, bears_witness(Q) from T1 to T2, other(P,Q)
then    gets(P,2) from T2 to T3.

if      refuses(P) from T1 to T2,  refuses(Q) from T1 to T2, other(P,Q)
then    gets(P,1) from T2 to T3.

if      refuses(O) from T1 to T2, other(I,O)
then    refuses(I) from T2 to T3.

if      bears_witness(O) from T1 to T2, other(I,O)
then    bears_witness(I) from T2 to T3.


gets(Prisoner,Years)    initiates total_years_in_jail(Prisoner,NewYears)
if      total_years_in_jail(Prisoner,OldYears),    NewYears is OldYears+Years.

gets(Prisoner,Years)    terminates total_years_in_jail(Prisoner, OldYears).

/** <examples>
?- go(Timeline).
*/
'''
