from pylps.core import *

initialise(max_time=10)

create_fluents('locked(_)', 'trash(_)', 'bin1(_)')
create_actions('dispose(_, _)', 'unlock(_)')
create_variables('Object', 'Container')

initially(
    locked('container1'), trash('bottle1'),
    bin1('container1'), bin1('container2')
)

observe(unlock('container1').frm(4, 5))

reactive_rule(trash(Object).at(T1)).then(
    bin1(Container).at(T1),
    dispose(Object, Container).frm(T2, T3),
)

unlock(Container).terminates(locked(Container))
dispose(Object, Container).terminates(trash(Object))

false_if(dispose(Object, Container), locked(Container))

execute()

show_kb_log()

'''
maxTime(10).
fluents locked(_), trash(_), bin(_).
actions dispose(_,_).
events unlock(_).

initially  locked(container1), trash(bottle1),
bin(container1), bin(container2).
observe     unlock(container1) from 4 to 5.


if trash(Object) at T1
then  bin(Container) at T1,
        dispose(Object, Container) from T2 to _T3, T1 =<T2.

unlock(Container) terminates locked(Container).
dispose(Object, _Container) terminates  trash(Object).

false  dispose(_Object, Container), locked(Container).
'''
