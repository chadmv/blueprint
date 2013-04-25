import os
import logging

logging.basicConfig(level=logging.INFO)

os.environ["BLUEPRINT_CFG"] = os.path.dirname(__file__) + "/../etc/blueprint.cfg"

def getTestScene(name):
    return os.path.dirname(__file__) + "/scenes/" + name
