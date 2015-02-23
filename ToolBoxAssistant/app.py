# -*- coding: utf-8 -*-
import os
import shlex
import tarfile
from subprocess import Popen, PIPE
from tempfile import gettempdir
from urllib2 import urlopen
from zipfile import ZipFile

from helpers import unnest_dir, chdir


class App(object):
    """
    The base application class.
    """
    def __init__(self, tba, name, specs):
        self.tba = tba
        self.name = name
        self.app_type = specs['type']
        self.url = specs['url']
        self.path = specs['path']
        self.unnest = specs.get('unnest', False)
        self.build_commands = specs.get('build')
        self.is_updated = False

    def _log_output(self, message, logtype='error'):
        message = message if message else 'an unknown error occured'
        method = getattr(self.tba.log, logtype, 'error')
        # message can be an Exception object, convert it to string first
        for line in str(message).splitlines():
            method(line)

    def _run_command(self, cmd):
        cmd = shlex.split(cmd)
        p = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        # display STDOUT content
        if self.tba.debug and stdout:
            self._log_output(stdout, logtype='debug')
        # display an error (STDERR or generic message) if returncode is non-zero
        if p.returncode != 0:
            self._log_output(stderr)
            return False
        # display STDERR content if debug is enabled
        if self.tba.debug and stderr:
            self._log_output(stderr, logtype='warning')  # TODO: display this as WARNING, not ERROR
        return True

    def sync(self):
        op_ok = False
        if not os.path.exists(self.path):
            self.tba.log.info('downloading %s' % self.name)
            op_ok = self.download()
        else:
            self.tba.log.info('updating %s' % self.name)
            op_ok = self.update()
        if op_ok:
            unnest_dir(self.path)

    def build(self):
        if self.build_commands is None:
            return True
        self.tba.log.info('building %s' % self.name)
        op_ok = False
        with chdir(self.path):
            for cmd in self.build_commands:
                op_ok = self._run_command(cmd)
                if not op_ok:
                    break
        return op_ok

    def download(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError


class ArchiveApp(App):
    """
    Archive-based application.
    """
    archive_handlers = {
        'zip': ZipFile,
        'tar': tarfile.open,
        'tar.gz': tarfile.open,
        'tar.bz2': tarfile.open,
    }

    def read_version(self):
        version_file = os.path.join(self.tba.config_dir, self.name)
        if not os.path.exists(version_file):
            return None
        with open(version_file) as ifile:
            version = ifile.read().strip()
        return version

    def store_version(self):
        version_file = os.path.join(self.tba.config_dir, self.name)
        with open(version_file, 'w') as ofile:
            ofile.write(self.url.split('/')[-1].split('?')[0])

    def build(self):
        op_ok = super(ArchiveApp, self).build()
        if op_ok:
            self.store_version()
        return op_ok

    def download(self):
        fname = self.url.split('/')[-1].split('?')[0]
        temppath = os.path.join(gettempdir(), fname)
        opener = urlopen(self.url)
        try:
            data = opener.read()
        except Exception as err:
            self._log_output(err)
            return False
        with open(temppath, 'wb') as ofile:
            ofile.write(data)
        handler = None
        for extension in self.archive_handlers:
            if fname.endswith(extension):
                handler = self.archive_handlers[extension]
                break
        if handler is None:
            self.tba.log.error('unsupported archive for application %s' % self.name)
            return False
        mode = 'r'
        archive_type = fname.split('.')[-1]
        if archive_type in ('gz', 'bz2'):
            mode = 'r:%s' % archive_type
        archive = handler(temppath, mode=mode)
        archive.extractall(self.path)
        os.remove(temppath)
        self.is_updated = True
        return True

    def update(self):
        if self.read_version() == self.url.split('/')[-1].split('?')[0]:
            return True
        return self.download()


class VersionedApp(App):
    """
    Version controlled application.
    """
    download_commands = {
        'git': 'git clone %s %s',
        'hg': 'hg clone %s %s',
        'svn': 'svn checkout %s %s'
    }
    update_commands = {
        'git': ['git pull origin master'],
        'hg': [
            'hg pull -r tip default',
            'hg update'
        ],
        'svn': ['svn update']
    }

    def download(self):
        if self.app_type not in self.download_commands:
            self.tba.log.error('unsupported VCS for application %s' % self.name)
            return False
        cmd = self.download_commands[self.app_type] % (self.url, self.path)
        return self._run_command(cmd)

    def update(self):
        if self.app_type not in self.update_commands:
            self.tba.log.error('unsupported VCS for application %s' % self.name)
            return False
        op_ok = False
        with chdir(self.path):
            cmds = self.update_commands[self.app_type]
            for cmd in cmds:
                op_ok = self._run_command(cmd)
                if not op_ok:
                    break
        self.is_updated = op_ok  # TODO: check if some changes have been pulled
        return op_ok


class AppFactory(object):
    """
    Factory to dynamically instanciate an App object
    suited for given application type (archived/versionned).
    """
    loader_map = {
        'git': VersionedApp,
        'hg': VersionedApp,
        'svn': VersionedApp,
        'archive': ArchiveApp
    }

    @classmethod
    def load(cls, tba, name, specs):
        app_cls = cls.loader_map[specs['type']]
        return app_cls(tba, name, specs)
