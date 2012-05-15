#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ap3.core import AP3obj
from ap3.album import Album
from ap3.photo import Photo
from ap3.serializer import PrettyJsonSerializer

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

