#!/usr/bin/env python
# -*- coding: utf-8-

import os
basepath = os.path.abspath(os.path.dirname(__file__))

import cherrypy
from cherrypy import tools

from ap3.album import Album, Photo

class Root(object):
    exposed = True
    def GET(self):
        raise cherrypy.HTTPRedirect("/static/index.html", 302)

class AP3AlbumMeta(object):
    exposed = True

    def __init__(self, name, rootpath):
        self.name = name
        self.rootpath = rootpath

    def GET(self, *args, **kwargs):
        cherrypy.response.headers["Content-Type"] = "application/json"

        path = '/'.join(args)
        try:
            obj = Album(os.path.join(self.rootpath, path))
        except OSError:
            raise cherrypy.HTTPError(404)
        return obj.serialize(recursive=False)

class AP3PhotoMeta(object):
    exposed = True
    def __init__(self, rootpath):
        self.rootpath = rootpath

    def GET(self, *args, **kwargs):
        cherrypy.response.headers["Content-Type"] = "application/json"

        if not args:
            raise cherrypy.HTTPError(404, 'No argument specified.')

        path = '/'.join(args)
        try:
            obj = Photo(os.path.join(self.rootpath, path))
        except OSError:
            raise cherrypy.HTTPError(404)

        return obj.serialize(recursive=False)

class AP3PhotoData(object):
    exposed = True
    def __init__(self, rootpath):
        self.rootpath = rootpath

    def GET(self, *args, **kwargs):
        if not args:
            raise cherrypy.HTTPError(500, 'No arguments specified.')

        if not args[0].isdigit():
            if args[0] != "orig":
                raise cherrypy.HTTPError(500, "Invalid argument.")

        path = '/'.join(args)
        try:
            obj = Photo(os.path.join(self.rootpath, path))
        except OSError:
            raise cherrypy.HTTPError(404)

        cherrypy.response.headers["Content-Type"] = "image/jpeg"
        return obj.getDataSmall()

# Configure Autophoto 3
from ap3.core import AP3obj
from ap3.serializer import PrettyJsonSerializer
from ap3.cache import SingleDirectoryHashCache

SingleDirectoryHashCache.setCachePath("/home/ed/tmp/ap3cache")

AP3obj.setRoot("/home/ed/Documents/autophoto2")
AP3obj.setSerializer(PrettyJsonSerializer)
AP3obj.setCacher(SingleDirectoryHashCache)

root = Root()
root.album = AP3AlbumMeta("main", "/home/ed/Documents/autophoto2")
root.photo = AP3PhotoMeta("/home/ed/Documents/autophoto2")
root.photodata = AP3PhotoData("/home/ed/Documents/autophoto2")

conf = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8000,
        'tools.gzip.on': True,
        'engine.autoreload_on': True,
    },
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    },
    '/photo': {
        'tools.gzip.on': False,
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.root': basepath,
        'tools.staticdir.dir': 'static',
    },
}
cherrypy.quickstart(root, '/', conf)
