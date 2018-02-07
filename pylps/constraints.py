import copy
import operator
from collections import defaultdict

from unification import *

from pylps.constants import *
from pylps.kb import KB
from pylps.exceptions import *
from pylps.utils import *

from pylps.unifier import unify_fact


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
