#-----------------------------------------------------------------------------
# manage_applications.py
#
# Copyright (c) 2024 Daniel M. Teal
#
# License: MIT License
#
# Python script to scan installed applications and delete unauthorized apps.
#-----------------------------------------------------------------------------
"""manage_applications.py""" # for pylint
# pylint: disable=line-too-long

import ctypes
import os
import re
import subprocess
import winreg


ALLOW_APPS = ['microsoft', 'python', 'mozilla', 'notepad++', 'vmware', 'java', '7-zip',
               'gimp', 'inkscape']
INSTALLED_APPS = []

# Windows registry keys for managing installed applications in HKEY_LOCAL_MACHINE
APPKEY1 = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
APPKEY2 = r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'

SHELL32 = ctypes.windll.shell32


#-----------------------------------------------------------------------------
# is_admin()
#-----------------------------------------------------------------------------
def is_admin():
    """Returns TRUE if user is an admin"""
    result = SHELL32.IsUserAnAdmin() != 0
    return result


#-----------------------------------------------------------------------------
# reg_query_value()
#-----------------------------------------------------------------------------
def reg_query_value(key, name):
    """Query the value for the provided key"""
    try:
        value = winreg.QueryValueEx(key, name)
        return value[0]
    except WindowsError:
        return ""


#-----------------------------------------------------------------------------
# validate_command_pathname()
#
# Unquoted command strings with a space in the pathname will not work when
# passed as a command because the shell interpreter will only use the start
# of the pathname instead of the full pathname.  For example, the following path:
#
#     C:\Program Files(x86)\Test Application\Test.exe arg1 arg2 arg3
#
# Results in the shell attempting to start "C:\Program" with the rest as
# arguments.  This function will convert the string and return the following:
#
#     "C:\Program Files(x86)\Test Application\Test.exe" arg1 arg2 arg3
#
# However, it will only work if the file exists on the local filesystem.
#-----------------------------------------------------------------------------
def validate_command_pathname(command):
    """Validates pathname in a command"""

    # Search for 'C:\Program Files' and 'C:\Program Files (x86)' by checking
    # if the string starts with 'C:\Program Files' at the very start.  The
    # \A option forces a match at the start of the string to skip over a
    # '"' at the beginning
    if re.search(r'\AC:\\Program Files', command, flags=re.IGNORECASE):

        # The string does not start with a '"' so split it into
        # components separated by white space
        split_command = command.split()

        # Incrementally add each component to a string to see if the path exists
        new_command = ''
        path_found = False
        for path_component in split_command:

            new_command += f"{path_component}"

            # Check if the new command is the complete executable
            if path_found is False:
                if os.path.isfile(new_command) is True:
                    path_found = True
                    new_command = '"' + new_command + '"'

            # Add on the space
            new_command += r" "

        # Return the new command string with the quoted executable pathname
        return new_command

    # Default is to return the unmodified command
    return command


#-----------------------------------------------------------------------------
# enumerate_apps_from_regkey()
#-----------------------------------------------------------------------------
def enumerate_apps_from_regkey(key):
    """Enumerates the applications from a registry key"""
    i = 0
    while True:
        try:
            # Get the next subkey name
            subkey_name = winreg.EnumKey(key, i)

            # Open the subkey
            subkey_key = winreg.OpenKey(key, subkey_name)

            # See if the values exist for the subkey
            name = reg_query_value(subkey_key, r'DisplayName')
            uninstall = validate_command_pathname(reg_query_value(subkey_key, r'UninstallString'))
            quiet_uninstall = validate_command_pathname(reg_query_value(subkey_key, r'QuietUninstallString'))

            # Close the subkey
            winreg.CloseKey(subkey_key)

            # If the subkey has a display name and an uninstall command, then append it to the list of applications
            if name != "" and uninstall != "":
                INSTALLED_APPS.append({'Name':name, 'Uninstall':uninstall, 'QuietUninstall':quiet_uninstall})

            # Advance to the next subkey
            i += 1

        except WindowsError:
            break


#-----------------------------------------------------------------------------
# enumerate_app_from_user()
#
# Attempt to open the specified subkey for the user.  If it exists, then
# enumerate the applications from it.
#-----------------------------------------------------------------------------
def enumerate_app_from_user(user_key, sub_key):
    """Enumerates applications from the specified user key"""

    try:
        registry_key = winreg.OpenKey(user_key, sub_key)
        enumerate_apps_from_regkey(registry_key)
        winreg.CloseKey(registry_key)

    except WindowsError:
        pass


#-----------------------------------------------------------------------------
# enumerate_apps_from_users()
#
# Applications can be installed for just a user and not system wide.  Scan
# the HKEY_USERS key to enumerate the SIDs of all users and attempt to
# enumerate applications per user.
#-----------------------------------------------------------------------------
def enumerate_apps_from_users():
    """Enumerates the applications installed for users"""
    i = 0
    while True:
        try:
            # Get the next subkey name
            user_sid = winreg.EnumKey(winreg.HKEY_USERS, i)

            # Open the subkey
            user_sid_key = winreg.OpenKey(winreg.HKEY_USERS, user_sid)

            # Enumerate all of the applications for the user
            enumerate_app_from_user(user_sid_key, APPKEY1)

            # Enumerate all of the WOW64 applications for the user
            enumerate_app_from_user(user_sid_key, APPKEY2)

            # Close the subkey
            winreg.CloseKey(user_sid_key)

            # Advance to the next subkey
            i += 1

        except WindowsError:
            break


#-----------------------------------------------------------------------------
# run_command()
#-----------------------------------------------------------------------------
def run_command(command):
    """Runs the provided command"""
    try:
        # Execute the command
        subprocess.run(command,
                       check=True,
                       shell=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)

    except subprocess.CalledProcessError as e:
        print(f"Command failed: [{command}]. Error: {e}")


#-----------------------------------------------------------------------------
# delete_app_query()
#-----------------------------------------------------------------------------
def delete_app_query(name):
    """Queries the user for deleting the application"""

    user_input = input(f"Delete App {name}?: ").lower()
    if user_input in ['y', 'yes']:
        return True

    return False


#-----------------------------------------------------------------------------
# main()
#-----------------------------------------------------------------------------
def main():
    """Main function"""

    # Check if we have admin privileges
    if is_admin() is False:
        print("Administrator privileges are not available")
        return

    # Enumerate the apps from the registry
    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, APPKEY1)
    enumerate_apps_from_regkey(registry_key)
    winreg.CloseKey(registry_key)

    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, APPKEY2)
    enumerate_apps_from_regkey(registry_key)
    winreg.CloseKey(registry_key)

    enumerate_apps_from_users()

    # Parse through the installed applications
    for app in INSTALLED_APPS:

        good_app = False
        name = app['Name']
        uninstall = app['Uninstall']
        quiet_uninstall = app['QuietUninstall']

        # Skip the application if the name is listed in the allowed application list
        for matchapp in ALLOW_APPS:
            if re.search(matchapp, name, flags=re.IGNORECASE):
                print(f"AllowApp: {name}")
                good_app = True

        # Delete the application if it is not good
        if good_app is False:
            if delete_app_query(name) is True:
                print(f"Deleting: {name}")
                if quiet_uninstall != "":
                    run_command(quiet_uninstall)
                else:
                    run_command(uninstall)
            else:
                print(f"Skipping: {name}")


main()
