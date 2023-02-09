CURRENT=$(pip3 freeze | grep gamut)
if [[ $CURRENT ]]; then
	echo '...removing gamut...'
	for package in $CURRENT; do
		pip3 uninstall $package
	done
fi
python3 setup.py install --record files.txt
