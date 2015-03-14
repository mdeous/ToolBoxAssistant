# ToolBoxAssistant

An utility to easily manage your toolbox applications.

## Introduction

ToolBoxAssistant works by reading a JSON file containing the toolbox location and applications information.
By default it searches for a `toolbox.json` in the current directory. It can install applications from a
version control system (git / mercurial / subversion), or directly from an archive URL, and supports build
directives if needed.

## Installation

### From source

    python setup.py install

### From PyPI

NOT YET

## Usage


```
usage: tba [-h] [-f FILE] [-v] {sync,genspec} ...

Easily manage your toolbox applications.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  toolbox specfile to use (default: toolbox.json)
  -v, --verbose         display debug information

Subcommands:
  {sync,genspec}        (use "tba <cmd> -h" for commands help)
    sync                synchronize installed applications with specfile
    genspec             generate specfile from installed applications
```

### sync

Reads the specifications file, and automatically install listed applications, or updates them if they are already
installed. If the `-u`/`--unlisted` option is used, a warning is issued if versionned applications are installed
but not listed in the specfile.

```
usage: tba sync [-h] [-u]

optional arguments:
  -h, --help      show this help message and exit
  -u, --unlisted  list installed applications missing from specfile
```

### genspec

Searches for versionned applications in given folder and generate a specfile. If the `-m`/`--merge` option is used,
given file is updated.

```
usage: tba genspec [-h] [-m FILE] path

positional arguments:
  path                  toolbox folder to scan for applications

optional arguments:
  -h, --help            show this help message and exit
  -m FILE, --merge FILE
                        merge found applications with existing specfile
```

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

## Bugs / Feature requests

If you find any bug, or have any feature you would like to see implemented, feel free to fill a ticket in the
issue tracker, or even better, fix/code it by yourself and do a pull-request.

## License

This project is licensed under the GNU GPLv3.
