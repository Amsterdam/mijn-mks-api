"""
Setup voor de MKS koppeling 
"""
from codecs import open

from os import path
from setuptools import setup, find_packages

# Get the long description from the README file
readme_file = path.join(path.abspath(path.dirname(__file__)), 'README.rst')
with open(readme_file, encoding='utf-8') as f:
    proj_readme = f.read()

setup(
    name='mijn-mks-api',
    version='0.0.1',
    description='Koppeling met MKS',
    long_description=proj_readme,
    url='https://github.com/Amsterdam/mijn-mks-api',
    packages=['mks'],
    install_requires=[],

    extras_require={
        'tests': [

        ]
    }
)
