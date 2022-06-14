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
    from tkUtilities import *
except ModuleNotFoundError:
    from .coordinates import *
    from .tkUtilities import *
    
# Utilities for vector math; used for canvas item coordinates
V = vector

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
    DEFAULT_CANVAS_WIDTH = 800
    DEFAULT_CANVAS_HEIGHT = 400

    def __init__(  # Constructor
            self,
            window=None,      # Run visualization within given window
            title=None,
            canvasWidth=None,  # Canvas portal size
            canvasHeight=None,
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

        if canvasWidth is None: canvasWidth = self.DEFAULT_CANVAS_WIDTH
        if canvasHeight is None: canvasHeight = self.DEFAULT_CANVAS_HEIGHT
        self.targetCanvasWidth = canvasWidth
        self.targetCanvasHeight = canvasHeight
        self.canvasFrame = Frame(self.window)
        self.canvasFrame.pack(side=TOP, expand=True, fill=BOTH)
        if canvasBounds:
            self.canvasVScroll = Scrollbar(self.canvasFrame, orient=VERTICAL)
            self.canvasVScroll.pack(side=RIGHT, expand=False, fill=Y)
            if canvasWidth == 800:  # Shrink canvas width to show scrollbar
                self.targetCanvasWidth, canvasWidth = 785, 785
        else:
            self.canvasVScroll = None
        self.canvas = Scrim(
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

    def expandCanvasFor(self, *itemOrBBox):
        '''Expand canvas scroll region if needed to view given canvas items
        (integers) or bounding boxes (4-tuples or 4-element lists)'''
        bounds = getattr(self, 'canvasBounds', 
                         (0, 0, *widgetDimensions(self.canvas)))
        bbox = BBoxUnion(*(
            self.canvas.bbox(item) if isinstance(item, int) else item
            for item in itemOrBBox if isinstance(item, int) or
            isinstance(item, (list, tuple)) and len(item) == 4))
        if not BBoxContains(bounds, bbox):
            self.setCanvasBounds(BBoxUnion(bounds, bbox))
        
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
    def canvas_itemConfig(self, canvasitem, *key, **kwargs):
        '''Do what the tk canvas itemconfigure command does, but return only
        the setting for each item attribute, not the tuple with the name and
        default value.'''
        return self.canvas.itemConfig(canvasitem, *key, **kwargs)

    def canvas_coords(self, tagOrID, *args):
        return self.canvas.coords(tagOrID, *args)

    def copyCanvasItem(self, item, **kwargs):
        '''Deprecated.  Use Scrim.copyItem instead '''
        return self.canvas.copyItem(item, **kwargs)
    
    def fadeNonLocalItems(self, items, colors=Scrim.FADED_COLORS):
        '''Deprecated.  Use Scrim.fadeItems instead '''
        return self.canvas.fadeItems(items, colors)
        
    def restoreLocalItems(self, items, colors, top=True):
        '''Deprecated.  Use Scrim.restoreItems instead. '''
        return self.canvas.restoreItems(items, colors, top)

    def itemsFillColor(self, items, *colors):
        '''Deprecated.  Use Scrim.itemsColor instead. '''
        return self.canvas.itemsColor(items, colors)

    def dispose(self, callEnviron, *items):
        'Delete items from the canvas and call environment, if it is a set'
        for item in items:
            if isinstance(callEnviron, set):
                callEnviron.discard(item)
            self.canvas.delete(item)

    def getItemFont(self, item):
        return self.canvas.getItemFont(item)
    
    def createCanvasText(self, x, y, **kwargs):
        '''Enforce special requirements when creating canvas text items.
        Record the font at initialization as a tag for use in scaling text
        items.
        '''
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

    def scaleTextItem(self, item, scale=None):
        if self.canvas.type(item) != 'text':
            return
        if scale is None: scale = getattr(self, 'scale', 1)
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
        if items and V(delta).len2() >= 0.001: # If some items and delta

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
                        tuple(items) + 
                        (tuple(see) if isinstance(see, (list, tuple, set))
                         else ()),
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
                        (list(see) if isinstance(see, (list, tuple, set))
                         else []),
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
                    (list(see) if isinstance(see, (list, tuple, set)) else []),
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
                        (list(see) if isinstance(see, (list, tuple, set))
                         else []),
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
                    (list(see) if isinstance(see, (list, tuple, set)) else []),
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
                        (list(see) if isinstance(see, (list, tuple, set))
                         else []),
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
                    (list(see) if isinstance(see, (list, tuple, set)) else []),
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
        canvasDims = widgetDimensions(self.canvas)
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
                     (V(widgetDimensions(self.canvas)) /
                      V(V(self.canvasBounds[2:]) - V(self.canvasBounds[:2]))))

    def scrollToSee(self, itemsOrBBoxes, sleepTime=0.01, steps=10, **kwargs):
        '''Scroll to show all the provided canvas items or bounding boxes. It
        uses the scrollSettingsToSee method to determine what scroll
        settings are needed to see all the item bboxes, or at least the
        highest priority ones.  See that method for its keyword
        parameters.  If sleepTime is 0, the scrolling is done in a
        single jump with no waits inbetween.  If no scrolling is required
        to see all the itmes, the scroll settings are not changed.
        '''
        if self.canvasHScroll is None or self.canvasVScroll is None:
            return
        newX, newY = self.scrollSettingsToSee(itemsOrBBoxes, **kwargs)
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
                if self.animationsRunning():
                    self.wait(sleepTime)
        self.canvas.xview_moveto(newX[0])
        self.canvas.yview_moveto(newY[0])

    def scrollSettingsToSee(
            self, itemsOrBBoxes, expand=True, firstPriority=True, debug=False):
        '''Find the scroll settings needed to see the given canvas items (int
        or string) or bounding boxes (sequence of 4 coordinates) or
        coordinate list.  The union of the bounding boxes of the items
        (ignoring any items that have been deleted) determines what
        should be seen.  If expand is true and the items bounding box
        extends beyond the canvas bounds, the bounds are expanded (and
        scrollbars adjusted).  If not all the items could fit in the
        (adjusted) visible region, a binary search is done to find the
        largest subset of items that could fit.  The subset is either
        the first items in the sequence or the latter items depending
        on the firstPriority flag.
        '''
        if self.canvasHScroll is None or self.canvasVScroll is None:
            return
        BBoxes = [self.canvas.bbox(item) if isinstance(item, (int, str)) 
                  else BBoxEnclosing(*item)
                  for item in itemsOrBBoxes
                  if (isinstance(item, (int, str)) and self.canvas.type(item))
                  or isinstance(item, (list, tuple))]
        BBox = BBoxUnion(*BBoxes)
        visibleCanvas = self.visibleCanvas()
        if debug:
            print(('Request to scroll.  Current visible: {visibleCanvas} '
                   'Bounding box to see: {BBox}').format(**locals()))
        if expand and not BBoxEmpty(BBox) and (
                not BBoxContains(self.canvasBounds, BBox)):
            if debug:
                print(
                    'Expanding canvas bounds from', self.canvasBounds, end=' ')
            self.setCanvasBounds(BBox)
            if debug:
                print('to', self.canvasBounds)
        canvasDims = BBoxSize(visibleCanvas)
        canvasBounds = self.canvasBounds
        visibleCanvasFraction = self.visibleCanvasFraction()
        xPos = list(self.canvasHScroll.get())
        yPos = list(self.canvasVScroll.get())
        keep, step, tried = len(BBoxes), len(BBoxes) // 2, set()
        while keep > 0:
            seen = keep in tried
            tried.add(keep)
            if BBoxSize(BBox) <= canvasDims:
                if keep == len(BBoxes) or seen: break
                keep += step
            else:
                keep -= step
            step = max(1, step // 2)
            BBox = BBoxUnion(*(BBoxes[:keep] if firstPriority else
                               BBoxes[-keep:]))
        if debug and 1 < len(BBoxes) and keep < len(BBoxes):
            print(('Reduced requested bounding box to {} keeping {} {} of {} '
                   'boxes so size is {} and canvas is {}').format(
                       BBox, 'first' if firstPriority else 'last',
                       keep, len(BBoxes), BBoxSize(BBox), canvasDims))

        # When bounding box could fit on canvas, determine scrollbar positions
        if BBoxSize(BBox) <= canvasDims:
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
            if debug:
                if xPos != list(self.canvasHScroll.get()):
                    print('Changing horizontal scroll from {} to {}'.format(
                        self.canvasHScroll.get(), xPos))
                if yPos != list(self.canvasVScroll.get()):
                    print('Changing vertical scroll from {} to {}'.format(
                        self.canvasVScroll.get(), yPos))
        elif debug:
            print('Unable to reduce bounding box to fit within', canvasDims)
        
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

negativeNumber = re.compile(r'(-[0-9]+)[,.]?')
signedNumber = re.compile(r'([+-][0-9]+)[,.]?')
nonNegativeNumber = re.compile(r'([0-9]+)[,.]?')
option = re.compile(r'(-[^0-9].*)')
other = re.compile(r'(.*)')

def categorizeArguments(
        arguments: 'Command line arguments',
        signed: 'Categorize +N as signed and return among negative args' =False,
) -> 'Returns lists of non-negative, negative, option, & other argument strings':
    patterns = (nonNegativeNumber, signedNumber if signed else negativeNumber,
                option, other)
    result = tuple(list() for p in patterns)
    for arg in arguments:
        for i, pattern in enumerate(patterns):
            match = pattern.match(arg)
            if match:
                result[i].append(match.group(1))
                break
    return result
    

if __name__ == '__main__':
    import random

    nonneg, negative, options, otherArgs = categorizeArguments(sys.argv[1:])
    for name, args in (('Non-negative', nonneg), ('Negative', negative),
                       ('Options', options), ('Other', otherArgs)):
        print('{} argument{}: {}'.format(
            name, '' if len(args) == 1 else 's',
            ', '.join(repr(a) for a in args)))
              
    grid = '-grid' in options
    
    app = Visualization(title='Visualization test',
                        canvasBounds=(0, 0, 1000, 500) if grid else None)

    centerText = app.canvas.create_text(
        app.targetCanvasWidth // 2, app.targetCanvasHeight // 2,
        text='Center of the canvas', fill=app.VALUE_COLOR, font=app.VALUE_FONT)

    def makeLineWithBBox(
            N=9, color='blue', vertColor='red', bg='old lace', gap=10):
        tags = ('crazyLine', 'crazyLineLabel', 'crazyBBox')
        for tag in tags:
            app.canvas.delete(tag)
        crazyLineCoords = [(random.randrange(app.targetCanvasWidth // 2 - gap),
                            random.randrange(app.targetCanvasHeight // 2 - gap))
                           for j in range(N)]
        bbox = BBoxEnclosing(*flat(*crazyLineCoords))
        crazyBBox = app.canvas.create_rectangle(
            *bbox, fill=bg, tags='crazyBBox')
        crazyLine = app.canvas.create_line(
            *flat(*crazyLineCoords[:-1]), tags='crazyLine', arrow=LAST,
            fill=color, smooth=True,
            splinesteps=max(app.targetCanvasWidth, app.targetCanvasHeight) // 4)
        verts = [app.canvas.create_text(*p, text=str(i),
                                        fill=vertColor, tags='crazyLine') 
                 for i, p in enumerate(crazyLineCoords[:-1])]
        crazyLineLabel = app.canvas.create_text(
            *crazyLineCoords[-1], text='Crazy line', fill=color,
            tags='crazyLineLabel')
        for tag in tags:
            app.canvas.tag_bind(tag, '<Button>', 
                                lambda e: makeLineWithBBox(
                                    N, color, vertColor, bg, gap))

    makeLineWithBBox()

    
    app.startAnimations()
    for anchor in Scrim.anchorVectors:
        app.canvas.changeAnchor(anchor, centerText)
        app.canvas.itemConfig(
            centerText, text='Center of the canvas ({})'.format(anchor))
        app.wait(0.1)

    if grid:
        app.canvas.itemConfig(centerText, text='')
        spans = [app.canvas.create_line(
            10 if dim else 0, 0 if dim else 10,
            10 if dim else 20, 20 if dim else 10, fill='blue', arrow=BOTH,
            width=1, arrowshape=(16, 20, 6), tags='span') for dim in (0, 1)]
        extremes = [app.canvas.create_text(
            8 if dim else end * 10 + 5, end * 10 + 5 if dim else 8,
            anchor = E if dim else S, text='', fill='blue', tags='span')
                    for dim in (0, 1) for end in (0, 1)]
        app.canvas.tag_lower('span')
        
        def updateCanvasSpans(event=None):
            viz = app.visibleCanvas()
            mid = BBoxCenter(viz)
            gap = 40
            for dim in (0, 1):
                app.canvas.coords(
                    spans[dim],
                    mid[1 - dim] if dim else viz[dim],
                    viz[dim] if dim else mid[1 - dim],
                    mid[1 - dim] if dim else viz[dim + 2],
                    viz[dim + 2] if dim else mid[1 - dim])
                for end in (0, 1):
                    coord = viz[end * 2 + dim]
                    item = extremes[2 * dim + end]
                    app.canvas.coords(
                        item,
                        mid[1 - dim] - 2 if dim else coord - (end*2 - 1) * gap,
                        coord - (end*2 - 1) * gap if dim else mid[1 - dim] - 2)
                    app.canvas.itemConfig(item, text=str(coord))

        app.window.bind('<Configure>', updateCanvasSpans)
        updateCanvasSpans()
        
        canvasSize = BBoxSize(app.canvasBounds)
        ticsize = 8
        color = 'red'
        axes, tics, labels, lastLabel = [], [], [], []
        for dim in (0, 1):
            mid = canvasSize[1 - dim] // 2
            axes.append(app.canvas.create_line(
                mid if dim else app.canvasBounds[dim],
                app.canvasBounds[dim] if dim else mid,
                mid if dim else app.canvasBounds[dim + 2],
                app.canvasBounds[dim + 2] if dim else mid, fill=color, width=1))
            for a in range(0, canvasSize[dim] + 1, 40):
                tics.append(app.canvas.create_line(
                    mid - ticsize if dim else a,
                    a if dim else mid - ticsize,
                    mid + ticsize if dim else a,
                    a if dim else mid + ticsize, fill=color, width=1))
                labels.append(app.canvas.create_text(
                    mid - ticsize * 2 if dim else a,
                    a if dim else mid - ticsize * 2,
                    anchor=E if dim else S, text=str(a), fill=color))
            lastLabel.append(len(labels) - 1)
                
        LRScrollBtnBG = app.canvas.create_rectangle(
            canvasSize[0] // 2 + 40, canvasSize[1] // 2 + 40,
            canvasSize[0] // 2 + 140, canvasSize[1] // 2 + 60,
            fill='sky blue', width=1)
        LRScrollBtn = app.canvas.create_text(
            canvasSize[0] // 2 + 90, canvasSize[1] // 2 + 50,
            text='Scroll Right')
        def toggleScroll(event=None):
            text = app.canvas.itemConfig(LRScrollBtn, 'text')
            right = text.endswith('ight')
            app.canvas.itemConfig(
                LRScrollBtn, text='Scroll Left' if right else 'Scroll Right')
            app.scrollToSee([labels[lastLabel[0] if right else 0]],
                            expand=False, debug=True)
        for item in (LRScrollBtnBG, LRScrollBtn):
            app.canvas.tag_bind(item, '<Button-1>', toggleScroll)

    app.runVisualization()
