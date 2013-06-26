#!/usr/bin/env python
import os
import json
import unittest
import logging

import setup
import blueprint

from common import TestLayer, TestTask

class LayerTests(unittest.TestCase):

    def setUp(self):
        self.job = blueprint.Job("test")
        self.layer = blueprint.TaskIterator("test")

    def testCreateAndGet(self):
        """Create a new layer and add it to a job in non-script mode."""
        self.job.addLayer(self.layer)
        self.assertEquals(self.layer, self.job.getLayer("test"))
        self.assertEquals("test", self.layer.getName())

    def testGetSetArgs(self):
        """Test Get/Set args"""
        value = (1,2,3)
        self.layer.setArg("foo", value)
        self.assertEquals(value, self.layer.getArg("foo"))
        self.assertTrue(self.layer.isArgSet("foo"))
        self.assertFalse(self.layer.isArgSet("bar"))

    def testAddDepend(self):
        """Testing adding a dependency."""
        self.assertEquals(0, len(self.layer.getDepends()))
        other = blueprint.Layer("test2")
        self.layer.dependOn(other, blueprint.DependType.All)
        self.assertEquals(1, len(self.layer.getDepends()))

    def testAddDependByTaskWithConstructor(self):
        """Test setup depend by task with constructor."""
        l1 = TestLayer("testLayerA")
        l2 = TestLayer("testLayerB", depend="testLayerA")
        self.assertEquals(blueprint.DependType.ByTask, l2.getDepends()[0].type)

    def testAddDependAllWithConstructor(self):
        """Test setup depend:all with constructor"""
        l1 = TestLayer("testLayerA")
        l2 = TestLayer("testLayerB", depend="testLayerA:all")
        self.assertEquals(blueprint.DependType.All, l2.getDepends()[0].type)

    def testAddOutput(self):
        """Test adding an output."""
        self.assertEquals(0, len(self.layer.getOutputs()))
        self.layer.addOutput("comp", "/foo/bar.#.dpx")
        self.layer.getOutput("comp")
        self.assertEquals(1, len(self.layer.getOutputs()))

    def testAddInput(self):
        """Test adding an input."""
        self.assertEquals(0, len(self.layer.getInputs()))
        self.layer.addInput("scene", "/foo/bar.blender")
        self.layer.getInput("scene")
        self.assertEquals(1, len(self.layer.getInputs()))

    def testAfterInit(self):
        """Test that after_init is being run by the metaclass."""
        l = TestLayer("test2")
        self.assertTrue(l.afterInitSet)

    def testSetup(self):
        """Test that _setup is being called."""
        # To call setup you must have a job
        l = TestLayer("test2")
        self.job.addLayer(l)
        self.assertFalse(l.setupSet)
        self.job.setup()
        self.assertTrue(l.setupSet)

    def testExecute(self):
        """Test that _execute is being called."""
        l = TestLayer("test2")
        self.assertFalse(l.executeSet)
        l.execute(1)
        self.assertTrue(l.executeSet)

    def testBeforeExecute(self):
        """Test that _beforeExecute is being called."""
        l = TestLayer("test2")
        self.assertFalse(l.beforeExecuteSet)
        l.beforeExecute()
        self.assertTrue(l.beforeExecuteSet)

    def testAfterExecute(self):
        """Test that _afterExecute is being called."""
        l = TestLayer("test2")
        self.assertFalse(l.afterExecuteSet)
        l.afterExecute()
        self.assertTrue(l.afterExecuteSet)

    def testSetFrameRange(self):
        """Test setting the frame range attr."""
        self.job.addLayer(self.layer)
        self.assertEquals("1001-1001", self.layer.getFrameRange())
        self.assertEquals(1001, self.layer.getFrameSet()[0])
        self.assertEquals(1001, self.layer.getFrameSet()[-1])
        self.layer.setFrameRange("1-10")
        self.assertEquals("1-10", self.layer.getFrameRange())
        self.assertEquals(1, self.layer.getFrameSet()[0])
        self.assertEquals(10, self.layer.getFrameSet()[-1])

    def testGetLocalFrameSetChunked(self):
        """Test getting the local frameset."""
        l = TestLayer("test2", chunk=10, range="1-20")
        frameset = l.getLocalFrameSet(1)
        self.assertEquals("1-10", str(frameset.normalize()))
        frameset = l.getLocalFrameSet(11)
        self.assertEquals("11-20", str(frameset.normalize()))

    def testGetLocalFrameSetSingle(self):
        """Test getting the local frameset."""
        l = TestLayer("test2")
        frameset = l.getLocalFrameSet(1)
        print frameset

class TaskTests(unittest.TestCase):

    def testCreateTask(self):
        t = TestTask("test")

if __name__ == "__main__":
    suite = unittest.TestSuite()
    for t in (LayerTests, TaskTests):
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(t))
    unittest.TextTestRunner(verbosity=2).run(suite)



