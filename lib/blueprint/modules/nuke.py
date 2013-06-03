
import os
import logging
import tempfile
import json

import blueprint.io as io
from blueprint.layer import Layer, SetupTask

logger = logging.getLogger(__name__)

"""
This is the base of a dynamically generated script that is used
to walk a nuke scene, gather outputs, and register then with
blueprint.
"""
NUKE_SETUP_SCRIPT = """

import json
nuke.scriptReadFile('%(nuke_script_path)s')

outputs = []
for write_node in nuke.allNodes('Write'):
    # Skip over disabled nodes
    if write_node.knob('disable').value():
        continue
    outputs.append([write_node.name(), write_node['file'].getText()])

json.dump(outputs, open('%(tmp_data_path)s', 'w'))
"""

class NukeSetup(SetupTask):
    def __init__(self, parent, **kwargs):
        SetupTask.__init__(self, parent, **kwargs)

    def _execute(self, *args):

        tmp_dir = tempfile.gettempdir()

        opts = {
            "nuke_script_path": self.getParentLayer().getArg("script"),
            "tmp_data_path": "%s/nuke_setup_data.json" % tmp_dir
        }

        # Apply the opts to the setup script code and write
        # the script out to the task's temp area.
        setup_script_code = NUKE_SETUP_SCRIPT % opts
        setup_script_path = "%s/nuke_setup_script.py" % tmp_dir

        # Execute nuke on the script we just wrote out.
        open(setup_script_path, "w").write(setup_script_code)
        cmd = ["nuke"]
        cmd.extend(("-t", setup_script_path))
        self.system(cmd)

        # Load in the file nuke wrote out and register the outputs
        # with blueprint.
        outputs = json.load(open(opts["tmp_data_path"], "r"))
        for node_name, path in outputs:
            self.getParentLayer().addOutput(node_name, path, {"node": node_name})


class Nuke(Layer):

    def __init__(self, name, **kwargs):
        Layer.__init__(self, name, **kwargs)
        self.requireArg("script", (str,))

    def _setup(self):
        NukeSetup(self)

    def _execute(self, frames):
        
        cmd = [
            "nuke",
            "-V", 
            "-x", 
            "-c", self.getArg("c", "8G"),
            "-m", os.getenv("PLOW_THREADS"),
            "-f", 
            "-F", "%s-%s" %(frames[0], frames[-1]),
            self.getArg("script")
        ]
        self.system(cmd)

