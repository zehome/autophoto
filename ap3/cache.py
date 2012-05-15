# -*- coding: utf-8 -*-

import os

class AbstractCache(object):
    def set(self, prop, path):
        pass
    def get(self, prop, path):
        return None
    def getpath(self, prop, path):
        return None

class SelfDirectoryCache(AbstractCache):
    def _getCacheDirectory(self, prop, path):
        dirname = os.path.dirname(path)
        cachedir = os.path.join(dirname, ".cache")

        # On the fly!
        if not os.path.exists(cachedir):
            os.mkdir(cachedir, 0775)
        return cachedir

    def _getCacheFilename(self, prop, path):
        baseName = os.path.basename(path)
        fileName = "%(prop)s.%(name)s" % {
            'prop': prop, 'name': baseName }
        return fileName

    def _getCacheFilepath(self, prop, path):
        dirname = self._getCacheDirectory(prop, path)
        fname = self._getCacheFilename(prop, path)
        fpath = os.path.join(dirname, fname)
        return fpath

    def set(self, prop, path, data):
        f = open(self._getCacheFilepath(prop, path), "wb+")
        return f.write(data)

    def get(self, prop, path):
        try:
            return open(self._getCacheFilepath(prop, path), "rb")
        except IOError:
            return None

    def getpath(self, prop, path):
        return self._getCacheFilepath(prop, path)

