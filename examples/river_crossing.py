from pylps.core import *

initialise(max_time=10)

create_actions('show(_)', 'valid(_)', 'say(_, _)')
create_events('river(_, _, _, _)', 'member(_, _)')
create_facts('inp(_, _)', 'crossing(_, _, _)')
create_variables(
    'A', 'B', 'C', 'P', 'V', 'X', 'Y', 'Z', 'Tail',
    'Action', 'Start', 'End', 'Plan',
)

inp(['l', 'l', 'l', 'l'], ['r', 'r', 'r', 'r'])
# inp(['l', 'l', 'l', 'l'], ['r', 'l', 'l', 'l'])
# inp(['l', 'l', 'l', 'l'], ['r', 'l', 'r', 'l'])

crossing(['l', X, Y, Z], ['r', X, Y, Z], 'farmer_cross')
crossing(['r', X, Y, Z], ['l', X, Y, Z], 'farmer_back')

crossing(['l', 'l', Y, Z], ['r', 'r', Y, Z], 'fox_cross')
crossing(['r', 'r', Y, Z], ['l', 'l', Y, Z], 'fox_back')

crossing(['l', X, 'l', Z], ['r', X, 'r', Z], 'goose_cross')
crossing(['r', X, 'r', Z], ['l', X, 'l', Z], 'goose_back')

crossing(['l', X, Y, 'l'], ['r', X, Y, 'r'], 'beans_cross')
crossing(['r', X, Y, 'r'], ['l', X, Y, 'l'], 'beans_back')

reactive_rule(inp(Start, End)).then(
    river(Start, End, [Start], P).frm(T1, T2),
    show(P).frm(T2, T3),
)

goal(river(A, A, _, []).frm(T, T))

goal(river(A, B, V, P).frm(T1, T3)).requires(
    crossing(A, C, Action),
    C.not_in(V),
    valid(C).frm(T1, T2),
    say(Action, C).frm(T1, T2),
    river(C, B, [C | V], Plan).frm(T2, T3),
    P.is_([Action | Plan]),
)

false_if(valid([A, B, B, C]), A != B)
false_if(valid([A, C, B, B]), A != B)
# false_if(valid(X), valid(Y), X != Y)

execute(debug=False, strategy=STRATEGY_GREEDY)

show_kb_log()

'''
% The ability to give a solution depends on the ordering of the facts,
% if attempting to only perform 1 move per time step

% If last constraint is removed, both solutions are produced

maxTime(10).

actions say(_, _), say_1(_, _), valid(_), show(_).

input([l, l, l, l], [r, r, r, r]).

crossing([l, X, Y, Z], [r, X, Y, Z], farmer_cross).
crossing([r, X, Y, Z], [l, X, Y, Z], farmer_back).

crossing([l, l, Y, Z], [r, r, Y, Z], fox_cross).
crossing([r, r, Y, Z], [l, l, Y, Z], fox_back).

crossing([l, Y, l, Z], [r, Y, r, Z], goose_cross).
crossing([r, Y, r, Z], [l, Y, l, Z], goose_back).

crossing([l, Y, Z, l], [r, Y, Z, r], beans_cross).
crossing([r, Y, Z, r], [l, Y, Z, l], beans_back).

if input(Start, End) then
    river(Start, End, [Start], P) from T1 to T2,
    show(P).

river(A,A,_,[]) from T to T.

river(A, B, V, P) from T1 to T3 if
    crossing(A, C, Action),
    \+ member(C, V),
    valid(C) from T1 to T2,
    say(Action, C) from T1 to T2,
    river(C, B, [C|V], Plan) from T2 to T3,
    P = [Action | Plan].

false valid([A, B, B, C]), A \= B.
false valid([A, C, B, B]), A \= B.
false valid(X), valid(Y), X \= Y.
'''
