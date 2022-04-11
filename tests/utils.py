import subprocess

from constants import TESTING_PROJECT_ROOT


def run_pytest(optional_args, timeout=30):
    """
    Run Pytest proccess by providing optional arguments to it
    
    :param optional_args Optional arguements to Pytest process
    :param timeout Time limit to pytest process exit
    :return process exit code, standard output and stdard error 
    """
    process = subprocess.Popen(['pytest'] + optional_args + ['tests'], 
                               stderr=subprocess.PIPE, stdout=subprocess.PIPE, 
                               text=True, shell=True, cwd=TESTING_PROJECT_ROOT)
    process.wait(timeout=timeout)
    return process.returncode, process.stdout.read(), process.stderr.read()
