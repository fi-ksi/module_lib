"""
Check student's codes with flake8 & mypy tool
Reqired: working 'flake8'/'mypy' from command line
"""

import subprocess
from typing import List, Optional
import re

from utils.checker_helpers import report


def _execute_command(cmd: List[str]) -> str:
    """Executes any command and returns stdout"""
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    process.wait()
    assert process.stderr.read().decode('utf-8') == '', \
        f'{cmd[0]} returned nonempty stderr!'
    return str(process.stdout.read().decode('utf-8'))


def flake8_stdout(filename: str) -> str:
    """Runs flake8 on file 'filename' and returns stdout as plain string"""
    output = _execute_command([
        'flake8',
        '--extend-ignore=W292',
        '--disable-noqa',
        '--format=%(row)d:%(col)d: %(code)s %(text)s',
        filename
    ])
    return output


def flake8_check(filename: str) -> bool:
    """Prints flake8 result and outputs if code was ok"""
    flake8_violations = flake8_stdout(filename)
    flake8_ok = (flake8_violations == '')
    if flake8_ok:
        report("INFO", "Gratulujeme, Váš kód splňuje požadavky na styl.")
    else:
        report("FAIL",
               f"Váš kód nesplňuje požadavky na styl:\n {flake8_violations}")
    return flake8_ok


def _strip_mypy_filename(stdout: str) -> str:
    return '\n'.join(re.sub(r'^.*?:', '', line) for line in stdout.split('\n'))


def mypy_stdout(filename: str, args: List[str]) -> str:
    """Runs mypy on file 'filename' and returns stdout as plain string"""
    command = ['mypy', '--strict', '--no-error-summary']
    command.extend(args)
    command.append(filename)
    output = _execute_command(command)
    return _strip_mypy_filename(output)


def mypy_check(
        filename: str, additional_args: Optional[List[str]] = None) -> bool:
    """Prints mypy result and outputs if code was ok"""
    if additional_args is None:
        additional_args = []
    mypy_violations = mypy_stdout(filename, additional_args)
    mypy_ok = (mypy_violations == '')
    if mypy_ok:
        report("INFO", "Gratulujeme, Váš kód splňuje požadavky na typování.")
    else:
        report("FAIL",
               f"Váš kód nesplňuje požadavky na typování:\n {mypy_violations}")
    return mypy_ok
