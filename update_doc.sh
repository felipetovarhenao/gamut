cd doc
rm -r -f build
sphinx-apidoc --ext-autodoc -o . .. 
make html
open -a "Google Chrome" ./build/html/index.html