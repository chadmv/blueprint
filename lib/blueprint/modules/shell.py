
import logging

from blueprint.layer import TaskIterator, Task
from blueprint.io import system

logger = logging.getLogger(__name__)

class Shell(TaskIterator):

    def __init__(self, name, **args):
        """
        Executes a shell command over a given frame range.
        """
        TaskIterator.__init__(self, name, **args)
        self.requireArg("cmd", (list, tuple))
        self.setArg("service", "shell")

    def _execute(self, frames):
        for frame in frames:
            system(self.getArg("cmd"))


class ShellCommand(Task):

    def __init__(self, name, **args):
        """
        Executes a command.
        """
        Task.__init__(self, name, **args)
        self.requireArg("cmd", (list, tuple))
        self.setArg("service", "shell")

    def _execute(self):
        system(self.getArg("cmd"))







