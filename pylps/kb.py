'''
Class for the knowledge base
'''


class KB(object):
    rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def show_reactive_rules(self):
        print(self.rules)
