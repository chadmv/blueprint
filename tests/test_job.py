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

    def testAddLayer(self):
        l = blueprint.Layer("add_twice")
        self.job.addLayer(l)
        # The second time should be ignored
        self.job.addLayer(l)

    def testGetSetFrameRange(self):
        self.assertEquals("1001-1001", self.job.getFrameRange())
        self.assertEquals(1001, self.job.getFrameSet()[0])
        self.assertEquals(1001, self.job.getFrameSet()[-1])
        self.job.setFrameRange("1-10")
        self.assertEquals("1-10", self.job.getFrameRange())
        self.assertEquals(1, self.job.getFrameSet()[0])
        self.assertEquals(10, self.job.getFrameSet()[-1])

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(JobTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
