import logging
import subprocess
import fileseq
import os

import blueprint.conf as conf
from blueprint.exception import CommandException

logger = logging.getLogger(__name__)

def getOutputSeq(scene_file, format):
    """
    A utility function for converting a scene file name into an output
    sequence name.
    """
    basename = os.path.splitext(os.path.basename(scene_file))[0]
    return os.path.join(
        conf.get("bp.output_dir"),
        basename,
        "%s.#.%s" % (basename, format))

def system(cmd, frames=None):
    """
    Utility method for shelling out.  Takes a shell
    command in the form of an array.
    """
    cmd = map(str, cmd)
    cmdStr = " ".join(cmd)
    logger.info("About to run: %s", cmdStr)
    p = subprocess.Popen(cmd, shell=False)
    ret = p.wait()

    if ret != 0:
        raise CommandException(
            'Command exited with a status of %d: "%s"' % (ret, cmdStr),
            exitStatus=ret
        )

def mkdir(path, check=True):
    """
    Make the given directory.
    """
    if check:
        if os.path.exists(path):
            return True

    command = conf.get("system.mkdir")
    command.append(path)
    system(path)

class FileIO(object):
    def __init__(self, path, attrs=None):
        self.path = path
        self.attrs = attrs or dict()

    @property
    def dirname(self):
        return os.path.dirname(self.path)

    @property
    def basename(self):
        return os.path.splitext(os.path.basename(self.path))[0]

    @property
    def ext(self):
        return os.path.splitext(os.path.basename(self.path))[1]

    def __str__(self):
        return "<FileIO %s %s>" % (self.path, self.attrs)

    def __repr__(self):
        return "<FileIO %s %s>" % (self.path, self.attrs)
