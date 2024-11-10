#-----------------------------------------------------------------------------
# manage_users.py
#
# Copyright (c) 2024 Daniel M. Teal
#
# License: MIT License
#
# Python script to manage users on a system.
#-----------------------------------------------------------------------------
"""manage_users.py""" # for pylint
# pylint: disable=line-too-long

import configparser
import ctypes
import re
import subprocess
import requests
import wmi

from bs4 import BeautifulSoup

WMI_SERVICE = wmi.WMI()

SHELL32 = ctypes.windll.shell32

README_PATH = r'C:\CyberPatriot\Readme.url'

PASSWORD = r'CyberPatriot2024!'

MASTER_ACCOUNT = []
ADMIN_ACCOUNTS = []
USER_ACCOUNTS = []
ALL_ACCOUNTS = []


#-----------------------------------------------------------------------------
# is_admin()
#-----------------------------------------------------------------------------
def is_admin():
    """Returns TRUE if user is an admin"""
    result = SHELL32.IsUserAnAdmin() != 0
    return result


#-----------------------------------------------------------------------------
# parse_url_file()
#
# This function parses the provided file and returns the URL it points to.
#-----------------------------------------------------------------------------
def parse_url_file(url_file_path):
    """Parses URL file to obtain the full URL"""
    config = configparser.ConfigParser()
    config.read(url_file_path)

    result = config.get('InternetShortcut', 'URL')
    return result


#-----------------------------------------------------------------------------
# parse_readme_content()
#
# This function parses readme file to obtain user information
#-----------------------------------------------------------------------------
def parse_readme_content(content):
    """Parses the readme content"""

    # Get the user data in the <pre> section
    soup = BeautifulSoup(content, 'html.parser')
    pre = soup.find_all('pre')
    userdata = str(pre)

    # Parse the user data
    admin_section = False
    user_section = False
    for line in userdata.splitlines():
        if re.search('Authorized Administrators', line):
            admin_section = True
            user_section = False
        elif re.search('Authorized Users', line):
            admin_section = False
            user_section = True
        elif re.search('</pre>', line):
            admin_section = False
            user_section = False
        else:
            words = line.split()
            if len(words) > 0:
                if admin_section is True:
                    if re.search('(you)', line):
                        MASTER_ACCOUNT.append(words[0])
                        ALL_ACCOUNTS.append(words[0])
                    elif len(words) == 1:
                        ADMIN_ACCOUNTS.append(words[0])
                        ALL_ACCOUNTS.append(words[0])
                if user_section is True:
                    USER_ACCOUNTS.append(words[0])
                    ALL_ACCOUNTS.append(words[0])

    return True


#-----------------------------------------------------------------------------
# delete_user()
#
# This function deletes a user account.
#-----------------------------------------------------------------------------
def delete_user(username):
    """Deletes the specified user"""
    try:
        # Construct the command
        command = f"net user {username} /DELETE"

        # Execute the command
        subprocess.run(command,
                       check=True,
                       shell=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        print(f"User {username} deleted successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Failed to delete user {username}. Error: {e}")


#-----------------------------------------------------------------------------
# delete_user_directory()
#
# This function deletes a user directory.
#-----------------------------------------------------------------------------
def delete_user_directory(username):
    """Deletes the specified user"""
    try:
        # Construct the command
        command = f"rd /s /q C:\\Users\\{username}"

        # Execute the command
        subprocess.run(command,
                       check=True,
                       shell=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        print(f"User directory C:\\Users\\{username} deleted successfully.")

    # This may fail since sometimes the user directory does not exist
    except subprocess.CalledProcessError:
        print(f"Failed to delete user directory C:\\Users\\{username}")


#-----------------------------------------------------------------------------
# set_user_password()
#-----------------------------------------------------------------------------
def set_user_password(username):
    """Sets the password for the specified user"""
    try:
        # Construct the command
        command = f"net user {username} {PASSWORD}"

        # Execute the command
        subprocess.run(command,
                       check=True,
                       shell=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        print(f"User {username} password changed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Failed to change password for user {username}. Error: {e}")


#-----------------------------------------------------------------------------
# set_user_admin_access()
#-----------------------------------------------------------------------------
def set_user_admin_access(username, enabled):
    """Sets the password for the specified user"""
    try:
        # Construct the command
        if enabled is True:
            command = f"net localgroup Administrators {username} /add"
        else:
            command = f"net localgroup Administrators {username} /delete"

        # Execute the command
        subprocess.run(command,
                       check=True,
                       shell=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        print(f"User {username} administrator access changed successfully.")

    # We expect this to fail if the user was already correctly set as an administator (or not)
    except subprocess.CalledProcessError:
        print(f"User {username} administrator access was already correct.")


#-----------------------------------------------------------------------------
# parse_readme_for_user_accounts()
#
# This function secures user accounts for the image.
#-----------------------------------------------------------------------------
def parse_readme_for_user_accounts():
    """This function finds user accounts according to the readme"""
    result = True

    # Determine the URL for the readme
    url = parse_url_file(README_PATH)
    print(f"The URL is: {url}")

    # Get the data from the URL with a 10 second timeout
    readme_response = requests.get(url, timeout=10)

    # Parse the readme content to obtain the admin users
    parse_readme_content(readme_response.text)

    print(f"Master account: {MASTER_ACCOUNT}")
    print(f"Admin accounts: {ADMIN_ACCOUNTS}")
    print(f"User accounts: {USER_ACCOUNTS}")

    # Check the number of accounts
    if len(MASTER_ACCOUNT) != 1:
        result = False
    elif len(ADMIN_ACCOUNTS) < 1:
        result = False
    elif len(USER_ACCOUNTS) < 1:
        result = False

    if result is True:
        print(r"Account information obtained successfully!")
    else:
        print(r"Account information was NOT obtained successfully!")
        return result

    return result


#-----------------------------------------------------------------------------
# configure_user_accounts()
#-----------------------------------------------------------------------------
def configure_user_accounts():
    """Process the users"""

    users = WMI_SERVICE.Win32_UserAccount()
    for user in users:

        # Ensure Administrator is disabled
        if user.Name == "Administrator":
            user.PasswordRequired = True
            user.PasswordChangeable = True
            user.PasswordExpires = False
            user.Disabled = True

        # Ensure DefaultAccount is disabled
        elif user.Name == "DefaultAccount":
            user.PasswordChangeable = True
            user.PasswordExpires = False
            user.Disabled = True

        # Ensure Guest is disabled
        elif user.Name == "Guest":
            user.PasswordChangeable = False
            user.PasswordExpires = False
            user.Disabled = True

        # Ensure WDAGUtilityAccount is disabled
        elif user.Name == "WDAGUtilityAccount":
            user.PasswordChangeable = True
            user.PasswordExpires = False
            user.Disabled = True

        # Delete unknown accounts
        elif user.Name not in ALL_ACCOUNTS:
            delete_user(user.Name)
            delete_user_directory(user.Name)

        # Do not modify the master account
        elif user.Name in MASTER_ACCOUNT:
            print(f"User {user.Name} is the master account for this image")

        # Ensure all allowed accounts (except master) have the master password
        else:
            user.PasswordRequired = True
            user.PasswordChangeable = True
            user.PasswordExpires = True
            user.Disabled = False
            set_user_password(user.Name)

            # Update administrator group access
            if user.Name in ADMIN_ACCOUNTS:
                set_user_admin_access(user.Name, True)
            else:
                set_user_admin_access(user.Name, False)


#-----------------------------------------------------------------------------
# main()
#-----------------------------------------------------------------------------
def main():
    """Main function"""

    # Check if we have admin privileges
    if is_admin() is False:
        print("Administrator privileges are not available")
        return

    # Secure the user accounts
    if parse_readme_for_user_accounts() is True:
        configure_user_accounts()


main()
