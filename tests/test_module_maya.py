#!/usr/bin/env python
import unittest
import os

import setup
import blueprint
import fileseq

from blueprint.modules.maya import Maya

class MayaModuleTests(unittest.TestCase):

    def setUp(self):
        self.job = blueprint.Job("maya_test")
        self.layer = Maya("foo", scene=setup.getTestScene("sphere_v1.mb"))
        self.job.addLayer(self.layer)

    def testSetup(self):
        self.job.setup()

    def testSetup(self):
        self.job.setup()
        self.job.getLayer("foo").execute(fileseq.FrameSet("1-1"))


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(MayaModuleTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
