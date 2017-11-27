import subprocess


def run_pylps_example(example_name):
    completed = subprocess.run(
        ['python', 'examples/' + example_name + '.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    actual = completed.stdout.decode('utf-8').split('\r\n')[:-1]

    return actual
