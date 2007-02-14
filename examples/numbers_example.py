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

Disable memcached if you have to by removing the keyword 
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
    
    g.layers.updateScheme(
        'title.font',
        FontStyle(size=10)
    )
    g.layers.updateScheme(
        'axes.dependent.labeling.value.font',
        FontStyle(size=8, align='right')
    )
    g.layers.updateScheme(
        'axes.independent.labeling.category-labels.font',
        FontStyle(size=8, align='center')
    )
    
    # Uncomment the below/edit paths for EXACT match to Apple's graph
    '''
    g.layers.updateScheme(
        'title.font',
        FontStyle(
            face='GillSansBold.ttf',
            size=10,
        )
    )
    g.layers.updateScheme(
        'axes.dependent.labeling.value.font',
        FontStyle(
            face='GillSans.ttf',
            size=10,
            align='right',
        )
    )
    g.layers.updateScheme(
        'axes.independent.labeling.category-labels.font',
        FontStyle(
            face='GillSans.ttf',
            size=10,
            align='center',
        )
    )
    '''
    
    # Further stylization
    g.layers.updateScheme('axes.independent.labeling.category-labels.margin-top', 8)
    g.layers.updateScheme('axes.independent.ticks.major.enabled', False)
    g.layers.updateScheme('axes.independent.ticks.minor.enabled', False)

    # Instantiate the new graph
    g.title = "AVERAGE PLANT HEIGHTS"
    g.x_title = 'Time'
    g.y_title = 'Plant Height (cm)'

    # Generate the data sets
    control = g.Series('Control')
    control.append('Week 1', 2.1)
    control.append('Week 5', 5.7)
    control.append('Week 10', 8.6)
    control.append('Week 15', 10.5)

    salt = g.Series('Road Salt')
    salt.append('Week 1', 1.7)
    salt.append('Week 5', 4.1)
    salt.append('Week 10', 6.6)
    salt.append('Week 15', 7.6)

    g.importSeries(control, salt)

    # Render the graph
    g.render('numbers_example.png')
