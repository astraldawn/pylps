from pylps.constants import *
from pylps.kb import KB
from pylps.solver import solve_multigoal, process_cycle_actions
from pylps.unifier import unify_conds, reify_goals, unify_obs


class _ENGINE(object):
    start_time = 1
    current_time = 1
    max_time = 5

    def set_params(self, max_time):
        self.max_time = max_time

    def run(self):
        self.current_time = self.start_time
        KB.reset_goals()

        while self.current_time <= self.max_time:
            KB.clear_cycle_actions()
            self._check_observations()
            self._check_rules()
            self._check_goals()

            self.current_time += 1

    def _check_observations(self):
        for observation in KB.observations:
            if observation.end == self.current_time:
                # Unify with the KB?
                unify_obs(observation)

    def _check_rules(self):
        # Check rules
        for rule in KB.rules:
            # Check conditions of the rules
            substitutions = unify_conds(rule.conds, self.current_time)

            # If there are no substitutions, go to the next rule
            if not substitutions:
                continue

            for substitution in substitutions:
                new_goals = reify_goals(rule.goals, substitution, defer=True)
                KB.add_goals(new_goals, substitution)

    def _check_goals(self):
        '''
        Work through the goals individually
        '''
        solved_group = set()

        cur_goal_pos = 0

        KB_goals = KB.goals.children

        while(cur_goal_pos < len(KB_goals)):
            multigoal = KB_goals[cur_goal_pos]

            if multigoal in solved_group:
                multigoal.update_result(G_SOLVED)
                cur_goal_pos += 1
                continue

            solve_multigoal(multigoal, self.current_time)
            # print(self.current_time, multigoal)

            if multigoal.result in SOLVED_RESPONSES:
                solved_group.add(multigoal)
            elif multigoal.result is G_CLAUSE_FAIL:  # Go back one

                # Cannot solve the original, so discard it and move on
                # Will not be able to go back anymore
                if cur_goal_pos == 0:
                    multigoal.update_result(G_DISCARD)
                    cur_goal_pos += 1
                    continue

                prev_goal = KB_goals[cur_goal_pos - 1]
                if prev_goal.result in SOLVED_RESPONSES:
                    solved_group.remove(prev_goal)
                    prev_goal.reset(propagate=True)
                    continue

            cur_goal_pos += 1

        if KB_goals:
            # KB.display_cycle_actions()
            new_children = []
            for child in KB_goals:
                if (child.result in SOLVED_RESPONSES or
                        child.result is G_DISCARD):
                    continue
                new_children.append(child)

            KB.set_children(new_children)
            process_cycle_actions()


ENGINE = _ENGINE()
