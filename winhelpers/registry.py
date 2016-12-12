import winreg
import win32process
#from .util import is32bit_py, is64bit_os

# Windows registry access is foobar when 32bit programs run on 64bit OS
wow64 = win32process.IsWow64Process()
rflag = (winreg.KEY_READ | winreg.KEY_WOW64_64KEY) if wow64 else winreg.KEY_READ
wflag =  winreg.KEY_WRITE | winreg.KEY_SET_VALUE
wflag = (wflag | winreg.KEY_WOW64_64KEY) if wow64 else wflag

KEY = winreg.HKEY_LOCAL_MACHINE
GUIDPATH = u"SOFTWARE\Microsoft\Cryptography"
GUIDNAME = u"MachineGuid"


def get_registry_setting(rpath, name):
   reg = winreg.OpenKey(KEY, rpath, access=rflag)
   return winreg.QueryValueEx(reg, name)


def get_registry_settings(rpath):
   reg = winreg.OpenKey(KEY, rpath, access=rflag)
   count = winreg.QueryInfoKey(reg)[1]
   settings = {}
   for i in range(count):
      (name, value, _) = winreg.EnumValue(reg, i)
      settings[name] = value
   return settings


def store_to_registry(data, rkey, rpath):
   try:
      reg = winreg.OpenKey(rkey, rpath, access=wflag)
   except EnvironmentError:
      reg = winreg.CreateKey(rkey, rpath)

   for dk, dv in data.items():
      if type(dv) == str:
         vtype = winreg.REG_SZ
      elif type(dv) == int:
         vtype = winreg.REG_DWORD
      else:
         raise Exception("can only handle strings and integers")
      winreg.SetValueEx(reg, dk, None, vtype, dv)

   winreg.CloseKey(reg)


MACHINE_GUID = get_registry_setting(GUIDPATH, GUIDNAME)
