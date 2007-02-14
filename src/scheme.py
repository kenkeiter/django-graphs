# Copyright (c) 2007 by Kenneth Keiter <ken@kenkeiter.com>
#
# This file is part of django-graph.
#
# django-graph is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# django-graph is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with django-graph.  If not, see <http://www.gnu.org/licenses/>.

import render_utils
import cairo
from font import FontStyle

class PresentationSchema(dict):
    def __init__(self, *largs):
        self.affects = largs

    def addRule(self, layer, declarations, selector=None):
        if layer in self.keys():
            if selector is None:
                self[layer].update(declarations)
            elif isinstance(self[layer], dict):
                if selector not in self[layer].keys():
                    self[layer][selector] = {}
                self[layer][selector].update(declarations)
        else:
            self[layer] = {}
            if selector is None:
                self[layer].update(declarations)
            else:
                self[layer][selector] = declarations

    def pathUpdate(self, selector, value):
        selector = filter(lambda c: c not in "()[]{}\\\'\"", selector) # prevent XSS
        path = selector.split('.')
        try:
            exec('self[\'' + '\'][\''.join(path) + '\'] = value')
            return True
        except:
            return False

    def getFontStyles(self):

        def deepFind(target):
            if isinstance(target, dict):
                results = []
                for t in target:
                    d = deepFind(target[t])
                    if d is not None:
                        results.extend(d)
                return results
            if isinstance(target, list):
                pass
            if isinstance(target, FontStyle):
                return [target]
            return None

        return deepFind(self)

    def __getattr__(self, name):
        if name in self.keys():
            return self[name]

class LinearGradient(object):
    """
    The LinearGradient class abstracts the creation of radial gradients 
    in Cairo. An instance of this class can be provided as a color in 
    any situation where render_utils.setDynamicSource is used (i.e. 
    most of the time)
    """
    
    def __init__(self, start, end, stops=[]):
        """
        Instantiate a new LinearGradient instance.
        
        Parameters:
            start = tuple: (x0, y0)
            end = tuple: (x1, y1)
            stops = (optional) list of tuples in the form 
                (offset, color, transparency)
        """
        self.start = start
        self.end = end
        self.stops = stops
    
    def addStop(self, offset, color, alpha):
        """
        Adds a transition point to the gradient.
        
        Parameters:
            offset = an offset (in pixels)
            color = a hex color with or without the leading '#'
            alpha = transparency (range 0..1)
        """
        self.stops.append((offset, color, alpha))
    
    def asPattern(self):
        """
        Get the LinearGradient as a Cairo pattern to be applied in 
        the context.
        """
        pattern = cairo.LinearGradient(self.start[0], self.start[1], self.end[0], self.end[1])
        for stop in self.stops:
            r, g, b = render_utils.hexToRGB(stop[1])
            pattern.add_color_stop_rgba (float(stop[0]), r, g, b, float(stop[2]))
        return pattern
    
class RadialGradient(object):
    """
    The RadialGradient class abstracts the creation of radial gradients 
    in Cairo. An instance of this class can be provided as a color in 
    any situation where render_utils.setDynamicSource is used (i.e. 
    most of the time)
    """
    
    def __init__(self, start, end, stops=[]):
        """
        Instantiate a new RadialGradient instance.
        
        Parameters:
            start = tuple: (x_origin, y_origin, radius)
            end = tuple: (x_origin, y_origin, radius)
            stops = (optional) list of tuples in the form 
                (offset, color, transparency)
        """
        self.start = start
        self.end = end
        self.stops = stops
    
    def addStop(self, offset, color, alpha):
        """
        Adds a transition point to the gradient.
        
        Parameters:
            offset = an offset (in pixels)
            color = a hex color with or without the leading '#'
            alpha = transparency (range 0..1)
        """
        self.stops.append((offset, color, alpha))
    
    def asPattern(self):
        """
        Get the RadialGradient as a Cairo pattern to be applied in 
        the context.
        """
        pattern = cairo.RadialGradient(
            self.start[0], 
            self.start[1], 
            self.start[2],
            self.end[0], 
            self.end[1],
            self.end[2],
        )
        for stop in self.stops:
            r, g, b = render_utils.hexToRGB(stop[1])
            pattern.add_color_stop_rgba(stop[0], r, g, b, stop[1])
        return pattern

class Image(object):
    pass
