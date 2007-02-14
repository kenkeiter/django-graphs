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

class LayerManager(list):

    def __init__(self, context, canvas_dimensions):
        self.context = context
        self.canvas_dimensions = canvas_dimensions

    def importBaseScheme(self, scheme):
        self.scheme = scheme
        self.updateScheme = self.scheme.pathUpdate # alias

    def new(self, layer_name, obj, initial_position = (0,0)):
        obj.name = layer_name
        obj.position = initial_position
        obj.manager = self
        obj.context = self.context
        if obj.__class__.__name__.lower() in self.scheme.keys():
            obj.scheme = self.scheme[obj.__class__.__name__.lower()]
        self.insert(0, obj)
        return obj

    def getLayerByName(self, layer_name):
        for layer in self:
            if layer.name == layer_name:
                return layer
        return False

    def hasLayer(self, layer_name):
        if self.getLayerByName(layer_name) is not False:
            return True
        return False

    def getDimensions(self, layer_name):
        return self.getLayerByName(layer_name).dimensions()

    def findLayersWithinBox(self, uppercorner, lowercorner):
        box = (range(uppercorner[0], lowercorner[0]), \
            range(uppercorner[1], lowercorner[1]))
        for layer in self:
            if any([(x in box[0]) for x in layer[0]]) and \
                any([(x in box[1]) for x in layer[1]]):
                yield layer

    def isCollision(self, layer1_name, layer2_name):
        l1 = self.getLayerByName(layer1_name).positionalBounds()
        l2 = self.getLayerByName(layer2_name).positionalBounds()
        if any([(x in l1[0]) for x in l2[0]]) and \
            any([(x in l1[1]) for x in l2[1]]):
            return True

    def getStackPosition(self, layer):
        return self.index(layer)

    def getCurrentDepth(self):
        return len(self)

    def destroy(self, layer_name):
        index = self.getStackPosition(self.getLayerByName(layer_name))
        del self[index]

    def renderAll(self):
        self.reverse()
        for layer in self:
            try:
                if layer.scheme['enabled']:
                    layer.render(layer.scheme['transparency'] * 0.01)
            except:
                layer.render(1)
        self.reverse() # return it back to normal

    def moveToTop(self, layer):
        currentPos = layer.zIndex()
        if currentPos != 0:
            self.insert(0, layer)
            del self[currentPos + 1]

    def moveToBottom(self, layer):
        currentPos = layer.zIndex()
        if currentPos != len(self):
            self.append(layer)
            del self[currentPos - 1]

    def moveUp(self, layer):
        currentPos = layer.zIndex()
        if currentPos - 2 >= 0:
            self.insert(currentPos - 2, layer)
            del self[currentPos + 1]

    def moveDown(self, layer):
        ''' Work on this '''
        currentPos = layer.zIndex()
        if currentPos + 2 >= 0:
            self.insert(currentPos + 2, layer)
            del self[currentPos + 1]

    def __getattr__(self, attr_name):
        return self.getLayerByName(attr_name)

    def __repr__(self):
        items = ['<\'%s\': %r>' % (item.name, item) for item in self]
        return '[' + ','.join(items) + ']'

class Layer(object):

    # Layer Specifics
    name = 'Unnamed Layer'
    position = (0,0)
    manager = None
    context = None
    scheme = None
    padding = {'top': 0, 'left': 0, 'bottom': 0, 'right': 0}

    # Manipulation Methods
    def zIndex(self): return self.manager.getStackPosition(self)
    def moveToTop(self): return self.manager.moveToTop(self)
    def moveToBottom(self): return self.manager.moveToBottom(self)
    def moveUp(self): return self.manager.moveUp(self)
    def moveDown(self): return self.manager.moveDown(self)

    def dimensions(self):
        return 0,0

    def render(self, opacity=1):
        if hasattr(self, 'initLayer') and callable(self.initLayer):
            self.initLayer()
        if hasattr(self, 'renderLayer') and callable(self.renderLayer):
            self.context.push_group()
            self.renderLayer()
            self.context.pop_group_to_source()
            self.context.paint_with_alpha(opacity)

    def reposition(self, new_position):
        self.position = new_position

    def positionalBounds(self):
        """
        Returns two tuples (within a tuple) that are the minimum and
        maximum coordinates of the layer.
        """
        dims = self.dimensions()
        xrange = range(self.position[0], dims[0])
        yrange = range(self.position[1], dims[1])
        return (xrange, yrange)

    ###################################################################
    # Op Overriding
    ###################################################################

    def __contains__(self, other):
        l1 = self.positionalBounds()
        if isinstance(other, Layer):
            l2 = self.getLayerByName(layer2_name).positionalBounds()
            if any([(x in l1[0]) for x in l2[0]]) and any([(x in l1[1]) for x in l2[1]]):
                return True
        elif isinstance(other, (tuple, list)):
            if other[0] in l1[0] and other[1] in l1[1]:
                return True
        return False

    def __selfAndTargetDimensions(self, other):
        """
        Rather hackish and poorly-named function to be used
        with magic names to determine if input is valid and
        what the input should be.
        """
        myDimensions = self.dimensions()
        if isinstance(other, Layer):
            otherDimensions = other.dimensions()
        elif isinstance(other, (int, float, long)):
            otherDimensions = (other, other)
        else:
            otherDimensions = other
        return (myDimensions, otherDimensions)

    def __add__(self, other):
        myDimensions, otherDimensions = self.__selfAndTargetDimensions(other)
        return (myDimensions[0] + otherDimensions[0], myDimensions[1] + otherDimensions[1])

    __radd__ = __add__

    def __sub__(self, other):
        myDimensions, otherDimensions = self.__selfAndTargetDimensions(other)
        return (myDimensions[0] - otherDimensions[0], myDimensions[1] - otherDimensions[1])

    def __mul__(self, other):
        myDimensions, otherDimensions = self.__selfAndTargetDimensions(other)
        return (myDimensions[0] * otherDimensions[0], myDimensions[1] * otherDimensions[1])

    __rmul__ = __mul__

    def __floordiv__(self, other):
        myDimensions, otherDimensions = self.__selfAndTargetDimensions(other)
        return (myDimensions[0] // otherDimensions[0], myDimensions[1] // otherDimensions[1])

    def __mod__(self, other):
        myDimensions, otherDimensions = self.__selfAndTargetDimensions(other)
        return (myDimensions[0] % otherDimensions[0], myDimensions[1] % otherDimensions[1])

    def __pow__(self, other):
        myDimensions, otherDimensions = self.__selfAndTargetDimensions(other)
        return (pow(myDimensions[0], otherDimensions[0]), pow(myDimensions[1], otherDimensions[1]))

    def __div__(self, other):
        myDimensions, otherDimensions = self.__selfAndTargetDimensions(other)
        return (myDimensions[0] / otherDimensions[0], myDimensions[1] / otherDimensions[1])
