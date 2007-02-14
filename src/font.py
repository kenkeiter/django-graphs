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
import ctypes
import os
import cairo
import math
import settings

# FontBook --------------------------------------------------------------------

class FontBook(object):
    """
    The FontBook class manages all faces and styles used by django-graph.
    """

    def __init__(self, context, cache = None):
        """
        Initialize the FontBook instance, freetype rendering engine, borg
        FontStyle, and assorted variables.

        Parameters:
            context = a Cairo rendering context instance
            cache = an acceptable object implementing the cache interface

        Useful Variables:
            FontBook.styles = a list() of styles that have been imported into
                the font book
            FootBook.built_in = a set() of fonts built into Cairo

        Notes:
            The FontStyle object uses the so-called 'borg' pattern so that
            every instance of FontStyle created already has a manager (the
            FontBook instance) available -- keeping the oft-used FontStyle
            class light.
        """
        # initialize engines and components
        self.context = context
        self.engine = FreeTypeEngine(cache=cache)
        FontStyle.initManagement(self)
        self.styles = []
        self.faces = {}
        self.built_in = ['sans', 'sans-serif', 'serif']
        self.cache = cache

    def initializeFace(self, face_name_or_path, style_settings=None):
        """
        Initialize a new font face, loading it in FreeType if
        face_name_or_path is not in self.built_in. Cache the resulting
        instance of FontFace locally.

        Parameters:
            face_name_or_path = the name of a built-in face (such as
                'sans' or 'serif') or the path to a supported font file
            style_settings = (optional) a dict with slant, weight, and size
                keys. Will be ignored if FreeType is used.

        Returns:
            An instance of FontFace
        """
        #self, context, name, face, settings={}, cache=None)
        if face_name_or_path in self.faces.keys():
            return self.faces[face_name_or_path]

        if face_name_or_path.lower() in self.built_in:
            face = face_name_or_path # str -- FontFace will use toy API
            settings = style_settings
        else:
            face = self.engine.loadFont(face_name_or_path) # TT API
            settings = {} # ignore settings for TT

        new_face = FontFace(
            context=self.context,
            name=face_name_or_path,
            face=face,
            settings=style_settings,
            cache = self.cache
        )

        self.faces[face_name_or_path] = new_face
        return new_face

    def registerStyle(self, style):
        self.styles.append(style)

# FreeTypeEngine --------------------------------------------------------------

class FreeTypeEngine(object):
    """
    The FreeTypeEngine object provides an interface to the FreeType library
    from the Cairo rendering libraries via Python.
    """

    class PycairoContext(ctypes.Structure):
        """
        Used singularly by FreeTypeEngine.laodFont() to store C cairo context.
        """
        _fields_ = [
            ('PyObject_HEAD', ctypes.c_byte * object.__basicsize__),
            ('ctx', ctypes.c_void_p),
            ('base', ctypes.c_void_p),
        ]

    def __init__(self, cache = None):
        """
        Initializes the FreeType font engine.

        Parameters:
            cache = an acceptable instance of a caching object

        Raises:
            render_utils.RenderError if unable to init engine or paths to libs are bad.

        Notes:
            Paths to libs are set in settings.py -- which is created at
            install time (since the libaries are almost never in a common
            place, *nix's "locate" command is used by setup.py)
        """
        self.cache = cache # set cache regardless of value
        self.loadedFontBuffers = [] # prevent GC by holding ptrs here.
        try:
            self.freetype_dl = ctypes.CDLL(settings.FREETYPE_LIB_PATH)
            self.cairo_dl = ctypes.CDLL(settings.CAIRO_LIB_PATH)
            self.freetype_lib = ctypes.c_void_p()
            ft_response = self.freetype_dl.FT_Init_FreeType(
                ctypes.byref(self.freetype_lib)
            )
            if ft_response != 0:
                raise
        except:
            raise render_utils.RenderError('Unable to initialize the FreeTypeEngine. \
                Check lib paths in settings.py.')


    @property
    def cachingEnabled(self):
        return self.cache is not None

    def __loadFontIntoMemory(self, path):
        """
        Attempt to laod a font file into memory. If caching is enabled, attempt
        to load the file from there first. If not, or the file is not found in
        the cache, load the file into memory from physical storage and cache
        it if caching is enabled.

        Parameters:
            path = the path to the desired font

        Returns:
            ctypes string_buffer or None

        Raises:
            render_utils.render_utils.RenderError if font does not exist.
        """
        if self.cachingEnabled:
            try:
                font_data = self.cache.get('djangographs.fonts.files.%s' % str(path.__hash__()))
                ptr = ctypes.create_string_buffer(font_data) # malloc equiv.
                self.loadedFontBuffers.append(ptr)
                return ptr
            except:
                pass
        if not os.path.isfile(path) and not os.path.islink(path):
            raise render_utils.RenderError('Supplied font file (%s) does not exist.' % path)
        try:
            font_data = open(path, 'rb').read()
            if self.cachingEnabled:
                self.cache.set('djangographs.fonts.files.%s' % str(path.__hash__()), font_data)
            ptr = ctypes.create_string_buffer(font_data)
            self.loadedFontBuffers.append(ptr)
            return ptr
        except:
            return None


    def loadFont(self, path=None, face_index=0):
        '''
        Attempt to load a FreeType font face into memory from either a file
        or the cache (if enabled). If caching is enabled, the font will be
        added if it is not already.

        Parameters:
            path = the path to the desired font file (.ttf, etc.)
            face_index = the index of the face if the file contains
                multiple faces.

        Returns:
            Cairo font_face created by cairo.Context.get_font_face()

        Raises:
            render_utils.RenderError on FreeType failure.

        Notes:
            Apple DFONT files are not supported since they store their data
            in the resource fork instead of the data fork. DFONT is relatively
            proprietary, but I expect to have DFONT support available in the
            next major release.
        '''

        if path is None:
            raise render_utils.RenderError('Path to font file not defined.')

        # init values/types
        ft_face = ctypes.c_void_p() # destination face
        self.cairo_dl.cairo_ft_font_face_create_for_ft_face.restype = ctypes.c_void_p
        create_status = -1 # default to fail
        surface = cairo.ImageSurface(cairo.FORMAT_A8, 0, 0)
        render_context = cairo.Context(surface)
        cairo_t = self.PycairoContext.from_address(id(render_context)).ctx

        font_data = self.__loadFontIntoMemory(path)

        create_status = self.freetype_dl.FT_New_Memory_Face(
            self.freetype_lib,
            font_data,
            ctypes.c_long(len(font_data.raw)),
            face_index,
            ctypes.byref(ft_face)
        )

        if create_status != 0:
            raise render_utils.RenderError('Failed to create a new FreeType face.')
        cr_face = self.cairo_dl.cairo_ft_font_face_create_for_ft_face(ft_face)
        if self.cairo_dl.cairo_set_font_face(cairo_t, cr_face) != 0:
            raise render_utils.RenderError('Unable to prepare font for face creation.')
        return render_context.get_font_face()

# FontFace --------------------------------------------------------------------

class FontFace(object):
    """
    The FontFace object acts as a container for a single Cairo font face
    (either built in, or from FreeType)
    """

    def __init__(self, context, name, face, settings={}, cache=None):
        """
        Initialize the FontFace instance.

        Parameters:
            context = a Cairo rendering context instance
            name = the name (or path) of the font
            face = the name (if built-in) or a font_face created by
                a Cairo context
            settings = a dict with size, slant, and weight keys only
                used if the font is built in.
            cache = an object implementing the cache interface
        """
        self.ft_face = face
        self.name = name
        self.dimension_cache = {}
        self.context = context
        self.settings = settings
        self.cache = cache

    @property
    def cachingEnabled(self):
        # self explanatory (said the comment)
        return self.cache is not None

    def activate(self):
        """
        Set Cairo context's active font face to the font represented
        by this FontFace object.
        """
        if isinstance(self.ft_face, basestring):
            # built-in fonts use select_font_face
            self.context.select_font_face(
                self.ft_face,
                self.settings['slant'],
                self.settings['weight']
            )
        else:
            # non-built-in fonts use set_font_face
            self.context.set_font_face(self.ft_face)

    def __computeCacheKey(self, size, content, rotation):
        """
        Determine the key to use with the cache to refer to a specific
        permutation of the face.

        Parameters:
            size = size (in pt.) of the font (int/float)
            content = the actual content we're testing (str)
            rotation = the rotation in degrees (int/float)

        Returns:
            string made up of concatenated characteristics
        """
        cache_addy = (
            self.name.__hash__(),
            size,
            rotation,
            content.__hash__()
        )
        return 'fn:%d,size:%d,rotation:%d.chsh:%d' % cache_addy

    def __setCachedDimensions(self, size, content, rotation, dimensions):
        """
        Locally (and remotely, if enabled) insert dimensions into the cache.

        Parameters:
            size = size (in pt.) of the font (int/float)
            content = the actual content we're testing (str)
            rotation = the rotation in degrees (int/float)
            dimensions = tuple or list of dims in format [width, height]
        """
        key = self.__computeCacheKey(size, content, rotation)
        self.dimension_cache[key.__hash__()] = dimensions
        if self.cachingEnabled:
            self.cache.set('djangographs.fonts.dimensions.' + key, dimensions)

    def __getCachedDimensions(self, size, content, rotation):
        """
        Get dimensions cached locally (or remotely, if enabled).

        Parameters:
            size = size (in pt.) of the font (int/float)
            content = the actual content we're testing (str)
            rotation = the rotation in degrees (int/float)

        Returns:
            A tuple or list of dims in form [width, height] or None if the
            key isn't available in the cache.
        """
        key = self.__computeCacheKey(size, content, rotation)
        try:
            return self.dimension_cache[key.__hash__()]
        except:
            if self.cachingEnabled:
                cache_result = self.cache.get('djangographs.fonts.dimensions.' + key)
                # do a simple local cache (for key, hash is fast + unique)
                if key not in self.dimension_cache:
                    self.dimension_cache[key.__hash__()] = cache_result
                return cache_result
            else:
                return None

    def dimensions(self, size, content, rotation = 0):
        """
        Determine the dimensions (in pixels) of the provided content with
        a given size and (optionally) rotation.

        Parameters:
            size = size (in pt.) to be used in the calculations (int/float)
            content = content to find the dimensions of (str)
            rotation = humanized (str) or dehumanized (int) rotation

        Returns:
            A tuple in the format (width, height)

        Notes:
            Dimensions are cached locally (or remotely, if enabled) as they
            are created. Determining dimensions is processor-intensive --
            caching improves performance measurably in most situations.
        """
        if isinstance(rotation, str):
            rotation = render_utils.dehumanizeRotation(rotation)
        try:
            dims = self.__getCachedDimensions(size, content, rotation)
            if dims is None:
                raise
            return dims
        except:
            self.context.save()
            self.activate()
            self.context.set_font_size(size)
            w, h, x_adv, y_adv = self.context.text_extents(content)[2:]
            if rotation != 0:
                w = w * math.cos(math.radians(abs(rotation)))
                h = h * math.sin(math.radians(abs(rotation)))
            self.context.restore()
            # cache dimensions
            self.__setCachedDimensions(size, content, rotation, (w, h))
            return w, h

    def render(self, size, position, align, content, rotation = 0):
        """
        Render content to the context.

        Parameters:
            size = size (in pt.) to render the text with (int/float)
            position = tuple or list in format (x, y) from the upper-left-
                hand corner of the canvas (int, int)
            align = ('center', 'left', or 'right') positions are from the
                upper-left-hand corner of the text block being rendered.
            content = string of content to be rendered on the canvas (str)
            rotation = rotation of the text in deg./humanized around the
                upper-left-hand corner of the text block (string/int/float)

        Returns:
            The width and height of the rendered text in the format
                (width, height)
        """
        if isinstance(rotation, str):
            rotation = render_utils.dehumanizeRotation(rotation)
        x, y = position
        self.context.save()
        self.activate()
        self.context.set_font_size(size)
        width, height = self.dimensions(size, content, rotation)
        y += height # measure fonts from the upper left-hand corner
        align = align.lower()
        if align == 'center':
            x = x - (width / 2)
        elif align == 'left':
            pass # default align
        elif align == 'right':
            x = x - width
        else:
            raise render_utils.RenderError('Unknown align when attempting to render font.')
        self.context.move_to(x, y)
        if rotation != 0:
            self.context.translate(x, y)
            self.context.rotate(math.radians(rotation))
            #self.context.text_path(content)
            #self.context.fill()
            self.context.show_text(content)
        else:
            self.context.show_text(content)
        self.context.fill()
        self.context.restore()
        return (width, height)

# FontStyle --------------------------------------------------------------------

class FontStyle(object):
    """
    The FontStyle class abstracts FontFace and provides a method
    of encapsulating style changes in a mutable object. FontStyle
    uses the Borg development pattern (in that every instance shares
    a single FontBook).
    """
    __shared_book = None

    @staticmethod
    def initManagement(book):
        """
        Set the instance of FontBook to be used by all FontStyles.
        This only needs to be called once and not on an instance
        of FontStyle.

        Parameters:
            book = an instance of FontBook
        """
        FontStyle.__shared_book = book

    def __init__(self, **kwargs):
        """
        Initialize a new FontStyle object. Allows one to override
        the default styles upon creation via keyword args.

        Parameters:
            *Note: All are keywords
            face = the name (built-in) or path of a font face to use (str)
            size = size (in pt.) to use for this style
            slant = the slant (0 or 1) to be used for the font if built-in
            weight = the weight (0 or 1) to be used for the font if built in
            align = alignment ('centered', 'left', 'right') to be used
                for the style
        """
        self.book = self.__shared_book # intantiate statics
        if self.book is not None:
            self.book.registerStyle(self) # let thyself be known
        else:
            raise 'No FontBook provided for new FontStyle object.'
        if hasattr(self, 'style'):
            self.update(kwargs)
        else:
            self.style = self.defaults
            self.update(kwargs)

    def update(self, options=None, **kwopts):
        """
        Update the font's options with a new dict or set of keyword args.

        Parameters:
            options = dict of options (with any keys matching
                FontStyle.defaults) with which to update style's attribs.
            keywords:
                face = the name (built-in) or path of a font face to use (str)
                size = size (in pt.) to use for this style
                slant = the slant (0 or 1) to be used for the font if built-in
                weight = the weight (0 or 1) to be used for the font if built in
                align = alignment ('centered', 'left', 'right') to be used
                    for the style
        """
        if options is not None:
            self.style.update(options)
        if len(kwopts) > 0:
            self.style.update(kwopts)
        self.ft_face = self.book.initializeFace(self.style['face'], self.style)

    @property
    def defaults(self):
        return {
            'face': 'sans',
            'size': 12,
            'slant': 0,
            'weight': 0,
            'align': 'left',
        }

    def dimensions(self, content, rotation = 0):
        """
        Get the dimensions of the provided content with the given rotation.

        Parameters:
            content = Iterable or string with content
            rotation = humanized or unhumanized version of the rotation

        Returns:
            If content is iterable will return a list of dimensions.
            Otherwise, will return tuple of (width, height).
        """
        if hasattr(content, '__iter__') and \
            not isinstance(content, basestring):
            return [self.ft_face.dimensions(self.style['size'], item, \
                rotation) for item in content]
        else:
            return self.ft_face.dimensions(
                self.style['size'],
                content,
                rotation
            )

    def render(self, content, position, rotation = 0):
        """
        Render the content using this font style on the canvas given a
        position and rotation.

        Parameters:
            content = str to render
            position = (x,y) tuple or list of coordinates with origin in
                upper-left-hand corner of canvas.
            rotation = humanized or unhumanized version of the rotation
        """
        self.ft_face.render(
            self.style['size'],
            position,
            self.style['align'],
            content,
            rotation
        )
