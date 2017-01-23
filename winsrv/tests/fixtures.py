import sys
from pytest import fixture
import win32service, win32serviceutil


@fixture
def installed(service):
   "Provide instllation and removal of Windows Service class"

   service.install_service()

   # return the installed class
   yield service

   service.remove_service()
