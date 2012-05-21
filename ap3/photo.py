# -*- coding: utf-8 -*-

import os
import time
import cStringIO

Image = None
epeg = None

try:
    import epeg
except:
    pass

if not epeg:
    import Image

from ap3.core import AP3obj

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
            "type": "IMG",
            "imgtype": self.getType(),
            "name": self.basename.decode("utf-8", 'replace'),
            "rpath": self.getDirName().decode("utf-8", 'replace'),
            "size": stat.st_size,
            "mtime": stat.st_mtime,
        }

        if kwargs.get("extended"):
            data["security"] = {
                "uid": stat.st_uid,
                "gid": stat.st_gid,
                "mode": stat.st_mode,
            }
            data["absolutepath"] = self.abspath
        return data

    def _thumbnail(self, prop):
        f = self.cache.get(prop, self.abspath)
        if not f:
            max_size = self._settings["image_size_%s" % (prop,)]
            if epeg:
                e = epeg.Epeg(fileinput=open(self.abspath, "rb"))
                out_filename = self.cache.getpath(prop, self.abspath)
                t3 = time.time()
                resized = e.simple_resize(out_filename, max_size)
                t4 = time.time()
                e.close()
                if resized:
                    print "Resizing took: %.04fs"  % (t4-t3,)
                    f = self.cache.get(prop, self.abspath)
                else:
                    f = open(self.abspath, "rb")
            else:
                im = Image.open(self.abspath)
                oldFormat = im.format
                im.thumbnail(max_size, Image.ANTIALIAS)
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


