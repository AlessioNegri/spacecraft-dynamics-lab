cls

sphinx-apidoc -f -o api ../../spacelab

sphinx-build -b html . _build/html
