# ToolBoxAssistant

An utility to easily manage your toolbox applications.

## Introduction

ToolBoxAssistant works by reading a JSON file containing the toolbox location and applications information.
By default it searches for a `toolbox.json` in the current directory.

For an example JSON file containing all the possible keys and values it can contain, see the `example.json` file.

## Installation

### From source

    python setup.py install

### From PyPI

NOT YET

## Usage

```
$ tba -h
usage: tba [-h] [-d] [-f FILE] {sync,check,genspec}

Easily manage your toolbox applications.

positional arguments:
  {sync,check,genspec}

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           display external commands output
  -f FILE, --file FILE  toolbox specifications file to use
```

### sync

Reads the specifications file, and automatically install listed applications. Already installed applications
are updated if they are versionned.

### check

NOT IMPLEMENTED YET

### genspec

NOT IMPLEMENTED YET

## License

This project is licensed under the GNU GPLv3.
