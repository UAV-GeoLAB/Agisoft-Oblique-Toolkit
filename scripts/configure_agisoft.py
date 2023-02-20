"""
    Simple script that should find Metashape Python interpreter and install required PIP packages.
"""
import argparse
from pathlib import Path
from subprocess import run
from sys import argv

from utility import find_agisoft_python

REQUIREMENTS_PATH = Path(__file__).parent.parent / 'requirements.txt'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--silent", action='store_true', dest="silent")
    parser.add_argument('--metashape-path', dest='metashape_path')
    args = parser.parse_args(argv[1:])

    # Identify Metashape Python interpreter path
    if not args.silent:
        print("Attempting to determine Agisoft Metashape Python interpreter path.")

    metashape_python_exe = find_agisoft_python(args.metashape_path)

    if not args.silent:
        print("Python path resolved succesfully. Using: " + str(metashape_python_exe))

    # Install Python requirements
    if not args.silent:
        print("Installing needed Python packages.")

    run_arguments = [str(metashape_python_exe.absolute()), '-m', 'pip', 'install', '-r',
                     str(REQUIREMENTS_PATH.absolute())]
    result = run(run_arguments, capture_output=True)

    stdout = result.stdout.decode('utf-8')
    stderr = result.stderr.decode('utf-8')
    if not args.silent:
        print('PIP install output:')
        print(stdout)

    if result.returncode == 0 and not args.silent:
        print("Installation complete. Agisoft Python has been configured.")

    elif result.returncode != 0:
        raise Exception("Package installation failed with error: \n" + stderr)
