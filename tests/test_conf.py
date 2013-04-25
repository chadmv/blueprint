#!/usr/bin/env python
import unittest
import os

import setup
import blueprint

class ConfTests(unittest.TestCase):

    def testGetModule(self):
        """
        Test getting a module configuration.
        """
        cfg = blueprint.conf.get("modules.maya")
        self.assertEquals(4, cfg["padding"])
        self.assertEquals("name.#.ext", cfg["fnc"])
        self.assertEquals("sw", cfg["renderer"])
        self.assertEquals("png", cfg["format"])

    def testGetDefaults(self):
        """
        Test getting the blueprint defaults
        """
        cfg = blueprint.conf.get("bp")
        self.assertEquals("test-scene.shot-%(USER)s_%(JOB_NAME)s",
            cfg["job_name_template"])

    def testAutoInterpolate(self):
        """
        Test automatic interpolation.
        """
        home = os.environ.get("HOME", "")
        value = blueprint.conf.get("bp.output_dir")
        self.assertEquals("%s/blueprint/rnd" % home, value)

    def testPassInterpolate(self):
        """
        Test passing values to interpolate
        """
        user = os.environ.get("USER", "")
        value = blueprint.conf.get("bp.job_name_template", JOB_NAME="comp")
        self.assertEquals("test-scene.shot-%s_%s" % (user, "comp"), value)

    def testInterpolateFunction(self):
        """
        Manual test of the interpolation function.
        """
        s = "%(a)s + %(b)s"
        self.assertEquals("1 + 2", blueprint.conf.interp(s, a="1", b="2"))

    def testGetDefaultValue(self):
        """
        Test fetching an invalid key.
        """
        self.assertEquals(blueprint.conf.Default, blueprint.conf.get("nothing"))
    
    def testGetRaiseException(self):
        """
        Test throwing an exception.
        """
        self.assertRaises(blueprint.exception.BlueprintException, 
            blueprint.conf.get, "nothing", default=blueprint.conf.Raise)

    def testEnvOverride(self):
        """
        Test the environment override feature.
        """
        os.environ["TEST_TEST_TEST"] = "a"
        self.assertEquals("a", blueprint.conf.get("test.test.test"))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(ConfTests)
    unittest.TextTestRunner(verbosity=2).run(suite)