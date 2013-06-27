
import os
import logging
import tempfile
import json

import blueprint.io as io
from blueprint.layer import SetupTask, TaskIterator

logger = logging.getLogger(__name__)

"""
This is the base of a dynamically generated script that is used
to walk a nuke scene, gather outputs, and register then with
blueprint.
"""
NUKE_SETUP_SCRIPT = """

import json
nuke.scriptReadFile('%(nuke_script_path)s')

only_nodes = frozenset(%(node_list)s)
outputs = []
for write_node in nuke.allNodes('Write'):
    # Skip over disabled nodes
    if write_node.knob('disable').value():
        continue
    if not only_nodes or write_node.name() in only_nodes:
        outputs.append([write_node['file'].getText(), {
            'node': write_node.name(),
            'colorspace': write_node['colorspace'].value(),
            'file_type': write_node['file_type'].value(),
            'datatype': write_node['datatype'].value(),
            'compression:': write_node['compression'].value()
        }])

json.dump(outputs, open('%(tmp_data_path)s', 'w'))
"""

class NukeSetup(SetupTask):
    def __init__(self, parent, **kwargs):
        SetupTask.__init__(self, parent, **kwargs)

    def _execute(self, *args):

        tmp_dir = tempfile.gettempdir()

        opts = {
            "nuke_script_path": self.getParentLayer().getArg("script"),
            "tmp_data_path": "%s/nuke_setup_data.json" % tmp_dir,
            "node_list": str(self.getArg("nodes", list()))
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
        for path, attrs in outputs:
            self.getParentLayer().addOutput(attrs["node"], path, attrs)

class Nuke(TaskIterator):

    def __init__(self, name, **kwargs):
        TaskIterator.__init__(self, name, **kwargs)
        self.requireArg("script", (str,))
        self.setArg("service", "nuke")

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
        ]
        if self.getArg("nodes"):
            cmd.extend(("-X", ",".join(self.getArg("nodes"))))

        cmd.append(self.getArg("script"))
        self.system(cmd)

