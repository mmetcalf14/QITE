import importlib
import platform
import sys
import warnings

from sys import version_info

def check_import(mname):
    try:
        importlib.import_module(mname)
    except ImportError:
        print("* Required module: {0} not found, run: pip install {0}".format(mname))

def check_platform():
    platform_error_msg = "docplex is not compatible with this version of Python: only 64 bits on Windows, Linux, Darwin and AIX, with Python 2.7.9+, 3.4+ are supported."

    platform_system = platform.system()
    if platform_system in ('Darwin', 'Linux', 'Windows', 'Microsoft', 'AIX'):
        if version_info[0] == 3:
            if version_info < (3, 4, 0):
                warnings.warn(platform_error_msg)
        elif version_info[0] == 2:
            if version_info[1] != 7:
               warnings.warn(platform_error_msg)
        else:
            warnings.warn(platform_error_msg)
    else:
        print("docplex is not officially supported on this platform. Use it at your own risk.", RuntimeWarning)

    is_64bits = sys.maxsize > 2 ** 32
    if is_64bits is False:
        warnings.warn("docplex is not officially supported on 32 bits. Use it at your own risk.", RuntimeWarning)

def run_docplex_check_list():
    check_platform()

    # check requirements
    check_import("six")
    check_import("enum")
    check_import("cloudpickle")

    # check cplex
    try:
        from cplex import Cplex

        cpx = Cplex()
        del cpx
    except ImportError:
        print("Cplex DLL not found, if present , you must add it to PYTHNPATH")

    # check pandas
    try:
        import pandas as pd
        from pandas import DataFrame, Series
        dd = DataFrame({})
    except ImportError:
        print("-- pandas is not present, some features might be unavailable.")


if __name__ == "__main__":
    run_docplex_check_list()
