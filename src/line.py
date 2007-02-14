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

import graph
import layers
import scheme, schemata
import render_utils

from layering import Layer

class LineGraph(graph.Graph):

    from graph import Series as BaseSeries
    
    class Series(BaseSeries):
        pass
    
    def __init__(self, *args, **kwargs):
        super(LineGraph, self).__init__(*args, **kwargs)
        self.layers.importBaseScheme(schemata.defaultBarScheme())
        self.title = ''
        self.x_title = ''
        self.y_title = ''
        
    def render(self, output_file):
        # create layers
        if self.layers.scheme['background']['enabled']:
            self.layers.new('background', layers.Background())
        if self.layers.scheme['title']['enabled']:
            position = (self.dimensions[0] / 2, 0)
            self.layers.new('title', layers.Title(self.title), position)
        # create axes layer
        x_axis, y_axis = self.__generateAxes()
        zero_pos = x_axis.positionOfValue(0)
        
        for series in self.series.itervalues():
            self.layers.new(
                'set_' + ''.join(str(series.title).split()), 
                self.Set(series, x_axis, y_axis), 
                zero_pos
            )

        # render and output
        self.layers.renderAll()
        self.output_interface.writeToFile(output_file)

    class Set(Layer):

        def __init__(self, values, x_axis, y_axis):
            self.values = values
            self.y_axis = y_axis
            self.x_axis = x_axis
            self.zero_pos = self.y_axis.positionOfValue(0)

        def dimensions(self):
            w = self.width - ((self.width / 100) * self.scheme['series-spacing'])
            return (w, 200)

        def renderLayer(self):
            render_utils.setDynamicSource(self.context, '#000000')
            for i, category in enumerate(self.values):
                y_position = self.y_axis.positionOfValue(category[0])[1]
                x_position = self.x_axis.positionOfValue(category.title)[0]
                if i == 0:
                    self.context.move_to(x_position, y_position)
                self.context.line_to(x_position, y_position)
            self.context.stroke()

    def __generateBackground(self):
        return layers.Background()

    def __generateAxes(self):
        height = self.dimensions[1] - (self.layers.title + self.layers.legend)[1] - 15
        width = self.dimensions[0] - 20
        axes = layers.Axes((width, height), self.series, self.categories)
        self.layers.new(
            'axes', 
            axes, 
            (10, self.layers.title.dimensions()[1])
        )
        x_axis = axes.independentAxis(title=self.x_title, fixed=True)
        y_axis = axes.dependentAxis(title=self.y_title, fixed=True)
        return x_axis, y_axis
