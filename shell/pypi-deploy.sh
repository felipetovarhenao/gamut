rm -r -f build
rm -r -f dist
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
