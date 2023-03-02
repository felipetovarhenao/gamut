from setuptools import setup, find_namespace_packages
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text()

MODULE = 'gamut'
VERSION = '1.1.0'
DESCRIPTION = 'Granular Audio Musaicing Toolkit for Python'


def get_install_requires():
    excluded = ['sphinx']
    with open('requirements.txt', 'r') as f:
        return [line for line in f.read().splitlines() if all(x not in line.lower() for x in excluded)]


setup(
    name=MODULE,
    version=VERSION,
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
