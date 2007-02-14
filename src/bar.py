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
import layering, layers
import scheme, schemata
import render_utils
import axis_decorations

class VerticalBarGraph(graph.Graph):
    """
    The VerticalBarGraph class allows one to generate vertical
    bar graphs using django-graphs.
    """

    from graph import Series
    
    def __init__(self, *args, **kwargs):
        super(VerticalBarGraph, self).__init__(*args, **kwargs)
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
        
        # setup the axes
        x_axis, y_axis = self.__generateAxes()
        
        self.__decorateAxes(x_axis, y_axis)

        for i, category in enumerate(x_axis.categories):
            self.layers.new(
                'set_' + ''.join(str(category.title).split()), 
                self.Set(category, x_axis, y_axis), 
                x_axis.positionOfValue(i)
            )

        # render and output
        self.layers.renderAll()
        self.output_interface.writeToFile(output_file)

    def __generateBackground(self):
        return layers.Background()

    def __generateAxes(self):
        axes_scheme = self.layers.scheme['axes']
        height = self.dimensions[1] - self.layers.title.dimensions()[1] - axes_scheme['padding'] * 2
        width = self.dimensions[0] - axes_scheme['padding'] * 2
        axes = layers.Axes((width, height), self.series, self.categories)
        self.layers.new(
            'axes', 
            axes, 
            (axes_scheme['padding'], self.layers.title.dimensions()[1] + self.layers.title.position[1])
        )
        x_axis = axes.independentAxis(title=self.x_title, fixed=True, bucket_mode=True)
        y_axis = axes.dependentAxis(title=self.y_title, fixed=True)
        return x_axis, y_axis
    
    def __decorateAxes(self, x_axis, y_axis):
        for axis in (x_axis, y_axis):
            if axis.scheme['ticks']['major']['enabled']:
                axis.importDecoration(axis_decorations.Ticks(axis.scheme['ticks']['major']))
            if axis.scheme['ticks']['minor']['enabled']:
                axis.importDecoration(axis_decorations.Ticks(axis.scheme['ticks']['minor'], 'half'))
            if axis.scheme['gridlines']['enabled']:
                axis.importDecoration(axis_decorations.Gridlines(axis.scheme['gridlines']))
            if axis.type == 'dependent':
                if axis.scheme['labeling']['value']['enabled']:
                    axis.importDecoration(axis_decorations.DependentValueLabels(axis.scheme['labeling']['value']))
            else:
                if axis.scheme['labeling']['series-labels']['enabled']:
                    axis.importDecoration(axis_decorations.IndependentSeriesLabels(axis.scheme['labeling']['series-labels']))
                if axis.scheme['labeling']['category-labels']['enabled']:
                    axis.importDecoration(axis_decorations.CategoryLabels(axis.scheme['labeling']['category-labels'], 'half'))
        

    class Set(layering.Layer):

        def __init__(self, values, x_axis, y_axis):
            self.values = values
            self.y_axis = y_axis
            self.x_axis = x_axis
            self.zero_pos = self.y_axis.positionOfValue(0)[1]

        def dimensions(self):
            w = self.width - ((self.width / 100) * self.scheme['series-spacing'])
            return (w, 200)

        @property
        def seriesGap(self):
            return self.seriesWidth * (self.scheme['series-spacing'] * .01)

        @property
        def edgeSpacing(self):
            return (self.seriesWidth * (self.scheme['set-spacing'] * .01)) / 2

        @property
        def seriesWidth(self):
            series_factor = self.scheme['set-spacing'] * .01 # converts percent to decimal
            return self.x_axis.categoryWidth / (len(self.values) + series_factor)

        def renderLayer(self):
            offset = 0
            if len(self.values) > 1:
                offset =  self.seriesGap / (len(self.values) - 1)
            cumulative_gap_width = self.seriesGap * (len(self.values) - 1) - offset
            position = self.position[0] + self.edgeSpacing - cumulative_gap_width, self.position[1]

            for i, value in enumerate(self.values):
                v_position = self.y_axis.positionOfValue(value)[1]

                if i > 0:
                    x = position[0] + (i * (self.seriesGap + self.seriesWidth))
                else:
                    x = position[0] + (i * self.seriesWidth)

                self.context.rectangle(
                    x,
                    v_position,
                    self.seriesWidth,
                    self.zero_pos - v_position
                )
                if callable(self.manager.scheme['series']['color']):
                    render_utils.setDynamicSource(
                        self.context,
                        self.manager.scheme['series']['color'],
                        {'value': value, 'loop': i, 'position': v_position}
                    )
                else:
                    try:
                        render_utils.setDynamicSource(
                            self.context,
                            self.manager.scheme['series']['color'][i]
                        )
                    except:
                        raise render_utils.RenderError('Color index out of range.')
                #self.context.stroke()
                self.context.fill()
