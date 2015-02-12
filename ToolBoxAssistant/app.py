# -*- coding: utf-8 -*-
import os
import shlex
from subprocess import Popen, PIPE
from tarfile import TarFile
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

    def _log_exception(self, message):
        for line in str(message).splitlines():
            self.tba.log.error(line)

    def _run_command(self, cmd):
        cmd = shlex.split(cmd)
        p = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if self.tba.debug:
            for line in stdout.splitlines():
                self.tba.log.debug(line)
        if p.returncode != 0:
            self._log_exception(stderr)
            return False
        return True

    def sync(self):
        op_ok = False
        if not os.path.exists(self.path):
            self.tba.log.info('downloading %s' % self.name)
            op_ok = self.download()
        else:
            if isinstance(self, VersionedApp):
                self.tba.log.info('updating %s' % self.name)
                op_ok = self.update()
            else:
                self.tba.log.warning(
                    '%s is not versionned, check for new version and update specfile' % self.name
                )
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
        'tar': TarFile,
        'tar.gz': TarFile,
        'tar.bz2': TarFile,
        'tgz': TarFile
    }

    def download(self):
        fname = self.url.split('/')[-1].split('?')[0]
        temppath = os.path.join(gettempdir(), fname)
        opener = urlopen(self.url)
        try:
            data = opener.read()
        except Exception as err:
            self._log_exception(err)
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
        archive = handler(temppath)
        archive.extractall(self.path)
        os.remove(temppath)
        return True

    def update(self):
        return True


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
