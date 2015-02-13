# ToolBoxAssistant

An utility to easily manage your toolbox applications.

## Introduction

ToolBoxAssistant works by reading a JSON file containing the toolbox location and applications information.
By default it searches for a `toolbox.json` in the current directory.

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

## The `toolbox.json` file

The following JSON example shows all the specifications that can be defined within the `toolbox.json` file:

```javascript
{
  "path": "/tmp/toolbox-example",
  "apps": {
    "sqlmap": {
      "type": "git",
      "url": "https://github.com/sqlmapproject/sqlmap",
      "path": "web/sqlmap"
    },
    "androguard": {
      "type": "hg",
      "url": "https://code.google.com/p/androguard/",
      "path": "mobility/androguard"
    },
    "skipfish": {
      "type": "svn",
      "url": "http://skipfish.googlecode.com/svn/trunk/",
      "path": "web/skipfish",
      "build": [
        "make"
      ]
    },
    "nmap": {
      "type": "archive",
      "url": "https://nmap.org/dist/nmap-6.47.tar.bz2",
      "path": "network/nmap",
      "build": [
        "./configure",
        "make"
      ]
    }
  }
}


```

## License

This project is licensed under the GNU GPLv3.
