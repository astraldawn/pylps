'''
Tuple based unification engine
Referenced from: https://github.com/aimacode/aima-python/blob/master/logic.py
'''
import copy
import operator
from collections import defaultdict

from unification import *

from pylps.constants import *
from pylps.config import CONFIG
from pylps.logic_objects import TemporalVar
from pylps.kb import KB
from pylps.exceptions import *
from pylps.utils import *


def unify_conds(conds, cycle_time):
    substitutions = []
    for cond in conds:
        temporal = False

        # Temporal check
        try:
            cond_object = cond[0]
            temporal = True
        except TypeError:
            cond_object = cond

        if temporal:
            if cond_object.BaseClass is FLUENT:
                # Note that there might be more than one possible sub
                substitutions.extend(unify_fluent(cond, cycle_time))
            else:
                raise UnhandledObjectError(cond_object.BaseClass)
        else:
            if cond_object.BaseClass is FACT:
                substitutions.extend(
                    unify_fact(cond_object, reactive_rule=True))
            else:
                raise UnhandledObjectError(cond_object.BaseClass)

    return substitutions


def unify_fluent(cond, cycle_time):
    fluent = cond[0]
    temporal_var = cond[1]

    substitutions = []

    # Check if fluent is in KB
    if not KB.exists_fluent(fluent):
        return substitutions

    # Unify with temporal vars, return the substitution
    substitutions.append(unify(var(temporal_var.name), cycle_time))

    return substitutions


def unify_fact(fact, reactive_rule=False):
    substitutions = []
    kb_facts = KB.get_facts(fact, reactive_rule)
    for kb_fact in kb_facts:
        unify_res = unify_args(fact.args, kb_fact.args)
        substitutions.append(unify_res)
    return substitutions


def reify_goals(goals, subs, defer=False):
    '''
    Note that goals are interative

    E.g.

    reactive_rule(country(X)).then(
        colour(C),
        paint(X, C).frm(T1, T2)
    )

    If consequent rules are swapped, should raise some error
    '''
    temporal = False
    used_var = set()

    # Checking whether or not a variable is used
    # Look to combine these
    for goal in goals:
        # Temporal check
        try:
            goal_object_original = goal[0]
            temporal = True
        except TypeError:
            goal_object_original = goal

        for arg in goal_object_original.args:
            try:
                if arg.BaseClass is VARIABLE:
                    used_var.add(var(arg.name))
            except TypeError:
                pass

        if temporal:
            for temporal_var in goal[1:]:
                used_var.add(var(temporal_var.name))

    sub_vars = list(subs.keys())
    for variable in sub_vars:
        if variable not in used_var:
            del subs[variable]

    if defer:
        return copy.deepcopy(goals)

    new_goals_set = set()  # To prevent repeat goals
    new_goals = []         # To keep ordering constant

    for goal in goals:
        temporal = False
        goal_res = None

        # Temporal check
        try:
            goal_object_original = goal[0]
            temporal = True
        except TypeError:
            goal_object_original = goal

        goal_object = copy.deepcopy(goal_object_original)

        goal_object.args = reify_args(
            goal_object.args, subs)

        if temporal:
            if goal_object.BaseClass is ACTION:
                goal_res = _reify_event(goal, subs)
            elif goal_object.BaseClass is EVENT:
                goal_res = _reify_event(goal, subs)
            else:
                raise UnhandledObjectError(goal_object.BaseClass)
        else:
            if (goal_object.BaseClass is FACT and
                    goal_object not in new_goals_set):
                new_goals_set.add(goal_object)
                new_goals.append(goal_object)
            else:
                raise UnhandledObjectError(goal_object.BaseClass)

        if goal_res:
            converted_goals = []
            for goal_re in goal_res:
                if isinstance(goal_re, Var):
                    converted_goals.append(TemporalVar(goal_re.token))
                else:
                    converted_goals.append(goal_re)

            converted_goals = tuple(goal for goal in converted_goals)
            combined_goal = (goal_object,) + converted_goals
            if combined_goal not in new_goals_set:
                new_goals.append(combined_goal)

    return tuple(g for g in new_goals)


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


def unify_obs(observation):
    # TODO: There should be an IC check
    action = observation.action
    start = observation.start
    end = observation.end
    causality = KB.exists_causality(action)

    KB.log_action_obs(action, (start, end))

    # If there is causality, need to make the check
    if causality:
        substitutions = unify_args(causality.action.args, action.args)

        if not check_reqs(causality.reqs, substitutions):
            return

    for outcome in causality.outcomes:
        if outcome[0] == A_TERMINATE:
            raise UnhandledOutcomeError(A_TERMINATE)
        elif outcome[0] == A_INITIATE:
            if KB.add_fluent(outcome[1]):
                KB.log_fluent(outcome[1], end, F_INITIATE)
        else:
            raise UnknownOutcomeError(outcome[0])


def constraints_satisfied(goal):
    action = copy.deepcopy(goal.obj)

    # Reify a copy of the action
    combined_subs = {**goal.subs, **goal.new_subs}
    action = reify_obj_args(action, combined_subs)

    # THen clear the combined subs
    combined_subs = {}
    # print(action)
    # print(action, combined_subs)

    '''
    TODO:
    This could become very complicated, for example,
    you need to have 2 associated substitutions,

    Associated subsitutions are ignored for now
    Also a set is used, which may affect the outcome
    '''
    sub_dict = defaultdict(set)

    # print(action, combined_subs)
    # print(KB._cycle_actions)
    # print()

    for constraint in KB.get_constraints(action):

        # Assume the constraint is true
        c_satis = True

        for indiv_con in constraint:

            if not c_satis:
                continue

            # Attempt to falsify
            c_satis = check_constraint(
                action, indiv_con, combined_subs, sub_dict)

            # print(action, c_satis)

        '''
        If any single constraint (which can consist of many indiv_cons)
        is satisfied, then fail
        '''
        if c_satis:
            return False

    return True


def check_constraint(action, constraint, combined_subs, sub_dict):
    obj, state = constraint

    if obj.BaseClass is ACTION:
        if obj.name == action.name:
            vars_unified = 0
            vars_cnt = 0

            for obj_arg, action_arg in zip(obj.args, action.args):
                try:
                    if (obj_arg.BaseClass is VARIABLE):
                        vars_cnt += 1

                        if Var(obj_arg.name) not in sub_dict:
                            combined_subs.update(
                                unify_args([obj_arg], [action_arg]))
                            vars_unified += 1
                except AttributeError:
                    pass

            # If every var is unified, it must satisfy
            if vars_unified == vars_cnt:
                return True

        # print(obj, action, sub_dict)
        r_obj = reify_obj_args(obj, combined_subs)

        '''
            This potentially can get very time consuming, probably
            have to go via DFS? Similar code will be required for
            going through the options in reactive rules

            TODO: Support multiple variables
        '''
        var = None
        for arg in r_obj.args:
            try:
                if arg.BaseClass == VARIABLE:
                    if var:
                        raise UnimplementedOutcomeError(
                            "constraint multiple variables")
                    var = Var(arg.name)
            except AttributeError:
                pass

        # Do nothing if no substitutions
        # if not var:
        #     continue

        t_sub_set = set()

        cycle_actions = KB.get_cycle_actions(r_obj)

        # Action has never occured, so its impossible to sub / falsify
        if not cycle_actions:
            return False

        # Unsubstituted variable
        if var and var not in sub_dict:
            for cycle_action in cycle_actions:
                new_subs = unify_args(r_obj.args, cycle_action.args)
                for k, v in new_subs.items():
                    sub_dict[k].add(v)

            return True

        if var in sub_dict:
            # print(r_obj, var, action, sub_dict, cycle_actions)

            for sub in sub_dict[var]:
                combined_subs[var] = sub
                t_obj = reify_obj_args(r_obj, combined_subs)

                action_exists = KB.exists_cycle_action(t_obj)
                t_sub_set.add(action_exists)

            if state and True not in t_sub_set:
                return False

    elif obj.BaseClass is FACT:
        r_obj = reify_obj_args(obj, combined_subs)
        new_subs = unify_fact(r_obj)

        for new_sub_d in new_subs:
            for k, v in new_sub_d.items():
                sub_dict[k].add(v)

    elif obj.BaseClass is FLUENT:
        fluent_exists = KB.exists_fluent(obj)

        # All truth must be satisfied to consider
        # Might need to rework this (see the handling for action)
        if state and not fluent_exists:
            return False
        elif not state and fluent_exists:
            return False

    elif obj.BaseClass is EXPR:
        r_obj = reify_obj_args(obj, combined_subs)

        var = None
        for arg in r_obj.args:
            try:
                if arg.BaseClass == VARIABLE:
                    if var:
                        raise UnimplementedOutcomeError(
                            "constraint multiple variables")
                    var = Var(arg.name)

                    # If variable is not available, impossible to eval
                    if var not in sub_dict:
                        return False

            except AttributeError:
                continue

        for sub in sub_dict[var]:
            t_args = reify_args(r_obj.args, {var: sub})

            if r_obj.op is operator.ne:
                # Apply operator
                res = r_obj.op(t_args[0], t_args[1])

                # Constraint is matched
                if res is True:
                    return res
            else:
                raise UnimplementedOutcomeError("operator constraint")

        return False
    else:
        raise UnhandledObjectError(obj.BaseClass)

    return True


def check_reqs(reqs, substitutions):
    if reqs == []:
        return True

    # print(reqs, substitutions)
    for req in reqs:
        true_satis = True
        # false_satis = True
        for (obj_original, state) in req:
            # copy object, do not want to modify KB
            obj = copy.deepcopy(obj_original)
            if obj.BaseClass == FACT:
                obj.args = reify_args(obj.args, substitutions)
                fact_exists = KB.exists_fact(obj)
                if state and not fact_exists:
                    true_satis = False
            else:
                raise UnhandledObjectError(obj.BaseClass)

        if not true_satis:
            return False

    return True
