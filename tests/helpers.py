import subprocess


def run_pylps_example(example_name):
    completed = subprocess.run(
        ['python', 'examples/' + example_name + '.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    actual = completed.stdout.decode('utf-8').split('\r\n')[:-1]

    return actual


def run_pylps_test_program(program_name):
    completed = subprocess.run(
        ['python', 'tests/programs/' + program_name + '.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    actual = completed.stdout.decode('utf-8').split('\r\n')[:-1]

    return actual
