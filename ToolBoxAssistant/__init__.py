# -*- coding: utf-8 -*-
import os
import re
from argparse import ArgumentParser
try:
    import simplejson as json
except ImportError:
    import json

from ToolBoxAssistant.app import AppFactory
from ToolBoxAssistant.helpers import get_svn_url, readfile, find_versionned_folders, yes_no
from ToolBoxAssistant.log import get_logger

VERSION = '0.1'


class ToolBoxAssistant(object):
    """
    The main class
    """
    config_basedir = os.path.join(os.path.expanduser('~'), '.tba')
    tba_required_fields = ['path', 'apps']
    app_required_fields = ['type', 'url', 'path']
    vcs_repo_finders = {
        'git': (
            '.git/config',
            re.compile(r'\[remote "origin"\]\s+url = (.*)$', re.M),
            lambda regex, cfg: regex.search(readfile(cfg)).group(1)
        ),
        'hg': (
            '.hg/hgrc',
            re.compile(r'default = (.*)$'),
            lambda regex, cfg: regex.search(readfile(cfg)).group(1)
        ),
        'svn': (
            '',
            re.compile(r'Repository Root: (.*)$', re.M),
            get_svn_url
        )
    }

    def __init__(self):
        self.log = get_logger('tba')
        self.config_dir = None
        self.args = None

    def setup_config_dir(self, path):
        self.config_dir = os.path.join(
            self.config_basedir,
            path.replace(os.path.sep, '_').strip('_')
        )
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def load_specs(self, fpath):
        """
        Loads a specifications file and checks for missing fields.
        """
        with open(fpath) as ifile:
            data = json.load(ifile)
        for field in self.tba_required_fields:
            if field not in data:
                self.log.error('missing top-level field in specs: %s' % field)
                return None
        for app_name in data['apps']:
            app_specs = data['apps'][app_name]
            for app_field in self.app_required_fields:
                if app_field not in app_specs:
                    self.log.error('missing app field in specs: %s' % app_field)
                    return None
        return data

    def do_sync(self):
        """
        Synchronizes installed application with the specfile.
        """
        if (not os.path.exists(self.args.file)) or (not os.path.isfile(self.args.file)):
            self.log.error('File not found: %s' % self.args.file)
            return
        specs = self.load_specs(self.args.file)
        if specs is None:
            return
        self.setup_config_dir(specs['path'])
        rootpath = specs['path']
        for app_name in specs['apps']:
            app_specs = specs['apps'][app_name]
            if not app_specs['path'].startswith(os.path.sep):
                app_specs['path'] = os.path.join(rootpath, app_specs['path'])
            app = AppFactory.load(self, app_name, app_specs)
            app.sync()
            if app.is_updated:
                app.build()
        if self.args.unlisted:
            for _, folder in find_versionned_folders(rootpath):
                folder, app_name = os.path.split(folder)
                self.log.warn('found unlisted application in %s: %s' % (folder, app_name))

    def do_genspec(self):
        """
        Scans current folder for versionned applications and
        creates a specfile accordingly.
        """
        self.setup_config_dir(self.args.path)
        new_specs = {
            'path': self.args.path,
            'apps': {}
        }
        if self.args.merge is not None:
            new_specs = self.load_specs(self.args.merge)
        apps_specs = new_specs['apps']
        for vcs_type, app_folder in find_versionned_folders(self.args.path):
            folder, app_name = os.path.split(app_folder)
            self.log.info('found application in %s: %s (%s)' % (folder, app_name, vcs_type))
            cfg_file, regex, handler = self.vcs_repo_finders[vcs_type]
            cfg_path = os.path.join(app_folder, cfg_file)
            app_specs = {
                'type': vcs_type,
                'url': handler(regex, cfg_path),
                'path': app_folder[len(self.args.path)+1:],
            }
            apps_specs[app_name] = app_specs

        outfile = self.args.merge or self.args.file
        if os.path.exists(outfile):
            self.log.warning('file already exists: %s' % outfile)
            if not yes_no('Overwrite ?'):
                self.log.error('operation aborted by user')
                return
        with open(outfile, 'w') as ofile:
            json.dump(new_specs, ofile, sort_keys=True, indent=2, separators=(',', ': '))
        self.log.info('specfile written to %s' % outfile)
        self.log.info('you may now add build information to the new specfile')

    def run(self):
        """
        Main entry-point.
        """
        parser = ArgumentParser(description='Easily manage your toolbox applications.')
        parser.add_argument(
            '-f', '--file',
            help='toolbox specfile to use (default: toolbox.json)',
            default='toolbox.json'
        )
        subparsers = parser.add_subparsers(
            title='Subcommands',
            help='(use "%(prog)s <cmd> -h" for commands help)',
            dest='action'
        )

        sync_parser = subparsers.add_parser(
            'sync',
            help='synchronize installed applications with specfile'
        )
        sync_parser.add_argument(
            '-u', '--unlisted',
            help='list installed applications missing from specfile',
            action='store_true'
        )
        sync_parser.add_argument(
            '-v', '--verbose',
            help='display external commands output',
            action='store_true'
        )
        sync_parser.set_defaults(func=self.do_sync)

        genspec_parser = subparsers.add_parser(
            'genspec',
            help='generate specfile from installed applications (NOT IMPLEMENTED YET)'
        )
        genspec_parser.add_argument(
            'path',
            help='toolbox folder to scan for applications'
        )
        genspec_parser.add_argument(
            '-m', '--merge',
            help='merge found applications with existing specfile',
            metavar='FILE'
        )
        genspec_parser.set_defaults(func=self.do_genspec)

        args = parser.parse_args()
        if not args.file.startswith(os.path.sep):
            args.file = os.path.join(os.getcwd(), args.file)
        self.args = args
        self.args.func()
