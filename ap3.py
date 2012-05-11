#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

def JsonSerializer(data):
    return json.dumps(data)

def PrettyJsonSerializer(data):
    return json.dumps(data, sort_keys=True, indent=4)

class AP3obj(object):
    _settings = {"rootpath": None, "serializer": JsonSerializer}

    @classmethod
    def setRoot(cls, path):
        """Pass the abspath to the root directory of the application."""
        cls._settings["rootpath"] = os.path.abspath(path)

    @classmethod
    def setSerializer(cls, callback):
        cls._settings["serializer"] = callback

    def __init__(self, path, *args, **kw):
        self.abspath = os.path.abspath(path)
        self.relpath = self.getRelativePath(self.abspath)

    def getRelativePath(self, path):
        # Check for unconfigures AP3obj !
        assert(self._settings["rootpath"] is not None)
        assert(path.startswith(self._settings["rootpath"]))
        return os.path.relpath(path, self._settings["rootpath"])

    @property
    def basename(self):
        return os.path.basename(self.abspath)

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

class Photo(AP3obj):
    def __init__(self, *args, **kwargs):
        super(Photo, self).__init__(*args, **kwargs)
        self._stat = None

    @property
    def stat(self):
        if not self._stat:
            self._stat = os.stat(self.abspath)
        return self._stat

    def _serialize(self, **kwargs):
        stat = self.stat

        return {
            "name": self.basename,
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "security": {
                "uid": stat.st_uid,
                "gid": stat.st_gid,
                "mode": stat.st_mode,
            },
        }

    def __unicode__(self):
        return self.basename

class Album(AP3obj):
    def _serialize(self, **kwargs):
        data = {
            "abspath": self.abspath,
            "relpath": self.relpath,
        }
        if kwargs.get("listing", True):
            data["listing"] = [ o._serialize(listing=False) for o in self.listMe() ]
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
    print a.serialize()
