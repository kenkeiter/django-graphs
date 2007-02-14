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
import math
import render_utils

class Ticks(object):

    def __init__(self, scheme, tick_type='whole'):
        self.tick = tick_type
        self.scheme = scheme
        self.axis = None
        self.context = None

    def initRendering(self):
        self.context.set_antialias(1)
        self.context.set_line_width(self.scheme['stroke-thickness'])
        render_utils.setDynamicSource(self.context, self.scheme['color'])

    def finishRendering(self):
        self.context.stroke()

    def render(self, **kwargs):
        for arg_name, arg_value in kwargs.items():
            self.__setattr__(arg_name, arg_value)

        if self.scheme['align'] == 'outside':
            offset = 0
        elif self.scheme['align'] == 'centered':
            offset = 0 - round(self.scheme['length'] / 2)
        else:
            offset = 0 - self.scheme['length']
        if self.axis.orientation == 'horizontal':
            self.context.move_to(self.point[0], self.point[1] + offset)
            self.context.line_to(self.point[0], self.point[1] + offset + self.scheme['length'])
        else:
            self.context.move_to(self.point[0] + offset, self.point[1])
            self.context.line_to(self.point[0] + offset + self.scheme['length'], self.point[1])

class DependentValueLabels(object):

    def __init__(self, scheme, tick_type='whole'):
        self.tick = tick_type
        self.scheme = scheme
        self.axis = None
        self.context = None

    def initRendering(self):
        self.context.set_antialias(1)
        render_utils.setDynamicSource(self.context, self.scheme['color'])

    def finishRendering(self):
        self.context.fill()

    def render(self, **kwargs):
        for arg_name, arg_value in kwargs.items():
            self.__setattr__(arg_name, arg_value)

        if self.axis.type == 'dependent':
            height = self.scheme['font'].dimensions(self.scheme['formatter'] % self.value, self.scheme['rotation'])[1]
            self.scheme['font'].render(
                self.scheme['formatter'] % self.value,
                (self.point[0] - self.scheme['margin-right'], self.point[1] - height / 2),
                render_utils.dehumanizeRotation(self.scheme['rotation'])
            )

class CategoryLabels(object):

    def __init__(self, scheme, tick_type='half'):
        self.tick = tick_type
        self.scheme = scheme
        self.axis = None
        self.context = None

    def initRendering(self):
        self.context.set_antialias(1)
        render_utils.setDynamicSource(self.context, self.scheme['color'])

    def finishRendering(self):
        pass

    def render(self, **kwargs):
        for arg_name, arg_value in kwargs.items():
            self.__setattr__(arg_name, arg_value)

        if self.axis.axisNumeric_p:
            height = self.scheme['font'].dimensions(self.scheme['number-formatter'] % self.value)[1]
            self.scheme['font'].render(
                self.scheme['number-formatter'] % self.value,
                (self.point[0], self.point[1] + self.scheme['margin-top']),
                render_utils.dehumanizeRotation(self.scheme['rotation'])
            )
        else:
            height = self.scheme['font'].dimensions(self.value)[1]
            self.scheme['font'].render(
                self.value,
                (self.point[0], self.point[1] + self.scheme['margin-top']),
                render_utils.dehumanizeRotation(self.scheme['rotation'])
            )

class Gridlines(object):

    def __init__(self, scheme, tick_type='whole'):
        self.tick = tick_type
        self.scheme = scheme
        self.axis = None
        self.context = None

    def initRendering(self):
        self.context.set_antialias(1)
        render_utils.setDynamicSource(self.context, self.scheme['color'])
        self.context.set_line_width(self.scheme['stroke-thickness'])
        self.__length = self.axis.intercept.length

    def finishRendering(self):
        self.context.stroke()

    def render(self, **kwargs):
        for arg_name, arg_value in kwargs.items():
            self.__setattr__(arg_name, arg_value)
        if self.axis.orientation == 'horizontal':
            self.context.move_to(self.point[0], self.point[1])
            self.context.line_to(self.point[0], self.point[1] - self.__length)
        else:
            self.context.move_to(self.point[0], self.point[1])
            self.context.line_to(self.point[0] + self.__length, self.point[1])
