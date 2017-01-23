import sys, os, re, logging, tempfile
from logging import FileHandler
from logging.handlers import NTEventLogHandler


# Windows servicemanager eats exceptions, so need some extra logging magic...

def log_exception(exception_logger, exctype, value, tb):
   exception_logger.error("%s (%s): %s" % (exctype, value, tb))


# Utilities for service creation

def ccc(name): # Camel Case Converter
   s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
   return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)


def set_service_metadata(name, dct):
   dct["_svc_name_"] = name
   nname = ccc(name) # normalized
   dct["_svc_display_name_"] = nname + " service base"
   dct["_svc_description_"] =   "A subclassable " + nname + " service base"
   return dct


def servicemetadataprovider(cls):
   "class decorator for setting the metadata"
   name = cls.__name__
   cls._svc_name_ = name
   nname = ccc(name) # normalized
   cls._svc_display_name_ = nname + " service base"
   cls._svc_description_ =   "A subclassable " + nname + " service base"
   return cls


def eventloggerprovider(cls):
   "create new logger using class name"
   logger = logging.getLogger(cls.__name__)
   level = getattr(cls, "LOGLEVEL", logging.DEBUG)
   logger.setLevel(level)

   if sys.platform == "win32":
      logger.addHandler(NTEventLogHandler(cls.__name__))

   if os.environ.get("EVENTLOGGER_FILE"):
      tempdir = tempfile.gettempdir()
      logger.addHandler(FileHandler(tempdir + os.sep + "testing.log"))

   cls._logger = logger
   return cls
