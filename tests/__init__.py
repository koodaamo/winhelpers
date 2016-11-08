from winhelpers.service.windows import MinimalReferenceService
from winhelpers.service.examples.windows import BasicWindowsAsyncioService, \
                                                WindowsAsyncioService, \
                                                WindowsWAMPService

tested_services = (MinimalReferenceService, BasicWindowsAsyncioService, \
                   WindowsAsyncioService, WindowsWAMPService)
