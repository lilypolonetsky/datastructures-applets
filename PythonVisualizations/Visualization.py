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

def BBoxesOverlap(bbox1, bbox2):
    'Determine if bounding boxes overlap'
    return (rangesOverlap(bbox1[0], bbox1[2], bbox2[0], bbox2[2]) and 
            rangesOverlap(bbox1[1], bbox1[3], bbox2[1], bbox2[3]))

def rangesOverlap(lo1, hi1, lo2, hi2, zeroOK=True):
    'Determine if a range overlaps another.  Allow zero overlap, if requested.'
    return ((hi1 > lo2 or (zeroOK and hi1 == lo2)) and
            (lo1 < hi2 or (zeroOK and lo1 == hi2)))

def BBoxContains(bbox1, bbox2):
    'Return whether bounding box 1 fully contains bounding box 2'
    return (bbox1[0] <= bbox2[0] and bbox1[1] <= bbox2[1] and
            bbox1[2] >= bbox2[2] and bbox1[3] >= bbox2[3])

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
        return [
            max(bbox[0] for bbox in bboxes), max(bbox[1] for bbox in bboxes),
            min(bbox[2] for bbox in bboxes), min(bbox[3] for bbox in bboxes)]

def BBoxUnion(*bboxes):
    'Return the smallest bounding box containing a sequence of bounding boxes'
    if len(bboxes) == 0:
        return [0, 0, 0, 0]
    elif len(bboxes) == 1:
        return bboxes[0]
    else:
        return [
            min(bbox[0] for bbox in bboxes), min(bbox[1] for bbox in bboxes),
            max(bbox[2] for bbox in bboxes), max(bbox[3] for bbox in bboxes)]

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

        self.canvasBounds = canvasBounds
        self.targetCanvasWidth = canvasWidth
        self.targetCanvasHeight = canvasHeight
        self.canvasFrame = Frame(self.window)
        self.canvasFrame.pack(side=TOP, expand=True, fill=BOTH)
        if canvasBounds:
            self.canvasVScroll = Scrollbar(self.canvasFrame, orient=VERTICAL)
            self.canvasVScroll.pack(side=RIGHT, expand=False, fill=Y)
        else:
            self.canvasVScroll = None
        self.canvas = Canvas(
            self.canvasFrame, width=canvasWidth, height=canvasHeight,
            bg=self.DEFAULT_BG)
        self.canvas.pack(side=TOP, expand=True, fill=BOTH)
        if canvasBounds:
            self.canvas['scrollregion'] = ' '.join(map(str, canvasBounds))
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

    # CANVAS ITEM METHODS
    def canvas_itemconfigure(  # Get a dictionary with the canvas item's
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
                          **self.canvas_itemconfigure(canvasitem))
        for eventType in self.canvas.tag_bind(canvasitem): # Copy event handlers
            self.canvas.tag_bind(newItem, eventType,
                                 self.canvas.tag_bind(canvasitem, eventType))
        return newItem

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
            bbox = bboxes[0]  # Get bounding box of all items
            for bb in bboxes[1:]:
                bbox = [min(bbox[0], bb[0]), min(bbox[1], bb[1]),
                        max(bbox[2], bb[2]), max(bbox[3], bb[3])]
            canvasDimensions = self.widgetDimensions(self.canvas)
            # Compute delta vector that moves them on a line away from the
            # center of the canvas
            delta = ((bbox[0] + bbox[2] - canvasDimensions[0]) / 2,
                     0 - bbox[3])
            if edge == S:
                delta = (delta[0], canvasDimensions[1] - bbox[1])
            elif edge in (W, E):
                delta = (0 - bbox[2],
                         (bbox[1] + bbox[3] - canvasDimensions[1]) / 2)
                if edge == E:
                    delta = (canvasDimensions[0] - bbox[0], delta[1])
            # Ensure no more that 45 degree angle to departure boundary
            if abs(delta[0]) > abs(delta[1]) and edge not in (E, W):
                delta = (abs(delta[1]) * (-1 if delta[0] < 0 else 1), delta[1])
            elif abs(delta[0]) < abs(delta[1]) and edge not in (N, S):
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
            see=False,       # Scroll to see moved items
            expand=True):    # Expand canvas bounds before scrolling if needed
        self.wait(0)
        for step, _ in self.moveItemsBySequence(
                items, delta, steps, startFont=startFont, endFont=endFont,
                see=see, expand=expand):
            self.wait(sleepTime)

    def moveItemsBySequence( # Iterator for moveItemsBy
            self, items, delta, steps=10, startFont=None, endFont=None,
            see=False,       # Scroll to see moved items
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
                    self.scrollToSee(items, sleepTime=0, expand=expand)
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
            see=False,       # Scroll to see moved items
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
            see=False,       # Scroll to see moved items
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
                    self.scrollToSee(moved, sleepTime=0, expand=expand)
                yield (step, steps) # Yield step in sequence
            
            # Force position of new objects to their exact destinations
            for pos, item in zip(toPositions, items):
                self.canvas.coords(item, *pos)
                if changeFont and self.canvas.type(item) == 'text':
                    self.canvas.itemconfigure(item, font=endFont)

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
            see=False,       # Scroll to see moved items
            expand=True):    # Expand canvas bounds before scrolling if needed
        self.wait(0)
        for step, _ in self.moveItemsLinearlySequence(
                items, toPositions, steps, startFont=startFont, endFont=endFont,
                see=see, expand=expand):
            self.wait(sleepTime)

    def moveItemsLinearlySequence( # Iterator for moveItemsLinearly
            self, items, toPositions, steps=10, startFont=None, endFont=None,
            see=False,       # Scroll to see moved items
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
                    self.scrollToSee(moved, sleepTime=0, expand=expand)
                yield (step, steps) # Yield step in sequence
            
            # Force position of new objects to their exact destinations
            for pos, item in zip(toPositions, items):
                self.canvas.coords(item, *pos)
                if changeFont and self.canvas.type(item) == 'text':
                    self.canvas.itemconfigure(item, font=endFont)
             
    def moveItemsOnCurve(    # Animate canvas items moving from their current
            self, items,     # location to destinations along a curve
            toPositions,     # items can be a single item or list of items
            startAngle=90,   # Starting angle away from destination
            steps=10,        # Number of intermediate steps to reach destination
            sleepTime=0.1,   # Base time between steps (adjusted by user)
            startFont=None,  # Change font size from start to endFont, if
            endFont=None,    # given
            see=False,       # Scroll to see moved items
            expand=True):    # Expand canvas bounds before scrolling if needed
        self.wait(0)
        for step, _ in self.moveItemsOnCurveSequence(
                items, toPositions, startAngle, steps, startFont=startFont,
                endFont=endFont, see=see, expand=expand):
            self.wait(sleepTime)
            
    def moveItemsOnCurveSequence( # Iterator for moveItemsOnCurve
            self, items, toPositions, startAngle=90, steps=10, startFont=None,
            endFont=None,
            see=False,       # Scroll to see moved items
            expand=True):    # Expand canvas bounds before scrolling if needed
        items, toPositions = self.reconcileItemPositions(items, toPositions)
        if items and toPositions:
            steps = max(1, steps) # Must use at least 1 step
            changeFont = startFont and endFont and startFont != endFont

            # move the items until they reach the toPositions
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
                    self.scrollToSee(moved, sleepTime=0, expand=expand)
                yield (step, steps) # Yield step in sequence
            
            # Force position of new objects to their exact destinations
            for pos, item in zip(toPositions, items):
                self.canvas.coords(item, *pos)
                if changeFont and self.canvas.type(item) == 'text':
                    self.canvas.itemconfigure(item, font=endFont)
                    
    def visibleCanvas(self):
        'Return bounding box of visible canvas coordinates'
        canvasDims = self.widgetDimensions(self.canvas)
        if any(x is None for x in 
               (self.canvasBounds, self.canvasHScroll, self.canvasVScroll)):
            return (0, 0) + canvasDims
        xPos = self.canvasHScroll.get()
        yPos = self.canvasVScroll.get()
        Xbounds = (self.canvasBounds[0], self.canvasBounds[2])
        Ybounds = (self.canvasBounds[1], self.canvasBounds[3])
        return [
            max(bounds[0], min(bounds[1], int(pos * (bounds[1] - bounds[0]))))
            for bounds, pos in zip((Xbounds, Ybounds) * 2,
                                   (xPos[0], yPos[0], xPos[1], yPos[1]))]
    
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
        bounds, the bounds are expanded (and scrollbars adjusted).
        If not all the items fit in the (adjusted) visible region, the set
        of items is reduced by half taking the first half as the priority
        to be seen (or second half if firstPriority is not true).  The
        halving repeats until a (possibly empty) subset that fits is found.
        '''
        if self.canvasHScroll is None or self.canvasVScroll is None:
            return
        BBoxes = [self.canvas.bbox(item) for item in items
                  if self.canvas.type(item)]
        BBox = BBoxUnion(*BBoxes)
        if not BBoxEmpty(BBox) and not BBoxContains(self.canvasBounds, BBox):
            newBB = BBoxUnion(BBox, self.canvasBounds)
            self.canvasBounds = tuple([math.floor(c) for c in newBB[:2]] +
                                      [math.ceil(c) for c in newBB[2:]])
            self.canvas['scrollregion'] = ' '.join(str(c) 
                                                   for c in self.canvasBounds)
        canvasDims = self.widgetDimensions(self.canvas)
        canvasBounds = self.canvasBounds
        visibleCanvas = self.visibleCanvas()
        visibleCanvasFraction = self.visibleCanvasFraction()
        xPos = list(self.canvasHScroll.get())
        yPos = list(self.canvasVScroll.get())
        while BBoxes and not BBoxEmpty(BBox) and not BBoxContains(
                visibleCanvas, BBox):
            if (BBox[2] - BBox[0] <= canvasDims[0] and  # When BBox could fit
                BBox[3] - BBox[1] <= canvasDims[1]):    # within canvas
                for pos, XorY in ((xPos, 0), (yPos, 1)): # Adjust each dimension
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
                break
            else:
                half = len(BBoxes) // 2
                BBoxes = BBoxes[:half] if firstPriority else BBoxes[-half:]
                BBox = BBoxUnion(*BBoxes)
        
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
