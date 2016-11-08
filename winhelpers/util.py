import sys, re, logging
from logging.handlers import NTEventLogHandler


# Windows logger factory

def get_windows_logger(name="Python Windows service", level=logging.INFO):
   logger = logging.getLogger(name)
   logger.setLevel(level)
   logger.addHandler(NTEventLogHandler(name))
   return logger


# Windows servicemanager eats exceptions, so need some extra logging magic...

exception_logger = get_windows_logger(name="Python exceptions", level=logging.DEBUG)

def log_exception(exctype, value, tb):
   exception_logger.error("%s (%s): %s" % (exctype, value, tb))

sys.excepthook = log_exception


# Utilities for service creation

def set_logger(name, dct):
   dct["logger"] = get_windows_logger(name=name)
   return dct

def ccc(name): # Camel Case Converter
   s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
   return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)


def servicemetadataprovider(cls):
   "class decorator for setting the metadata"
   name = cls.__name__
   cls._svc_name_ = name
   nname = ccc(name) # normalized
   cls._svc_display_name_ = nname + " service base"
   cls._svc_description_ =   "A subclassable " + nname + " service base"
   return cls
