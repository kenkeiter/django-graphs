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

from scheme import *
from font import FontStyle
#import bar

def defaultBarScheme():
    style = PresentationSchema('vbar')
    style.addRule(
        layer='background',
        declarations={
            'enabled': True,
            'color': '#ffffff',
            'transparency': 100,
        }
    )
    style.addRule(
        layer='title',
        declarations={
            'enabled': True,
            'font': FontStyle(size=12, align='center'),
            'color': '#333333',
            'transparency': 100,
            'margin-top': 7,
            'margin-bottom': 10,
        }
    )
    style.addRule(
        layer='axes',
        declarations={
            'enabled': True,
            'transparency': 100,
            'padding': 10,
        }
    )
    style.addRule(
        layer='axes',
        selector='independent',
        declarations={
            'enabled': True,
            'transparency': 100,
            'format': {
                'min': 'auto',
                'max': 'auto',
                'increment': 1,
            },
            'labeling': {
                'series-labels': {
                    'enabled': False,
                    'rotation': 'horizontal',
                    'font': FontStyle(size=10),
                    'margin-top': 2,
                    'margin-bottom': 2,
                    'color': '#000000',
                },
                'category-labels': {
                    'enabled': True,
                    'rotation': 'horizontal',
                    'font': FontStyle(size=10, align='center'),
                    'margin-top': 4,
                    'margin-bottom': 0,
                    'color': '#000000',
                    'number-formatter': '%.2f',
                },
                'title': {
                    'enabled': True,
                    'rotation': 'horizontal',
                    'font': FontStyle(),
                    'margin-top': 4,
                    'margin-bottom': 0,
                    'color': '#000000',
                },
            },
            'ticks': {
                'major': {
                    'enabled': True,
                    'color': '#000000',
                    'length': 5,
                    'align': 'inside', # outside, or centered
                    'stroke-thickness': 1,
                },
                'minor': {
                    'enabled': True,
                    'color': '#000000',
                    'length': 3,
                    'align': 'inside', # outside, or centered
                    'stroke-thickness': 1,
                }
            },
            'gridlines': {
                'enabled': False, # or True
                'color': '#AAAAAA',
                'stroke-thickness': 2, # any int
            },
            'border': {
                'enabled': True, # or False
                'stroke-thickness': 1, # any int
                'color': "#000000",
            },
        }
    )
    style.addRule(
        layer='axes',
        selector='dependent',
        declarations={
            'enabled': True,
            'transparency': 100,
            'format': {
                'min': 'auto',
                'max': 'auto',
                'steps': 4,
            },
            'labeling': {
                'value': {
                    'enabled': True,
                    'rotation': 'horizontal',
                    'font': FontStyle(size=10, align='center'),
                    'color': '#000000',
                    'margin-left': 8,
                    'margin-right': 10,
                    'formatter': '%.2f',
                },
                'title': {
                    'enabled': False,
                    'rotation': 'vertical',
                    'font': FontStyle(),
                    'color': '#000000',
                    'margin-left': 8,
                    'margin-right': 0,
                },
            },
            'ticks': {
                'major': {
                    'enabled': False,
                    'color': '#000000',
                    'length': 5,
                    'align': 'inside', # outside, or centered
                    'stroke-thickness': 1,
                },
                'minor': {
                    'enabled': False,
                    'color': '#000000',
                    'length': 3,
                    'align': 'inside', # outside, or centered
                    'stroke-thickness': 1,
                }
            },
            'gridlines': {
                'enabled': True, # or True
                'color': '#AAAAAA',
                'stroke-thickness': 1, # any int
            },
            'border': {
                'enabled': False, # or False
                'stroke-thickness': 1, # any int
                'color': "#BDBDBD",
            },
        }
    )
    style.addRule(
        layer='series',
        declarations={
            'enabled': True,
            'color': ('#1E5691', '#3E9A3B', '#FAA014', '#DA2025', '#7E367F', '#76807F'),
            'transparency': 100,
        }
    )
    style.addRule(
        layer='set',
        declarations={
            'enabled': True,
            'transparency': 100,
            'background-color': '#ffffff',
            'background-transparency': 100, # percent
            'series-spacing': 10, # percent
            'set-spacing': 100, # percent
        }
    )
    style.addRule(
        layer='legend',
        declarations={
            'enabled': True,
            'transparency': 100,
            'background-color': '#ffffff',
            'background-transparency': 100,
            'position': 'bottom',
        }
    )
    return style
