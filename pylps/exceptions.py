class ConfigError(Exception):
    def __init__(self, config_option, value):
        self.config_option = config_option
        self.value = value


class UnhandledObjectError(Exception):
    def __init__(self, obj_type):
        self.obj_type = obj_type


class UnimplementedOutcomeError(Exception):
    def __init__(self, outcome_type):
        self.outcome_type = outcome_type


class UnknownOutcomeError(Exception):
    def __init__(self, outcome_type):
        self.outcome_type = outcome_type


class PylpsUnimplementedOutcomeError(Exception):
    def __init__(self, outcome_type):
        self.outcome_type = outcome_type
