# winsrv

Easy-to-use base class and mixin for Windows Service creation and management.
Basically just some wrappers around pywin32 win32serviceutil stuff and some
helpful class decorators.

For usage example, see tests/test_service.py

Tests pass at least on Windows 7 and Windows 10. Usage reports on other 
modern Windows OSes welcome.

When submitting issues, please first run "pytest" and attach results from
failing tests.

