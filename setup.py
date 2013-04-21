#!/usr/bin/env python

import os
import glob
from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)


#
# Data 
#
def get_data(*paths):
    data = []
    for p in paths:
        if not p.startswith(ROOT):
            p = os.path.join(ROOT, p)
        data.extend(glob.iglob(p))
    return data

#
# Setup
#
setup(name='Blueprint',
      version='0.1',

      package_dir = {'': 'lib', 'tests':'tests'},
      packages=find_packages('lib') + find_packages(),

      scripts=glob.glob("bin/*"),

      test_suite="tests.test_all",

      data_files=[
        ('/usr/local/etc/blueprint', glob.glob('etc/*')),
      ],

      author='Matt Chambers',
      author_email='yougotrooted@gmail.com',
      url='https://github.com/sqlboy/blueprint',
      description='A Python library for distributing computing using the Plow Render Farm',
     )
