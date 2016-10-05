import winreg

KEY = winreg.HKEY_LOCAL_MACHINE
GUIDPATH = u"SOFTWARE\Microsoft\Cryptography"
GUIDNAME = u"MachineGuid"

def get_registry_setting(rpath, name):
   reg = winreg.OpenKey(KEY, rpath)
   return winreg.QueryValueEx(reg, name)

def get_registry_settings(rpath):
   reg = winreg.OpenKey(KEY, rpath)
   count = winreg.QueryInfoKey(reg)[1]
   settings = {}
   for i in range(count):
      (name, value, _) = winreg.EnumValue(reg, i)
      settings[name] = value
   return settings

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
      winreg.SetValueEx(reg, dk, None, vtype, dv)

   winreg.CloseKey(reg)


MACHINE_GUID = get_registry_setting(GUIDPATH, GUIDNAME)
