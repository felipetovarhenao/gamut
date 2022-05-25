from setuptools import setup, find_packages
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text()

MODULE = 'gamut'
VERSION = '0.1.8.2'
DESCRIPTION = 'Granular Audio Musaicing Toolkit for Python'

setup(
	name=MODULE,
	version=VERSION,
	author='Felipe Tovar-Henao',
	author_email='<felipe.tovar.henao@gmail.com>',
	description=DESCRIPTION,
	packages=find_packages(),
	license='OSI Approved :: ISC License (ISCL)',
	install_requires=['progress', 'librosa', 'sounddevice'],
	keywords=['DSP', 'audio musaicing', 'granulation', 'machine learning', 'ML', "MIR", 'music', 'sound design', 'concatenative synthesis'],
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