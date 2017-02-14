# winsrv

Easy-to-use base class and mixin for Windows Service creation and management.
Basically just some wrappers around pywin32 win32serviceutil stuff and some
helpful class decorators.

For usage example, see tests/test_service.py

Known to work on Windows 7. Usage reports on Windows 8 & 10 welcome.

When submitting issues, please first run "pytest" and attach results from
failing tests.

