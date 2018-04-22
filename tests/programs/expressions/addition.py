from pylps.core import *
from pylps.lps_data_structures import LPSConstant


initialise()

create_actions('show(_, _, _, _, _)')
create_variables('X', 'Y', 'Z', 'Z1', 'Z2', 'Z3', 'Z4')

reactive_rule(True).then(
    X.is_(2),
    Y.is_(3),
    Z.is_(X + Y),
    Z1.is_(X + 5),
    Z2.is_(LPSConstant(7) + Y),
    Z3.is_((Z1 + Z2) + Z),
    Z4.is_((Z1 + Z2) + (Z + (Z3 + 1))),
    show(Z, Z1, Z2, Z3, Z4),
)

execute()

show_kb_log()
