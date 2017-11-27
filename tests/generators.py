def fluent_initiate(name, args, time):
    return "['fluent_initiate', '%s', %s, %s]" % (
        name, str(args), str(time))


def fluent_terminate(name, args, time):
    return "['fluent_terminate', '%s', %s, %s]" % (
        name, str(args), str(time))


def action(name, args, time):
    return "['action', '%s', %s, %s]" % (
        name, str(args), str(time))
