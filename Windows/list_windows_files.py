#-----------------------------------------------------------------------------
# list_windows_files.py
#
# Copyright (c) 2024 Daniel M. Teal
#
# License: MIT License
#
# Python script to list files on Windows.
#-----------------------------------------------------------------------------
"""list_windows_files.py""" # for pylint
# pylint: disable=unused-variable

import os
import stat


#-----------------------------------------------------------------------------
# get_file_info()
#-----------------------------------------------------------------------------
def get_file_info(pathname):
    """Gets file information for the provided pathname"""

    if os.path.isfile(pathname):
        file_stat = os.lstat(pathname)
        permissions = stat.filemode(file_stat.st_mode)

        print(f"{pathname} {permissions} {file_stat.st_size}")


#-----------------------------------------------------------------------------
# list_files()
#-----------------------------------------------------------------------------
def list_files(dirname):
    """Recursively ists all files from the specified pathname"""

    for dirpath, dirnames, filenames in os.walk(dirname):
        for filename in filenames:
            pathname = os.path.join(dirpath, filename)
            get_file_info(pathname)


# Prompt the user to enter a pathname
PATHNAME_ARG = input("Enter the pathname: ")

# List the files
list_files(PATHNAME_ARG)
