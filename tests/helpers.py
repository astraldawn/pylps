import subprocess
import os

TEST_ENV = os.getenv('TEST_ENV', None)
CIRCLE_CI_PATH = '/home/circleci/repo/'
LINUX_SPLIT_CHAR = '\n'
WINDOWS_SPLIT_CHAR = '\r\n'


def run_pylps_example(example_name):
    path = ''
    split_char = WINDOWS_SPLIT_CHAR
    if TEST_ENV:
        path = CIRCLE_CI_PATH
        split_char = LINUX_SPLIT_CHAR

    completed = subprocess.run(
        ['python', path + 'examples/' + example_name + '.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    actual = completed.stdout.decode('utf-8').split(split_char)[:-1]

    return actual


def run_pylps_test_program(program_group, program_name):
    path = ''
    split_char = WINDOWS_SPLIT_CHAR
    if TEST_ENV:
        path = CIRCLE_CI_PATH
        split_char = LINUX_SPLIT_CHAR

    completed = subprocess.run(
        ['python', path + 'tests/programs/' + program_group + '/' +
         program_name + '.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    actual = completed.stdout.decode('utf-8').split(split_char)[:-1]

    return actual
