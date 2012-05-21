# -*- coding: utf-8 -*-

import os

from ap3.core import AP3obj
from ap3.photo import Photo

class Album(AP3obj):
    PHOTO_EXTENSIONS = (".jpg", ".jpeg")
    def __init__(self, *args, **kwargs):
        super(Album, self).__init__(*args, **kwargs)
        self.name = os.path.basename(self.relpath)
        self._dirlist_cache = None

    def canRead(self, path):
        readok = super(Album, self).canRead(path)
        if readok:
            # Files/Directories starting with "." are
            # not permitted by default.
            pathbasename = os.path.basename(path)
            readok = not pathbasename.startswith(".")
        return readok

    def getObjectKlass(self, path):
        """Discover what type of object we should build."""
        if os.path.isdir(path):
            return Album
        elif os.path.isfile(path) or os.path.islink(path):
            ext = os.path.splitext(path)[1].lower()
            if ext in Album.PHOTO_EXTENSIONS:
                return Photo
        return None

    def _get_dirlist(self):
        if self._dirlist_cache is None:
            self._dirlist_cache = []
            for xname in os.listdir(self.abspath):
                xpath = os.path.join(self.abspath, xname)
                if self.canRead(xpath):
                    self._dirlist_cache.append(xpath)
        return self._dirlist_cache

    def listMe(self):
        for xpath in self._get_dirlist():
            klass = self.getObjectKlass(xpath)
            if not klass:
                print "Unknown file %s." % (xname,)
            else:
                yield klass(xpath)

    def countMe(self):
        ret = 0
        for xpath in self._get_dirlist():
            if self.getObjectKlass(xpath):
                ret += 1
        return ret

    def getCover(self):
        for e in self.listMe():
            if isinstance(e, Photo):
                return e._serialize()
        # Recursive! (if album only contains subdirectories)
        for e in self.listMe():
            if isinstance(e, Album):
                return e.getCover()

    def _serialize(self, **kwargs):
        data = {
            "type": "DIR",
            "name": self.name.decode("utf-8", 'replace'),
            "rpath": self.relpath.decode("utf-8", 'replace'),
            "cover": self.getCover(),
            "elements": self.countMe(),
        }
        if kwargs.get("extended"):
            data["absolutepath"] = self.abspath

        if kwargs.get("listing", True):
            kwargs["listing"] = kwargs.get("recursive", False)
            data["listing"] = [ o._serialize(**kwargs) for o in self.listMe() ]
        return data

    def __unicode__(self):
        return self.basename
    def __str__(self):
        return self.__unicode__()

