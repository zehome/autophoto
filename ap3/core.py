#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import traceback

from ap3.cache import SelfDirectoryCache
from ap3.serializer import JsonSerializer

# Some constants
DEFAULT_SIZE_SMALL = (640, 480)
DEFAULT_SIZE_MEDIUM = (1280, 1024)

class AP3obj(object):
    _settings = {
        "rootpath": None,
        "serializer": JsonSerializer,
        "image_size_medium": DEFAULT_SIZE_MEDIUM,
        "image_size_small": DEFAULT_SIZE_SMALL,
        "cacher": SelfDirectoryCache,
    }

    def __init__(self, path, *args, **kw):
        self.abspath = os.path.abspath(path)
        self.relpath = self.getRelativePath(self.abspath)

    def __str__(self):
        return self.__unicode__()

    @classmethod
    def setRoot(cls, path):
        """Pass the abspath to the root directory of the application."""
        cls._settings["rootpath"] = os.path.abspath(path)

    @classmethod
    def setSerializer(cls, callback):
        cls._settings["serializer"] = callback

    @classmethod
    def setCacher(cls, klass):
        cls._settings["cacher"] = klass

    @property
    def basename(self):
        return os.path.basename(self.abspath)

    @property
    def cache(self):
        return self._settings["cacher"]()

    def canRead(self, path):
        return True

    def getRelativePath(self, path):
        # Check for unconfigures AP3obj !
        assert(self._settings["rootpath"] is not None)
        assert(path.startswith(self._settings["rootpath"]))
        return os.path.relpath(path, self._settings["rootpath"])

    def _serialize(self, **kwargs):
        assert(False)

    def serialize(self, **kwargs):
        data = self._serialize(**kwargs)
        try:
            return self._settings["serializer"](data)
        except:
            traceback.print_exc()
            print data
