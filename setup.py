#!/usr/bin/env python

import os
import sys
import glob
import shutil
import logging
from setuptools import setup, find_packages, Command
from setuptools.command.install import install as _install
from distutils import log


ETC_INSTALL_DIR = "/usr/local/etc/blueprint"


class InstallCommand(_install):

    def run(self):
        _install.run(self)

        self.announce("Running post-install", log.INFO)

        src_paths = set()
        exist_paths = set()
        src = "etc"
        dst = ETC_INSTALL_DIR

        if not os.path.exists(dst):
            os.makedirs(dst)

        for name in os.listdir(src):
            src_path = os.path.join(src, name)
            dst_path = os.path.join(dst, name)

            if not os.path.exists(dst_path):
                self.copy_file(src_path, dst_path)  
            else:
                self.announce("{0} already exists".format(dst_path), log.INFO)

#
# Setup
#
setup(name='plow-blueprint',
      version='0.1.3',

      package_dir = {'': 'lib', 'tests':'tests'},
      packages=find_packages('lib') + find_packages(),
      zip_safe=False,

      scripts=glob.glob("bin/*"),

      cmdclass={"install": InstallCommand},

      test_suite="tests.test_all",

      author='Matt Chambers',
      author_email='yougotrooted@gmail.com',
      url='https://github.com/sqlboy/blueprint',
      description='A Python library for distributing computing using the Plow Render Farm',
     )
