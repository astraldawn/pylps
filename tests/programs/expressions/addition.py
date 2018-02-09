from pylps.core import *

initialise()

reactive_rule(True).then(
)
'''
actions show(_).

if true then
    X is 2,
    Y is 3,
    Z is X + Y,
    show(Z),
    Z1 is X + 5,
    show(Z1),
    Z2 is 7 + Y,
    show(Z2).
'''
