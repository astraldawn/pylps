from pylps.core import *
from pylps.visualiser import PylpsVisualiserApp
from pylps.vis_object import PylpsVisObject, pylps_vis_meta
from kivy.uix.label import Label

initialise(max_time=10)

create_fluents('location(_, _)')
create_actions('swap(_, _, _, _)')
create_events('swapped(_, _, _, _)')
create_variables('X', 'Y', 'Z', 'N1', 'N2', 'N3')

initially(
    location('d', 1), location('c', 2), location('b', 3), location('a', 4),
)

reactive_rule(
    location(X, N1).at(T1),
    N2.is_(N1 + 1),
    location(Y, N2).at(T1),
    Y < X,
).then(
    swapped(X, N1, Y, N2),
)

goal(swapped(X, N1, Y, N2)).requires(
    location(X, N1).at(T1),
    location(Y, N2).at(T1),
    Y < X,
    swap(X, N1, Y, N2),
)

goal(swapped(X, N1, Y, N2)).requires(
    location(X, N1).at(T1),
    location(Y, N2).at(T1),
    X < Y,
)

swap(X, N1, Y, N2).initiates(location(X, N2))
swap(X, N1, Y, N2).terminates(location(X, N1))
swap(X, N1, Y, N2).initiates(location(Y, N1))
swap(X, N1, Y, N2).terminates(location(Y, N2))

false_if(swap(X, N1, Y, N2), swap(Y, N2, Z, N3),)

execute()

display_log = kb_display_log()


# class location(object, metaclass=pylps_vis_meta):
# class LocationDisplay(PylpsVisObject):
class LocationDisplay():
    def __init__(self, *args):
        self.value = args[0]
        self.pos = args[1]
        self.x = -250 + self.pos * 100
        self.y = 0

    def get_widget(self):
        w = Label(
            text=self.value,
            pos=(self.x, self.y)
        )
        return w


class SwapDisplay():
    def __init__(self, *args):
        self.pos1 = args[1]
        self.pos2 = args[3]
        self.x = -200 + self.pos1 * 100
        self.y = 20

    def get_widget(self):
        w = Label(
            text="<--- SWAPPED --->",
            pos=(self.x, self.y)
        )
        return w


display_classes = {
    'location': LocationDisplay,
    'swap': SwapDisplay
}

app = PylpsVisualiserApp(display_log, display_classes)
app.run()
