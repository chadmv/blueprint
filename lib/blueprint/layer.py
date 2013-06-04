import os
import logging
import tempfile
import fileseq

from collections import namedtuple

import conf
from job import Job
from io import FileIO, system
from app import PluginManager
from exception import LayerException

logger = logging.getLogger(__name__)

Depend = namedtuple("Depend", ["dependent", "dependOn", "type", "args"])

class DependType(object):
    All = "DependAll"
    ByTask = "ByTask"

class LayerAspect(type):

    def __call__(cls, *args, **kwargs):
        """
        Intercepts the creation of layer objects and assigns
        them to the current job, of there is one.  The current job
        is set when a job is loaded via script.
        """
        layer = super(LayerAspect, cls).__call__(*args, **kwargs)

        if Job.Current:
            Job.Current.addLayer(layer)
        
        layer.afterInit()
        return layer


class Layer(object):
    """
    A base class which implments the core functionality of
    an executable entity.
    """
    __metaclass__ = LayerAspect

    def __init__(self, name, **args):
        self.__name = name
        self.__args = args

        self.__job = None
        self.__req_args = []
        self.__depends = []
        self.__setups = []
        self.__outputs = {}
        self.__inputs = {}
        self.__range = args.get("range")
        self.__chunk = args.get("chunk", 1)

        self.__handleDependArg()
        self.__loadDefaultArgs()

    def getName(self):
        return self.__name

    def setArg(self, name, value):
        self.__args[name] = value

    def getArg(self, name, default=None):
        return self.__args.get(name, default)

    def isArgSet(self, name):
        return self.__args.has_key(name)

    def requireArg(self, name, types=None):
        self.__req_args.append((name, types))

    def dependOn(self, other, args=None):
        self.__depends.append(Depend(self, other, DependType.ByTask, args))

    def dependAll(self, other, args=None):
        self.__depends.append(Depend(self, other, DependType.All, args))

    def getDepends(self):
        return list(self.__depends)

    def getJob(self):
        return self.__job

    def putData(self, name, data):
        if not self.__job:
            raise BlueprintException("The layer %s requires a job to before setup() is run" % self.__name)
        if not self.__job.getArchive():
            raise BlueprintException("A job archive must exist before dynamic data can be added.")
        self.__job.getArchive().putData(name, data, self)

    def getData(self, name):
        return self.__job.getArchive().getData(name, data, self)
        
    def setJob(self, job):
        self.__job = job

    def getOutput(self, name):
        return self.__outputs[name]

    def getInput(self, name):
        return self.__inputs[name]

    def getOutputs(self):
        return self.__outputs.values()

    def getInputs(self):
        return self.__inputs.values()

    def addInput(self, name, path, attrs=None):
        self.__inputs[name] = FileIO(path, attrs)
        # If the job doesn't have an archive yet
        # add these at setup time.
        if self.__job and self.__job.getArchive():
            self.putData("inputs", self.__inputs)

    def addOutput(self, name, path, attrs=None):
        self.__outputs[name] = FileIO(path, attrs)
        # If the job doesn't have an archive yet
        # add these at setup time.
        if self.__job and self.__job.getArchive():
            self.putData("outputs", self.__outputs)

    def getSetupTasks(self):
        return list(self.__setups)

    def addSetupTask(self, task):
        self.__setups.append(task)

    def system(self, cmd):
        system(cmd)

    def afterInit(self):
        self._afterInit()
        PluginManager.runAfterInit(self)

    def setup(self):
        # If any inputs or outputs are set add them to the archive
        self.putData("inputs", self.__inputs)
        self.putData("outputs", self.__outputs)
        self._setup()
        PluginManager.runSetup(self)

    def beforeExecute(self):
        self._beforeExecute()
        PluginManager.runBeforeExecute(self)

    def execute(self, frame=None):

        self.beforeExecute()

        if frame:
            frameset = self.getLocalFrameSet(frame)
            self._execute(frameset)
        else:
            self._execute()

        self.afterExecute()

    def afterExecute(self):
        self._afterExecute()
        PluginManager.runAfterExecute(self)

    def getTempDir(self):
        return tempfile.gettempdir()
    
    def getDir(self):
        return self.__job.getArchive().getPath(self.getName())

    def system(self, cmd):
        system(cmd)

    def getFrameRange(self):
        frange = self.getArg("range", None)
        if not frange:
            return self.getJob().getFrameRange()
        return frange

    def getFrameRange(self):
        if self.__range:
            return self.__range
        else:
            return self.getJob().getFrameRange()

    def getFrameSet(self):
        return fileseq.FrameSet(self.getFrameRange())

    def setFrameRange(self, frange):
        self.__range = frange

    def getLocalFrameSet(self, frame):
        """
        Return the local frameset when running in execute mode.
        """
        frameset = None
        
        if self.getChunk() <= 0:
            framset = self.getFrameSet()
        elif self.getChunk() >1:
            result = []

            full_range = self.getFrameSet()
            end = len(full_range) - 1

            idx = full_range.index(frame)
            for i in range(idx, idx+self.getChunk()):
                if i > end:
                    break
                result.append(full_range[i])
            frameset = fileseq.FrameSet(",".join(map(str, result)))
        else:
            frameset = fileseq.FrameSet(str(frame))

        if frameset is None:
            raise LayerException("Unable to determine local frameset.")

        return frameset

    def getChunk(self):
        return self.__chunk

    def _afterInit(self):
        """
        _afterInit is called once all the layer args
        have their final values.
        """
        pass

    def _setup(self):
        pass

    def _beforeExecute(self):
        pass

    def _execute(self):
        pass

    def _afterExecute(self):
        pass

    def __loadDefaultArgs(self):
        """
        Load in default args for this module from the configuration file
        and populate the __defaults.
        """
        mod = self.__class__.__name__.lower()
        logger.debug("Loading default args for module: %s" % mod)

        default_args = conf.get("modules.%s" % mod, None)
        if not default_args:
            return
        for k, v in default_args.iteritems():
            logger.debug("Setting default %s arg: %s=%s" % (mod, k, v))
            self.setArg(k, v)
    
    def __handleDependArg(self):
        """
        Handles the dependOn kwarg passed in via the constructor.

        foo = Layer("foo", dependOn=["bar", "bing:all"])
        Layer("zing", dependOn=[(foo, Layer.DependAll)])
        """
        if not self.isArgSet("depend"):
            return

        depends = self.getArg("depend")
        if not isinstance(depends, (list,tuple)):
            depends = [depends]

        for dep in depends:
            if isinstance(dep, (tuple, list)):
                self.dependOn(LayerDepend(self, dep[0], dep[1]))
            else:
                onLayer = str(dep)
                if onLayer.endswith(":all"):
                    self.dependAll(onLayer.split(":")[0])
                else:
                    self.dependOn(onLayer)

    def __str__(self):
        return self.getName()

class Task(Layer):
    """
    Tasks are indiviudal processes with no-frame range.  Tasks must be parented
    to a layer.
    """
    def __init__(self, name, **args):
        Layer.__init__(self, name, **args)
   
class SetupTask(Task):

    def __init__(self, layer, **args):
        Task.__init__(self, "%s_setup" % layer.getName(), **args)
        self.__parent = layer 
        layer.dependOn(self, DependType.All)
        self.setArg("layer", "setup_tasks")
        self.setArg("service", "setup_task")

    def getParentLayer(self):
        return self.__parent



