import os.path
import codecs
from setuptools import setup, find_namespace_packages
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text()

MODULE = 'gamut'
DESCRIPTION = 'Granular Audio Musaicing Toolkit for Python'


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def get_install_requires():
    excluded = ['sphinx']
    with open('requirements.txt', 'r') as f:
        return [line for line in f.read().splitlines() if all(x not in line.lower() for x in excluded)]


setup(
    name=MODULE,
    version=get_version('gamut/__version__.py'),
    author='Felipe Tovar-Henao',
    author_email='<felipe.tovar.henao@gmail.com>',
    description=DESCRIPTION,
    url='https://felipetovarhenao.github.io/gamut',
    packages=find_namespace_packages(),
    license='OSI Approved :: ISC License (ISCL)',
    include_package_data=True,
    entry_points={
        'console_scripts': ['gamut=gamut:cli', 'gamut-ui=gamut:gui']
    },
    install_requires=get_install_requires(),
    keywords=['DSP', 'audio musaicking', 'granulation', 'machine learning',
              'ML', "MIR", 'music', 'sound design', 'concatenative synthesis'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Other Audience',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
