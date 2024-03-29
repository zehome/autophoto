#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python ctypes binding for libepeg, from enlightenment
# To get it:
#
# svn co http://svn.enlightenment.org/svn/e/OLD/epeg epeg

from ctypes import *
from ctypes.util import find_library

__version__ = "1.0"

_libepeg_path = find_library('epeg')
_libepeg = CDLL(_libepeg_path)

class Epeg_Thumbnail_Info(Structure):
    _fields_ = [
        ('uri', c_char_p),
        ('mtime', c_ulonglong),
        ('w', c_int),
        ('h', c_int),
        ('mimetype', c_char_p)
    ]

    def __unicode__(self):
        return "%s %s %s %s %s" % (self.uri, self.mtime, self.w, self.h, self.mimetype)
    def __str__(self):
        return self.__unicode__()

EPEG_GRAY8 = 0
EPEG_YUV8 = 1
EPEG_RGB8 = 2
EPEG_BGR8 = 3
EPEG_RGBA8 = 4
EPEG_BGRA8 = 5
EPEG_ARGB32 = 6
EPEG_CMYK = 7

# Prototypes
_libepeg.epeg_file_open.restype = c_void_p
_libepeg.epeg_file_open.argtypes = [c_char_p, ]

_libepeg.epeg_memory_open.restype = c_void_p
_libepeg.epeg_memory_open.argtypes = [c_void_p, c_int]

_libepeg.epeg_size_get.restype = None
_libepeg.epeg_size_get.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]

_libepeg.epeg_decode_size_set.restype = None
_libepeg.epeg_decode_size_set.argtypes = [c_void_p, c_int, c_int]

_libepeg.epeg_colorspace_get.restype = None
_libepeg.epeg_colorspace_get.argtypes = [c_void_p, POINTER(c_int)]

_libepeg.epeg_decode_colorspace_set.restype = None
_libepeg.epeg_decode_colorspace_set.argtypes = [c_void_p, c_int]

_libepeg.epeg_comment_get.restype = c_char_p
_libepeg.epeg_comment_get.argtypes = [c_void_p, ]

_libepeg.epeg_thumbnail_comments_get.restype = None
_libepeg.epeg_thumbnail_comments_get.argtypes = [c_void_p, POINTER(Epeg_Thumbnail_Info) ]

_libepeg.epeg_thumbnail_comments_enable.restype = None
_libepeg.epeg_thumbnail_comments_enable.argtypes = [c_void_p, c_int]

_libepeg.epeg_quality_set.restype = None
_libepeg.epeg_quality_set.argtypes = [c_void_p, c_int]

_libepeg.epeg_file_output_set.restype = None
_libepeg.epeg_file_output_set.argtypes = [c_void_p, c_char_p]

_libepeg.epeg_memory_output_set.restype = None
_libepeg.epeg_memory_output_set.argtypes = [c_void_p, POINTER(c_void_p), POINTER(c_int)]

_libepeg.epeg_encode.restype = c_int
_libepeg.epeg_encode.argtypes = [c_void_p, ]

_libepeg.epeg_close.restype = None
_libepeg.epeg_close.argtypes = [c_void_p, ]


class EpegException(Exception): pass

class Epeg(object):
    def __init__(self, filename=None, fileinput=None):
        self.image = None
        self._image_data = None
        self._image_path = None

        if filename is None and fileinput is None:
            raise EpegException("You must specify either filename or file object!")

        if filename:
            self._image_path = filename
            self._open(self._image_path)
        else:
            self._image_data = fileinput.read()
            self._open_from_memory(self._image_data)

        if not self.image:
            raise EpegException("Unable to open image '%s'.\n" % filename)

    def __del__(self):
        self.close()

    def _open(self, path):
        """open specified path to the jpeg file. Raises EpegException on error."""
        self.image = _libepeg.epeg_file_open(c_char_p(path))
        if not self.image:
            raise EpegException("Unable to open file %s.\n" % path)

    def _open_from_memory(self, data):
        """data representation of "int" size"""
        size = len(data)
        self.image = _libepeg.epeg_memory_open(c_char_p(data), c_int(size))

    def size_get(self):
        """returns (width, height) tuple of the current loaded image"""
        assert(self.image)
        c_w, c_h = c_int(), c_int()
        _libepeg.epeg_size_get(self.image, byref(c_w), byref(c_h))
        return (c_w.value, c_h.value)

    def decode_size_set(self, width, height):
        assert(self.image)
        _libepeg.epeg_decode_size_set(self.image, width, height)

    def colorspace_get(self):
        assert(self.image)
        colorspace = c_int()
        _libepeg.epeg_colorspace_get(self.image, byref(colorspace))
        return colorspace.value

    def decode_colorspace_set(self, colorspace):
        assert(self.image)
        _libepeg.epeg_decode_colorspace_set(self.image, c_int(colorspace))

    def comment_get(self):
        assert(self.image)
        ptr = c_char_p(_libepeg.epeg_comment_get(self.image))
        return ptr.value

    def comment_set(self, comment):
        assert(self.image)
        _libepeg.epeg_comment_set(self.image, comment)

    def thumbnail_comments_get(self):
        assert(self.image)
        ti = Epeg_Thumbnail_Info()
        _libepeg.epeg_thumbnail_comments_get(self.image, byref(ti))
        return ti

    def thumbnail_comments_enable(self, value):
        assert(self.image)
        _libepeg.epeg_thumbnail_comments_enable(self.image, c_int(value))

    def quality_set(self, quality):
        assert(self.image)
        assert(quality >= 0 and quality <= 100)
        _libepeg.epeg_quality_set(self.image, c_int(quality))

    def write_to_file(self, filename):
        assert(self.image)
        _libepeg.epeg_file_output_set(self.image, filename)
        self.encode()

    def write_to_memory(self):
        assert(self.image)
        data_ptr = c_char_p()
        data_size = c_int()
        _libepeg.epeg_memory_output_set(self.image, byref(data_ptr), byref(data_size))
        self.encode()
        return data_ptr and data_ptr.value or b""

    def encode(self):
        assert(self.image)
        ret = c_int(_libepeg.epeg_encode(self.image))
        return ret

    def close(self):
        if self.image and _libepeg:
            _libepeg.epeg_close(self.image)
        self.image = None

    def simple_resize(self, output_filename, size):
        w, h = self.size_get()
        need_resize = w > size[0] or h > size[1]
        if need_resize:
            if (w > h):
                h = size[0] * h / w
                w = size[0]
            else:
                w = size[1] * w / h
                h = size[1]

            self.decode_size_set(w, h)
            self.quality_set(100)
            self.thumbnail_comments_enable(0)
            self.write_to_file(output_filename)
        return need_resize

if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv) < 2:
        print "Not enough arguments!"
        sys.exit(0)

    epeg = Epeg(fileinput=open(sys.argv[1], "rb"))
    t1 = time.time()
    epeg.simple_resize("x.jpg", (640,480))
    print time.time() - t1
