#!/usr/bin/env python

import os
import sys
import glob
import shutil
import logging
from setuptools import setup, find_packages, Command


ETC_DST = "/usr/local/etc/blueprint"


class PostInstallCommand(Command):

    description = "Run the post-install process"
    user_options = [  ]

    def initialize_options(self):
        self.__src_paths = set()
        self.__exist_paths = set()
        self.__src = "etc"
        self.__dst = ETC_DST

        for name in os.listdir(self.__src):
            src_path = os.path.join(self.__src, name)
            dst_path = os.path.join(self.__dst, name)
            if not os.path.exists(dst_path):
                self.__src_paths.add((src_path, dst_path))
            else:
                self.__exist_paths.add(dst_path)

    def finalize_options(self):
        pass

    def run(self):
        for p in self.__exist_paths:
            self.announce("{0} already exists".format(p), logging.INFO)

        for src, dst in self.__src_paths:
            dirname, name = os.path.split(dst)
            
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            self.announce("Copying {0} to {1}".format(name, dst), logging.INFO)
            self.copy_file(src, dst)  

#
# Setup
#
setup(name='Blueprint',
      version='0.1.1',

      package_dir = {'': 'lib', 'tests':'tests'},
      packages=find_packages('lib') + find_packages(),

      scripts=glob.glob("bin/*"),

      cmdclass={"post_install": PostInstallCommand},

      test_suite="tests.test_all",

      # data_files=[
      #   ('/usr/local/etc/blueprint', glob.glob('etc/*')),
      # ],

      author='Matt Chambers',
      author_email='yougotrooted@gmail.com',
      url='https://github.com/sqlboy/blueprint',
      description='A Python library for distributing computing using the Plow Render Farm',
     )
