#!/usr/bin/env python

import unittest

import os
import sys

import logging
logging.basicConfig(level=logging.INFO)

import setup

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(TEST_DIR, "../lib")

sys.path.append(SRC_DIR)
sys.path.append(TEST_DIR)

os.chdir(TEST_DIR)


TESTS = [
    'test_app',
    'test_layer',
    'test_taskrun',
    # 'test_modules',  # this depends on blender. can't include it
]


def additional_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromNames(TESTS))
    return suite


if __name__ == "__main__":
    suite = additional_tests()
    unittest.TextTestRunner(verbosity=2).run(suite)

