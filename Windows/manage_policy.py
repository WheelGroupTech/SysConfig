#-----------------------------------------------------------------------------
# manage_policy.py
#
# Copyright (c) 2024 Daniel M. Teal
#
# Python script to manage system security policy.
#-----------------------------------------------------------------------------
"""manage_policy.py""" # for pylint
# pylint: disable=line-too-long

import ctypes
import subprocess

SHELL32 = ctypes.windll.shell32


#-----------------------------------------------------------------------------
# is_admin()
#-----------------------------------------------------------------------------
def is_admin():
    """Returns TRUE if user is an admin"""
    result = SHELL32.IsUserAnAdmin() != 0
    return result


#-----------------------------------------------------------------------------
# set_password_policy()
#-----------------------------------------------------------------------------
def set_password_policy():
    """Sets the password policy"""
    try:
        # Construct the command by setting the password policy
        command = r"net accounts /uniquepw:24 /minpwlen:12 /maxpwage:90 /minpwage:1"

        # Extend the command by adding lockout settings
        command += r" /lockoutthreshold:10 /lockoutduration:30 /lockoutwindow:30"

        # Execute the command
        subprocess.run(command,
                       check=True,
                       shell=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        print(r"Password policy set successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Failed to set password policy. Error: {e}")


#-----------------------------------------------------------------------------
# enable_firewall_defaults()
#-----------------------------------------------------------------------------
def enable_firewall_defaults():
    """Resets the firewall to defaults"""
    try:
        # Construct the command
        command = r"netsh advfirewall reset"

        # Execute the command
        subprocess.run(command,
                       check=True,
                       shell=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        print(r"Firewall successfully reset.")

    except subprocess.CalledProcessError as e:
        print(f"Failed to reset the firewall. Error: {e}")


#-----------------------------------------------------------------------------
# Secure registry policy settings
#-----------------------------------------------------------------------------
REG = [
       # Windows auomatic updates
       r'"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update" /v AUOptions /t REG_DWORD /d 3 /f',

       # Turns on UAC
       r'"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA /t REG_DWORD /d 1 /f',

       # Secure Internet Explorer
       r'"HKCU\Software\Microsoft\Internet Explorer\Main" /v DoNotTrack /t REG_DWORD /d 1 /f',
       r'"HKCU\Software\Microsoft\Internet Explorer\Download" /v RunInvalidSignatures /t REG_DWORD /d 1 /f',
       r'"HKCU\Software\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_LOCALMACHINE_LOCKDOWN\Settings" /v LOCALMACHINE_CD_UNLOCK /t REG_DWORD /d 1 /f',
       r'"HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v WarnonBadCertRecving /t REG_DWORD /d 1 /f',
       r'"HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v WarnOnPostRedirect /t REG_DWORD /d 1 /f',
       r'"HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v WarnonZoneCrossing /t REG_DWORD /d 1 /f',
       r'"HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v DisablePasswordCaching /t REG_DWORD /d 1 /f', 

       # Disable autorun for CDROM drives
       r'"HKCU\SYSTEM\CurrentControlSet\Services\CDROM" /v AutoRun /t REG_DWORD /d 0 /f',

       # Disable Windows crash dumps
       r'"HKLM\SYSTEM\CurrentControlSet\Control\CrashControl" /v CrashDumpEnabled /t REG_DWORD /d 0 /f',

       # Restrict CD ROM drive
       r'"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v AllocateCDRoms /t REG_DWORD /d 1 /f',

       # Automatic Admin logon - disables auto logon of ALL admin users - ensure the account and password are known before enabling
       # r'"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v AutoAdminLogon /t REG_DWORD /d 0 /f',

       # Logo message text
       r'"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v LegalNoticeText /t REG_SZ /d "CyberEagle Use Only" /f',

       # Logon message title bar
       r'"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v LegalNoticeCaption /t REG_SZ /d "CyberEagles" /f',

       # Wipe page file from shutdown
       r'"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v ClearPageFileAtShutdown /t REG_DWORD /d 1 /f',

       # Disallow remote access to floppie disks
       r'"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v AllocateFloppies /t REG_DWORD /d 1 /f',

       # Prevent print driver installs
       r'"HKLM\SYSTEM\CurrentControlSet\Control\Print\Providers\LanMan Print Services\Servers" /v AddPrinterDrivers /t REG_DWORD /d 1 /f',

       # Limit local account use of blank passwords to console
       r'"HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v LimitBlankPasswordUse /t REG_DWORD /d 1 /f',

       # Auditing access of Global System Objects
       r'"HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v auditbaseobjects /t REG_DWORD /d 1 /f',

       # Auditing Backup and Restore
       r'"HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v fullprivilegeauditing /t REG_DWORD /d 1 /f',

       # Disable AutoRun and AutoPlay
       r'"HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 255 /f'

       # Do not display last user on logon
       r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v dontdisplaylastusername /t REG_DWORD /d 1 /f',

       # UAC setting (Prompt on Secure Desktop)
       r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v PromptOnSecureDesktop /t REG_DWORD /d 1 /f',

       # Enable Installer Detection
       r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableInstallerDetection /t REG_DWORD /d 1 /f',

       # Undock without logon
       r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v undockwithoutlogon /t REG_DWORD /d 0 /f',

       # Maximum Machine Password Age
       r'HKLM\SYSTEM\CurrentControlSet\services\Netlogon\Parameters /v MaximumPasswordAge /t REG_DWORD /d 15 /f',

       # Disable machine account password changes
       r'HKLM\SYSTEM\CurrentControlSet\services\Netlogon\Parameters /v DisablePasswordChange /t REG_DWORD /d 1 /f',

       # Require Strong Session Key
       r'HKLM\SYSTEM\CurrentControlSet\services\Netlogon\Parameters /v RequireStrongKey /t REG_DWORD /d 1 /f',

       # Require Sign/Seal
       r'HKLM\SYSTEM\CurrentControlSet\services\Netlogon\Parameters /v RequireSignOrSeal /t REG_DWORD /d 1 /f',

       # Sign Channel
       r'HKLM\SYSTEM\CurrentControlSet\services\Netlogon\Parameters /v SignSecureChannel /t REG_DWORD /d 1 /f',

       # Seal Channel
       r'HKLM\SYSTEM\CurrentControlSet\services\Netlogon\Parameters /v SealSecureChannel /t REG_DWORD /d 1 /f',

       # Don't disable CTRL+ALT+DEL
       r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v DisableCAD /t REG_DWORD /d 0 /f',

       # Restrict Anonymous Enumeration #1
       r'HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v restrictanonymous /t REG_DWORD /d 1 /f',

       # Restrict Anonymous Enumeration #2
       r'HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v restrictanonymoussam /t REG_DWORD /d 1 /f',

       # Idle Time Limit - 45 mins
       r'HKLM\SYSTEM\CurrentControlSet\services\LanmanServer\Parameters /v autodisconnect /t REG_DWORD /d 45 /f',

       # Require Security Signature - Disabled pursuant to checklist
       r'HKLM\SYSTEM\CurrentControlSet\services\LanmanServer\Parameters /v enablesecuritysignature /t REG_DWORD /d 0 /f',

       # Enable Security Signature - Disabled pursuant to checklist
       r'HKLM\SYSTEM\CurrentControlSet\services\LanmanServer\Parameters /v requiresecuritysignature /t REG_DWORD /d 0 /f',

       # Disable Domain Credential Storage
       r'HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v disabledomaincreds /t REG_DWORD /d 1 /f',

       # Don't Give Anons Everyone Permissions
       r'HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v everyoneincludesanonymous /t REG_DWORD /d 0 /f',

       # SMB Passwords unencrypted to third party? No
       r'HKLM\SYSTEM\CurrentControlSet\services\LanmanWorkstation\Parameters /v EnablePlainTextPassword /t REG_DWORD /d 0 /f',

       # Null Session Pipes Cleared
       r'HKLM\SYSTEM\CurrentControlSet\services\LanmanServer\Parameters /v NullSessionPipes /t REG_MULTI_SZ /d "" /f',

       # Remotely accessible registry paths cleared
       r'HKLM\SYSTEM\CurrentControlSet\Control\SecurePipeServers\winreg\AllowedExactPaths /v Machine /t REG_MULTI_SZ /d "" /f',

       # Remotely accessible registry paths and sub-paths cleared
       r'HKLM\SYSTEM\CurrentControlSet\Control\SecurePipeServers\winreg\AllowedPaths /v Machine /t REG_MULTI_SZ /d "" /f',

       # Restict anonymous access to named pipes and shares
       r'HKLM\SYSTEM\CurrentControlSet\services\LanmanServer\Parameters /v NullSessionShares /t REG_MULTI_SZ /d "" /f',

       # Allow to use Machine ID for NTLM
       r'HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v UseMachineId /t REG_DWORD /d 0 /f',

      ]


#-----------------------------------------------------------------------------
# set_registry_policy_settings()
#-----------------------------------------------------------------------------
def set_registry_policy_settings():
    """Sets secure registry settings"""

    for reg_cmd in REG:
        try:
            # Construct the command
            command = f"reg add {reg_cmd}"

            # Execute the command
            subprocess.run(command,
                           check=True,
                           shell=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            print(f"RegSuccess {reg_cmd}")

        except subprocess.CalledProcessError as e:
            print(f"RegFailure {reg_cmd} Error: {e}")


#-----------------------------------------------------------------------------
# main()
#-----------------------------------------------------------------------------
def main():
    """Main function"""

    # Check if we have admin privileges
    if is_admin() is False:
        print("Administrator privileges are not available")
        return

    # Set the password policy
    set_password_policy()

    # Reset the firewall
    enable_firewall_defaults()

    # Set the registry settings
    set_registry_policy_settings()

main()
