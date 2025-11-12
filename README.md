# descent

An attempt to help my dad to update his family tree data, possibly involving my
descent into madness.

This is written to allow me to take GEDCOM files from two, fairly archaic,
programs and update them to be a viable import for more modern software.

> This isn't good code, it is written to solve a particular problem
> If you have the same or similar problem... good luck!

## The problem

- My dad originally used the DOS based [Pedigree](https://wiki.pugweb.org.uk/)
back in the early 90's I think.
- He then "updated" to [ScionPC](https://www.tamurajones.net/ScionPC8.0.xhtml)
- Some, now unknown, middle step was used as you can't directly import the
GEDCOM output of Pedigree to ScionPC
- Somewhere in that process data got lost

Thankfully, he didn't get rid of anything so nothing, I think, actually got
lost. Just misplaced.

## Solution

- Pick a modern tool, I went for [Gramps](https://gramps-project.org/blog/),
as the import target.
- Find some third party tool to do most of the heavy lifting. Thanks
[Python Gedcom Parser](https://github.com/nickyreynke/python-gedcom)
- Write a number of scripts to do distinct jobs to try and get to the goal.

## Requirements

- ```python -m venv {path-to-venv}```
- ```source {path-to-venv}/bin/activate```
- [Python Gedcom Parser](https://github.com/nickyreynke/python-gedcom)
  - This repo feels abandoned but it is absolutely good enough for our purposes
  - The pip package is outdated but cloning the repo and importing that gives
  us what we need
  - ```{path-to-venv}/bin/pip install {path-to-cloned-python-gedcom}```

## Scripts

1. ```convert-to-utf8.py``` Simple conversion script as the initial Pedigree
output isn't UTF-8
1. ```pre-processor.py``` Just enough hackery to allow the parser to open the
input file
1. ```updater.py``` Line by line updating of the GEDCOM file
1. ```aligner.py``` Reorder a GEDCOM file to make it easy to compare two
versions in some other tool like [meld](https://meldmerge.org/) or
[WinMerge](https://winmerge.org/)
