import platform
import winreg

bitness = platform.architecture()[0]
bflag = winreg.KEY_WOW64_32KEY if bitness == "32bit" else winreg.KEY_WOW64_64KEY

KEY = winreg.HKEY_LOCAL_MACHINE
GUIDPATH = u"SOFTWARE\Microsoft\Cryptography"
GUIDNAME = u"MachineGuid"


def get_registry_setting(rpath, name):
   rflag = winreg.KEY_READ | bflag
   reg = winreg.OpenKey(KEY, rpath, access=rflag)
   return winreg.QueryValueEx(reg, name)


def get_registry_settings(rpath):
   rflag = winreg.KEY_READ | bflag
   reg = winreg.OpenKey(KEY, rpath, access=rflag)
   count = winreg.QueryInfoKey(reg)[1]
   settings = {}
   for i in range(count):
      (name, value, _) = winreg.EnumValue(reg, i)
      settings[name] = value
   return settings


def store_to_registry(data, rkey, rpath):
   wflag =  winreg.KEY_WRITE | winreg.KEY_SET_VALUE | bflag
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
