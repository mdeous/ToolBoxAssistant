# -*- coding: utf-8 -*-
import os
import re
try:
    import simplejson as json
except ImportError:
    import json

from ToolBoxAssistant.app import AppFactory
from ToolBoxAssistant.helpers import get_svn_url, readfile, find_versionned_folders, yes_no, Color
from ToolBoxAssistant.log import logger

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
        self.config_dir = None

    def setup_config_dir(self, path):
        self.config_dir = os.path.join(
            self.config_basedir,
            path.replace(os.path.sep, '_').strip('_')
        )
        if not os.path.exists(self.config_dir):
            logger.debug('creating configuration folder: %s' % Color.GREEN+self.config_dir+Color.END)
            os.makedirs(self.config_dir)

    def load_specs(self, fpath):
        """
        Loads a specifications file and checks for missing fields.
        """
        with open(fpath) as ifile:
            logger.debug('loading specfile: %s' % Color.GREEN+fpath+Color.END)
            data = json.load(ifile)
        for field in self.tba_required_fields:
            if field not in data:
                logger.error('missing top-level field in specs: %s' % Color.GREEN+field+Color.END)
                return None
        for app_name in data['apps']:
            app_specs = data['apps'][app_name]
            for app_field in self.app_required_fields:
                if app_field not in app_specs:
                    logger.error('missing app field in specs: %s' % Color.GREEN+app_field+Color.END)
                    return None
        return data

    def do_sync(self, args):
        """
        Synchronizes installed application with the specfile.
        """
        if (not os.path.exists(args.file)) or (not os.path.isfile(args.file)):
            logger.error('file not found: %s' % Color.GREEN+args.file+Color.END)
            return
        specs = self.load_specs(args.file)
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
        if args.unlisted:
            for _, folder in find_versionned_folders(rootpath):
                folder, app_name = os.path.split(folder)
                logger.warn('found unlisted application in %s: %s' % (
                    folder, Color.GREEN+app_name+Color.END
                ))

    def do_genspec(self, args):
        """
        Scans current folder for versionned applications and
        creates a specfile accordingly.
        """
        self.setup_config_dir(args.path)
        new_specs = {
            'path': args.path,
            'apps': {}
        }
        if args.merge is not None:
            new_specs = self.load_specs(args.merge)
        apps_specs = new_specs['apps']
        new_apps_found = False
        for vcs_type, app_folder in find_versionned_folders(args.path):
            app_path = app_folder[len(args.path)+1:]
            if app_path not in [apps_specs[a]['path'] for a in apps_specs]:
                new_apps_found = True
                folder, app_name = os.path.split(app_folder)
                logger.info('found%s application in %s: %s (%s)' % (
                    ' new' if args.merge is not None else '',
                    folder, Color.GREEN+app_name+Color.END, vcs_type
                ))
                cfg_file, regex, handler = self.vcs_repo_finders[vcs_type]
                cfg_path = os.path.join(app_folder, cfg_file)
                app_specs = {
                    'type': vcs_type,
                    'url': handler(regex, cfg_path),
                    'path': app_path,
                }
                apps_specs[app_name] = app_specs
        if new_apps_found:
            outfile = args.merge or args.file
            if os.path.exists(outfile):
                logger.warning('file already exists: %s' % Color.GREEN+outfile+Color.END)
                if not yes_no('Overwrite ?'):
                    logger.error('operation aborted by user')
                    return
            with open(outfile, 'w') as ofile:
                json.dump(new_specs, ofile, sort_keys=True, indent=2, separators=(',', ': '))
            logger.info('specfile written to %s' % Color.GREEN+outfile+Color.END)
            logger.info('you may now add build information to the new specfile')
        else:
            logger.info('no new application found')
