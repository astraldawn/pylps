import argparse
import os
import subprocess

from tempfile import NamedTemporaryFile

from pylps_helper.parser import PARSER


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help='pylps files')
    args = parser.parse_args()

    for file in args.files:
        program = []
        try:
            with open(file, 'r') as myfile:
                data = myfile.readlines()
                for line in data:
                    program.append(line.replace('\n', ''))
        except FileNotFoundError as e:
            raise e

        output = PARSER.parse_program(program)

        # Create a temp file
        pylpsFile = NamedTemporaryFile(mode='w', delete=False)
        for line in output:
            pylpsFile.file.write(line + '\n')

        # Note 0o777 is to write permissions correctly
        os.chmod(pylpsFile.name, 0o777)

        pylpsFile.file.close()

        subprocess.run(['python', pylpsFile.name])

        os.remove(pylpsFile.name)
