#!/usr/bin/env python

# Copyright (c) 2007 by Kenneth Keiter <ken@kenkeiter.com>
#
# This file is part of django-graph.
#
# Django-graph is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Django-graph is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with django-graph.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup
import ctypes.util

def doc(*files):
    return open(os.path.join(os.path.dirname(__file__), *files)).read()

def locateLib(file):
    path = ctypes.util.find_library(file)
    if path is None:
        path = ''
    while not os.path.exists(path):
        path = raw_input('Path to %s:' % file)
        if not os.path.exists(path):
            print 'Path not found.'
    return path

def updateSettings(file):
    print """
We may need to update src/settings.py with paths to the FreeType and Cairo
libraries for your system. If you have never done this before, you will
want to do it now.
    """
    update_p = raw_input('Update settings.py for my system (y): ')
    if update_p.lower() == 'y' or update_p == '':
        settings = """
# This file was dynamically created by setup.py
FREETYPE_LIB_PATH = '%s'
CAIRO_LIB_PATH = '%s'
        """ % (locateLib('libfreetype'), locateLib('libcairo'))
        f = open(file, 'w')
        f.write(settings)
    else:
        print '** Please open src/settings.py now to ensure accuracy. **'
        accurate_p = raw_input('My paths in settings.py are accurate (y or n): ')
        if accurate_p.lower() == 'n' or accurate_p == '':
            print 'Fix your settings.py file and try again.'
            exit()

if __name__ == '__main__':

    updateSettings(os.path.join(os.path.dirname(__file__), 'src', 'settings.py'))

    setup(
        name='djangographs',
        version='0.1.2a',
        author='Kenneth Keiter',
        author_email='ken@sixpixelsapart.com',
        description='A library for creating graphs and charts with Python',
        long_description='\n\n'.join((doc('README.txt'), doc('CHANGES.txt'))),
        license='GPL 3',
        keywords='django graph chart cairo',
        packages=['djangographs', 'djangographs.backends'],
        package_dir={
            'djangographs': 'src',
            'djangographs.backends': os.path.join('src', 'backends'),
        },
        url='http://code.google.com/p/django-graphs/',
        zip_safe=True,
        dependency_links=(
            "http://cairographics.org/pycairo/",
        ),
    )
