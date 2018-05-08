from ordered_set import OrderedSet
from unification import *

from pylps.causality import *
from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.lps_objects import Observation
from pylps.kb import KB
from pylps.config import CONFIG


def process_solutions(solutions, cycle_time):

    preference = CONFIG.solution_preference

    maximum_solved = max([sol.solved for sol in solutions])

    if preference is SOLN_PREF_MAX:
        solutions = sorted(
            solutions,
            # Go for maximum solved + maximum number of actions
            key=lambda sol: (sol.solved, len(sol.proposed.actions)),
            reverse=True)

    new_kb_goals = OrderedSet()

    # Ensure that actions executed per cycle are unique
    unique_actions = set()
    processed = set()
    solved = False
    soln_max_solved = False

    for solution in solutions:

        if maximum_solved != 0 and solution.solved == maximum_solved:
            solved = True

        for state in solution.states:

            if state.result is G_SOLVED:
                soln_max_solved = True
                processed.add(state.reactive_id)
                _process_state(state, unique_actions)

            elif state.result is G_DEFER:
                # soln_max_solved = True
                processed.add(state.reactive_id)
                _process_state(state, unique_actions)

                new_state = copy.deepcopy(state)

                # Clear actions / fluents and set to unprocessed
                new_state.clear_actions()
                new_state.clear_fluents()
                new_state.set_result(G_NPROCESSED)

                # Allow another temporal sub
                new_state.set_temporal_used(False)

                new_kb_goals.add(new_state)
            elif state.result is G_DISCARD:
                processed.add(state.reactive_id)
                continue
            elif state.result is G_NPROCESSED:
                continue

        if (preference is SOLN_PREF_MAX and soln_max_solved) or solved:
            break

    unsolved_existing_goals = OrderedSet()

    for start_state in KB.goals:
        if start_state.reactive_id in processed:
            continue

        unsolved_existing_goals.add(start_state)

    unsolved_existing_goals.update(new_kb_goals)

    KB.set_goals(unsolved_existing_goals)


def _process_state(state, unique_actions):

    # debug_display('STATE', state)

    for action in state.actions:
        if action in unique_actions:
            continue

        # if CONFIG.experimental:
        #     r_action = reify_action(action, state.subs)
        # else:
        r_action = action

        # Convert args for action
        converted_args = convert_args_to_python(r_action)

        # Add into observations
        KB.add_cycle_obs(Observation(
            r_action, action.start_time, action.end_time))

        # Log action
        KB.log_action_new(r_action, converted_args=converted_args)
        unique_actions.add(r_action)

        if CONFIG.cycle_fluents:
            continue

        initiates, terminates = process_causalities(r_action)
        commit_outcomes(initiates, terminates)

    for fluent_outcome in state.fluents:
        if not CONFIG.cycle_fluents:
            continue

        outcome, fluent = fluent_outcome.outcome, fluent_outcome.fluent

        if outcome == A_TERMINATE:
            if KB.remove_fluent(fluent):
                KB.log_fluent(fluent, cycle_time + 1, F_TERMINATE)
        elif outcome == A_INITIATE:
            if KB.add_fluent(fluent):
                KB.log_fluent(fluent, cycle_time + 1, F_INITIATE)
        else:
            raise UnknownOutcomeError(outcome)


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
        try:
            if goal.BaseClass is VARIABLE:
                new_subs.update({
                    var(goal.name): var(clause.name + SUFFIX),
                })
                return True
        except AttributeError:
            pass

        new_var = var(clause.name + SUFFIX)

        if new_var not in new_subs:
            new_subs.update({
                new_var: goal
            })
            return True

        if new_subs[new_var] == goal:
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
        clause, counter, goal, new_subs, new_reqs):
    # Temporal variable updating
    new_subs.update({
        var(clause.goal[0].start_time.name + VAR_SEPARATOR + str(counter)):
        var(goal.start_time.name),
        var(clause.goal[0].end_time.name + VAR_SEPARATOR + str(counter)):
        var(goal.end_time.name)
    })

    if not clause.reqs:
        return

    for req in clause.reqs:
        new_req = copy.deepcopy(req)

        # Handling negated clauses
        if isinstance(new_req, tuple) and len(new_req) == 2:
            for arg in new_req[0].args:
                rename_arg(counter, arg)

            if req[0].BaseClass is ACTION or req[0].BaseClass is EVENT:
                new_req[0].start_time.name += VAR_SEPARATOR + str(counter)
                new_req[0].end_time.name += VAR_SEPARATOR + str(counter)
        else:
            for arg in new_req.args:
                rename_arg(counter, arg)

            if req.BaseClass is ACTION or req.BaseClass is EVENT:
                new_req.start_time.name += VAR_SEPARATOR + str(counter)
                new_req.end_time.name += VAR_SEPARATOR + str(counter)

        new_reqs.append(new_req)

    # debug_display('SUBS', new_subs)
    # debug_display('REQS', clause.reqs)
    # debug_display('NEW_REQS', new_reqs)
