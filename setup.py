from setuptools import setup, find_packages

setup(
    name = 'hookiifier',
    version = '0.9',
    license = 'GPLv2',
    packages = find_packages(),
    package_data= {
        'HOOKIIFIER': ['templates/*.mako', 'static/*']
    },
    install_requires = [
        'mysql',
        'mako'
    ],
    entry_points = {
        'console_scripts': [
            'hookiifier = HOOKIIFIER.hookiifier:main'
        ]
    }
)
