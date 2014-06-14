This is a port of my first Python project (2007) from [its Google Code project](https://code.google.com/p/django-graphs/) to GitHub. *It may or may not still work.* The port was done for historical reasons. The content of the README below may or may not be relevant.

---

# Django-Graphs

Data presentation is hard enough without graphs looking like they somehow traveled forward through time from 1987 to the present. Django-graphs aims to create a beautiful, extensible, and fast graph rendering library for standalone or conjunctive usage with Django. When running stand-alone, django-graphs is fast and flexible. When running with Django, django-graphs provides cache functionality, simple decorators which turn return values from controllers into cached graphs automatically, and out-of-the-box support for additions such as Psyco and memcached.

## Installing Django-Graphs

### Requirements

To successfully use Django-Graphs, you'll first need to download install the Cairo graphics library and its Python bindings (PyCairo?). You can find instructions for installing Cairo on the Cairo project website: http://cairographics.org/download/

You'll also need the FreeType? library. This is often installed already. If you're using a nix system (including OS X) try running a locate libfreetype and see if you can find one that ends in .dylib or .so. This will be your library.

Optional, but recommended

In order to use caching with memcached, you'll need the Python client API, which you can download from ftp://ftp.tummy.com/pub/python-memcached/

### Installation

If you want to be all hip and cutting-edge, you can check out the development version of Django-Graphs from SVN. To do this, open up a terminal and:

svn checkout http://django-graphs.googlecode.com/svn/trunk/ django-graphs-read-only

From there, execute python setup.py install to install the development version.

Unless you've written your own settings.py file, you'll probably want to let setup.py edit the file for you. Upon executing setup.py, the installer will prompt you for the paths to libcairo and libfreetype if it's unable to find them (often the case). You can use that clever locate command (if you're using Linux, Unix, or OS X) to find them. Something like locate libfreetype or locate libcairo should do the trick. On Linux, Unix, or OS X you'll be looking for a file ending in either .so or .dylib. Take the paths resulting from those searches and enter them when prompted by setup.py. Once it gets ahold of those paths, setup.py will write the configuration file for you and proceed with the install.

When you're done, open up a new Python interpreter and try import djangographs. If no exception is thrown, that's a good sign. There are some examples under the "examples" folder in the files you downloaded using SVN. Have fun!

## Font-Rendering Mechanics

### Introduction

In Django-Graphs, fonts have become a top priority. The scope of this document covers everything from font management to caching.

### The Nitty-Gritty

#### The `FontBook` Object

The `FontBook` object's primary purpose is to manage the different faces and style permutations defined by the user. It also abstracts the `FreeTypeEngine` class (whose name is self-explanatory).

##### Useful Public Methods and Properties
+ `FontBook.engine` is an instance of `FreeTypeEngine`, if you should need to access it directly.
+ `FontBook.styles` is a `list()` of all styles currently in play.
+ `FontBook.faces` is a `dict()` of `FontFace` instances whose keys are the name or path of the font being represented.
+ `FontBook.built_in` is a (short) `list()` of fonts built into the Cairo toy API - you can use them in lieu of loading a TrueType font -- although the processing overhead is similar.
+ `FontBook.initializeFace(face_name_or_path, style_settings=None)` allows you to load a font face by its name (if built-in) or its path (if TrueType). The style_settings param is a dict in which you can specify 'slant', 'weight', and 'size' keys (to be used only if the font is built-in).

#### The `FreeTypeEngine` Class

The `FreeTypeEngine` class provides access to the low-level font rendering functionality provided by the FreeType library. The primary method of `FreeTypeEngine` is `loadFont(path, face_index=0)` which will return a raw Cairo font face (not yet encapsulated in FontFace). The `loadFont` method uses the `ctypes` module to load a FreeType font face from a pointer in memory -- which is created using the private `FreeTypeEngine.__loadFontIntoMemory(path)` method. The nice thing about `__loadFontIntoMemory` is that if a valid external cache (such as memcached) is available, it will load the font from the hard disk into the faster cache and pull it from there every time it needs it. While the file being put into the cache is sometimes as large as 180 kb, it _does_ improve the speed measurably (by almost a fifth of the overall rendering time). If the cache isn't available, it'll just load it from the hard disk - no questions asked.

Generally, you will never have to deal with the `FreeTypeEngine` or its inner workings -- which is nice because it can be very finicky.

#### The `FontFace` Object

`FontFace` instances act as containers for both built-in and FreeType-based font faces. The `FontFace` instances are instantiated by the `FontBook` instance, but are primarily used by the `FontStyle` instances -- which make use of its ability to provide dimensions for and render the face on the canvas. Upon instantiation, `FontFace` instances are provided with access to the supplied cache interface (if one was instantiated for the `Graph` instance) -- as a result, `FontFace` caches the results every time the processor-heavy `dimensions()` method is called. It also handles the actual rendering of the font on the canvas via Cairo's toy rendering API (soon to be replaced by our own font rendering engine).

#### The `FontStyle` Object

The `FontStyle` object encapsulates changes in a font's presentation. Every time a font's rendered style needs to change (i.e. a change in size, slant, weight, etc.), a new FontStyle instance must be created, or the existing instance must be modified.

##### Useful Public Methods and Properties
+ `update(options=None, **kwopts)` allows us to change the `FontStyle`'s parameters without creating a new instance. It handles updating its `FontBook` with the new data, 

### How It All Fits Together

To give you a quick idea of how this all works, here's a good overview: a `FontBook` instance is instantiated for every new graph that's created. The `FontBook` has one `engine` (an instance of `FreeTypeEngine`) and many `FontFace` instances, as well as many `FontStyle` instances.

Assuming that our instance of `Graph` (actually, a subclass thereof) is called `g`, the FontBook instance would be addressed as `g.fonts`. When the `Graph` instance is instantiated, it creates the new `FontBook` instance which, in turn, instantiates the `FontFace` object statically with itself (modeling the so-called 'borg development pattern'). From that point on, every time a new `FontStyle` is created, it registers itself with the instance of `FontBook` that we first created. If the `FontStyle` instance encapsulates a font face that hasn't been loaded already, a new `FontFace` is created that represents that face, and the face itself is loaded by either the `FreeTypeEngine` or Cairo's toy API.

So, to recap:

  * `FontBook`s track font faces and their styling
  * The `FreeTypeEngine` acts as an interface to the FreeType library
  * `FontFace`s represent a single font face and provide metrics/rendering for that face.
  * `FontStyle` encapsulates changes in a font's presentation and act as an interface to those changes.

### Examples

Rendering the font... all alone:

```python
from djangographs.font import *
from djangographs.render_utils import setDynamicSource
import cairo

# Init the rendering surface
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
context = cairo.Context(surface)

# Init the book
fonts = FontBook(context, cache=None)

# Create a font style (with the defaults), and render it.
style = FontStyle()
setDynamicSource(context, '#ff9900')
style.render('Hello, world.', (10, 10))
surface.write_to_png('output.png')
```

## Layer Mechanics

### Of LayerManagers and Layers

One of the best features in django-graphs is that it's *layer-based*. This means that everything rendered on the graph is _actually_ an object that can be repositioned and re-ordered. What does this mean to you? It means that you can write your own layers to be included in the graphs you generate! Oh, and once they're included you can move them around.

### How Layers Work

For those of you that _aren't_ graphic designers, you may not know how layers work or what they are. It's best to explain this with an example:

http://sixpixelsapart.com/images/layer_demo.gif

In the above example, layers 1 and 2 and the transparent background are super-imposed on one another. Layers 1 and 2 have transparent elements (respectively, the star and spiral) that have been cut out -- allowing the layers below to show through.

### About the `LayerManager` class

A `LayerManager` is automatically instantiated for each and every graph under the attribute name `Graph().layers`. The `LayerManager` does exactly what you'd think it would: manage layers. Getting into some detail, the LayerManager does the following things:

+ instantiate new layers with information such as their `position`, `manager` (itself), and a Cairo drawing `context`.
+ organize and manipulate layers by their z-index position or name
+ abstract the gathering of statistics
+ determine interactions between layers (i.e. whether they intersect or if one is inside another)

#### How It Works

The LayerManager class extends the `list` class. This means that the LayerManager can be looped over and layers contained within it can be manipulated just like a list. Alternately, it provides an amount of functionality for managing layers by the name that their creator refers to them as -- as well as functionality to manage their positioning, dimensions, and overlapping (collisions). If you're creating your own layers, it might be useful to understand what functionality the `LayerManager` offers (all methods below are part of the `LayerManager` class and `Graph.layers`):

*Prototype* | *Description*
`new(obj, layer_name, initial_position)` | Where `obj` is an instantiated (via `__init__`) `Layer()` subclass instance, and initial_position is a tuple containing x and y coordinates for the item, new appends a layer to the top of the stack.
`hasLayer(layer_name)` | Returns `True` if layer is in the stack or `False` if not.
`getLayerByName(layer_name)` | Returns a `Layer` object from the stack based upon its name.
`getDimensions(layer_name)` | Shortcut for `getLayerByName('somelayer').dimensions()`.
`findLayersWithinBox(uppercorner, lowercorner)` | Accepts two tuples which are (x,y) coordinates of the upper-left-hand and lower-right-hand corners (respectfully) of a rectangle in which to check if layers exist. Returns a `list` of `Layer` objects.
`isCollision(layer1_name, layer2_name)` | Checks to see if two layers are touching based upon their position and dimensions. Returns `True` or `False`.
`getStackPosition(layer)` | Accepts a `Layer` subclass and determines its position in the stack.
`getCurrentDepth(layer)` | Accepts a `Layer` subclass and returns its position in the stack.
`destroy(layer_name)` | Deletes a layer in the stack by its name.
`renderAll()` | Calls the hidden `render()` method of all the layers in the stack, which in turn call each layer's `renderLayer()` method.

### The Layer Subclass
In django-graphs, each component of a graph (the data, axes, legend, title, etc.) is a class that extends the `Layer` class. As a rule, each subclass of `Layer` need only implement two methods: `dimensions()` and `renderLayer()`. Each layer subclass is created by an instance of `LayerManager` whose `new(obj_name, layer_name, initial_position=(x,y), extra_args={})` method instantiates each newly-created object with a `name`, `position`, `manager`, and Cairo drawing `context`.

Let's briefly outline what each of these values does:

+ The `name` is the layer itself (this attribute is accessible to the subclass as `self.name`)
+ `position`, which is a tuple in the format `(x,y)`. The `position` attribute (accessed by the subclass as `self.position`) gives the layer some idea of where it should be positioned in respect to the overall canvas. If the x or y of the position is larger than the width or height of the canvas, the layer will most likely not be displayed. When rendering, each layer (although it _can_ render anywhere on the Cairo surface) should render with the `position` as its relative point of origin.
+ `manager` is the instance of the LayerManager that created the object itself -- this provides a nifty way for the layer to have some idea of what's going on in the other layers.
+ `context` is the Cairo drawing context on which commands can be executed. Commands that modify the context should *not* be used unless they are being called (directly or indirectly) by `renderLayer()` in the subclass.

Let's create an example shall we?

```python
from djangographs.layering import Layer
from djangographs.render_utils import *

class FunTriangle(Layer):
    
    def __init__(self, line_thickness = 4):
        self.line_thickness = line_thickness
    
    def dimensions(self):
        # cheating, we know our triangle will take up
        # 100 x 100 pixels. Return a tuple in the format 
        # (width, height)
        return (100, 100)
    
    def renderLayer(self):
        x, y = self.position
        self.context.move_to(x, y) # move to the layer's position
        self.context.line_to(x + 100, y) # draw a line to 100px to the right of the origin
        self.context.line_to(x + 100, y + 100) # draw a line from the previous line's endpoint to 100 pixels down from that
        self.context.close_path() # close the path, completing the triangle
        self.set_line_width(self.line_thickness)
        self.context.stroke() # apply the stroke
        setDynamicSource(self.context, '#ff0000') # color it red
        self.context.fill() # fill the triangle with that color
```

Now we implement it:

```python
# let layer_manager be our instance of LayerManager
# let g be an instance of an object extending Graph

# create a triangle at x:10,y:10 on the canvas
g.layers.new('triangle', FunTriangle(), (10,10))
```

... More later!
