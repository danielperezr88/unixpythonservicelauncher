
import os
import sys
import inspect


def retrCwd():
    if hasattr(sys, "frozen") and sys.frozen in ("windows_exe", "console_exe"):
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


def maybeCreateDirs(dirnames, base='.'):
    if not isinstance(dirnames, list):
        dirnames = [dirnames]
    for dirname in [os.path.join(base, dn) for dn in dirnames if dn != '']:
        if not os.path.exists(dirname):
            os.makedirs(dirname)
