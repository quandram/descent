# descent

An attempt to help my dad to update his family tree data, possibly involving my descent into madness

## Requirements

- ```python -m venv {path-to-venv}```
- ```source {path-to-venv}/bin/activate```
- [Python Gedcom Parser](https://github.com/nickyreynke/python-gedcom)
  - This repo feels abandoned but it is absolutely good enough for our purposes
  - The pip package is outdated but cloning the repo and importing that gives us what we need
  - ```{path-to-venv}/bin/pip install {path-to-cloned-python-gedcom}```

## Scripts

1. ```convert-to-utf8.py``` Simple conversion script as the initial Pedigree output isn't UTF-8
1. ```pre-processor.py``` Just enough hackery to allow the parser to open the input file
1. ```updater.py``` Line by line updating of the GEDCOM file

