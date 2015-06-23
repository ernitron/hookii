from setuptools import setup, find_packages

setup(
    name = 'hookiifier',
    version = '0.9',
    license = 'GPLv2',
    packages = find_packages(),
    package_data= {
        'HOOKIIFIER': ['templates/*.mako']
    },
    install_requires = [
        'mysql',
    ],
    entry_points = {
        'console_scripts': [
            'hookii-archive = HOOKIIFIER.hookiifier:main'
        ]
    }
)
