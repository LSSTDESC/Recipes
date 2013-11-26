"""Utensils for directory and file handling"""
import os
import sys
import shutil

def makedir(path, replace=True):
    """Create a directory path, replacing existing path if desired."""
    try:
        os.makedirs(path)
    except OSError:
        sys.stdout.write("About to replace %s, deleting its contents.  Proceed? [Y/n] " % path)
        response = sys.stdin.readline().strip()
        if response in ('', 'y', 'Y'):
            shutil.rmtree(path)
        else:
            return
        os.makedirs(path)
