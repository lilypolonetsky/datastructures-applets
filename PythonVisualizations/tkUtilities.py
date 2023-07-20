__doc__ = """
Utilty methods and classes for Tk, and in particular, a specialized
version of canvas called 'Scrim', and a cache of Tk images.
"""

import re, sys, math, os
from tkinter import *
from tkinter import ttk
import tkinter.font as tkfont
from enum import Enum

try:
    from PIL import Image as Img
    from PIL import ImageTk
except ModuleNotFoundError as e:
    print('Pillow module not found.  Did you try running:')
    print('pip3 install -r requirements.txt')
    raise e

try:
    from coordinates import *
except ModuleNotFoundError:
    from .coordinates import *
    
V = vector

def BBoxesOverlap(bbox1, bbox2, zeroOK=True):
    'Determine if bounding boxes overlap'
    half = len(bbox1) // 2
    return all(rangesOverlap(bbox1[j], bbox1[j + half], 
                             bbox2[j], bbox2[j + half], zeroOK=zeroOK)
               for j in range(half))

def rangesOverlap(lo1, hi1, lo2, hi2, zeroOK=True):
    'Determine if a range overlaps another.  Allow zero overlap, if requested.'
    return ((hi1 > lo2 or (zeroOK and hi1 == lo2)) and
            (lo1 < hi2 or (zeroOK and lo1 == hi2)))

def BBoxContains(bbox1, bboxOrPoints):
    '''Return whether bounding box 1 fully contains a bounding box or point 
    list of the form (x0, y0, x1, y1, ... , xN, yN) which can be a single
    point.'''
    half = len(bbox1) // 2
    return all(bbox1[j] <= bboxOrPoints[j + k] and
               bboxOrPoints[j + k] <= bbox1[j + half]
               for j in range(half) for k in range(0, len(bboxOrPoints), half))

def BBoxEmpty(bbox):
    'Return whether a bounding box has any area'
    half = len(bbox) // 2
    return not all(bbox[j] < bbox[j + half] for j in range(half))

def BBoxIntersection(*bboxes):
    'Return the, possibly empty, intersection of sequence of bounding boxes'
    if len(bboxes) == 0:
        return [0, 0, 0, 0]
    elif len(bboxes) == 1:
        return bboxes[0]
    else:
        half = len(bboxes[0]) // 2
        return tuple((max if j < half else min)(bbox[j] for bbox in bboxes)
                     for j in range(len(bboxes[0])))

def BBoxUnion(*bboxes):
    'Return the smallest bounding box containing a sequence of bounding boxes'
    if len(bboxes) == 0:
        return [0, 0, 0, 0]
    elif len(bboxes) == 1:
        return bboxes[0]
    else:
        half = len(bboxes[0]) // 2
        return tuple((min if j < half else max)(bbox[j] for bbox in bboxes)
                     for j in range(len(bboxes[0])))

def BBoxEnclosing(*coordinates, dims=2):
    '''Compute the enclosing bounding box for a set of coordinates in the
    form of a Tk coordinate list: x0, y0, x1, y1, ..., xN, yN
    The dims keyword parameter can be 3 or more for higher dimensional BBoxes'''
    minCoords = tuple(min(coordinates[j] 
                          for j in range(dim, len(coordinates), dims))
                      for dim in range(dims))
    maxCoords = tuple(max(coordinates[j] 
                          for j in range(dim, len(coordinates), dims))
                      for dim in range(dims))
    return minCoords + maxCoords

def BBoxCenter(bbox):
    half = len(bbox) // 2
    return V(V(bbox[:half]) + V(bbox[half:])) / 2

def BBoxSize(bbox):
    half = len(bbox) // 2
    return V(bbox[half:]) - V(bbox[:half])

def filterDict(d, filter=lambda key: True):
    '''Return a new copy of dictionary containing only those keys that satisfy
    a filter test'''
    return dict((k, v) for k, v in d.items() if filter(k))

# Tk definitions
# Modifier key constants
SHIFT, CAPS_LOCK, CTRL, ALT = 0x01, 0x02, 0x04, 0x08

# Oddly the ttk module does not define this like tk's ACTIVE
PRESSED = 'pressed'

# Mouse button constants
MOUSE_BUTTON_1, MOUSE_BUTTON_2, MOUSE_BUTTON_3 = 0x0100, 0x0200, 0x0400
class Modifier(Enum):
    Shift = SHIFT
    Caps_Lock = CAPS_LOCK
    Control = CTRL
    Left_Alt = ALT
    Num_Lock = 0x010
    Right_Alt = 0x080
    Mouse_B1 = MOUSE_BUTTON_1
    Mouse_B2 = MOUSE_BUTTON_2
    Mouse_B3 = MOUSE_BUTTON_3

# Window geometry specification strings
geomPattern = re.compile(r'(\d+)[\sXx]+(\d+)([+-])(-?\d+)([+-])(-?\d+)')

# General Tk widget methods
def widgetDimensions(widget):  # Get widget's (width, height)
    geom = widgetGeometry(widget) # Use config if not yet negotiated
    return ((int(widget.config('width')[-1]), int(widget.config('height')[-1]))
            if geom[0] == 1 and geom[1] == 1 else geom[:2])

def widgetGeometry(widget, geom=None):
    'Get widget geometry from <width>x<height><sign>x0<sign>y0 geom string'
    if geom is None:
        widget.update_idletasks()
        geom = widget.winfo_geometry()
    parsed = geomPattern.match(geom)
    if parsed is None:
        return
    nums = tuple(int(parsed.group(p)) for p in (1, 2, 4, 6))
    if parsed.group(3) == '-' or parsed.group(5) == '-':
        nums = nums[:2] + (
            widget.winfo_screenwidth() - nums[2] if parsed.group(3) == '-'
            else nums[2],
            widget.winfo_screenheight() - nums[3] if parsed.group(5) == '-'
            else nums[3])
    else:
        return nums

def widgetState(widget, state=None): # Get or set widget state
    if isinstance(widget, (ttk.Button,)):
        if state is None:
            stateFlags = widget.state()
            return DISABLED if DISABLED in stateFlags else NORMAL
        else:
            widget.state(('!disabled', '!pressed') if state == NORMAL 
                         else (state, ))
    else:
        if state is None:
            return widget['state']
        else:
            widget['state'] = state

sizePattern = re.compile(r'-?\d+')

def textWidth(font, text=' '):
    return tkFontFromSpec(font).measure(text)
        
def textHeight(font, text=' '):
    lines = text.split('\n')
    nLines = len(lines) if lines and len(lines[-1]) > 0 else len(lines) - 1
    return tkFontFromSpec(font).metrics()['linespace'] * nLines

def tkFontFromSpec(spec):
    family = spec[0]
    size = spec[1] if (len(spec) > 1 and 
                       (isinstance(spec[1], int) or
                        (isinstance(spec[1], str) and 
                         sizePattern.match(spec[1])))) else 0
    return tkfont.Font(
        family=family, size=size,
        weight=lookFor(('bold', 'light'), spec, 'normal'),
        slant=lookFor(('italic', 'oblique'), spec, 'roman'),
        underline=1 if lookFor(('underline',), spec, 0) else 0,
        overstrike=1 if lookFor(('overstrike',), spec, 0) else 0)
        
def lookFor(keys, spec, default):  # Find keyword in font spec
    strings = [x.lower() for x in spec if isinstance(x, str)]
    for key in keys:
        if key.lower() in strings:
            return key
    return default

def parseTkFont(fontspec):
    if isinstance(fontspec, tkfont.Font):
        actual = fontspec.actual()
        return (actual['family'], actual['size'],
                *(() if actual['weight'] == 'normal' else (actual['weight'],)),
                *(() if actual['slant'] == 'roman' else (actual['slant'],)),
                *(() if actual['underline'] == 0 else ('underline',)),
                *(() if actual['overstrike'] == 0 else ('overstrike',)))
    elif isinstance(fontspec, str):
        font = fontspec.split()
        if len(font) > 1:
            return (font[0], int(font[1]), *font[2:])
        return parseTkFont(tkfont.nametofont(fontspec))

def buttonImage(btn, image=None):
    'Get or set the image of a Tk button'
    if image is None:   # Tk stores the actual image in the image attribute
        return btn.image
    else:    
        btn['image'] = image # This triggers an update to the button appearance
        btn.image = image  # and this puts the aclual image in the attribute
        return image

def genericEventHandler(
        to=sys.stdout, fields={'num', 'state', 'char', 'keycode', 'keysym',
                               'width', 'height', 'x', 'y', 'x_root', 'y_root',
                               'serial', 'time'}):
    def genericHandler(event):
        if to:
            print('{} event on {}:'.format(event.type, event.widget),
                  ', '.join('{} = {!r}'.format(attr, getattr(event, attr))
                            for attr in fields),
                  file=to)
            if event.state and isinstance(event.state, int):
                print('Modifiers: {}'.format(
                    ', '.join([mod.name for mod in Modifier
                               if event.state & mod.value])), file=to)
    return genericHandler
    
class Scrim(Canvas):
    '''Enhanced Tk Canvas widget with more convenience methods.
    '''
    # CANVAS ITEM METHODS
    def itemConfig(self, canvasitem, *key, **kwargs):
        '''Do what the tk canvas itemconfigure command does, but return only
        the setting for each item attribute, not the tuple with the name and
        default value.'''
        config = self.itemconfigure(canvasitem, *key, **kwargs)
        if isinstance(config, dict):
            for k in config:     # Replace tuple values with the last item
                if isinstance(config[k], tuple):  # in tuple
                    config[k] = config[k][-1]
        elif len(kwargs) == 0 and isinstance(config, tuple):
            config = config[-1]
        return config
    
    def copyItemAttributes(   # Copy attributes from one canvas item to another
            self, fromItem, toItem, *attributes):
        kwargs = dict((attrib, self.itemConfig(fromItem, attrib))
                      for attrib in attributes)
        self.itemConfig(toItem, **kwargs)

    def copyItem(self, canvasitem, includeBindings=True):
        'Make a copy of an item in the canvas'
        creator = getattr(self,  # Get canvas creation function for type
                          'create_{}'.format(self.type(canvasitem)))
        newItem = creator(*self.coords(canvasitem),
                          **self.itemConfig(canvasitem))
        if includeBindings:  # Copy event handlers if requested
            self.copyItemHandlers(canvasitem, newItem)
        return newItem

    def copyItemHandlers(self, fromItem, toItem):
        for eventType in self.tag_bind(fromItem):
            self.tag_bind(toItem, eventType, self.tag_bind(fromItem, eventType))

    anchorVectors = {
        NW: (-1, -1), N: (0, -1), NE: (1, -1),
        W: (-1, 0), CENTER: (0, 0), E: (1, 0),
        SW: (-1, 1),  S: (0, 1),  SE: (1, 1)}

    def changeAnchor(self, newAnchor, *items):
        'Change the anchor but not the position of a text item'
        for item in items:
            if self.type(item) == 'text':
                anchor = self.itemConfig(item, 'anchor')
                if anchor in self.anchorVectors and anchor != newAnchor:
                    bbox = self.bbox(item)
                    size = V(bbox[2:]) - V(bbox[:2])
                    coords = self.coords(item)
                    delta = V(V(self.anchorVectors[newAnchor]) - 
                              V(self.anchorVectors[anchor])) / 2
                    self.coords(item, V(coords) + V(V(delta) * V(size)))
                    self.itemConfig(item, anchor=newAnchor)

    def coords(self, tagOrID, *args):
        result = super().coords(tagOrID, *args)
        if len(args) == 0 and result:
            return tuple(result)
        return result

    def bbox(self,
             tagOrID: 'Tag or ID of item for bounding box' =None
    ) -> 'Return Tk bounding box when defined, else approximate it':
        result = super().bbox(tagOrID)
        if result: return result
        kind = tagOrID and self.type(tagOrID)
        if kind and self.itemConfig(tagOrID, 'state') == HIDDEN:
            coords = V(self.coords(tagOrID))
            if kind == 'text':
                font = self.getItemFont(tagOrID)
                text = self.itemConfig(tagOrID, 'text')
                size = V(textWidth(font, text), textHeight(font, text))
                halfSize = V(size / 2)
                anchor =  self.itemConfig(tagOrID, 'anchor')
                upperLeft = tuple(map(
                    int,
                    V(coords - halfSize) - V(
                        halfSize * V(self.anchorVectors[anchor]))))
                return upperLeft + (V(upperLeft) + size)
            else:
                box = list(coords[:2]) + list(coords[:2])
                for i in range(2, len(coords)):
                    box[i % 2] = min(box[i % 2], coords[i])
                    box[i % 2 + 2] = max(box[i % 2 + 2], coords[i])
                return tuple(map(int, box))

    FADED_COLORS = {
        'fill': 'bisque', 'outline': 'bisque',
        'activefill': 'bisque', 'activeoutline': 'bisque',
        'disabledfill': 'gray90', 'disabledoutline': 'gray90',
        }

    FADED_FILL = filterDict(FADED_COLORS, lambda k: k.endswith('fill'))
    FADED_OUTLINE = filterDict(FADED_COLORS, lambda k: k.endswith('outline'))

    TYPE_COLORS = {
        'arc': set(('fill', 'outline', 'activefill', 'activeoutline',
                    'disabledfill', 'disabledoutline',)),
        'oval': set(('fill', 'outline', 'activefill', 'activeoutline',
                     'disabledfill', 'disabledoutline',)),
        'polygon': set(('fill', 'outline', 'activefill', 'activeoutline',
                        'disabledfill', 'disabledoutline',)),
        'rectangle': set(('fill', 'outline', 'activefill', 'activeoutline',
                          'disabledfill', 'disabledoutline',)),
        'bitmap': set(('foreground', 'background',
                       'activeforeground', 'activebackground',
                       'disabledforeground', 'disabledbackground',)),
        'line': set(('fill', 'activefill', 'disabledfill',)),
        'text': set(('fill', 'activefill', 'disabledfill',)),
        'image': set(),
        'window': set(),
        None: set()
    }
    
    def fadeItems(self, items, colors=(FADED_FILL,)):
        '''Set colors of canvas items to faded colors while creating a list of
        dictionaries holding the current color settings of the items.
        The colors argument is a list of color dictionaries or a
        single dictionary to use in configuring the items.  If the
        length of items exceeds the length of colors, the last (or
        only) color dictionary in the sequence is used.  Returns a
        list of color dictionaries, one for each item.  The color keys
        are filtered by each canvas item's type when reading and writing.
        '''
        if isinstance(colors, (list, tuple)):
            return self.itemsColor(items, *colors)
        return self.itemsColor(items, colors)
        
    def restoreItems(self, items, colors, top=True):
        '''Restore fill color of local variable canvas items to the colors
        specifed for them in the colors list.  This list is what is
        returned by fadeItems: a list of dictionaries just like those
        passed to colors in fadeItems.  Optionally, raise the items to
        display on top of other canvas items following their order in
        the items sequence.
        '''
        if isinstance(colors, (list, tuple)):
            self.itemsColor(items, *colors)
        else:
            self.itemsColor(items, colors)
        if top:
            for item in items:
                if isinstance(item, int):
                    self.tag_raise(item)

    def itemsColor(self, items, *colors):
        '''Get or set item color attributes for a list of items.  When colors is
        not provided, it returns the list of configured colors.  When provided
        1 or more colors are provided, the corresponding items are configured
        to use that fill color.  If there are more items than colors, the
        last color dictionary is used for the remaining items.  The color keys
        are filtered by each canvas item's type when reading and writing.
        '''
        nColors = len(colors)
        itemColors = []
        for i, item in enumerate(items):
            itemColors.append(self.getItemColors(item))
            if nColors > 0:
                newColors = colors[min(i, nColors - 1)].copy()
                oldColors = itemColors[-1]
                for attribute in set(newColors.keys()) - set(oldColors.keys()):
                    del newColors[attribute]
                self.itemconfigure(item, **newColors)
        return itemColors

    def getItemColors(self, item):
        config = self.itemConfig(item)
        return dict([(key, config[key])
                     for key in self.TYPE_COLORS[self.type(item)]])

    def getItemFont(self, item):
        return parseTkFont(self.itemConfig(item, 'font'))

    def create_hashed_rectangle(
            self, x0, y0, x1, y1, angle=45, spacing=10, **kwargs):
        '''Create a hashed rectangle by drawing a polygon of parallel
        lines separarted by spacing pixels.  Color can be specified
        by either the fill or outline keyword argument.  Other keyword
        arguments have the same effect as for create_polygon.'''
        color = kwargs.get('outline', kwargs.get('fill', 'black'))
        kwargs['fill'] = ''
        kwargs['outline'] = color
        angle = angle % 180
        Arad = math.radians(angle)
        tanA = math.tan(Arad)
        cosA, sinA = math.cos(Arad), math.sin(Arad)
        BBox = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        size = BBoxSize(BBox)
        spacing = max(1, spacing)
        steps = math.ceil(V(size).dot(V(abs(sinA), abs(cosA))) / spacing)
        points = [(BBox[i], BBox[j])
                  for i, j in ((0, 1), (0, 3), (2, 3), (2, 1), (0, 1))]
        gap = spacing / max(abs(cosA), abs(sinA))
        for a in range(steps):
            odd = a % 2 == 1
            if 45 < angle and angle <= 135:
                xlo = BBox[0] + a * gap - max(0, size[1] / tanA)
                xhi = xlo + size[1] / tanA
                ylo = BBox[1] + max(0, xlo - BBox[2], BBox[0] - xlo) * abs(tanA)
                yhi = BBox[3] - max(0, xhi - BBox[2], BBox[0] - xhi) * abs(tanA)
            else:
                ylo = BBox[1] + a * gap - max(0, size[0] * tanA)
                yhi = ylo + size[0] * tanA
                xlo = BBox[0] + max(0, ylo - BBox[3], BBox[1] - ylo) / abs(tanA)
                xhi = BBox[2] - max(0, yhi - BBox[3], BBox[1] - yhi) / abs(tanA)
            p1 = (min(BBox[2], max(BBox[0], xlo if odd else xhi)),
                  min(BBox[3], max(BBox[1], ylo if odd else yhi)))
            p2 = (min(BBox[2], max(BBox[0], xhi if odd else xlo)),
                  min(BBox[3], max(BBox[1], yhi if odd else ylo)))
            dx, dy = V(p1) - V(points[-1])
            if dx * dy != 0:  # If next point spans a corner, include corner
                cornerX = BBox[0 if min(p1[0], points[-1][0]) == BBox[0] else 2]
                cornerY = BBox[1 if min(p1[1], points[-1][1]) == BBox[1] else 3]
                points.append((cornerX, cornerY))
            points.append(p1)
            points.append(p2)

        # Ensure last point is on outer boundary connected to first point
        if points[0][0] != points[-1][0] and points[0][1] != points[-1][1]:
            if points[1][0] == points[-1][0] or points[1][1] == points[-1][1]:
                points.append(points[1])
            else:
                points.append(points[3])
        return self.create_polygon(*flat(*points), **kwargs)

# Tk image utilities
__tk_image_cache__ = {'Img': {}, 'PhotoImage': {}, 'debug': False}

def getImage(filename, cache=True, path=None):
    if not cache or filename not in __tk_image_cache__['Img']:
        if path is None: path = sys.path
        fname = filename
        for dir in path:
            if os.path.exists(os.path.join(dir, filename)):
                fname = os.path.join(dir, filename)
                break
        if __tk_image_cache__['debug']:
            print('Reading {} into Img cache'.format(fname))
        __tk_image_cache__['Img'][filename] = Img.open(fname)
    return __tk_image_cache__['Img'][filename]

def getPhotoImage(filename, size, cache=True, path=None):
    image = getImage(filename, cache=cache, path=path)
    if not cache or (id(image), size) not in __tk_image_cache__['PhotoImage']:
        ratio = min(*(V(size) / V(image.size)))
        if __tk_image_cache__['debug']:
            print('Resizing {} into PhotoImage cache with ratio {}'.format(
                filename, ratio), end=' ')
        __tk_image_cache__['PhotoImage'][id(image), size] = ImageTk.PhotoImage(
            image.resize(int(round(d)) for d in V(image.size) * ratio))
        if __tk_image_cache__['debug']:
            print('as', __tk_image_cache__['PhotoImage'][id(image), size])
    return __tk_image_cache__['PhotoImage'][id(image), size]
    
if __name__ == '__main__':
    import random, glob, os, argparse

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-d', '--debug', default=False, action='store_true',
        help='Show debugging information.')
    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help='Add verbose comments')
    args = parser.parse_args()
    
    for dims in range(2, 4):
        print('=' * 70)
        p1 = tuple(c for c in range(1, dims + 1))
        p2 = tuple(c * (c + 1) + 1 for c in p1)
        mid = V(V(p1) + V(p2)) // 2
        bboxes = [p1 + mid, mid + p2, p1 + p2]
        badBBox = mid + p1
        for i in range(len(bboxes) - 1):
            boxiEmpty = BBoxEmpty(bboxes[i])
            print('BBox {} {} empty'.format(bboxes[i],
                                            'is' if boxiEmpty else 'is not'))
            for j in range(i + 1, len(bboxes)):
                print('BBox 1 = {!s:25}  BBox 2 = {!s:25}'.format(
                    bboxes[i], bboxes[j]))
                for f in (BBoxUnion, BBoxIntersection, BBoxesOverlap, BBoxContains):
                    print('{}({}, {}) = {}'.format(
                        f.__name__, bboxes[i], bboxes[j], 
                        f(bboxes[i], bboxes[j])))
                print('{}({}, {}) = {}'.format(
                    'BBoxContains', bboxes[j], bboxes[i],
                    BBoxContains(bboxes[j], bboxes[i])))
                if not boxiEmpty and BBoxEmpty(
                        BBoxIntersection(bboxes[i], bboxes[j])):
                    print('The first box is not empty but the intesection is.')
                if not all(BBoxContains(BBoxUnion(bboxes[i], bboxes[j]), bb)
                           for bb in (bboxes[i], bboxes[j])):
                    print('Union of {} {} does not contain both!'.format(
                        bboxes[i], bboxes[j]))
                if not all(BBoxContains(bb, BBoxIntersection(bboxes[i], bboxes[j]))
                           for bb in (bboxes[i], bboxes[j])):
                    print(('The bounding boxes {} {} do not both contain'
                           'their intersection!').format(bboxes[i], bboxes[j]))
                if not all(BBoxContains(
                        bb, BBoxIntersection(bboxes[i], bboxes[j]) * 2)
                           for bb in (bboxes[i], bboxes[j])):
                    print(('The bounding boxes {} {} do not both contain'
                           'their corner points!').format(bboxes[i], bboxes[j]))

        print('Bad BBox {} {} empty'.format(
                badBBox, 'is' if BBoxEmpty(badBBox) else 'is not'))

    def compare_bbox(
            scrim: 'Scrim object to check',
            item: 'Item on scrim to check',
            details: 'True -> show all config details, or dict of keys to show'
            =None):
        'Compare bounding box and coords before and after hiding it'
        kind = scrim.type(item)
        state = scrim.itemConfig(item, 'state')
        fill = scrim.itemConfig(item, 'fill')
        bbox = scrim.bbox(item)
        coords = scrim.coords(item)
        print('Before hiding', kind, 'item', item, 'with fill of', fill,
              'the bounding box is', bbox, 'and the coords are', coords)
        if details:
            config = scrim.itemConfig(item)
            for key in config:
                if config[key] and (details == True or key in details):
                    print('  {}: {!r}'.format(key, config[key]))
        scrim.itemConfig(item, state=HIDDEN)
        hiddenBBox = scrim.bbox(item)
        hiddenCoords = scrim.coords(item)
        print('After hiding its bounding box is', hiddenBBox, 'which is',
              'identical' if bbox == hiddenBBox else 'different')
        if bbox != hiddenBBox:
            print('Difference is', V(bbox) - V(hiddenBBox))
        print('After hiding its coordinates are', hiddenCoords, 'which are',
              'identical' if coords == hiddenCoords else 'different')
        scrim.itemConfig(item, state=state)
        
    tk = Tk()
    scrim = Scrim(tk, width=800, height=400)
    scrim.pack(side=TOP, expand=TRUE, fill=BOTH)
    excludeEvents = (
        EventType.Keymap, EventType.GraphicsExpose, EventType.NoExpose,
        EventType.CirculateRequest, EventType.SelectionClear,
        EventType.SelectionRequest, EventType.Selection,
        EventType.ClientMessage, EventType.Mapping, EventType.VirtualEvent)
    if args.debug:
        for event in EventType:
            if event not in excludeEvents:
                if args.verbose > 0:
                    print('Binding {} events on scrim'.format(event.name))
                scrim.bind('<{}>'.format(event.name), 
                           genericEventHandler(verbose=args.verbose), '+')
    tkButton = Button(tk, text='Tk Button')
    ttkButton = ttk.Button(tk, text='Ttk Button', state=DISABLED)
    tkButton.pack(side=LEFT, expand=TRUE)
    ttkButton.pack(side=LEFT, expand=TRUE)
    buttonState = scrim.create_text(400, 390, text='')
    print('The default font for canvas text items is:',
          scrim.getItemFont(buttonState))
    updateButtonState = lambda : (
        scrim.itemConfig(buttonState, 
                         text='Tk button: {}    Ttk button: {}'.format(
                             widgetState(tkButton), widgetState(ttkButton))))
    updateButtonState()
    tkButton['command'] = lambda : (
        widgetState(tkButton, DISABLED) or widgetState(ttkButton, NORMAL)
        or updateButtonState())
    ttkButton['command'] = lambda : (
        widgetState(tkButton, NORMAL) or widgetState(ttkButton, DISABLED)
        or updateButtonState())

    pngFiles = glob.glob(os.path.join('.', '*.png'))
    if pngFiles:
        __tk_image_cache__['debug'] = True
        buttonSize = widgetDimensions(tkButton)
        height = max(buttonSize[1], textHeight(scrim.getItemFont(buttonState)))
        images = [getPhotoImage(pngFile, (height, height))
                  for pngFile in pngFiles]
        imageButton = Button(tk, image=images[0])
        imageButton.pack(side=LEFT, expand=TRUE)
        buttonImage(imageButton, images[0])
        def rotateButtonImage():
            i = images.index(buttonImage(imageButton))
            print('Pressed {} button'.format(pngFiles[i]))
            buttonImage(imageButton, images[(i + 1) % len(images)])
        imageButton['command'] = rotateButtonImage
    palette = ('red', 'green', 'blue', '', 'pink', 'black', 'yellow',
               'orange', 'brown')
    nc = len(palette)
    states = ('Fade', 'Restore', 'Disable', 'Reenable')
    colors = {}
    
    geometry = scrim.create_text(5, 5, anchor=NW, text='', fill='black')
    def updateGeometry(event=None):
        scrim.itemConfig(
            geometry, text='widgetGeometry(tk) = {}'.format(
                widgetGeometry(tk)))
    tk.bind('<Configure>', updateGeometry, '+')
    updateGeometry()
            
    message = scrim.create_text(
        575, 10, anchor=NW, text='', fill='gray30', activefill='',
        font=('Courier', -14), width=300)
    print('The font for the group details text item is:',
          scrim.getItemFont(message))
    def groupButtonHandler(btn, tag):
        def groupButtonPress():
            parts = btn['text'].split()
            state = parts[0]
            if state not in states:
                return
            sIndex = states.index(state)
            btn['text'] = ' '.join((states[(sIndex + 1) % len(states)],
                                    *parts[1:]))
            if state == 'Fade':
                colors[tag] = scrim.fadeItems(scrim.find_withtag(tag))
            elif state == 'Restore':
                scrim.restoreItems(scrim.find_withtag(tag), colors[tag])
            elif state == 'Disable':
                scrim.itemConfig(tag, state=DISABLED)
            elif state == 'Reenable':
                scrim.itemConfig(tag, state=NORMAL)
            else:
                raise Exception('Unknown state: {}'.format(state))
            scrim.itemConfig(
                message,
                text='{} contains:\n'.format(tag) + '\n'.join([
                    'Item {} type {}\n{}'.format(
                    item, scrim.type(item), colors[tag][j])
                    for j, item in enumerate(scrim.find_withtag(tag))]))
            btn.update_idletasks()

        return groupButtonPress
    
    def hashedRectRotator(rect, bbox, angle=10, spacing=10,
                          deltaAngle=10, deltaSpacing=0):
        def rotateHashedRectangle(event=None):
            config = scrim.itemConfig(rect)
            newRect = scrim.create_hashed_rectangle(
                *bbox, angle=angle + deltaAngle, spacing=spacing + deltaSpacing,
                **config)
            scrim.delete(rect)
            scrim.tag_bind(newRect, '<Button-1>',
                           hashedRectRotator(newRect, bbox, angle + deltaAngle,
                                             spacing + deltaSpacing,
                                             deltaAngle, deltaSpacing))
        return rotateHashedRectangle
    
    tags = []
    shapeCreators = [scrim.create_arc, scrim.create_oval,
                     scrim.create_hashed_rectangle]
    
    for x0, y0 in (
            (50, 20), (100, 90), (180, 110), (240, 110), (300, 130), (380, 150)):
        g = len(tags)
        tag = 'group{:02d}'.format(g)
        shape = shapeCreators[g % len(shapeCreators)]
        kwargs = (
            {'start': 30, 'extent': 200} if shape == scrim.create_arc else
            {'angle': g * 9, 'spacing': g * 4}
            if shape == scrim.create_hashed_rectangle else {})
        bbox = (x0 + g * 10, y0 + 50, x0 + 100 + g * 10, y0 + 200 - g * 10)
        shapeItem = shape(
            *bbox, fill=palette[(g + 0) % nc], activefill=palette[(g + 1) % nc],
            disabledfill=palette[(g + 2) % nc],
            outline=palette[(g + 3) % nc], activeoutline=palette[(g + 4) % nc], 
            disabledoutline=palette[(g + 5) % nc],
            width=1, activewidth=3, disabledwidth=5, disableddash=(5, 5),
            tags=tag, **kwargs)
        if shape == scrim.create_hashed_rectangle:
            scrim.tag_bind(shapeItem, '<Button-1>',
                           hashedRectRotator(shapeItem, bbox, **kwargs))
        compare_bbox(scrim, shapeItem)
            
        g = (g + 1) % nc
        if palette[g] == '': g += 1
        line = scrim.create_line(
            x0 + g * 10, y0 - g * 10 + 50,
            x0 + 100 + g * 10, y0 - g * 10 + 45, arrow=LAST,
            fill=palette[(g + 0) % nc], activefill=palette[(g + 1) % nc],
            disabledfill=palette[(g + 2) % nc], width=1, activewidth=3,
            disabledwidth=5, disableddash=(5, 5), tags=tag)
        compare_bbox(scrim, line)
        g = (g + 1) % nc
        if palette[g] == '': g += 1
        text = scrim.create_text(
            x0 + 50 + g * 10, y0 - g * 10 + 35, text=tag,
            fill=palette[(g + 0) % nc], activefill=palette[(g + 1) % nc],
            disabledfill=palette[(g + 2) % nc], tags=tag)
        anchor = list(scrim.anchorVectors.keys())[g % len(scrim.anchorVectors)]
        scrim.changeAnchor(anchor, text)
        tags.append(tag)
        compare_bbox(scrim, text, details={'anchor': 1, 'text': 1})

    for tag in tags:
        btn = Button(tk, text='Fade {}'.format(tag))
        btn['command'] = groupButtonHandler(btn, tag)
        btn.pack(side=LEFT, expand=TRUE)

    tk.mainloop()
