#!/usr/bin/env python
import unittest
import os

import setup
import blueprint

class ArchiveTests(unittest.TestCase):

    def setUp(self):
        self.job = blueprint.Job("test")
        self.layer = blueprint.Layer("test")
        self.job.setup()

    def testArchivePath(self):
        p = self.job.getArchive()
        self.assertTrue(self.job.getName() in p.getPath())
        self.assertTrue(os.path.isdir(p.getPath()))

    def testPutGetData(self):
        p = self.job.getArchive()
        p.putData("foo_str", "a string")
        p.putData("foo_list", ["a", "list"])
        p.putData("foo_dict", {"a": "dict"})

        self.assertEquals("a string", p.getData("foo_str"))
        self.assertEquals(["a", "list"], p.getData("foo_list"))
        self.assertEquals({"a": "dict"}, p.getData("foo_dict"))

    def testPutGetFile(self):
        p = self.job.getArchive()
        path = p.putFile("sleep", os.path.dirname(__file__) + "/scripts/sleep.bps")
        self.assertEquals(path, p.getFile("sleep"))
        self.assertTrue(path.startswith(p.getPath()))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(ArchiveTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
