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
import render_utils
import axis_decorations

class Axis(object):

    # Initialization Methods --------------------------------------------------

    def __init__(self, **kwargs):
        """
        Initializes a new Axis() instance. Accepts scheme, position,
        orientation, type, categories, context, dimensions as keyword params.
        """
        for arg_name, arg_value in kwargs.items():
            self.__setattr__(arg_name, arg_value)
        if self.type == 'independent':
            self.titles = [cat.title for cat in self.categories]
        self.positive_data, self.negative_data = self.__sortData()
        self.dimensions = self.getDimensions()
        self.axisNumeric_p = self.isAxisNumeric()
        self.window = self.getWindow()
        self.positioningRatio = self.__getPositioningRatio()
        self.decorations = []

    def __sortData(self):
        """
        Sort the data by whether values are positive or negative. Return a
        tuple in the form (positive values, negative values).
        """
        if self.type == 'dependent':
            sort_set = []
            map(sort_set.extend, (c for c in self.categories))
        else:
            sort_set = self.titles
        return filter(lambda v: v > 0, sort_set), filter(lambda v: v < 0, sort_set)

    # Object Properties -------------------------------------------------------

    def getDimensions(self):
        """
        Grab the height (if the axis is horizontal) or the width (if the axis
        is vertical) of the current axis. Return an integer.
        """
        # TODO expand to include ticks and more accurate spacing
        v = 0
        s = self.scheme['labeling']
        if self.orientation == 'horizontal':
            metric = 1 # height of text (y)
        else:
            metric = 0 # width of text (x)
        if self.type == 'independent':
            if s['series-labels']['enabled']:
                v += self.labelMaxDimensions(s['series-labels'], \
                    [str(x.title) for x in self.series])[metric]
            if s['category-labels']['enabled']:
                v += self.labelMaxDimensions(s['category-labels'], \
                    map(str, self.titles))[metric]
            if s['title']['enabled']:
                v += self.labelMaxDimensions(s['title'], self.title)[metric]
        else:
            if s['value']['enabled']:
                v += self.labelMaxDimensions(s['value'], \
                    [str(x[0]) for x in self.categories])[metric]
            if s['title']['enabled']:
                v += self.labelMaxDimensions(s['title'], self.title)[metric]
        return v

    def isAxisNumeric(self):
        """
        Determine whether or not the axis's data contains no strings.
        """
        strings_in = lambda d: any((isinstance(v, basestring) for v in d))
        if strings_in(self.positive_data) or strings_in(self.negative_data):
            return False
        else:
            return True

    def getWindow(self):
        """
        Get a window tuple, equivocal to that of a graphing calculator. This
        duplicates Apple's algorithm from Numbers (rounding the maximum
        value from the dominant quadrant up to the nearest five if the
        number is max is less than 100). The resulting tuple is in the format
        (min value <int or float>, max value <int or float>).
        """
        if self.type == 'independent':
            # we only pay attention to len
            return 0 - len(self.negative_data), len(self.positive_data)
        else:
            # If num < 100 round up to nearest 5. If num > 100 don't round.
            p_max = render_utils.safe_max(self.positive_data)
            if p_max < 100:
                p_max = render_utils.roundUpToNearest(p_max, 5)
            p_min = render_utils.safe_min(self.negative_data)
            if p_min < 100:
                p_min = 0 - render_utils.roundUpToNearest(abs(p_min), 5) # re-invert

            if p_min != 0 and p_max != 0: # no need to scale. avoid 0 div errors.
                if abs(p_min) < p_max:
                    step_value = p_max / self.scheme['format']['steps']
                    p_min = step_value * round(p_min / step_value)
                else:
                    step_value = p_min / self.scheme['format']['steps']
                    p_max = step_value * round(p_max / step_value)

            return p_min, p_max

    def __getPositioningRatio(self):
        """
        Determine a ratio of x:1 for the positioning of the axis in regards
        to its intercept. For every x units in the larger quadrant, there
        will be one unit in the smaller quadrant. Returns a float.
        """
        # handle zero div (dominant quad is fully dominant)
        if self.window[0] == 0: return self.window[1]
        if self.window[1] == 0: return abs(self.window[0])
        # one quad isn't dominant
        if self.window[1] >= self.window[0]:
            return self.window[1] / abs(self.window[0])
        else:
            return abs(self.window[0]) / self.window[1]

    @property
    def length(self):
        """
        Get the length of the axis in pixels.
        """
        assert self.intercept, 'Axis must be intercepted before \
            self.length can be determined.'

        if self.intercept.fix_position:
            if self.orientation == 'horizontal':
                return self.canvas_dimensions[0] - self.intercept.dimensions
            else:
                return self.canvas_dimensions[1] - self.intercept.dimensions - self.axes_scheme['padding']
        else:
            if self.orientation == 'horizontal':
                return self.canvas_dimensions[0]
            else:
                return self.canvas_dimensions[1] - self.axes_scheme['padding'] * 2

    @property
    def categoryWidth(self):
        return self.length / len(self.titles) # bad juju.

    @property
    def relZero(self):
        """
        Calculate the relative zero position for the axis.
        """
        ratio = self.positioningRatio
        if not self.axisNumeric_p:
            return 0
        else:
            # we go on max and min
            if ratio == self.window[1] or ratio == abs(self.window[0]):
                return 0
            if self.window[1] < self.window[0]:
                return (self.length / (ratio + 1)) * ratio
            else:
                return self.length / (ratio + 1)

    @property
    def absBottom(self):
        """
        absBottom returns the position of the bottom left-hand corner of the
        area designated for the axes.
        """
        return self.canvas_position[0], self.canvas_position[1] + \
            self.canvas_dimensions[1]

    @property
    def relLockedOrigin(self):
        """
        relLockedOrigin returns the origin if both axes were locked to
        the bottom and left-hand sides, respectively.
        """
        # CHANGED add assertion that axis is intercepted.
        assert self.intercept, 'Axis must be intercepted before \
            self.length can be determined.'

        if self.orientation == 'horizontal':
            return self.dimensions, self.intercept.dimensions
        else:
            return self.intercept.dimensions, self.dimensions

    @property
    def absLockedOrigin(self):
        """
        absLockedOrigin provides relLockedOrigin as an absolute position on
        the canvas.
        """
        return (
            self.canvas_position[0] + self.relLockedOrigin[1],
            self.canvas_position[1] + self.canvas_dimensions[1] - \
                self.relLockedOrigin[0],
        )

    @property
    def zeroValue(self):
        if self.axisNumeric_p:
            return (self.window[1] + abs(self.window[0])) / len(self.titles)
        else:
            return 0

    @property
    def relOrigin(self):
        """
        relOrigin provides the distance in pixels from the lower corner of
        the canvas (on the (x, y) axes) to the intercept points on each axis.
        This number is based on the position gathered from the ratio.
        """
        if self.orientation == 'horizontal':
            return self.intercept.relZero, self.relZero
        else:
            return self.relZero, self.intercept.relZero

    @property
    def absOrigin(self):
        """
        absOrigin provides relOrigin as an absolute position on the canvas.
        """
        return (
            self.absBottom[0] + self.relOrigin[1],
            self.absBottom[1] - self.relOrigin[0],
        )

    @property
    def borderOrigin(self):
        if self.fix_position:
            if self.intercept.fix_position:
                return self.absLockedOrigin
            else:
                if self.orientation == 'horizontal':
                    return self.absBottom[0], self.absLockedOrigin[1]
                else:
                    return self.absLockedOrigin[0], self.absBottom[1]
        else:
            if self.intercept.fix_position:
                if self.orientation == 'horizontal':
                    return self.absLockedOrigin[0], self.absOrigin[1]
                else:
                    return self.absOrigin[0], self.absLockedOrigin[1]
            else:
                if self.orientation == 'horizontal':
                    return self.absBottom[0], self.absOrigin[1]
                else:
                    return self.absOrigin[0], self.absBottom[1]

    # Methods -----------------------------------------------------------------

    def labelMaxDimensions(self, label_scheme, contents, use_cache = True):
        """
        Return the dimensions of the largest string in the contents list.
        Takes two arguments: label_scheme, and contents - where label_scheme
        is the scheme to apply to the labels in the contents list or tuple.
        If the use_cache argument is True (which it is by default), only the
        height or width will be calculated (shaving ~.004 seconds from proc.
        time), and the other value will be 0.
        """
        text_dims = label_scheme['font'].dimensions(contents, \
            label_scheme['rotation'])
        if not isinstance(text_dims, list):
            width, height = text_dims
        else:
            width, height = render_utils.safe_max(text_dims)
        if 'margin-left' in label_scheme.keys(): width += label_scheme['margin-left']
        if 'margin-right' in label_scheme.keys(): width += label_scheme['margin-right']
        if 'margin-top' in label_scheme.keys(): height += label_scheme['margin-top']
        if 'margin-bottom' in label_scheme.keys(): height += label_scheme['margin-bottom']
        return (width, height)

    def positionOfValue(self, value):
        """
        Get the position of a value on the axis. Returns a tuple of
        x, y coordinates.
        """
        
        if self.bucketMode_p:
            offset = 0
        else:
            offset = -1
        if self.window[1] > self.window[0]:
            # if positive is dominant
            window = self.window[1] + offset
        else:
            # if negative is dominant
            window = self.window[0] + offset
        unit = (self.length - self.relZero) / window
        if isinstance(value, basestring):
            value = self.titles.index(value)
        if self.orientation == 'horizontal':
            zero = (self.borderOrigin[0], self.borderOrigin[1])
        else:
            zero = (self.borderOrigin[0], self.borderOrigin[1] - self.relOrigin[0])
        if self.orientation == 'horizontal':
            return zero[0] + (unit * value), zero[1]
        else:
            return zero[0], zero[1] - (unit * value)

    def interceptAxis(self, axis):
        """
        Specify an Axis object for the current Axis to
        intersect. Returns None.
        """
        self.intercept = axis

    # Rendering ---------------------------------------------------------------

    def __decorateAtTicks(self, *objs):
        """
        Loop overhead is larger than the overhead of setting up the context
        on each loop (via initRendering method of the object at hand). Cute.
        """
        for item in objs:
            # run these items for each tick on each axis
            self.context.save()
            item.context = self.context
            # init rendering for the object
            item.axis = self
            item.initRendering()
            # do the loop
            if self.type == 'dependent':
                if self.window[1] >= abs(self.window[0]):
                    focal_window = 1
                else:
                    focal_window = 0
                increment = abs(self.window[focal_window]) / self.scheme['format']['steps']
                if item.tick == 'whole':
                    upper_lim = abs(self.window[1]) + increment
                else:
                    upper_lim = abs(self.window[1])
                for pos in render_utils.frange(self.window[0], upper_lim, increment):
                    if item.tick == 'whole':
                        point = self.positionOfValue(pos)
                    else:
                        point = self.positionOfValue(pos + (increment / 2))
                    item.render(value=pos, point=point, increment=increment)
            else:
                cat_width = self.categoryWidth
                increment = 1 # fixed
                for point, value in ((self.positionOfValue(i), v) for i, v in enumerate(self.titles)):
                    if item.tick == 'whole':
                        item.render(value=value, point=point, increment=increment)
                    else:
                        shifted_point = point[0] + (cat_width / 2), point[1]
                        item.render(value=value, point=shifted_point, increment=increment)
            # tell the object to paint itself and restore canvas
            if hasattr(item, 'finishRendering') and callable(item.finishRendering):
                item.finishRendering()
            self.context.restore()

    def __renderBorder(self):
        self.context.save()
        self.context.set_antialias(1)
        self.context.set_line_width(self.scheme['border']['stroke-thickness'])
        render_utils.setDynamicSource(self.context, self.scheme['border']['color'])

        if self.orientation == 'horizontal':
            self.context.move_to(*self.borderOrigin)
            self.context.line_to(self.borderOrigin[0] + self.length, \
                self.borderOrigin[1])

        elif self.orientation == 'vertical':
            self.context.move_to(*self.borderOrigin)
            self.context.line_to(self.borderOrigin[0], \
                self.borderOrigin[1] - self.length)

        self.context.stroke()
        self.context.restore()

    def importDecoration(self, decoration):
        self.decorations.append(decoration)

    def __debug(self):
        print '%s (%s) -----------------------------------------------' % (self.orientation, self.type)
        print 'getWindow(): %s' % repr(self.window)
        print 'getDimensions(): %s' % repr(self.dimensions)
        print 'length: %s' % repr(self.length)
        try:
            print 'categoryWidth: %s' % repr(self.categoryWidth)
        except:
            pass
        print 'relZero: %s' % repr(self.relZero)
        print 'absBottom: %s' % repr(self.absBottom)
        print 'relLockedOrigin: %s' % repr(self.relLockedOrigin)
        print 'absLockedOrigin: %s' % repr(self.absLockedOrigin)
        try:
            print 'zeroValue: %s' % repr(self.zeroValue)
        except:
            pass
        print 'relOrigin: %s' % repr(self.relOrigin)
        print 'absOrigin: %s' % repr(self.absOrigin)
        print 'borderOrigin: %s' % repr(self.borderOrigin)
        print 'canvas_dimensions: %s' % repr(self.canvas_dimensions)
        print 'canvas_position: %s' % repr(self.canvas_position)

    def render(self):

        if self.scheme['border']['enabled']:
            self.__renderBorder()
        
        #self.__debug()

        self.__decorateAtTicks(*self.decorations)
