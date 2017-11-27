'''
Tuple based unification engine
Referened from: https://github.com/aimacode/aima-python/blob/master/logic.py
'''
from unification import *

from pylps.constants import *
from pylps.logic_objects import TemporalVar
from pylps.kb import KB
from pylps.utils import strictly_increasing


def unify_conds(conds, cycle_time):
    substitution = {}
    for cond in conds:
        cond_object = cond[0]

        if cond_object.BaseClass is FLUENT:
            # Note that there might be more than one
            substitution = _unify_fluent(cond, cycle_time)
        else:
            print('Unrecognised object %s' % cond_object)

    return substitution


def _unify_fluent(cond, cycle_time):
    fluent = cond[0]
    temporal_var = cond[1]

    # Check if fluent is in KB
    if not KB.exists_fluent(fluent):
        return False

    # Unify with temporal vars, return the substitution
    substitution = unify(var(temporal_var.name), cycle_time)

    return substitution


def reify_goals(goals, substitution):
    new_goals = set()  # To prevent repeat goals

    for goal in goals:
        goal_object = goal[0]
        goal_re = None

        if goal_object.BaseClass is EVENT:
            goal_res = _reify_event(goal, substitution)
        else:
            print('Unrecognised object %s' % goal_object)

        if goal_res:
            converted_goals = []
            for goal_re in goal_res:
                if isinstance(goal_re, Var):
                    converted_goals.append(TemporalVar(goal_re.token))
                else:
                    converted_goals.append(goal_re)

            converted_goals = tuple(goal for goal in converted_goals)
            new_goals.add((goal_object,) + converted_goals)

    return new_goals


def _reify_event(goal, substitution):
    # Events should be handled also
    # event = goal[0]

    # Unify the temporal vars from condition
    '''
    Essentially (T1, T2) --> (T1, T1+1), if T2 is not specified?
    '''
    temporal_vars = tuple(
        var(temporal_var.name)
        for temporal_var in goal[1:]
    )

    goal_res = reify(temporal_vars, substitution)

    return goal_res


def unify_goal(goal, cycle_time):
    requirements = set()

    # Check if this goal is associated with some clause
    for clause in KB.clauses:
        clause_goal = clause.goal[0]

        # TODO: FIX / CHANGE THIS
        # Check if the objects match
        if clause_goal[0] != goal[0]:
            continue

        clause_temporal_vars = tuple(
            var(temporal_var.name)
            for temporal_var in clause_goal[1:]
        )

        goal_temporal_vars = []
        cycle_sub_used = False
        defer = False

        for item in goal[1:]:
            if isinstance(item, TemporalVar):
                if cycle_sub_used:
                    defer = True
                else:
                    t_sub = unify(var(item.name), cycle_time)
                    goal_temporal_vars.append(reify(var(item.name), t_sub))
                    cycle_sub_used = True
            else:
                goal_temporal_vars.append(item)

        goal_temporal_vars = tuple(goal_temporal_vars)

        if defer:
            # Further temporal substitutions required, so it is not possible
            # to proceed. Reinsert the revised goal
            return False

        if not strictly_increasing(goal_temporal_vars):
            # Set this for now, ensure that it is strictly increasing
            return False

        # Attempt to make the match if possible
        substitution = unify(clause_temporal_vars, goal_temporal_vars)

        if substitution:
            for req in clause.reqs:
                req_object = req[0]
                req_temporal_vars = tuple(
                    var(temporal_var.name)
                    for temporal_var in req[1:]
                )
                req_temporal_vars = reify(req_temporal_vars, substitution)

                # Check if all temporal var satisfied, otherwise add to goal
                temporal_satisfied = True
                for item in req_temporal_vars:
                    if not isinstance(item, int):
                        temporal_satisfied = False
                        break

                if temporal_satisfied:
                    if req_object.BaseClass is ACTION:
                        # Unify with the KB (but for now is a simple check)
                        causalities = KB.exists_causality(req_object)

                        if causalities:
                            for causality in causalities:
                                if causality[0] == A_TERMINATE:
                                    KB.remove_fluent(causality[1])
                                    KB.log_action(
                                        req_object, req_temporal_vars
                                    )
                                    KB.log_fluent(
                                        causality[1],
                                        max(req_temporal_vars),
                                        F_TERMINATE
                                    )
                                elif causality[0] == A_INITIATE:
                                    print('Initiate req undefined')
                                    return False
                                else:
                                    print('Unrecognised causality')
                                    return False
                    else:
                        print('Unrecognised object %s' % goal_object)
                        return False

    return True


def unify_obs(observation):
    # TODO: There should be an IC check
    action = observation.action
    start = observation.start
    end = observation.end
    causalities = KB.exists_causality(action)

    if causalities:
        for causality in causalities:
            if causality[0] == A_TERMINATE:
                print('Terminate observation undefined')
                pass
            elif causality[0] == A_INITIATE:
                KB.add_fluent(causality[1])
                KB.log_action(
                    action, (start, end)
                )
                KB.log_fluent(
                    causality[1],
                    end,
                    F_INITIATE
                )
            else:
                print('Unrecognised causality')

# def _unify_event(goal, cycle_time):
#     event = goal[0]
#     temporal_vars = tuple(
#         var(temporal_var.name)
#         for temporal_var in goal[1:]
#     )

#     for kb_goal in KB.goals:
#         print(kb_goal)
#     # # Check if fluent is in KB
#     # if not KB.exists_fluent(fluent):
#     #     return False

#     # # Unify with temporal vars, return the substitution
#     # temporal_var_name = temporal_var.name
#     # substitution = unify(var(temporal_var_name), cycle_time)

#     substitution = {}

#     return substitution
