"""
The job class.
"""
import uuid
import os
import logging

import fileseq

import blueprint.conf as conf
from blueprint import Layer, Task, TaskContainer
from blueprint.archive import Archive
from blueprint.exception import LayerException

logger = logging.getLogger(__name__)


class Job(object):

    Current = None

    def __init__(self, name, frange="1001-1001"):
        self.setName(name)
        self.__id = str(uuid.uuid1())
        self.__layers = [ [], {} ]
        self.__archive = None
        self.__path = None
        self.__range = frange

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

        if layer in self.__layers[0]:
            logger.debug("The layer/task %s is already in the job." % layer.getName())
            return

        if self.__layers[1].has_key(layer.getName()):
            raise LayerException("Invalid layer/task name: %s , duplicate name." % layer)

        if isinstance(layer, Task):
            task = layer
            task_layer_name = task.getArg("layer", "default")
            if task.getArg("post"):
                task_layer_name = "%s_post" % task_layer_name
            task_layer = self.__layers[1].get(task_layer_name)
            if not task_layer:
                task_layer = TaskContainer(task_layer_name)
                task_layer.setArg("post", task.getArg("post"))
                self.addLayer(task_layer)
            task_layer.addTask(task)

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

        from blueprint import PluginManager

        self.__archive = Archive(self)
        self.__path = self.__archive.getPath()

        for layer in self.__layers[0]:
            layer.setup()

        PluginManager.runJobSetup(self)

        archive = self.__archive
        try:
            self.__archive = None
            archive.putData("blueprint.yaml", self)
        finally:
            self.__archive = archive

    def getFrameRange(self):
        """Return the string frame range for this job."""
        return self.__range

    def getFrameSet(self):
        """Return a FrameSet for the job's frame range."""
        return fileseq.FrameSet(self.__range)

    def setFrameRange(self, frange):
        """Set the job's frame range."""
        self.__range = frange

    def launch(self, **kwargs):
        from app import BlueprintRunner
        runner = BlueprintRunner(self, **kwargs)
        return runner.launch()
