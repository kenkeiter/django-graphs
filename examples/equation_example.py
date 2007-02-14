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

import memcache
from djangographs.bar import VerticalBarGraph
from djangographs.font import FontStyle

'''
This example duplicates an example graph provided in Apple's 
Numbers application. To create an exact duplicate, get ahold of 
Gill Sans Bold and Gill Sans Regular and enable the code commented 
out below (editing the face kw to match the paths to your fonts). 
Otherwise, check out the similar rendering.

Disable MemcachedConnection if you have to by removing the keyword 
and value from below.
'''

if __name__ == '__main__':

    """
    Assumes you're running Memcached locally. If not, remove the cache
    keyword and its value below.
    """

    g = VerticalBarGraph(dimensions=(390, 160), cache=memcache.Client(['127.0.0.1:11211']))

    # Stylize (not the final syntax for doing this)
    g.layers.updateScheme('title.color', '#333333')
    
    g.layers.updateScheme('title.font', FontStyle(size=10))
    g.layers.updateScheme(
        'axes.dependent.labeling.value.font',
        FontStyle(size=8, align='right')
    )
    g.layers.updateScheme(
        'axes.independent.labeling.category-labels.font',
        FontStyle(size=8, align='center')
    )
    
    # Further stylization
    g.layers.updateScheme('axes.independent.labeling.category-labels.margin-top', 8)
    g.layers.updateScheme('axes.independent.ticks.major.enabled', False)
    g.layers.updateScheme('axes.independent.ticks.minor.enabled', False)

    # Instantiate the new graph
    g.title = "y=x^2 and y=-x^2"
    g.x_title = 'X Value'
    g.y_title = 'Y Value'

    # Generate the data sets
    normal = g.Series('y as x^2').fromEquation(range(1,10), lambda x: x ** 2)
    inverted = g.Series('y as -x^2').fromEquation(range(1, 10), lambda x: -x ** 2)
    
    # Import the series
    g.importSeries(normal, inverted)

    # Render the graph
    g.render('equation_example.png')
