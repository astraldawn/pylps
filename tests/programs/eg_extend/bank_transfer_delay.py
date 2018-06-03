from pylps.core import *

initialise(max_time=10)

create_fluents('balance(_, _)')
create_actions('transfer(_, _, _)')
create_variables(
    'A', 'F', 'T', 'X', 'New', 'Old',
    'From', 'From1', 'From2', 'To', 'To1', 'To2',
    'Amount', 'Amount1', 'Amount2',
)

initially(balance('bob', 0), balance('fariba', 100),)
observe(transfer('fariba', 'bob', 10).frm(1, 2))

reactive_rule(
    transfer('fariba', 'bob', X),
    T3.is_(T2 + 2),
    balance('bob', A).at(T3),
    A >= 10,
).then(transfer('bob', 'fariba', 10).frm(T3, T4))

reactive_rule(
    transfer('bob', 'fariba', X),
    T3.is_(T2 + 2),
    balance('fariba', A).at(T3),
    A >= 20,
).then(transfer('fariba', 'bob', 20).frm(T3, T4))

transfer(F, T, A).initiates(balance(T, New)).iff(
    balance(T, Old), New.is_(Old + A))
transfer(F, T, A).initiates(balance(F, New)).iff(
    balance(F, Old), New.is_(Old - A))
transfer(F, T, A).terminates(balance(T, Old))
transfer(F, T, A).terminates(balance(F, Old))

false_if(transfer(From, To, Amount), balance(From, Old), Old < Amount)
false_if(transfer(From, To1, Amount1), transfer(From, To2, Amount2),
         To1 != To2)
false_if(transfer(From1, To, Amount1), transfer(From2, To, Amount2),
         From1 != From2)

execute(debug=False)

show_kb_log()

'''
maxTime(10).
actions     transfer(From, To, Amount).
fluents     balance(Person, Amount).

initially   balance(bob, 0), balance(fariba, 100).
observe     transfer(fariba, bob, 10)   from 1 to 2.

if      transfer(fariba, bob, X)    from  T1 to T2,
        T3 is T2+5,
        balance(bob, A) at T3, A >= 10
then    transfer(bob, fariba, 10)   from T3 to T4.

if      transfer(bob, fariba, X)    from  T1 to T2,
        T3 is T2+5,
        balance(fariba, A) at T3, A >= 20
then    transfer(fariba, bob, 20)   from  T3 to T4.

transfer(F,T,A) updates Old to New in balance(T, Old) if New is Old + A.
transfer(F,T,A) updates Old to New in balance(F, Old) if New is Old - A.

false   transfer(From, To, Amount), balance(From, Old),  Old < Amount.
false   transfer(From, To1, Amount1), transfer(From, To2, Amount2),  To1 \=To2.
false   transfer(From1, To, Amount1), transfer(From2, To, Amount2),  From1 \= From2.
'''
