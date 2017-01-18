"""
import platform
import winreg
import win32process

win32process.IsWow64Process()

bitness = platform.architecture()[0]
bflag = winreg.KEY_WOW64_32KEY if bitness == "32bit" else winreg.KEY_WOW64_64KEY

KEY = winreg.HKEY_LOCAL_MACHINE
GUIDPATH = u"SOFTWARE\Microsoft\Cryptography"
GUIDNAME = u"MachineGuid"

rflag = winreg.KEY_READ | bflag
reg = winreg.OpenKey(KEY, rpath, access=rflag)
return winreg.QueryValueEx(reg, name)
"""
