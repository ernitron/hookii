import sys
from setuptools import setup, find_packages

if sys.version_info < (2, 6):
    print('Python 2.6 or greater is required.')
    sys.exit(1)

if sys.version_info >= (3,):
    mysql = 'mysqlclient'
else:
    mysql = 'mysql'

setup(
    name = 'hookiifier',
    version = '0.9',
    license = 'GPLv2',
    packages = find_packages(),
    package_data= {
        'HOOKIIFIER': ['templates/*.mako', 'static/*']
    },
    install_requires = [
        mysql,
        'mako'
    ],
    entry_points = {
        'console_scripts': [
            'hookiifier = HOOKIIFIER.hookiifier:main'
        ]
    }
)
