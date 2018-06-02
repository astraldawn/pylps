from ordered_set import OrderedSet
from unification import *

from pylps.causality import *
from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.lps_objects import Observation
from pylps.kb import KB


def process_solutions(solutions, cycle_time):
    maximum_solved = max([sol.solved for sol in solutions])
    new_kb_goals = []

    # Ensure that actions executed per cycle are unique
    processed = set()
    solved_goals = set()

    cycle_actions = OrderedSet()

    for solution in solutions:

        for state in solution.states:

            if state.result is G_SOLVED:
                solved_goals.add(state.reactive_id)
                processed.add(state.reactive_id)
                cycle_actions |= state.actions

            elif state.result is G_DEFER:
                if state.reactive_id in solved_goals:
                    continue

                processed.add(state.reactive_id)

                # Kept because of the reactive_id possibly being solved
                cycle_actions |= state.actions

                new_state = state  # REMOVED DEEPCOPY

                # Clear actions / fluents and set to unprocessed
                new_state.clear_actions()
                new_state.clear_fluents()
                new_state.set_result(G_NPROCESSED)

                # Allow another temporal sub
                new_state.set_temporal_used(False)
                new_state.compress()
                new_kb_goals.append(new_state)

            elif state.result is G_DISCARD:
                processed.add(state.reactive_id)
                continue
            elif state.result is G_NPROCESSED:
                continue

        if maximum_solved > 0 and solution.solved == maximum_solved:
            break

    process_cycle(cycle_actions)

    unsolved_existing_goals = OrderedSet()

    for start_state in KB.goals:
        if start_state.reactive_id in processed or \
                start_state.reactive_id in solved_goals:
            continue

        unsolved_existing_goals.add(start_state)

    for state in new_kb_goals:

        if state.reactive_id in solved_goals:
            continue

        unsolved_existing_goals.add(state)

    KB.set_goals(unsolved_existing_goals)


def process_cycle(cycle_actions):
    '''
    TODO - Delay all commitment into KB until all are processed
    '''

    for action in cycle_actions:

        # Convert args for action
        converted_args = convert_args_to_python(action)

        # Add into observations
        KB.add_cycle_obs(Observation(
            action, action.start_time, action.end_time))

        # Log action
        KB.log_action_new(action, converted_args=converted_args)

        initiates, terminates = process_causalities(action)
        commit_outcomes(initiates, terminates)


def reify_actions(state, reify=True):
    actions = OrderedSet()
    for action in state.actions:
        if not reify:
            actions.add(action)
            continue

        action.args = reify_args(action.args, state.subs)
        action.update_start_time(
            reify_args([action.start_time], state.subs)[0])
        action.update_end_time(
            reify_args([action.end_time], state.subs)[0])
        actions.add(action)

    return actions


def match_clause_goal(clause, goal, new_subs, counter):
    SUFFIX = VAR_SEPARATOR + str(counter)

    # debug_display('MCG_CLAUSE', clause)
    # debug_display('MCG_GOAL', goal)
    # debug_display('MCG_SUBS', new_subs)
    # debug_display()

    if clause.BaseClass is CONSTANT:
        if goal.BaseClass is CONSTANT:
            return clause.const == goal.const

        # Match against a single element list
        if goal.BaseClass is LIST and len(goal) == 1:
            if goal.head.BaseClass is CONSTANT:
                return clause.const == goal.head.const

    if clause.BaseClass is VARIABLE:
        new_var = var(clause.name + SUFFIX)

        try:
            if goal.BaseClass is VARIABLE:
                new_subs.update({
                    var(goal.name): new_var,
                })
                return True
        except AttributeError:
            pass

        res = unify(new_var, goal, new_subs)

        if res:
            new_subs.update(res)
            return True

        return False

    if clause.BaseClass is TUPLE and goal.BaseClass is TUPLE:
        if len(clause) != len(goal):
            return False

        # If any items fail to match, should revert
        match_failed = False
        old_subs = copy.deepcopy(new_subs)

        for clause_item, goal_item in zip(clause.tuple, goal.tuple):
            if match_failed:
                continue

            res = match_clause_goal(
                clause_item, goal_item, new_subs, counter)

            if not res:
                match_failed = True

        if match_failed:
            new_subs = old_subs
            return False

        return True

    if clause.BaseClass is LIST and goal.BaseClass is VARIABLE:
        # Copy and rename
        new_clause = copy.deepcopy(clause)
        for item in new_clause._list:
            rename_arg(counter, item)

        new_subs.update({
            var(goal.name): new_clause,
        })
        # debug_display('LIST_MATCH', new_subs)
        return True

    if clause.BaseClass is LIST and goal.BaseClass is LIST:
        clause_head = clause.head
        goal_head = goal.head
        goal_tail = goal.tail

        # Simple empty
        if clause_head.BaseClass is CONSTANT and clause_head.const is None:
            return clause_head == goal_head

        # Operation
        if clause_head.BaseClass is TUPLE:
            operation = clause_head.tuple[0]

            # If operation is a constant, then do stuff
            if operation.BaseClass is CONSTANT and \
                    operation.const is MATCH_LIST_HEAD:

                old_subs = copy.deepcopy(new_subs)

                # TODO: Improve this
                if goal_head.BaseClass is TUPLE and \
                        len(goal_head) == len(clause_head):
                    match_head = match_clause_goal(
                        clause_head.tuple[1], goal_head.tuple[1],
                        new_subs, counter)
                    match_tail = match_clause_goal(
                        clause_head.tuple[2], goal_head.tuple[2],
                        new_subs, counter)
                else:
                    # Attempting to peel off an empty list
                    if len(goal) == 0:
                        return False

                    match_head = match_clause_goal(
                        clause_head.tuple[1], goal_head, new_subs, counter)
                    match_tail = match_clause_goal(
                        clause_head.tuple[2], goal_tail, new_subs, counter)

                # Both head and tail must match
                if match_head and match_tail:
                    return True

                new_subs = old_subs
                return False
            else:
                # This might break
                if len(clause) == len(goal):
                    return match_clause_goal(
                        clause_head, goal_head, new_subs, counter)

                return False

            return False

        # Match single
        if clause_head.BaseClass is VARIABLE:
            if len(goal) != 1:
                return False

            return match_clause_goal(
                clause_head, goal_head, new_subs, counter)

    return False


def create_clause_variables(
        clause, counter, goal, cur_subs, new_subs, new_reqs, reactive=False):

    # r_var = get_random_var()
    # Two way binding
    cg_st_name = clause.goal[0].start_time.name
    cg_et_name = clause.goal[0].end_time.name
    g_st_name = goal.start_time.name
    g_et_name = goal.end_time.name

    temporal_bind = {
        var(cg_st_name + VAR_SEPARATOR + str(counter)): var(g_st_name),
        var(g_et_name): var(cg_et_name + VAR_SEPARATOR + str(counter)),
    }

    if cg_st_name == cg_et_name and g_st_name == g_et_name:
        temporal_bind = {
            var(cg_st_name + VAR_SEPARATOR + str(counter)): var(g_st_name),
        }

    new_subs.update(temporal_bind)

    # debug_display('CG', clause.goal[0])
    # debug_display('CG', clause.goal[0].start_time, clause.goal[0].end_time)
    # debug_display('CG_TB', temporal_bind)

    if not clause.reqs:
        return

    for new_req in copy.deepcopy(clause.reqs):

        # Handling negated clauses
        if isinstance(new_req, tuple) and len(new_req) == 2:
            for arg in new_req[0].args:
                rename_arg(counter, arg)

            if new_req[0].BaseClass is ACTION or new_req[0].BaseClass is EVENT:
                new_req[0].start_time.name += VAR_SEPARATOR + str(counter)
                new_req[0].end_time.name += VAR_SEPARATOR + str(counter)
                new_req[0].from_reactive = reactive

            if new_req[0].BaseClass is FLUENT:
                new_req[0].time.name += VAR_SEPARATOR + str(counter)
        else:
            for arg in new_req.args:
                rename_arg(counter, arg)

            if new_req.BaseClass is ACTION or new_req.BaseClass is EVENT:
                new_req.start_time.name += VAR_SEPARATOR + str(counter)
                new_req.end_time.name += VAR_SEPARATOR + str(counter)
                new_req.from_reactive = reactive

            if new_req.BaseClass is FLUENT:
                new_req.time.name += VAR_SEPARATOR + str(counter)

        new_reqs.append(new_req)

    # debug_display('SUBS', new_subs)
    # debug_display('REQS', clause.reqs)
    # debug_display('NEW_REQS', new_reqs)


def add_to_cycle_proposed(cycle_proposed, state):
    cycle_proposed.add_actions(reify_actions(state, reify=True))
