cd docs
rm -r -f build
sphinx-apidoc --ext-autodoc -o . .. 
make html