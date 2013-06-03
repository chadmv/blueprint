"""
Plow outputs plugin.

Registers outputs with the plow server.
"""
import os
import logging
logger = logging.getLogger(__name__)

import blueprint

def afterExecute(layer):

    # When a setup task is complete outputs should
    # be registerd with its parent layer.
    if not isinstance(layer, (blueprint.SetupTask,)):
        return

    import plow

    parent = layer.getParentLayer()
    logger.info("Registering %d outputs" % len(parent.getOutputs()))
    for output in parent.getOutputs():
        logger.info("Registering output with plow: %s" % output.path)

        layer = plow.client.get_layer_by_id(os.environ.get("PLOW_LAYER_ID"))
        layer.add_output(output.path, output.attrs)

