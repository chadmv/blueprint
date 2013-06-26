"""Blender integration module"""
import os
import subprocess
import json
import logging

from blueprint.layer import TaskIterator, SetupTask

logger = logging.getLogger(__name__)

class BlenderSetup(SetupTask):
    """
    The BlenderSetup task will introspect the .blend file and
    try to detect and register outputs with blueprint.
    """
    def __init__(self, layer, **kwargs):
        SetupTask.__init__(self, layer, **kwargs)

    def _execute(self):

        layer = self.getLayer()

        cmd = ["blender"]
        cmd.append("-b")
        cmd.append(layer.getInput("scene_file").path)
        cmd.append("--python")
        cmd.append(os.path.join(os.path.dirname(__file__),
            "setup", "blender_setup.py"))

        output_path = "%s/blender_outputs_%d.json" % (self.getTempDir(), os.getpid())
        os.environ["PLOW_BLENDER_SETUP_PATH"] = output_path
        self.system(cmd)

        logger.info("Loading blender ouputs from: %s" % output_path)
        outputs = json.load(open(output_path, "r"))
        for output in outputs:
            layer.addOutput(output["pass"], output["path"], output)

class Blender(TaskIterator):
    """
    The Blender module renders frames from a blender scene.
    """
    def __init__(self, name, **kwargs):
        TaskIterator.__init__(self, name, **kwargs)
        self.requireArg("scene_file", (str,))

        self.addInput("scene_file",
            os.path.abspath(self.getArg("scene_file")))

    def _setup(self):
        self.addSetupTask(BlenderSetup(self))

    def _execute(self, frames):

        cmd = ["blender"]
        cmd.append("-b")
        cmd.append(self.getInput("scene_file").path)
        cmd.append("-noaudio")
        cmd.append("-noglsl")
        cmd.append("-nojoystick")
        cmd.extend(("-t", os.environ.get("PLOW_THREADS", "1")))

        for f in frames:
            cmd.extend(("-f", str(f)))

        self.system(cmd)
