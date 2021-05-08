__doc__ = """
Base class for Python visualizations.
Provides a common drawing canvas and movement tools.
"""

import time, re, sys, math
from tkinter import *
from tkinter import ttk
import tkinter.font as tkfont
from enum import Enum

try:
    from coordinates import *
except ModuleNotFoundError:
    from .coordinates import *
    
# Utilities for vector math; used for canvas item coordinates
V = vector
def add_vector(v1, v2):
    return V(v1) + V(v2)

def subtract_vector(v1, v2):
    return V(v1) - V(v2)

def divide_vector(v1, v2):   # v2 can be scalar
    if not isinstance(v2, (list, tuple)):
        v2 = [v2] * len(v1)  # Copy scalar value for vector dimension
    return V(v1) / V(v2)

def multiply_vector(v1, v2): # v2 can be scalar
    if not isinstance(v2, (list, tuple)):
        v2 = [v2] * len(v1)  # Copy scalar value for vector dimension
    return V(v1) * V(v2)

def rotate_vector(v1, angle=0): # Rotate vector by angle degrees
    return V(v1).rotate(angle)

def vector_length2(vect):    # Get the vector's length squared
    return V(vect).len2()

def vector_length(vect):     # Get the vector's length
    return V(vect).vlen()

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

def BBoxContains(bbox1, bbox2):
    'Return whether bounding box 1 fully contains bounding box 2'
    half = len(bbox1) // 2
    return all(bbox1[j] <= bbox2[j] and bbox1[j + half] >= bbox2[j + half]
               for j in range(half))

def BBoxEmpty(bbox):
    'Return whether a bounding box has any area'
    return not(bbox[0] < bbox[2] and bbox[1] < bbox[3])

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

def BBoxCenter(bbox):
    half = len(bbox) // 2
    return V(V(bbox[:half]) + V(bbox[half:])) / 2

# Tk definitions
# Modifier key constants
SHIFT, CAPS_LOCK, CTRL, ALT = 0x01, 0x02, 0x04, 0x08

# Window geometry specification strings
geom_delims = re.compile(r'[\sXx+-]')

# Animation states
class Animation(Enum):
    STOPPED = 1
    RUNNING = 2
    PAUSED = 3
    STEP = 4

class Visualization(object):  # Base class for Python visualizations

    # Default styles for display of values, variables, and their animation
    DEFAULT_BG = 'white'
    FONT_SIZE = -20
    DEFAULT_FONT = ('Helvetica', FONT_SIZE)
    VALUE_FONT = ('Helvetica', FONT_SIZE)
    VALUE_COLOR = 'black'
    VARIABLE_FONT = ('Courier', FONT_SIZE * 8 // 10)
    VARIABLE_COLOR = 'brown3'
    NONLOCAL_VARIABLE_COLOR = 'bisque'
    FOUND_FONT = ('Helvetica', FONT_SIZE)
    FOUND_COLOR = 'green2'
    SMALL_FONT = ('Helvetica', -9)

    def __init__(  # Constructor
            self,
            window=None,      # Run visualization within given window
            title=None,
            canvasWidth=800,  # Canvas portal size
            canvasHeight=400,
            canvasBounds=None): # Canvas extent (behind portal)
        self.title = title
        # Set up Tk windows for canvas and operational controls
        if window:
            self.window = window
        else:
            self.window = Tk()
            if title:
                self.window.title(title)
        self.destroyed = False
        self.window.bind('<Destroy>', self.setDestroyFlag)

        self.targetCanvasWidth = canvasWidth
        self.targetCanvasHeight = canvasHeight
        self.canvasFrame = Frame(self.window)
        self.canvasFrame.pack(side=TOP, expand=True, fill=BOTH)
        if canvasBounds:
            self.canvasVScroll = Scrollbar(self.canvasFrame, orient=VERTICAL)
            self.canvasVScroll.pack(side=RIGHT, expand=False, fill=Y)
            if canvasWidth == 800:  # For Trinket, shrink canvas width to show
                self.targetCanvasWidth, canvasWidth = 788, 788 # scrollbar
        else:
            self.canvasVScroll = None
        self.canvas = Canvas(
            self.canvasFrame, width=canvasWidth, height=canvasHeight,
            bg=self.DEFAULT_BG)
        self.canvas.pack(side=TOP, expand=True, fill=BOTH)
        self.__createCanvasText = self.canvas.create_text
        self.canvas.create_text = self.createCanvasText
        self.setCanvasBounds(canvasBounds)
        if canvasBounds:
            self.canvasHScroll = Scrollbar(self.canvasFrame, orient=HORIZONTAL)
            self.canvasHScroll.pack(side=TOP, expand=False, fill=X)
            self.canvasVScroll['command'] = self.canvas.yview
            self.canvasHScroll['command'] = self.canvas.xview
            self.canvas['xscrollcommand'] = self.canvasHScroll.set
            self.canvas['yscrollcommand'] = self.canvasVScroll.set
        else:
            self.canvasHScroll = None

        # Set up animation state variable
        self.animationState = Animation.STOPPED

    def setDestroyFlag(self, event=None): # Capture destruction of top window
        if event and event.widget == self.window:
            self.destroyed = True
        
    # General Tk widget methods
    def widgetDimensions(self, widget):  # Get widget's (width, height)
        geom = geom_delims.split(widget.winfo_geometry())
        if geom[0] == '1' and geom[1] == '1':  # If not yet managed, use config
            geom = (widget.config('width')[-1], widget.config('height')[-1])
        return int(geom[0]), int(geom[1])

    def widgetState(self, widget, state=None): # Get or set widget state
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

    def textWidth(self, font, text=' '):
        return self.tkFontFromSpec(font).measure(text)
        
    def textHeight(self, font, text=' '):
        lines = text.split('\n')
        nLines = len(lines) if lines and len(lines[-1]) > 0 else len(lines) - 1
        return self.tkFontFromSpec(font).metrics()['linespace'] * nLines

    def tkFontFromSpec(self, spec):
        family = spec[0]
        size = spec[1] if (len(spec) > 1 and 
                           (isinstance(spec[1], int) or
                            (isinstance(spec[1], str) and 
                             self.sizePattern.match(spec[1])))) else 0
        return tkfont.Font(
            family=family, size=size,
            weight=self.lookFor(('bold', 'light'), spec, 'normal'),
            slant=self.lookFor(('italic', 'oblique'), spec, 'roman'),
            underline=1 if self.lookFor(('underline',), spec, 0) else 0,
            overstrike=1 if self.lookFor(('overstrike',), spec, 0) else 0)
        
    def lookFor(self, keys, spec, default):  # Find keyword in font spec
        strings = [x.lower() for x in spec if isinstance(x, str)]
        for key in keys:
            if key.lower() in strings:
                return key
        return default

    def setCanvasBounds(self, canvasBounds, expandOnly=True):
        if canvasBounds is None:
            self.canvasBounds = None
            return
        intBounds = (math.floor(canvasBounds[0]), math.floor(canvasBounds[1]),
                     math.ceil(canvasBounds[2]), math.ceil(canvasBounds[3]))
        self.canvasBounds = (
            BBoxUnion(self.canvasBounds, intBounds) 
            if expandOnly and hasattr(self, 'canvasBounds') else intBounds)
        self.canvas['scrollregion'] = ' '.join(map(str, self.canvasBounds))
            
    # CANVAS ITEM METHODS
    def canvas_itemConfig(  # Get a dictionary with the canvas item's
            self, canvasitem): # configuration
        config = self.canvas.itemconfigure(canvasitem)
        for key in config:     # Replace tuple values with the last item
            if isinstance(config[key], tuple):  # in tuple
                config[key] = config[key][-1]
        return config

    def copyCanvasItem(      # Make a copy of an item in the canvas
            self, canvasitem):
        creator = getattr(self.canvas,  # Get canvas creation function for type
                          'create_{}'.format(self.canvas.type(canvasitem)))
        newItem = creator(*self.canvas.coords(canvasitem),
                          **self.canvas_itemConfig(canvasitem))
        for eventType in self.canvas.tag_bind(canvasitem): # Copy event handlers
            self.canvas.tag_bind(newItem, eventType,
                                 self.canvas.tag_bind(canvasitem, eventType))
        return newItem

    anchorVectors = {
        NW: (-1, -1), N: (0, -1), NE: (1, -1),
        W: (-1, 0), CENTER: (0, 0), E: (1, 0),
        SW: (-1, 1),  S: (0, 1),  SE: (1, 1)}

    def changeAnchor(self, newAnchor, *items):
        'Change the anchor but not the position of a text item'
        for item in items:
            if self.canvas.type(item) == 'text':
                anchor = self.canvas.itemconfigure(item, 'anchor')[-1]
                if anchor in self.anchorVectors and anchor != newAnchor:
                    bbox = self.canvas.bbox(item)
                    size = V(bbox[2:]) - V(bbox[:2])
                    coords = self.canvas.coords(item)
                    delta = V(V(self.anchorVectors[newAnchor]) - 
                              V(self.anchorVectors[anchor])) / 2
                    self.canvas.coords(item, V(coords) + V(V(delta) * V(size)))
                    self.canvas.itemconfigure(item, anchor=newAnchor)
    
    def copyItemAttributes(   # Copy attributes from one canvas item to another
            self, fromItem, toItem, *attributes):
        kwargs = dict((attrib, self.canvas.itemconfigure(fromItem, attrib)[-1])
                      for attrib in attributes)
        self.canvas.itemconfigure(toItem, **kwargs)
    
    def fadeNonLocalItems(self, items, colors=NONLOCAL_VARIABLE_COLOR):
        '''Set fill color of non-local variable canvas items to a faded color
        or sequence of colors.  If the length of items exceeds the length of
        colors, the last color in the sequence is used.
        Returns a list of the current fill color of each item that can be used
        to restore them later.
        '''
        if isinstance(colors, (list, tuple)):
            return self.itemsFillColor(items, *colors)
        return self.itemsFillColor(items, colors)
        
    def restoreLocalItems(self, items, colors=VARIABLE_COLOR, top=True):
        '''Restore fill color of local variable canvas items to either a given
        color or list of colors.  Optionally, raise the items to display on
        top of other canvas items'''
        if isinstance(colors, (list, tuple)):
            self.itemsFillColor(items, *colors)
        else:
            self.itemsFillColor(items, colors)
        if top:
            for item in items:
                if isinstance(item, int):
                    self.canvas.tag_raise(item)

    def itemsFillColor(self, items, *colors):
        '''Get or set item fill color for a list of items.  When colors is
        not provided, it returns the list of configured colors.  When provided
        1 or more colors are provided, the corresponding items are configured
        to use that fill color.  If there are more items than colors, the
        last color is used for the remaining items.
        '''
        nColors = len(colors)
        itemColors = []
        for i, item in enumerate(items):
            itemColors.append(self.canvas.itemconfigure(item, 'fill')[-1])
            if nColors > 0:
                self.canvas.itemconfigure(
                    item, fill=colors[min(i, nColors - 1)])
        return itemColors

    def dispose(self, callEnviron, *items):
        'Delete items from the canvas and call environment, if it is a set'
        for item in items:
            if isinstance(callEnviron, set):
                callEnviron.discard(item)
            self.canvas.delete(item)

    def getItemFont(self, item):
        font = self.canvas.itemconfigure(item, 'font')[-1].split()
        return (font[0], int(font[1]), *font[2:])
    
    def createCanvasText(self, x, y, **kwargs):
        'Enforce special requirements when creating canvas text items'
        font = kwargs.get('font', self.DEFAULT_FONT)
        tags = kwargs.get('tags', ())
        if not isinstance(tags, tuple): 
            tags = tuple(tags.split()) if isinstance(tags, str) else tuple(tags)
        tags += ('font={}'.format('|'.join(str(c) for c in font)), )
        options = dict(kwargs)
        options['tags'] = tags
        return self.__createCanvasText(x, y, **options)
        
    def scaleItems(
            self, x0, y0, scaleBy, fontScale, updateBounds='simple',
            fixPoint=(), items='all'):
        if fixPoint:
            screenFixPoint = V(fixPoint) - V(self.visibleCanvas())
        for item in (i for i in self.canvas.find_withtag(items)):
            itemType = self.canvas.type(item)
            if itemType == 'text':
                self.scaleTextItem(item, fontScale)
            elif itemType == 'line':
                self.scaleLineItem(item, scaleBy)
        self.canvas.scale(items, x0, y0, scaleBy, scaleBy)
        if updateBounds:
            if updateBounds == 'simple':
                newBB = [(d - origin) * scaleBy + origin 
                         for d, origin in zip(self.canvasBounds,
                                              (x0, y0, x0, y0))]
            else:
                newBB = BBoxUnion(*(self.canvas.bbox(i) 
                                    for i in self.canvas.find_withtag('all')))
            self.setCanvasBounds(newBB, expandOnly=scaleBy > 1)
        if fixPoint:
            self.window.update() # Need this to get adjusted scroll positions
            afterScale = V(V(fixPoint) - V(x0, y0)) * scaleBy
            upperLeft = V(afterScale) - V(screenFixPoint)
            bounds = self.canvasBounds
            visible = self.visibleCanvasFraction()
            pos = tuple(max(0, min(1 - visible[XorY],
                                   (upperLeft[XorY] - bounds[XorY]) /
                                   (bounds[2 + XorY] - bounds[XorY])))
                        for XorY in range(2))
            self.canvas.xview_moveto(pos[0])
            self.canvas.yview_moveto(pos[1])

    def scaleTextItem(self, item, scale):
        if self.canvas.type(item) != 'text':
            return
        for tag in self.canvas.itemconfigure(item, 'tags')[-1].split():
            if tag.startswith('font='):
                font = tag[5:].split('|')
                if len(font) > 1:
                    font[1] = - max(1, math.ceil(abs(int(font[1])) * scale))
                    self.canvas.itemconfigure(item, font=tuple(font))
                    return

    def scaleLineItem(self, item, scale):
        if self.canvas.type(item) != 'line':
            return
        shape = self.canvas.itemconfigure(item, 'arrowshape')[-1].split()
        newShape = tuple(scale * float(d) for d in shape)
        self.canvas.itemconfigure(item, arrowshape=newShape)

    def setupCanvasZoomHandlers(
            self, eventType, zoomBy=5/4, x0=0, y0=0, updateBounds=True):
        if any(x is None for x in 
               (self.canvasBounds, self.canvasHScroll, self.canvasVScroll)):
            return
        def zoomHandler(event):
            if event.widget != self.canvas:
                print('Unexpected call to zoomHandler from widget {}'.format(
                    event.widget))
            fixPoint = (self.canvas.canvasx(event.x), 
                        self.canvas.canvasy(event.y))
            scaleBy = (1 / zoomBy) if event.state & SHIFT else zoomBy
            self.scaleItems(
                x0, y0, scaleBy, scaleBy, fixPoint=fixPoint,
                updateBounds=updateBounds)
        self.canvas.bind(eventType, zoomHandler)
        
    #####################################################################
    #                                                                   #
    #                       Animation Methods                           #
    #                                                                   #
    #####################################################################
    # These methods animate canvas items moving in increments with an
    # adjustable speed.  The items are moved together as a group.
    # They take differing paths to get to their destinations.  The
    # items parameter for each method can be either a single item ID
    # or tag, or a list|tuple|set of IDs or tags. The steps parameter
    # specifies how many incremental steps should be taken in
    # completing the movement and must be 1 or more.  The sleepTime
    # specifies how long to wait between incremental steps.  A
    # sleepTime of 0 will produce the fastest steps, but you may not
    # see the intermediate positions of the items.  If startFont and
    # endFont are given, the font size will smoothly transition to
    # the endFont over the animation (using integer font sizes).
    # The font paramenters should be Tk (fontname, fontsize) tuples
    # and the fontsizes should be integers of the same sign.
    #
    # Each moveItems____ method calls a generator called
    # moveItems____Sequence that iterates over the steps yielding the
    # step from 0 up to steps-1 and the total number of steps (some
    # methods my change the number of steps) This enables combining
    # animation sequences by using the *Sequence generator to go
    # through the steps and performing other animation actions for
    # each step.  Each moveItems____ method calls self.wait(0) at the
    # beginning to wait if step mode has been engaged
    #
    # Most moveItems method take optional see and expand keyword
    # parameters that control scrolling the canvas to see the moved items
    # and expanding the canvas bounds to accommodate the new positions

    def moveItemsOffCanvas(  # Animate the removal of canvas items by sliding
            self, items,     # them off one of the canvas edges
            edge=N,          # One of the 4 tkinter edges: N, E, S, or W
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        self.wait(0)
        for step, _ in self.moveItemsOffCanvasSequence(items, edge, steps):
            self.wait(sleepTime)

    def moveItemsOffCanvasSequence(  # Iterator for moveItemsOffCanvas
            self, items, edge=N, steps=10):
        if not isinstance(items, (list, tuple, set)):
            items = (items,)
        if items:
            curPositions = [
                self.canvas.coords(i) for i in items if i is not None]
            bboxes = [self.canvas.bbox(i) for i in items if i is not None]
            itemsBBox = BBoxUnion(*bboxes)  # Get bounding box of all items
            visible = self.visibleCanvas()
            bounds = BBoxUnion(
                visible, self.canvasBounds if self.canvasBounds else visible)
            visibleCenter = BBoxCenter(visible)

            # Compute delta vector that moves them on a line away from the
            # center of the canvas
            delta = V(BBoxCenter(itemsBBox)) - V(visibleCenter)
            if edge in (N, S):
                delta = (delta[0], visible[3] - itemsBBox[1] if edge is S else
                         visible[1] - itemsBBox[3])
            elif edge in (W, E):
                delta = (visible[2] - itemsBBox[0] if edge is E else
                         visible[0] - itemsBBox[2], delta[1])

            # Ensure no more that 45 degree angle to departure boundary normal
            if abs(delta[0]) > abs(delta[1]) and edge in (N, S):
                delta = (abs(delta[1]) * (-1 if delta[0] < 0 else 1), delta[1])
            elif abs(delta[0]) < abs(delta[1]) and edge in (E, W):
                delta = (delta[0], abs(delta[0]) * (-1 if delta[1] < 0 else 1))
            for step, _ in self.moveItemsBySequence(items, delta, steps):
                yield (step, _)

    def moveItemsBy(         # Animate canvas items moving from their current
            self, items,     # location in a direction indicated by a single
            delta,           # delta vector. items can be 1 item or a list/tuple
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1,   # Base time between steps (adjusted by user)
            startFont=None,  # Change font size from start to endFont, if
            endFont=None,    # given
            see=(),          # Scroll to view moved items plus any items in see
            expand=True):    # Expand canvas bounds before scrolling if needed
        self.wait(0)
        for step, _ in self.moveItemsBySequence(
                items, delta, steps, startFont=startFont, endFont=endFont,
                see=see, expand=expand):
            self.wait(sleepTime)

    def moveItemsBySequence( # Iterator for moveItemsBy
            self, items, delta, steps=10, startFont=None, endFont=None,
            see=(),          # Scroll to view moved items plus any items in see
            expand=True):    # Expand canvas bounds before scrolling if needed
        if not isinstance(items, (list, tuple, set)):
            items = (items,)
        if not isinstance(delta, (list, tuple)) or len(delta) != 2:
            raise ValueError('Delta must be a 2-dimensional vector')
        if items and vector_length2(delta) >= 0.001: # If some items and delta

            steps = max(1, steps) # Must use at least 1 step
            changeFont = startFont and endFont and startFont != endFont

            # move the items in steps along vector
            moveBy = V(delta) / steps
            for step in range(steps):
                font = changeFont and (endFont[0], 
                                       (startFont[1] * (steps - (step + 1)) +
                                        endFont[1] * (step + 1)) // steps)
                for item in items:
                    if item is not None:
                        self.canvas.move(item, *moveBy)
                        if changeFont and self.canvas.type(item) == 'text':
                            self.canvas.itemconfigure(item, font=font)
                if see:
                    self.scrollToSee(
                        items + 
                        (tuple(see) if isinstance(see, (list, tuple)) else ()),
                        sleepTime=0, expand=expand)
                yield (step, steps) # Yield step in sequence
                
            # Force end font if provided
            if changeFont:
                for item in items:
                    if self.canvas.type(item) == 'text':
                        self.canvas.itemconfigure(item, font=endFont)
                
    def moveItemsTo(         # Animate canvas items moving rigidly 
            self, items,     # to destination locations along line(s)
            toPositions,     # items can be a single item or list of items
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1,   # Base time between steps (adjusted by user)
            startFont=None,  # Transition text item fonts from start to
            endFont=None,    # end font, if provided
            see=(),          # Scroll to view moved items plus any items in see
            expand=True):    # Expand canvas bounds before scrolling if needed
        self.wait(0)
        for step, _ in self.moveItemsToSequence(
                items, toPositions, steps, startFont=startFont, endFont=endFont,
                see=see, expand=expand):
            self.wait(sleepTime)

    def moveItemsToSequence( # Iterator for moveItemsTo
            self, items,     # to destination locations along line(s)
            toPositions,     # items can be a single item or list of items
            steps=10,        # Number of steps in movement
            startFont=None,  # Change font size from start to endFont, if
            endFont=None,    # given
            see=(),          # Scroll to view moved items plus any items in see
            expand=True):    # Expand canvas bounds before scrolling if needed
        items, toPositions = self.reconcileItemPositions(items, toPositions)
        if items and toPositions:
            steps = max(1, steps) # Must use at least 1 step
            moveBy = [V(V(toPos) - V(fromPos)) / steps
                      for toPos, fromPos in zip(
                              toPositions,
                              [self.canvas.coords(item)[:2] for item in items])]
            changeFont = startFont and endFont and startFont != endFont

            # move the items until they reach the toPositions
            moved = []
            for step in range(steps):
                font = changeFont and (endFont[0], 
                                       (startFont[1] * (steps - (step + 1)) +
                                        endFont[1] * (step + 1)) // steps)
                moved = []
                for i, item in enumerate(items):
                    if len(moveBy[i]) == 2:  # Unneeded test?
                        self.canvas.move(item, *moveBy[i])
                        if changeFont and self.canvas.type(item) == 'text':
                            self.canvas.itemconfigure(item, font=font)
                        if see and V(moveBy[i]).len2() >= 1:
                            moved.append(item)
                if see and moved:
                    self.scrollToSee(
                        moved + 
                        (list(see) if isinstance(see, (list, tuple)) else []),
                        sleepTime=0, expand=expand)
                yield (step, steps) # Yield step in sequence
            
            # Force position of new objects to their exact destinations
            for pos, item in zip(toPositions, items):
                self.canvas.coords(item, *pos)
                if changeFont and self.canvas.type(item) == 'text':
                    self.canvas.itemconfigure(item, font=endFont)
            if see and moved:
                self.scrollToSee(
                    moved + 
                    (list(see) if isinstance(see, (list, tuple)) else []),
                    sleepTime=0, expand=expand)

    # The moveItemsLinearly method uses all the coordinates of canvas
    # items in calculating the movement vectors.  Don't pass the
    # 'items' arguments with canvas tags attached to multiple items.
    # If you do, it will only move one of them and the number of
    # coordinates for it the toPositions argument could be a mismatch.
    # Pass item IDs to ensure a 1-to-1 mapping.
    def moveItemsLinearly(   # Animate canvas items moving each of their 
            self, items,     # coordinates linearly to new destinations
            toPositions,     # Items can be single or multiple, but not tags
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1,   # Base time between steps (adjusted by user)
            startFont=None,  # Change font size from start to endFont, if
            endFont=None,    # given
            see=(),          # Scroll to view moved items plus any items in see
            expand=True):    # Expand canvas bounds before scrolling if needed
        self.wait(0)
        for step, _ in self.moveItemsLinearlySequence(
                items, toPositions, steps, startFont=startFont, endFont=endFont,
                see=see, expand=expand):
            self.wait(sleepTime)

    def moveItemsLinearlySequence( # Iterator for moveItemsLinearly
            self, items, toPositions, steps=10, startFont=None, endFont=None,
            see=(),          # Scroll to view moved items plus any items in see
            expand=True):    # Expand canvas bounds before scrolling if needed
        items, toPositions = self.reconcileItemPositions(items, toPositions)
        if items and toPositions:
            steps = max(1, steps) # Must use at least 1 step
            moveBy = [V(V(toPos) - V(fromPos)) / steps
                      for toPos, fromPos in zip(
                              toPositions,
                              [self.canvas.coords(item) for item in items])]
            changeFont = startFont and endFont and startFont != endFont

            # move the items until they reach the toPositions
            moved = []
            for step in range(steps):
                font = changeFont and (endFont[0], 
                                       (startFont[1] * (steps - (step + 1)) +
                                        endFont[1] * (step + 1)) // steps)
                moved = []
                for i, item in enumerate(items):
                    if len(moveBy[i]) >= 2:
                        self.canvas.coords(
                            item, V(self.canvas.coords(item)) + V(moveBy[i]))
                        if changeFont and self.canvas.type(item) == 'text':
                            self.canvas.itemconfigure(item, font=font)
                        if see and V(moveBy[i]).len2() >= 1:
                            moved.append(item)
                if see and moved:
                    self.scrollToSee(
                        moved + 
                        (list(see) if isinstance(see, (list, tuple)) else []),
                        sleepTime=0, expand=expand)
                yield (step, steps) # Yield step in sequence
            
            # Force position of new objects to their exact destinations
            for pos, item in zip(toPositions, items):
                self.canvas.coords(item, *pos)
                if changeFont and self.canvas.type(item) == 'text':
                    self.canvas.itemconfigure(item, font=endFont)
            if see and moved:
                self.scrollToSee(
                    moved + 
                    (list(see) if isinstance(see, (list, tuple)) else []),
                    sleepTime=0, expand=expand)
             
    def moveItemsOnCurve(    # Animate canvas items moving from their current
            self, items,     # location to destinations along a curve
            toPositions,     # items can be a single item or list of items
            startAngle=90,   # Starting angle away from destination
            steps=10,        # Number of intermediate steps to reach destination
            sleepTime=0.1,   # Base time between steps (adjusted by user)
            startFont=None,  # Change font size from start to endFont, if
            endFont=None,    # given
            see=(),          # Scroll to view moved items plus any items in see
            expand=True):    # Expand canvas bounds before scrolling if needed
        self.wait(0)
        for step, _ in self.moveItemsOnCurveSequence(
                items, toPositions, startAngle, steps, startFont=startFont,
                endFont=endFont, see=see, expand=expand):
            self.wait(sleepTime)
            
    def moveItemsOnCurveSequence( # Iterator for moveItemsOnCurve
            self, items, toPositions, startAngle=90, steps=10, startFont=None,
            endFont=None,
            see=(),          # Scroll to view moved items plus any items in see
            expand=True):    # Expand canvas bounds before scrolling if needed
        items, toPositions = self.reconcileItemPositions(items, toPositions)
        if items and toPositions:
            steps = max(1, steps) # Must use at least 1 step
            changeFont = startFont and endFont and startFont != endFont

            # move the items until they reach the toPositions
            moved = []
            for step in range(steps):  # Go through all steps of the annimation
                toGo = steps - 1 - step  # remaining steps to go
                font = changeFont and (endFont[0], 
                                       (startFont[1] * toGo +
                                        endFont[1] * (step + 1)) // steps)
                ang = startAngle * toGo / steps  # angle decreases on each step
                scale = 1 + abs(ang) / 180  # scale is larger for higher angles
                moved = []
                for i, item in enumerate(items):
                    coords = self.canvas.coords(item)[:2]
                    if len(coords) == 2:
                        moveBy = V(V(V(toPositions[i]) - V(coords)) /
                                   ((toGo + 1) / scale)).rotate(ang)
                        self.canvas.move(item, *moveBy)
                        if changeFont and self.canvas.type(item) == 'text':
                            self.canvas.itemconfigure(item, font=font)
                        if see and V(moveBy).len2() >= 1:
                            moved.append(item)
                if see and moved:
                    self.scrollToSee(
                        moved + 
                        (list(see) if isinstance(see, (list, tuple)) else []),
                        sleepTime=0, expand=expand)
                yield (step, steps) # Yield step in sequence
            
            # Force position of new objects to their exact destinations
            for pos, item in zip(toPositions, items):
                self.canvas.coords(item, *pos)
                if changeFont and self.canvas.type(item) == 'text':
                    self.canvas.itemconfigure(item, font=endFont)
            if see and moved:
                self.scrollToSee(
                    moved + 
                    (list(see) if isinstance(see, (list, tuple)) else []),
                    sleepTime=0, expand=expand)

    def withinCanvas(self, point, visible=False):
        '''Determine if the given point lies within the canvas bounds, or
        optionally, the part of the canvas that's visible based on scrolling'''
        bounds = (self.canvasBounds if not visible and self.canvasBounds else
                  self.visibleCanvas())
        return (bounds[0] <= point[0] and point[0] <= bounds[2] and
                bounds[1] <= point[1] and point[1] <= bounds[3])

    def visibleCanvas(self):
        '''Return bounding box of visible canvas coordinates.
        When canvasBounds are smaller than canvas, the 'visible' bounds can
        exceed the canvasBounds bounding box.
        '''
        canvasDims = self.widgetDimensions(self.canvas)
        if any(x is None for x in 
               (self.canvasBounds, self.canvasHScroll, self.canvasVScroll)):
            return (0, 0) + canvasDims
        xPos = self.canvasHScroll.get()
        yPos = self.canvasVScroll.get()
        Xbounds = (self.canvasBounds[0], self.canvasBounds[2])
        Ybounds = (self.canvasBounds[1], self.canvasBounds[3])
        return [
            int(bounds[0] + pos * max(dim, bounds[1] - bounds[0]))
            for bounds, dim, pos in zip((Xbounds, Ybounds) * 2,
                                        canvasDims * 2,
                                        (max(0, xPos[0]), max(0, yPos[0]), 
                                         min(1, xPos[1]), min(1, yPos[1])))]
    
    def visibleCanvasFraction(self):
        'Return the ratio of the visible canvas to the canvas bounds in X, Y'
        return tuple(max(0, min(1, x)) for x in
                     (V(self.widgetDimensions(self.canvas)) /
                      V(V(self.canvasBounds[2:]) - V(self.canvasBounds[:2]))))

    def scrollToSee(self, items, sleepTime=0.01, steps=10, **kwargs):
        '''Scroll to show all the provided canvas items. It uses the
        scrollSettingsToSee method to determine what scroll settings
        are needed to see all the itmes, or at least the highest
        priority ones.  See that method for its keyword parameters.
        If sleepTime is 0, the scrolling is done in a single jump with
        waits inbetween.  If no scrolling is required to see all the
        itmes, the scroll settings are not changed.
        '''
        if self.canvasHScroll is None or self.canvasVScroll is None:
            return
        newX, newY = self.scrollSettingsToSee(items, **kwargs)
        xPos = self.canvasHScroll.get()
        yPos = self.canvasVScroll.get()
        if distance2(xPos + yPos, newX + newY) < .0001:
            return
        if sleepTime > 0:
            for step in range(1, steps + 1):
                self.canvas.xview_moveto(
                    (xPos[0] * (steps - step) + newX[0] * step) / steps)
                self.canvas.yview_moveto(
                    (yPos[0] * (steps - step) + newY[0] * step) / steps)
                self.wait(sleepTime)
        self.canvas.xview_moveto(newX[0])
        self.canvas.yview_moveto(newY[0])

    def scrollSettingsToSee(self, items, expand=True, firstPriority=True):
        '''Find the scroll settings needed to see the given canvas items.  The
        union of the bounding boxes of the items (ignoring those that
        have been deleted) determines what should be seen.  If expand
        is true and the items bounding box extends beyond the canvas
        bounds, the bounds are expanded (and scrollbars adjusted).  If
        not all the items could fit in the (adjusted) visible region,
        a binary search is done to find the largest subset of items
        that could fit.  The subset is either the first items in the
        sequence or the latter items depending on the firstPriority flag.
        '''
        if self.canvasHScroll is None or self.canvasVScroll is None:
            return
        BBoxes = [self.canvas.bbox(item) for item in items
                  if self.canvas.type(item)]
        BBox = BBoxUnion(*BBoxes)
        visibleCanvas = self.visibleCanvas()
        if expand and not BBoxEmpty(BBox) and (
                not BBoxContains(self.canvasBounds, BBox)):
            self.setCanvasBounds(BBox)
        canvasDims = self.widgetDimensions(self.canvas)
        canvasBounds = self.canvasBounds
        visibleCanvasFraction = self.visibleCanvasFraction()
        xPos = list(self.canvasHScroll.get())
        yPos = list(self.canvasVScroll.get())
        keep, step = len(BBoxes), len(BBoxes) // 2
        while step > 0:
            if (BBox[2] - BBox[0], BBox[3] - BBox[1]) <= canvasDims:
                if keep == len(BBoxes): break
                keep += step if firstPriority else -step
            else:
                keep -= step if firstPriority else -step
            step = step // 2
            BBox = BBoxUnion(*(BBoxes[:keep] if firstPriority else
                               BBoxes[-keep:]))

        # When bounding box could fit on canvas, adjust each scrollbar dimension
        if (BBox[2] - BBox[0], BBox[3] - BBox[1]) <= canvasDims:
            for pos, XorY in ((xPos, 0), (yPos, 1)):
                lo = max(canvasBounds[XorY],
                         min(visibleCanvas[XorY], BBox[XorY]))
                hi = min(canvasBounds[2 + XorY],
                         max(visibleCanvas[2 + XorY], BBox[2 + XorY]))
                if lo < visibleCanvas[XorY] or visibleCanvas[2 + XorY] < hi:
                    pos[0] = (      # Shift lower or higher, but not both
                        (lo if lo < visibleCanvas[XorY] else
                         hi - canvasDims[XorY]) - canvasBounds[XorY]) / (
                             canvasBounds[2 + XorY] - canvasBounds[XorY])
                    pos[1] = pos[0] + visibleCanvasFraction[XorY]
        else:
            pass  # Here for debugging only
        
        return tuple(xPos), tuple(yPos)
        
    def reconcileItemPositions(self, items, positions):
        'Standardize items paired with positions for moveItems routines'
        if not isinstance(items, (list, tuple, set)):
            items = (items,)
            if (isinstance(positions, (list, tuple)) and len(positions) > 0
                and isinstance(positions[0], (int, float))):
                positions = (positions, )
        if not isinstance(positions, (list, tuple)):
            raise ValueError('positions must be a list or tuple of positions')
        if len(items) != len(positions):
            raise ValueError(
                'Number of items must match length of positions')
        return items, positions
        
    # ANIMATION CONTROLS

    def wait(self, sleepTime): # Sleep for a period of time and handle user stop
        if sleepTime > 0:
            self.window.update()
            if self.destroyed:
                sys.exit()
            time.sleep(sleepTime)
        if self.destroyed:
            sys.exit()
        if self.animationState == Animation.STOPPED: # If user requested to stop
            raise UserStop()      # animation while waiting then raise exception

    def startAnimations(self, enableStops=True, state=None):
        self.animationState = state if state is not None else (
            self.animationState if self.animationState in (Animation.RUNNING,
                                                           Animation.STEP)
            else Animation.RUNNING)

    def stopAnimations(self):  # Stop animation
        self.animationState = Animation.STOPPED

    def pauseAnimations(self):
        self.animationState = Animation.PAUSED

    def animationsStopped(self):
        return self.animationState == Animation.STOPPED

    def animationsPaused(self):
        return self.animationState == Animation.PAUSED

    def animationsRunning(self):
        return self.animationState != Animation.STOPPED

    def animationsStepping(self):
        return self.animationState == Animation.STEP
    
    def runVisualization(self):
        self.window.mainloop()

class UserStop(Exception):   # Exception thrown when user stops animation
    pass

if __name__ == '__main__':
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

        print('Bad BBox {} {} empty'.format(
                badBBox, 'is' if BBoxEmpty(badBBox) else 'is not'))
        
    app = Visualization(title='Visualization test')

    centerText = app.canvas.create_text(
        app.targetCanvasWidth // 2, app.targetCanvasHeight // 2,
        text='Center of the canvas', fill=app.VALUE_COLOR, font=app.VALUE_FONT)

    app.startAnimations()
    for anchor in app.anchorVectors:
        app.changeAnchor(anchor, centerText)
        app.wait(0.1)

    app.runVisualization()
