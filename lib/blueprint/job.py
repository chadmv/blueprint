"""
The job class.
"""
import uuid
import os

import blueprint.conf as conf
from blueprint.archive import Archive
from blueprint.exception import LayerException

class Job(object):

    Current = None

    def __init__(self, name):
        self.setName(name)
        self.__id = str(uuid.uuid1())
        self.__layers = [ [], {} ]
        self.__archive = None
        self.__path = None

    def getPath(self):
        return self.__path

    def getName(self):
        return self.__name

    def setName(self, name):
        self.__name = conf.get("bp.job_name_template", JOB_NAME=name)

    def getId(self):
        return self.__id

    def getLayer(self, name):
        try:
            return self.__layers[1][name]
        except KeyError:
            raise LayerException("Layer %s does not exist." % name)

    def addLayer(self, layer):
        
        if self.__layers[1].has_key(layer.getName()):
            raise LayerException("Invalid layer name: %s , duplicate name." % layer)
        
        self.__layers[0].append(layer)
        self.__layers[1][layer.getName()] = layer
        layer.setJob(self)

    def getLayers(self):
        return self.__layers[0]

    def loadArchive(self):
        self.__archive = Archive(self)

    def getArchive(self):
        return self.__archive

    def getLogDir(self):
        return os.path.join(
            conf.get("bp.log_dir", JOB_NAME=self.__name),
            self.__id)

    def putData(self, key, value):
        return self.__archive.putData(key, value)

    def getData(self, key):
        return self.__archive.getData(key)

    def setup(self):

        self.__archive = Archive(self)
        self.__path = self.__archive.getPath()

        for layer in self.__layers[0]:
            layer.setup()

        archive = self.__archive
        try:
            self.__archive = None
            archive.putData("blueprint.yaml", self)
        finally:
            self.__archive = archive

