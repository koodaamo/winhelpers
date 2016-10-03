from setuptools import setup, find_packages
import sys, os

version = '1.5'

setup(name='winhelpers',
      version=version,
      description="Helpers for Python on the Windows platform",
      long_description="",
      classifiers=[
         "Operating System :: Microsoft :: Windows",
         "Environment :: Win32 (MS Windows)",
         "Programming Language :: Python :: 3.5",
         "Programming Language :: Python :: 3",
         "Programming Language :: Python :: 3 :: Only"
      ],
      keywords='',
      author='Petri Savolainen',
      author_email='petri.savolainen@koodaamo.fi',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      setup_requires=['pytest-runner',],
      tests_require=['pytest',],
      install_requires=["pypiwin32",],
      entry_points={
          "console_scripts": ['winhelper = winhelpers.command:winhelper'],
      },
      )
