import winreg

KEY = winreg.HKEY_LOCAL_MACHINE
GUIDPATH = u"SOFTWARE\Microsoft\Cryptography"
GUIDNAME = u"MachineGuid"

def get_setting(rpath, name):
   reg = winreg.OpenKey(KEY, rpath)
   return winreg.QueryValueEx(reg, name)

MACHINE_GUID = get_setting(GUIDPATH, GUIDNAME)

def store_to_registry(data, rkey, rpath):
   try:
      reg = winreg.OpenKey(rkey, rpath)
   except EnvironmentError:
      reg = winreg.CreateKey(rkey, rpath)

   for dk, dv in data.items():
      if type(dv) == str:
         vtype = winreg.REG_SZ
      elif type(dv) == int:
         vtype = winreg.REG_DWORD
      else:
         raise Exception("can only handle strings and integers")
      SetValue(reg, dk, vtype, dv)

   winreg.CloseKey(reg)

