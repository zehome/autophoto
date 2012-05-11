#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

# Python Imaging Library
import Image
import cStringIO

# Some constants
DEFAULT_SIZE_SMALL = (640, 480)
DEFAULT_SIZE_MEDIUM = (1280, 1024)

def JsonSerializer(data):
    return json.dumps(data)

def PrettyJsonSerializer(data):
    return json.dumps(data, sort_keys=True, indent=4)

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

class AP3obj(object):
    _settings = {
        "rootpath": None,
        "serializer": JsonSerializer,
        "image_size_medium": DEFAULT_SIZE_MEDIUM,
        "image_size_small": DEFAULT_SIZE_SMALL,
        "cacher": SelfDirectoryCache,
    }

    @classmethod
    def setRoot(cls, path):
        """Pass the abspath to the root directory of the application."""
        cls._settings["rootpath"] = os.path.abspath(path)

    @classmethod
    def setSerializer(cls, callback):
        cls._settings["serializer"] = callback

    @property
    def cache(self):
        return self._settings["cacher"]()

    def __init__(self, path, *args, **kw):
        self.abspath = os.path.abspath(path)
        self.relpath = self.getRelativePath(self.abspath)

    @property
    def basename(self):
        return os.path.basename(self.abspath)

    def getRelativePath(self, path):
        # Check for unconfigures AP3obj !
        assert(self._settings["rootpath"] is not None)
        assert(path.startswith(self._settings["rootpath"]))
        return os.path.relpath(path, self._settings["rootpath"])


    def _serialize(self, **kwargs):
        assert(False)

    def serialize(self, **kwargs):
        data = self._serialize(**kwargs)
        return self._settings["serializer"](data)

    def getObjectKlass(self, path):
        """Discover what type of object we should build."""
        if os.path.isdir(path):
            return Album
        elif os.path.isfile(path) or os.path.islink(path):
            for extension in ("jpg", "jpeg", "png"):
                if path.lower().endswith(extension):
                    return Photo
        else:
            print "Gni %s" % (path,)
        return None

    def checkPerms(self, path):
        return True

    def __str__(self):
        return self.__unicode__()

class Photo(AP3obj):
    def __init__(self, *args, **kwargs):
        super(Photo, self).__init__(*args, **kwargs)
        self._stat = None

    @property
    def stat(self):
        if not self._stat:
            self._stat = os.stat(self.abspath)
        return self._stat

    def getType(self):
        path = self.relpath.lower()
        if path.endswith("png"):
            return "PNG"
        elif path.endswith("jpg"):
            return "JPG"
        assert(False)

    def getDirName(self):
        return os.path.dirname(self.relpath)

    def _serialize(self, **kwargs):
        stat = self.stat

        data = {
            "name": self.basename,
            "relpath": self.getDirName(),
            "type": self.getType(),
            "size": stat.st_size,
            "mtime": stat.st_mtime,
        }

        if kwargs.get("extended"):
            data["security"] = {
                "uid": stat.st_uid,
                "gid": stat.st_gid,
                "mode": stat.st_mode,
            }
        return data

    def _thumbnail(self, prop):
        f = self.cache.get(prop, self.abspath)
        if not f:
            im = Image.open(self.abspath)
            oldFormat = im.format
            im.thumbnail(self._settings["image_size_%s" % (prop,)],
                Image.ANTIALIAS)
            sio = cStringIO.StringIO()
            im.save(sio, oldFormat)
            sio.seek(0)
            self.cache.set(prop, self.abspath, sio.read())
            sio.seek(0)
            f = sio
        return f and f.read() or None

    def getDataOriginal(self):
        """returns "full" size for this picture"""
        originalPath = self.abspath
        f = open(originalPath, "rb")
        return f.read()

    def getDataMedium(self):
        """returns "medium" size for this picture"""
        return self._thumbnail("medium")

    def getDataSmall(self):
        """returns "small" size for this picture"""
        return self._thumbnail("small")

    def __unicode__(self):
        return self.basename

class Album(AP3obj):
    def _serialize(self, **kwargs):
        data = {
            "abspath": self.abspath,
            "relpath": self.relpath,
        }
        if kwargs.get("listing", True):
            kwargs["listing"] = kwargs.get("recursive", False)
            data["listing"] = [ o._serialize(**kwargs) for o in self.listMe() ]
        return data

    def listMe(self):
        ret = []

        for xname in os.listdir(self.abspath):
            xpath = os.path.join(self.abspath, xname)
            if not self.checkPerms(xpath):
                print "No permission to read %s." % (xname,)
            else:
                klass = self.getObjectKlass(xpath)
                if not klass:
                    print "Unknown file %s." % (xname,)
                else:
                    ret.append(klass(xpath))

        return ret

    def __unicode__(self):
        return self.basename

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        directory = sys.argv[1]
    else:
        directory = "."

    AP3obj.setRoot(directory)
    AP3obj.setSerializer(PrettyJsonSerializer)

    a = Album(directory)
    print a.serialize(extended=True)

    for p in a.listMe():
        if isinstance(p, Photo):
            pData = p.getDataMedium()
            print "Got p: %s dataMedium: %d" % (p, len(pData))
            pData = p.getDataSmall()
            print "Got p: %s dataSmall: %d" % (p, len(pData))

