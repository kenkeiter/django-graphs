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

import cairo
import os
import cStringIO

class OutputMethod(object):
    
    def __init__(self):
        self._surface = None
        self._context = None
        self._output = cStringIO.StringIO()
        self.dimensions = None
    
    @property
    def context(self):
        if self._context is None:
            self._context = cairo.Context(self.surface)
        return self._context

    def writeToFile(self, path):
        self.surface.finish()
        fh = open(path, 'w')
        fh.write(self._output.getvalue())
        return path
        
    def writeToString(self):
        return self._output.getvalue()

class PNG(OutputMethod):
    
    def __init__(self):
        self._surface = None
        self._context = None
        self.dimensions = None
        
    @property
    def surface(self):
        if self.dimensions is None:
            raise 'No dimensions loaded for PNG output.'
        if self._surface is None:
            self._surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *self.dimensions)
        return self._surface
    
    def writeToFile(self, path):
        self.surface.write_to_png(path)
        return path
    
    def writeToString(self):
        output = cStringIO.StringIO()
        self.surface.write_to_png(output)
        return output.getvalue()

class SVG(OutputMethod):
        
    @property
    def surface(self):
        if self.dimensions is None:
            raise 'No dimensions loaded for SVG output.'
        if self._surface is None:
            self._surface = cairo.SVGSurface(self._output, *self.dimensions)
        return self._surface
   
class PDF(OutputMethod):

    @property
    def surface(self):
        if self.dimensions is None:
            raise render_utils.RenderError('No dimensions loaded for PDF output.')
        if self._surface is None:
            self._surface = cairo.PDFSurface(self._output, *self.dimensions)
        return self._surface
