"""The archive provides a mechanism for storing job runtime data."""

import os
import logging
import yaml
import shutil

import blueprint.conf as conf
from blueprint.exception import ArchiveException

logger = logging.getLogger(__name__)

class Archive(object):
    """
    The archive provides a mechanism for storing job/layer runtime data.
    It can be used for passing arbitrary metadata between tasks as well
    as files.
    """
    def __init__(self, job):
        self.__job = job
        self.__path = os.path.join(
            conf.get("bp.archive_dir", JOB_NAME=job.getName()),
            job.getId())
        self.__create()

    def __create(self):
        logger.debug("Using archive path: %s" % self.__path)
        if os.path.exists(self.__path):
            return
        os.makedirs(self.__path, 0777)
        os.mkdir(os.path.join(self.__path, "layers"), 0777)

    def putData(self, name, data, layer=None):
        """Put data into the job archive."""
        path = os.path.join(self.getPath(layer), name)
        logger.debug("Witing out data %s to path %s" % (name, path))
        fp = open(path, "w")
        try:
            fp.write(yaml.dump(data))
        finally:
            fp.close()
    
    def getData(self, name, layer=None, default=None):
        """
        Get data from the archive or throw an ArchiveException
        if data by the given name does not exist.
        """
        try:
            path = os.path.join(self.getPath(layer), name)
            logger.debug("Reading in data %s from path %s" % (name, path))
            stream = open(path, "r")
            return yaml.load(stream)
        except Exception, e:
            if isinstance(default, Exception):
                raise default
            else:
                return default

    def putFile(self, name, path):
        """ Copy a file into the job archive."""
        if name == "layers":
            raise ArchiveException("layers is a reserved archive name.")
        dst = os.path.join(self.getPath(), name)
        shutil.copyfile(path, dst)
        return dst

    def getFile(self, name):
        """
        Return the name of a file in the job archive.
        """
        return os.path.join(self.getPath(), name)

    def getPath(self, layer=None):
        if layer:
            try:
                layer_name = layer.getName()
            except:
                layer_name = str(layer)
            path = os.path.join(self.__path, "layers", layer_name)
        else:
            path = self.__path

        if not os.path.exists(path):
            try:
                os.mkdir(path, 0777)
            except OSError, e:
                raise ArchiveException("Failed to make archive dir: " + e)

        return path

    def __str__(self):
        return self.__path

