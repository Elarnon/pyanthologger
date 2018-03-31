from setuptools import setup, find_packages
from os import path

setup(
    name='pyanthologger',
    version='0.2.0',
    description='IRC quote bot to use with irctk',
    url='https://github.com/Elarnon/pyanthologger',
    packages=find_packages(),
    package_data={
        'pyanthologger': ['replies'],
    },
    entry_points={
        'console_scripts': [
            'pyanthologger=pyanthologger:main',
        ],
    },
)
