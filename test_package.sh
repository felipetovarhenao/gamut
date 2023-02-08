set -e
python3 setup.py install --record files.txt
gamut --version
gamut --test
xargs rm -rf < files.txt