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


import render_utils
import cairo
from layering import LayerManager
from font import FontBook
from backends.output import PNG

class Graph(dict):
    """
    Graph() is the baseclass of all charts/graphs created by Django-Graphs.
    It provides structual objects for graph data as well as
    """

    def __init__(self, dimensions=None, output=PNG(), cache=None, **kwargs):
        # initialize output
        self.output_interface = output
        self.output_interface.dimensions = dimensions
        self.render_surface = output.surface
        self.render_cx = output.context
        # initialize functionality
        self.dimensions = dimensions
        self.layers = LayerManager(self.render_cx, dimensions)
        self.fonts = FontBook(self.render_cx, cache=cache)
        # initialize default values
        self.series = {}
        self.categories = []
        # initialize usability aliases
        self.extend = self.layers.new

    def __importCategory(self, category):
        if not category.title in [x.title for x in self.categories]:
            self.categories.append(category)
        else:
            for globalcategory in self.categories:
                if globalcategory.title == category.title:
                    globalcategory.extend(category)

    def importSeries(self, *args):
        """
        importSeries() accepts a Series() as its primary argument. This 
        allows one to add a series (row of data) to the current graph.
        """
        for series in args:
            if isinstance(series, Series):
                self.series[series.title] = series
                map(self.__importCategory, series)
            else:
                raise TypeError('Imported series must be a subclass of Series.')


class Series(list):

    def __init__(self, title, dataset=None):
        """
        Series objects can be init'ed with a dataset so that
        points can be added with just a dict.
        """
        self.title = title
        if isinstance(dataset, dict):
            for x in dataset:
                self.append(x, dataset[x])

    @property
    def titles(self):
        return [cat.title for cat in self]

    def fromEquation(self, rng, func):
        for x in rng:
            self.append(x, func(x))
        return self

    def index(self, title):
        for i, category in enumerate(self):
            if category.title == title:
                return i
        raise KeyError('Unable to find index of given title.')

    def append(self, title, value):
        """Allows a point to be appended to the series."""
        if title not in self.titles:
            list.append(self, Category(title, self.title))
        self[self.index(title)].append(value)

    def extend(self, pairs):
        for title, value in pairs:
            self.append(title, value)

    def insert(self, position, pair):
        title, value = pair
        new_category = Category(title, self.title)
        new_category.append(value)
        list.insert(self, position, new_category)

    def remove(self, title):
        del self[self.index(title)]

    def count(x):
        return len(filter(lambda cat: cat.title == x, self))


class Category(list):
    def __init__(self, title, series_title):
        self.title = title
        self.series_title = series_title
        self.__hash__ = self.title.__hash__ # sort key

    def __repr__(self):
        return "<Category '%s': %r>" % (self.title, [x for x in self])
