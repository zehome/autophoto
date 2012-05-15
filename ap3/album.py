# -*- coding: utf-8 -*-

import os

from ap3.core import AP3obj
from ap3.photo import Photo

class Album(AP3obj):
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
            for extension in ("jpg", "jpeg", "png"):
                if path.lower().endswith(extension):
                    return Photo
        return None

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
            if not self.canRead(xpath):
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
    def __str__(self):
        return self.__unicode__()

