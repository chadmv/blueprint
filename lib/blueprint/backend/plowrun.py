import os
import yaml
import getpass
import pprint
import logging

import plow.client as plow
import blueprint
import blueprint.conf as conf

logger = logging.getLogger(__name__)

def launch(runner, spec):
    """
    Launch the given job spec to plow.
    """
    job = spec.launch()
    runner.getJob().putData("jobid", job.id)
    return job

def createLayerSpec(layer):
    lspec = plow.LayerSpec()
    lspec.name = layer.getName()
    lspec.tags =  layer.getArg("tags", ["unassigned"])
    lspec.isPost = layer.getArg("post", False)

    if layer.getArg("maxRetries"):
        lspec.maxRetries = layer.getArg("maxRetries")
    if layer.getArg("service"):
        lspec.service = layer.getArg("service")
    if layer.getArg("memory"):
        lspec.minRam = layer.getArg("memory")
    return lspec

def serialize(runner):
    """
    Convert the job from the internal blueprint stucture to a plow JobSpec.
    """
    job = runner.getJob()
    base_name = runner.getArg("name", job.getName())
    job_name = job.getName()
    log_dir = job.getLogDir()
    
    spec = plow.JobSpec()
    spec.project = os.environ.get("PLOW_PROJECT",
        conf.get("bp.project"))
    spec.username = getpass.getuser()
    spec.uid = os.getuid()
    spec.paused = runner.getArg("pause")
    spec.name =  job_name
    spec.logPath = log_dir
    spec.layers = []
    spec.env = { 
        "BLUEPRINT_SCRIPTS_PATH": conf.get("bp.scripts_dir"),
        "BLUEPRINT_ARCHIVE": job.getPath()
    }
    spec.env.update(runner.getArg("env"))

    for layer in job.getLayers():

        if isinstance(layer, blueprint.Task):
            # These are added via their task containers
            continue

        elif isinstance(layer, blueprint.TaskContainer):
            
            task_cnt_spec = createLayerSpec(layer)
            task_cnt_spec.command = [
                conf.get("bp.scripts_dir") + "/env_wrapper.sh",
                "taskrun",
                "-debug",
                "-task",
                "%{TASK}",
                os.path.join(job.getPath(), "blueprint.yaml")
            ]
            task_cnt_spec.tasks = []
            spec.layers.append(task_cnt_spec)

            for task in layer.getTasks():
                task_spec = plow.TaskSpec()
                task_spec.name = task.getName()
                task_spec.depends=[]
                task_spec.depends+=setupTaskDepends(job, task)
                task_spec.depends+=setupTaskDepends(job, layer)
                task_cnt_spec.tasks.append(task_spec)
        else:
            lspec = createLayerSpec(layer)
            lspec.depends = setupLayerDepends(job, layer)
            lspec.range = layer.getFrameRange()
            lspec.chunk = layer.getChunk()
            lspec.command = [
                conf.get("bp.scripts_dir") + "/env_wrapper.sh",
                "taskrun",
                "-debug",
                "-layer",
                layer.getName(),
                os.path.join(job.getPath(), "blueprint.yaml"),
                "-frame",
                "%{FRAME}"
            ]
            spec.layers.append(lspec)

    logger.debug(str(spec))
    return spec

def setupLayerDepends(job, layer):
    result = []
    for depend in layer.getDepends():
        dspec = plow.DependSpec()
        
        depend_on = job.getLayer(str(depend.dependOn))
        if isinstance(depend_on, (blueprint.Task,)):
            # Layer on Task
            dspec.type = plow.DependType.LAYER_ON_TASK
            dspec.dependentLayer = str(depend.dependent)
            dspec.dependOnTask = str(depend_on)
        else:
            # Layer on Layer + Task by Task
            if depend.type == blueprint.DependType.All:
                dspec.type = plow.DependType.LAYER_ON_LAYER
            elif depend.type == blueprint.DependType.ByTask:
                dspec.type = plow.DependType.TASK_BY_TASK
            else:
                raise Exception("Invalid layer depend type: %s"  % depend.type)
            dspec.dependentLayer = str(depend.dependent)
            dspec.dependOnLayer = str(depend.dependOn)

        result.append(dspec)
    return result


def setupTaskDepends(job, task):
    """
    Setup task dependencies.  Tasks can depend on other
    tasks or layers.
    """
    result = []
    for depend in task.getDepends():
        dspec = plow.DependSpec()
        depend_on = job.getLayer(str(depend.dependOn))
        if isinstance(depend_on, (blueprint.Task,)):
            # Task on Task
            dspec.type = plow.DependType.TASK_ON_TASK
            dspec.dependentTask = str(task)
            dspec.dependOnTask = str(depend_on)
        else:
            # Task on Layer
            dspec.type = plow.DependType.TASK_ON_LAYER    
            dspec.dependentTask = str(task)
            dspec.dependOnLayer = str(depend.dependOn)
        result.append(dspec)
    return result
