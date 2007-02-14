import math

def hexToRGB(hexstring, digits=2):
    upper_limit = float(int(digits * 'f', 16))
    r = int(hexstring[1:digits+1], 16)
    g = int(hexstring[digits + 1:digits * 2 + 1], 16)
    b = int(hexstring[digits * 2 + 1:digits * 3 + 1], 16)
    return r / upper_limit, g / upper_limit, b / upper_limit

def setDynamicSource(context, srcobject, function_keywords = None):
    import scheme

    if srcobject is None:
        return 0
    if callable(srcobject):
        srcobject = srcobject(**function_keywords)
    if isinstance(srcobject, str):
        color = hexToRGB(srcobject)
        context.set_source_rgb(*color)
    if isinstance(srcobject, (scheme.LinearGradient, scheme.RadialGradient)):
        context.set_source(srcobject.asPattern())

def dehumanizeRotation(humanized_rotation):
    rotations = {
        'horizontal': 0,
        'vertical': -90,
        'diagonal': -45,
        'ooh-ahh just a little bit': 15, # you know what I'm lookin for.
    }
    if isinstance(humanized_rotation, (float, int)):
        return humanized_rotation
    return rotations[humanized_rotation]
    
def frange(lower_limit, upper_limit, increment = 1.0):
    lower_limit = float(lower_limit)
    count = int(math.ceil((upper_limit - lower_limit) / increment))
    return (lower_limit + n * increment for n in xrange(0,count))

def safe_min(obj):
    try:
        return min(obj)
    except:
        return 0

def safe_max(obj):
    try:
        return max(obj)
    except:
        return 0

def roundUpToNearest(value, nearest=5):
    return int(round(((value + (nearest - 1)) / nearest ) * nearest))
    
class RenderError(Exception):
    pass
