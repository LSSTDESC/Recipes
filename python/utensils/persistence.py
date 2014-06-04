"""Utensils for directory and file handling"""
import os
import sys
import shutil

def makedir(path, replace=True, query=True):
    """Create a directory path, replacing existing path if desired."""
    if os.path.exists(path):
        if not replace:
            return
        if query:
            sys.stdout.write("About to delete %s. Proceed? [Y/n] " % path)
            response = sys.stdin.readline().strip()
        if not query or response in ('', 'y', 'Y'):
            print "Replacing existing", path
            shutil.rmtree(path)
        else:
            return
    os.makedirs(path)
