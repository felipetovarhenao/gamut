from sys import executable
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text()

MODULE = 'gamut'
VERSION = '1.0.10-dev1'
DESCRIPTION = 'Granular Audio Musaicing Toolkit for Python'


class GamutInstall(install):
    """
    Ensures correct kivy installation with pip
    """

    def run(self):
        subprocess.run([executable, '-m', 'pip', 'install', '"kivy[base]"'])
        super().run()


setup(
    name=MODULE,
    version=VERSION,
    author='Felipe Tovar-Henao',
    author_email='<felipe.tovar.henao@gmail.com>',
    description=DESCRIPTION,
    url='https://felipetovarhenao.github.io/gamut',
    packages=find_packages(),
    license='OSI Approved :: ISC License (ISCL)',
    include_package_data=True,
    entry_points={
        'console_scripts': ['gamut=gamut:cli', 'gamut-ui=gamut:gui']
    },
    cmdclass={'install': GamutInstall},
    install_requires=[
        'librosa',
        'matplotlib',
        'numpy',
        'progress',
        'PySoundFile',
        'scipy',
        'SoundFile',
        'sounddevice',
        'typing_extensions',
        'filetype'
    ],
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
