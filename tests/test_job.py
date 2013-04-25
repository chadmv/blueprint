#!/usr/bin/env python
import unittest
import os

import setup
import blueprint

class JobTests(unittest.TestCase):

    def setUp(self):
        self.job = blueprint.Job("test")
        self.layer = blueprint.Layer("test")
        self.job.addLayer(self.layer)

        self.job.setup()

    def testSimpleGetters(self):
        self.job.getName()
        self.job.getId()
        self.job.getLogDir()

    def testGetLayer(self):
        l = self.job.getLayer("test")
        self.assertEquals(self.layer, l)

    def testGetLayers(self):
        layers = self.job.getLayers()
        self.assertTrue(self.layer in self.job.getLayers())

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(JobTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
