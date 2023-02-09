set -e
rm -r -f build
rm -r -f dist
pip3 uninstall gamut==$1
python3 setup.py sdist bdist_wheel
twine upload --repository testpypi dist/*
