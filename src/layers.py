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

from __future__ import division
import scheme
from layering import Layer
import render_utils
from font import FontStyle

class Background(Layer):

    def dimensions(self):
        return self.canvas_dimensions

    def renderLayer(self):
        render_utils.setDynamicSource(self.context, self.scheme['color'])
        self.context.paint()

class Title(Layer):

    def __init__(self, content):
        self.content = content

    def dimensions(self):
        width, height = self.scheme['font'].dimensions(self.content)
        height += self.scheme['margin-top']
        height += self.scheme['margin-bottom']
        return (width, height)

    def renderLayer(self):
        render_utils.setDynamicSource(self.context, self.scheme['color'])
        self.scheme['font'].style['align'] = 'center' # override user settings
        self.scheme['font'].render(
            self.content, 
            (self.position[0], self.position[1] + self.scheme['margin-top'])
        )

class Legend(Layer):
    
    def __init__(self, series):
        self.series = content
    
    def dimensions(self):
        return (20,40)
    
    def renderLayer(self):
        pass


class Axes(Layer):
    
    from axis import Axis
    
    def __init__(self, dimensions, series, categories, independent_axis_orientation = 'horizontal'):
        self.__independentAxis = None
        self.__dependentAxis = None
        self.__independentAxisOrientation = independent_axis_orientation.lower()
        self.__dimensions = dimensions
        self.series = series
        self.categories = categories
    
    def dimensions(self):
        return self.__dimensions
    
    def __joinAxes(self):
        if self.__independentAxis and self.__dependentAxis:
            self.__independentAxis.interceptAxis(self.__dependentAxis)
            self.__dependentAxis.interceptAxis(self.__independentAxis)
    
    def independentAxis(self, title, fixed=False, bucket_mode=False):
        self.__independentAxis = self.Axis(
            context=self.context,
            canvas_dimensions=self.dimensions(),
            canvas_position=self.position,
            series=self.series,
            categories=self.categories,
            scheme=self.scheme['independent'],
            type='independent',
            orientation=self.__independentAxisOrientation,
            title=title,
            fix_position=fixed,
            bucketMode_p=bucket_mode,
            axes_scheme=self.scheme,
        )
        self.__joinAxes()
        return self.__independentAxis
    
    def dependentAxis(self, title, fixed=False, bucket_mode=False):
        if self.__independentAxisOrientation == 'horizontal':
            orientation = 'vertical'
        else:
            orientation = 'horizontal'
        self.__dependentAxis = self.Axis(
            context=self.context,
            canvas_dimensions=self.dimensions(),
            canvas_position=self.position,
            series=self.series,
            categories=self.categories,
            scheme=self.scheme['dependent'],
            type='dependent',
            orientation=orientation,
            title=title,
            fix_position=fixed,
            bucketMode_p=bucket_mode,
            axes_scheme=self.scheme,
        )
        self.__joinAxes()
        return self.__dependentAxis
    
    def renderLayer(self):
        self.__independentAxis.render()
        self.__dependentAxis.render()
        