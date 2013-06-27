
import os
import logging

import blueprint.io as io
from blueprint.layer import SetupTask, TaskIterator

logger = logging.getLogger(__name__)

class MayaSetup(SetupTask):
    def __init__(self, parent, **kwargs):
        SetupTask.__init__(self, parent, **kwargs)

    def _execute(self, *args):
        pass

class Maya(TaskIterator):

    def __init__(self, name, **kwargs):
        TaskIterator.__init__(self, name, **kwargs)
        self.requireArg("scene", (str,))
        self.setArg("service", "maya")

    def _execute(self, frames):
        
        output_seq = io.getOutputSeq(
        self.getArg("scene"), self.getArg("format"))

        cmd = [
            "Render",
            "-r", self.getArg("renderer"),
            "-s", str(frames[0]),
            "-e", str(frames[-1]),
            "-b", self.getArg("chunk", "1"),
            "-of", self.getArg("format", "png"),
            "-rd", os.path.dirname(output_seq),
            "-fnc", self.getArg("fnc"),
            "-pad", self.getArg("padding"),
            "-cam", self.getArg("camera"),
            self.getArg("scene")
        ]
        self.system(cmd)


