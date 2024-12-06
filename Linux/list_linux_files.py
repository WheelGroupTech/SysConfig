#-----------------------------------------------------------------------------
# list_linux_files.py
#
# Copyright (c) 2024 Daniel M. Teal
#
# License: MIT License
#
# Python script to list files on Linux.
#-----------------------------------------------------------------------------
"""list_linux_files.py""" # for pylint
# pylint: disable=unused-variable

import os
import pwd
import grp
import stat


#-----------------------------------------------------------------------------
# get_file_info()
#-----------------------------------------------------------------------------
def get_file_info(pathname):
    """Gets file information for the provided pathname"""

    file_stat = os.lstat(pathname)

    permissions = stat.filemode(file_stat.st_mode)

    owner_uid = file_stat.st_uid
    group_gid = file_stat.st_gid
    owner_name = pwd.getpwuid(owner_uid).pw_name
    group_name = grp.getgrgid(group_gid).gr_name

    print(f"{pathname} {permissions} {owner_name} {group_name} {file_stat.st_size}")


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
