import re

from pylps_helper.constants import *


class Parser(object):
    def __init__(self):
        self.output = [HEAD_STRING]
        self.actions = set()
        self.events = set()
        self.ae_regexes = set()
        self.variables = set()
        self.pylps_line = False

        self.MATCH_VARIABLE = re.compile('[A-Z][a-zA-Z0-9]*\s*')
        self.MATCH_LOWERCASE = re.compile('[a-z][a-zA-Z0-9]*\s*')
        self.MATCH_LOWERCASE_WITH_UNDERSCORE = \
            re.compile('(?:[a-z][a-zA-Z0-9]*_)*[a-z][a-zA-Z0-9]*\s*')
        self.MATCH_ENDING_BRACE = re.compile('\)\s*$')

        # Actions / events
        self.MATCH_CREATE_ACTIONS = re.compile(' *create_actions')
        self.MATCH_CREATE_EVENTS = re.compile(' *create_events')

        # PYLPS specific
        self.MATCH_OBSERVE = re.compile(' *observe')
        self.MATCH_REACTIVE = re.compile(' *reactive')
        self.MATCH_GOAL = re.compile('(?:goal\((.*)\))')

        # Flags
        self.matching_actions = False
        self.matching_events = False

    def reset(self):
        self.output = [HEAD_STRING]
        self.actions = set()
        self.events = set()
        self.ae_regexes = set()
        self.variables = set()
        self.pylps_line = False

    def parse_program(self, program):
        # First pass
        for line in program:
            self.parse_line(line)

        # Second pass
        self.variables = ["'" + x + "'" for x in self.variables]

        # Create variables
        self.output.append(
            'create_variables(' +
            ','.join(self.variables) + ')'
        )

        has_exec = False
        has_show_kb = False

        for line in program:
            self.output.append(line)

            if 'execute' in line:
                has_exec = True

            if 'show_kb_log' in line:
                has_show_kb = True

        # Ending
        if not has_exec:
            self.output.append(ENDING_LINES['exec'])

        if not has_show_kb:
            self.output.append(ENDING_LINES['show_kb'])

        return self.output

    def parse_line(self, line):
        if re.findall(self.MATCH_CREATE_ACTIONS, line) \
                or self.matching_actions:
            self.matching_actions = True
            self._handle_actions(line)
            return

        if re.findall(self.MATCH_CREATE_EVENTS, line) or self.matching_events:
            self.matching_events = True
            self._handle_events(line)
            return

        if any(regex.findall(line) for regex in self.ae_regexes):
            self.pylps_line = True

        if re.findall(self.MATCH_REACTIVE, line):
            self.pylps_line = True

        match = re.findall(self.MATCH_GOAL, line)
        if match:
            self.pylps_line = True
            match = match[0].split('.')
            self.events.add(match[0])

        if self.pylps_line:
            var_check = re.findall(self.MATCH_VARIABLE, line)
            for var in var_check:
                self.variables.add(var)

        if re.findall(self.MATCH_ENDING_BRACE, line):
            self.pylps_line = False

    def parse_results(self):
        print('\n')
        print('ACTIONS', self.actions)
        print('EVENTS', self.events)
        print('VARIABLES', self.variables)

    def _handle_actions(self, line):
        actions = re.findall(self.MATCH_LOWERCASE_WITH_UNDERSCORE, line)
        for action in actions:
            if action != 'create_actions':
                self.actions.add(action)
                self.ae_regexes.add(re.compile(action))

        if re.findall(self.MATCH_ENDING_BRACE, line):
            self.matching_actions = False

    def _handle_events(self, line):
        events = re.findall(self.MATCH_LOWERCASE_WITH_UNDERSCORE, line)
        for event in events:
            if event != 'create_events':
                self.events.add(event)
                self.ae_regexes.add(re.compile(event))

        if re.findall(self.MATCH_ENDING_BRACE, line):
            self.matching_events = False


PARSER = Parser()
