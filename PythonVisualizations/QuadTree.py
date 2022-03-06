from tkinter import *
from math import *
import re, random

try:
    from tkUtilities import *
    from drawnValue import *
    from VisualizationApp import *
    from OutputBox import *
    from TableDisplay import *
except ModuleNotFoundError:
    from .tkUtilities import *
    from .drawnValue import *
    from .VisualizationApp import *
    from .OutputBox import *
    from .TableDisplay import *
    
def euclideanDistance(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    return (dx*dx + dy*dy) ** 0.5

class Bounds(object): 
    def __init__(self, left = -inf, right  = inf, 
                       top  =  inf, bottom = -inf):
        Bounds.adjust(self, left, right, top, bottom)
        
    # mutator to initialize/change bounds in existing object
    def adjust(self, left, right, top, bottom):
        self._l = left
        self._r = right
        self._t = top
        self._b = bottom        
        
    # return a new Bounds, where some of the 
    # current boundaries have been adjusted
    def adjusted(self, left = None, right = None, 
                       top = None,  bottom = None):
  
        if left   == None: left   = self._l
        if right  == None: right  = self._r
        if top    == None: top    = self._t
        if bottom == None: bottom = self._b
        
        return Bounds(left, right, top, bottom)
    
    # return True if bounds of the rectangles intersect.
    # Two rectangles don't intersect if one is totally to 
    # the left of or above the other. So we negate to 
    # determine if they do intersect.    
    def intersects(self, other):
        return not (
            # check if self's box is to left or right of other
            self._r < other._l  or  self._l > other._r or 
            
            # check if self's box is above or below other
            self._b > other._t  or  self._t < other._b)  
    
    # return True if the bounds of self fall within other
    def within(self, other):
        return (self._r < other._r and 
                self._l > other._l and
                self._t < other._t and
                self._b > other._b)

    def __str__(self):
        return '<left:{:3.1f}, right:{:3.1f}, bottom:{:3.1f}, top:{:3.1f}>'.format(
            self._l, self._r, self._b, self._t)

# A bounding box that surrounds a search circle.
# Properly handles distorted circles resulting 
# from geographic coordinates.
class CircleBounds(Bounds):
    def __deltas(self, a, b, r, func=euclideanDistance):
        # default is infinite bounds, in case r is inf
        deltaA = deltaB = inf
        
        if r != inf:
            # for cartesian coordinates, the edges of the bounding 
            # box are r away from the center of the search circle.
            if func == euclideanDistance: deltaA = deltaB = r
            
            else: # geographic coordinates
                # The width of the bounding box is determined by
                # the width of the distorted circle at its widest
                # point.  
                alpha = r / RADIUS_OF_EARTH
                gamma = radians(90 - abs(b)) # b is latitude
            
                # if the circle itself crosses the pole then 
                # alpha >= gamma, so we leave deltaA as inf,
                # effectively treating the width as if it were inf 
                if alpha < gamma: 
                    # the circle doesn't cross a pole, so get
                    # longitude angle from center of circle at 
                    # the circle's widest width calculated using
                    # a spherical right triangle identity. 
                    deltaA = degrees(asin(sin(alpha) / sin(gamma))) #d_long
            
                # latitude angle directly above/below the 
                # center of the circle. This works since above
                # or below is directly on a meridian. 
                deltaB = degrees(alpha)    # d_lat
                
        return deltaA, deltaB

    # create the bounding box that surrounds the search
    # circle at a,b,r using the specified distance func
    def __init__(self, a, b, r, func=euclideanDistance):
        # remember the circle's parameters for later
        self.__a, self.__b, self._r = a, b, r       
        self.__func = func

        # get the width/height of the bounding box
        deltaA, deltaB = self.__deltas(a, b, r, func)
                
        # initialize the superclass's rectangular bounds
        super().__init__(a - deltaA,  # left
                         a + deltaA,  # right
                         b + deltaB,  # top
                         b - deltaB)  # bottom
    
    # if the circle's radius changed, mutate its bounds    
    def adjust(self, r):
        if r != self._r:
            self._r = r
            
            # new dimensions of bounding box
            deltaA, deltaB = \
                self.__deltas(self.__a, self.__b, r, self.__func)
            
            # update the box
            super().adjust(self.__a - deltaA,  # left
                           self.__a + deltaA,  # right
                           self.__b + deltaB,  # top
                           self.__b - deltaB)  # bottom    

class Node(drawnValue):
    fields = ('x', 'y', 'data', 'NE', 'SE', 'SW', 'NW', 'BBox')
    findex = dict((field, i) for i, field in enumerate(fields))
    findex['a'] = findex['x']
    findex['b'] = findex['y']
    def __init__(self, x, y, data, BBox):
        super().__init__((x, y, [data], None, None, None, None, BBox))

    def __getitem__(self, key): # Implement positIonal access
        if isinstance(key, int):
            if 0 <= key and key < len(Node.findex):
                return self.val[key]
            raise IndexError
        elif isinstance(key, str) and key in Node.findex:
            return self.val[Node.findex[key]]

    def __getattr__(self, name):
        if name in Node.findex:
            return self.val[Node.findex[name]]
        else:
            return super().__getattr__(name)

    def __setattr__(self, name, val):
        if name in Node.findex:
            fi = Node.findex[name]
            self.val = self.val[:fi] + (val, ) + self.val[fi+1:]
        else:
            return super().__setattr__(name, val)

    def __str__(self):
        return '<{} @ ({}, {})>'.format(', '.join(self.data), self.x, self.y)

class PointQuadtree(VisualizationApp):
    MAX_ARG_WIDTH = 4
    LINE_COLOR = 'SteelBlue4'
    TEXT_COLOR = 'red'
    ROOT_OUTLINE = 'yellow'
    TEXT_FONT = ("Helvetica", -10)
    CIRCLE_RADIUS = 4
    BUFFER_ZONE = (-30, -60, 60, 5)
    POINT_REGION_COLOR = 'cyan'
    POINT_COLOR = 'black'
    CROSSHAIR_SIZE = 15
    CROSSHAIR_COLOR = 'blue'
    CROSSHAIR_FONT = (VisualizationApp.VARIABLE_FONT[0], -10)
    QUERY_POINT_COLOR = 'red'
    MEASURE_COLOR = 'lime green'
    BOUNDS_CONFIG = {'outline': 'honeydew4', 'angle': 40, 'spacing': 20,
                     'dash': (10, 8, 2, 8)}
    C_BOUNDS_CONFIG = {'outline': 'orange red', 'angle': 80, 'spacing': 20,
                       'dash': (10, 8, 2, 8)}
    NEW_BOUNDS_CONFIG = {'outline': 'dark violet', 'angle': 120, 'spacing': 20,
                       'dash': (10, 8, 2, 8)}

    def __init__(self, maxArgWidth=MAX_ARG_WIDTH, title="Point Quadtree",
                 pointRegion=None, **kwargs):
        super().__init__(title=title, maxArgWidth = maxArgWidth, **kwargs)
        if pointRegion is None:
            pointRegion = V((0, 0, 800, 400)) - V(self.BUFFER_ZONE)
        self.pointRegion = pointRegion
        self.showBoundaries = IntVar()
        self.showBoundaries.set(1)
        self.makeButtons()
        self.new()

    def canvasCoords(self, userX, userY):
        dims = widgetDimensions(self.canvas)
        return (max(0, min(dims[0], self.pointRegion[0] + userX)),
                max(0, min(dims[1], self.pointRegion[3] - userY)))
    
    def userCoords(self, canvasX, canvasY):
        return canvasX - self.pointRegion[0], self.pointRegion[3] - canvasY

    def canvasBBox(self, userBBox):
        return (self.pointRegion[0] + userBBox[0],
                self.pointRegion[3] - userBBox[3],
                self.pointRegion[0] + userBBox[2],
                self.pointRegion[3] - userBBox[1])
    
    def userBBox(self, canvasBBox):
        return (canvasBBox[0] - self.pointRegion[0],
                self.pointRegion[3] - canvasBBox[3],
                canvasBBox[2] - self.pointRegion[0],
                self.pointRegion[3] - canvasBBox[1])
    
    def display(self):
        self.canvas.delete('all')
        self.pointRegionRectangle = self.canvas.create_rectangle(
            *self.pointRegion, fill=self.POINT_REGION_COLOR, width=0,
            outline='')
        
        self.canvas.tag_bind(self.pointRegionRectangle, '<Button>', self.setXY)
        self.canvas.tag_bind(self.pointRegionRectangle, '<Double-Button-1>',
                             self.createNode)
    
    def createLabeledArrow(
            self, nodeOrCoords, label, color=None, font=None,
            width=1, anchor=None, tags=('arrow',), **kwargs):
        if color is None: color = self.VARIABLE_COLOR
        if font is None: font = self.VARIABLE_FONT
        coords = (self.labeledArrowCoords(nodeOrCoords, **kwargs)
                  if isinstance(nodeOrCoords, Node) or
                  (isinstance(nodeOrCoords, (list, tuple)) and
                   len(nodeOrCoords) == 2 and
                   isinstance(nodeOrCoords[0], (int, float)))
                  else nodeOrCoords)
        if anchor is None: 
            anchor = self.labeledArrowAnchor(coords[0])
        arrow = self.canvas.create_line(
            *coords[0], arrow=LAST, fill=color, width=width, tags=tags)
        text = self.canvas.create_text(
            *coords[1], anchor=anchor, text=label, fill=color, tags=tags)
        return arrow, text

    def labeledArrowAnchor(self, arrowCoords):
        dx, dy = V(arrowCoords[2:]) - V(arrowCoords[:2])
        return (W if dx < 0 else E) if abs(dx) > abs(dy) else (
            N if dy < 0 else S)

    def labeledArrowCoords(
            self, nodeOrCoords, level=1, orientation=0, offset=3, **kwargs):
        center = self.canvasCoords(
            *((nodeOrCoords.x, nodeOrCoords.y)
              if isinstance(nodeOrCoords, Node) else nodeOrCoords))
        Vrad = V(V(0, self.CIRCLE_RADIUS + offset).rotate(orientation))
        tip = V(center) - Vrad
        Vdelta = V(
            V(0, abs(level) * abs(self.VARIABLE_FONT[1])).rotate(orientation))
        base = V(tip) - Vdelta
        return base + tip, base

    def noneCoords(self):
        return self.pointRegion[2], self.pointRegion[3] - self.pointRegion[1]

    def variableTextCoords(self, gap=3, left=True, line=1):
        visible = self.visibleCanvas()
        return (visible[0] + gap if left else visible[2] - gap,
                self.pointRegion[1] - gap -
                (line - 1) * abs(self.VARIABLE_FONT[1]))

    def outputBoxCoords(
            self, font: 'Font for output box, default is TEXT_FONT' =None,
            padding: 'Padding around text in output box' =5,
            N: 'Number of data items, default is number of points' =None):
        '''Coordinates for an output box at top of canvas with enough
        space to hold N values, defaulting to current quadtree item count.
        '''
        if N is None: N = sum(len(n.data) for n in self.nodes)
        N = max(1, N)
        if font is None: font = self.TEXT_FONT
        allDataWidth = textWidth(
            font,  self.traverseItemSeparator
            + self.traverseItemSeparator.join(
                item for n in self.nodes for item in n.data))
        dataHeight = textHeight(font, 'P0')
        datumWidth = max((padding,
                          *(textWidth(font, item + ', ')
                            for n in self.nodes for item in n.data)))
        regionWidth = self.pointRegion[2] - self.pointRegion[0]
        regionCenter = BBoxCenter(self.pointRegion)
        width = min(regionWidth, allDataWidth, N * datumWidth) + 2 * padding
        left = max(self.pointRegion[0], regionCenter[0] - width // 2)
        right = min(self.pointRegion[2], regionCenter[0] + width // 2)
        bottom = self.pointRegion[1] - dataHeight
        top = padding if width >= regionWidth else (
            bottom - dataHeight - 2 * padding)
        return left, top, right, bottom
    
    #fills the x,y coordinates and clears the item label entry
    def setXY(self, event):
        x, y = self.userCoords(event.x, event.y)
        self.setArguments(str(x), str(y), '')

    #creates new node in coordinates of double canvas mouse click
    def createNode(self, event):
        self.recordModifierKeyState(event=event)
        x, y = self.userCoords(event.x, event.y)
        n = sum(len(n.data) for n in self.nodes)
        while self._findNodeLabeled('P{}'.format(n)): n += 1
        self.setArguments(str(x), str(y), 'P{}'.format(n))
        self.insertButton.invoke()

    def crosshairCoords(self, a, b):
        x, y = self.canvasCoords(a, b)
        return ((x, y - self.CROSSHAIR_SIZE, x, y + self.CROSSHAIR_SIZE),
                (x - self.CROSSHAIR_SIZE, y, x + self.CROSSHAIR_SIZE, y),
                (x, y - self.CROSSHAIR_SIZE - 3),
                (x - self.CROSSHAIR_SIZE - 3, y))

    def createCrosshairItems(
            self, vertCoords, horizCoords, aCoords, bCoords,
            aLabel='a', bLabel='b', color=CROSSHAIR_COLOR, font=CROSSHAIR_FONT):
        vert = self.canvas.create_line(*vertCoords, fill=color, width=1)
        horiz = self.canvas.create_line(*horizCoords, fill=color, width=1)
        aText = self.canvas.create_text(
            *aCoords, text=aLabel, anchor=S, font=font, fill=color)
        bText = self.canvas.create_text(
            *bCoords, text=bLabel, anchor=E, font=font, fill=color)
        return (vert, horiz, aText, bText)

    def queryPointCoords(self, a, b):
        x, y = self.canvasCoords(a, b)
        return ((x, y - self.CIRCLE_RADIUS), (x + self.CIRCLE_RADIUS, y),
                (x, y + self.CIRCLE_RADIUS), (x - self.CIRCLE_RADIUS, y))

    def createQueryPointItems(
            self, polyCoords, color=QUERY_POINT_COLOR, label='a, b',
            tags='query', font=None):
        if font is None: font = (self.VARIABLE_FONT[0], self.TEXT_FONT[1])
        polygon = self.canvas.create_polygon(*polyCoords, fill=color, width=0,
                                             tags=tags)
        text = self.canvas.create_text(
            polyCoords[1][0], polyCoords[0][1], anchor=SW, text=label,
            fill=color, font=font, tags=tags)
        for item in (polygon, text):
            self.canvas.copyItemHandlers(self.pointRegionRectangle, item)
        return polygon, text

    def createMeasure(
            self, x0, y0, x1, y1, color=MEASURE_COLOR, width=2, tags='measure'):
        measure = self.canvas.create_line(
            *self.canvasCoords(x0, y0), *self.canvasCoords(x1, y1),
            width=width, arrow=BOTH, fill=color)
        self.canvas.copyItemHandlers(self.pointRegionRectangle, measure)
        return measure
    
    insertCode = '''
def insert(self, a={x}, b={y}, data={data!r}):
   self.__root = self.__insert(self.__root, a, b, data)   
'''
    
    #wrapper method for recursive insert
    def insert(self, x, y, data, start=True, code=insertCode, wait=0.1):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start,
            sleepTime=wait / 10 if code else 0)

        if code:
            crosshair = self.createCrosshairItems(*self.crosshairCoords(x, y))
            callEnviron |= set(crosshair)
            self.highlightCode(
                'self.__root = self.__insert(self.__root, a, b, data)',
                callEnviron)
        self.__root, new = self.__insert(
            self.__root, x, y, data, self.userBBox(self.pointRegion),
            wait=wait if code else 0, code=self._insertCode if code else '')
        self.canvas.itemConfig('root', state=NORMAL)
        if code:
            self.dispose(callEnviron, *crosshair)
            self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10 if code else 0)
        return new

    _insertCode = '''
def __insert(self, n={nVal}, a={x}, b={y}, data={data!r}):
   if not n: return Node(a, b, data)

   if n.a == a and n.b == b:
      n.data = data
      return n

   if   a >= n.a and b >  n.b:
      n.NE = self.__insert(n.NE, a, b, data)
   elif a >  n.a and b <= n.b: 
      n.SE = self.__insert(n.SE, a, b, data)
   elif a <= n.a and b <  n.b: 
      n.SW = self.__insert(n.SW, a, b, data)
   else: 
      n.NW = self.__insert(n.NW, a, b, data)   
   
   return n  
'''
    
    #creates a new node if none at designated coords
    #otherwise adds data to existing coordinate
    def __insert(self, n, x, y, data, bbox, code=_insertCode, wait=0.1):
        nVal = str(n)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=wait / 10)
        nArrowConfig = {'orientation': -135}
        nArrow = self.createLabeledArrow(n if n else (x, y), 'n',
                                         **nArrowConfig)
        callEnviron |= set(nArrow)

        self.highlightCode('not n', callEnviron, wait=wait)
        if not n:        # return a new Node if we've reached an empty leaf
            
            self.highlightCode(
                'return Node(a, b, data)', callEnviron, wait=wait)
            n = Node(x, y, data, bbox)
            self.nodes.append(n)
            n.items = self.createPointItems(n, self.__root is None)
            if self.__root is None:
                self.__root = n
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            self.updateBoundaryDisplay()
            return n, True

        # if the point to be inserted is identical to the current node,
        # replace its data and return False for the new node flag
        elif (self.highlightCode('n.a == a', callEnviron, wait=wait,
                                 returnValue=n.x == x) and
              self.highlightCode('n.b == b', callEnviron, wait=wait,
                                 returnValue=n.y == y)):
            self.highlightCode('n.data = data', callEnviron, wait=wait)
            n.data = [data]
            self.canvas.itemConfig(n.items[3], text=', '.join(n.data))
            
            self.highlightCode('return n', callEnviron)
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            self.updateBoundaryDisplay()
            return n, False

        elif (self.highlightCode('a >= n.a', callEnviron, wait=wait,
                                 returnValue=x >= n.x) and
              self.highlightCode('b >  n.b', callEnviron, wait=wait,
                                 returnValue=y > n.y)):
            self.highlightCode('n.NE = self.__insert(n.NE, a, b, data)',
                               callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            n.NE, new = self.__insert(
                n.NE, x, y, data, (n.x, n.y, n.BBox[2], n.BBox[3]), code, wait)
            self.canvas.restoreItems(nArrow, colors)
        elif (self.highlightCode('a >  n.a', callEnviron, wait=wait,
                                 returnValue=x > n.x) and
              self.highlightCode('b <= n.b', callEnviron, wait=wait,
                                 returnValue=y <=  n.y)):
            self.highlightCode('n.SE = self.__insert(n.SE, a, b, data)',
                               callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            n.SE, new = self.__insert(
                n.SE, x, y, data, (n.x, n.BBox[1], n.BBox[2], n.y), code, wait)
            self.canvas.restoreItems(nArrow, colors)
        elif (self.highlightCode('a <= n.a', callEnviron, wait=wait,
                                 returnValue=x <= n.x) and
              self.highlightCode('b <  n.b', callEnviron, wait=wait,
                                 returnValue=y <  n.y)):
            self.highlightCode('n.SW = self.__insert(n.SW, a, b, data)',
                               callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            n.SW, new = self.__insert(
                n.SW, x, y, data, (n.BBox[0], n.BBox[1], n.x, n.y), code, wait)
            self.canvas.restoreItems(nArrow, colors)
        else:
            self.highlightCode('n.NW = self.__insert(n.NW, a, b, data)',
                               callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            n.NW, new = self.__insert(
                n.NW, x, y, data, (n.BBox[0], n.y, n.x, n.BBox[3]), code, wait)
            self.canvas.restoreItems(nArrow, colors)
            
        self.highlightCode(('return n', 2), callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)
        self.updateBoundaryDisplay()
        return n, new

    def createPointItems(self, node, isRoot=False,
                         lineState=HIDDEN, rootRingState=HIDDEN):
        R = self.CIRCLE_RADIUS
        ring = self.CIRCLE_RADIUS + 2
        nX, nY = self.canvasCoords(node.x, node.y)
        bbox = self.canvasBBox(node.BBox)
        items = (
            self.canvas.create_line(
                nX, bbox[1], nX, bbox[3], state=lineState,
                fill=self.LINE_COLOR, tags=('boundary', 'vertical')),
            self.canvas.create_line(
                bbox[0], nY, bbox[2], nY, state=lineState,
                fill=self.LINE_COLOR, tags=('boundary', 'horizontal')),
            self.canvas.create_oval(
                nX - R, nY - R, nX + R, nY + R,
                fill=self.POINT_COLOR, tags=('point',)),
            self.canvas.create_text(
                nX, nY - R * 3, text=', '.join(node.data),
                fill=self.TEXT_COLOR, font=self.TEXT_FONT,
                tags=('point', 'label')))
        self.canvas.tag_lower('boundary', 'point')
        if isRoot:
            items += (self.canvas.create_oval(
                nX - ring, nY - ring, nX + ring, nY + ring, tags=('root',),
                outline=self.ROOT_OUTLINE, width=3, state=rootRingState),)
            self.canvas.tag_lower(items[-1], 'boundary')

        self.canvas.tag_bind(
            items[2], '<Button-1>',
            lambda e: self.setArguments(str(node.x), str(node.y),
                                        node.data[0] if node.data else ''))
        for item in items[:2]:
            self.canvas.copyItemHandlers(self.pointRegionRectangle, item)
        return items

    def randomFill(self, nPoints=1, label=None):
        gap = 5
        regionSize = V(BBoxSize(self.pointRegion)) - V((gap * 2, gap * 2))
        separation = self.CIRCLE_RADIUS * 3
        added = 0
        for i in range(nPoints):
            if label and label.startswith('P') and label[1:].isdigit():
                n = int(label[1:])
            else:
                n = sum(len(n.data) for n in self.nodes)
                label = 'P{}'.format(n)
            while self._findNodeLabeled(label):
                n += 1
                label = 'P{}'.format(n)

            x = random.randrange(gap, gap + regionSize[0])
            y = random.randrange(gap, gap + regionSize[1])
            nearest = self.findNearest(x, y, code='', wait=0)
            tries = 0
            while nearest and nearest[3] < separation and tries < 10:
                x = random.randrange(gap, gap + regionSize[0])
                y = random.randrange(gap, gap + regionSize[1])
                nearest = self.findNearest(x, y, code='', wait=0)
                tries += 1
            if ((nearest is None or nearest[3] >= separation) and
                self.insert(x, y, label, code='', wait=0)):
                added += 1
        return added

    #clears canvas, and deletes all the nodes
    #with accompanying data and lines
    def new(self):
        self.canvas.delete('all')
        self.points = []
        self.lines= []
        self.nodes = []
        self.__root = None
        self.display()

    def _findNodeLabeled(self, label):
        for node in self.nodes:
            if label in node.data: return node

    findExactCode = '''
def findExact(self, a={x}, b={y}):
   return self.__find(self.__root, a, b)
'''
    
    def findExact(self, x, y, start=True, code=findExactCode, wait=0.1):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start,
            sleepTime=wait / 10)

        if code:
            crosshair = self.createCrosshairItems(*self.crosshairCoords(x, y))
            callEnviron |= set(crosshair)
            self.highlightCode('return self.__find(self.__root, a, b)',
                               callEnviron)
        result = self._find(self.__root, x, y, wait=wait,
                            code=self._findCode if code else '')
        if code:
            self.dispose(callEnviron, *crosshair)
            self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)
        return result

    _findCode = '''
def __find(self, n={nVal}, a={x}, b={y}):
   if not n: return None

   if n.a == a and n.b == b: return n.data

   if   a >= n.a and b >  n.b:
      return self.__find(n.NE, a, b)
   elif a >  n.a and b <= n.b: 
      return self.__find(n.SE, a, b)
   elif a <= n.a and b <  n.b: 
      return self.__find(n.SW, a, b)
   else:                       
      return self.__find(n.NW, a, b)
'''
    def _find(self, n, x, y, code=_findCode, wait=0.1):
        nVal = str(n)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=wait / 10)
        nArrowConfig = {'orientation': -135}
        nArrow = self.createLabeledArrow(n if n else (x, y), 'n',
                                         **nArrowConfig)
        callEnviron |= set(nArrow)

        self.highlightCode('not n', callEnviron, wait=wait)
        if not n:
            self.highlightCode('return None', callEnviron)
            result = None

        elif (self.highlightCode('n.a == a', callEnviron, wait=wait,
                                 returnValue=n.x == x) and
              self.highlightCode('n.b == b', callEnviron, wait=wait,
                                 returnValue=n.y == y)):
            self.highlightCode('return n.data', callEnviron, wait=wait)
            result = n.data[0]

        elif (self.highlightCode('a >= n.a', callEnviron, wait=wait,
                                 returnValue=x >= n.x) and
              self.highlightCode('b >  n.b', callEnviron, wait=wait,
                                 returnValue=y > n.y)):
            self.highlightCode('return self.__find(n.NE, a, b)', callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            result = self._find(n.NE, x, y, code=code, wait=wait)
            self.canvas.restoreItems(nArrow, colors)
        elif (self.highlightCode('a >  n.a', callEnviron, wait=wait,
                                 returnValue=x > n.x) and
              self.highlightCode('b <= n.b', callEnviron, wait=wait,
                                 returnValue=y <=  n.y)):
            self.highlightCode('return self.__find(n.SE, a, b)', callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            result = self._find(n.SE, x, y, code=code, wait=wait)
            self.canvas.restoreItems(nArrow, colors)
        elif (self.highlightCode('a <= n.a', callEnviron, wait=wait,
                                 returnValue=x <= n.x) and
              self.highlightCode('b <  n.b', callEnviron, wait=wait,
                                 returnValue=y <  n.y)):
            self.highlightCode('return self.__find(n.SW, a, b)', callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            result = self._find(n.SW, x, y, code=code, wait=wait)
            self.canvas.restoreItems(nArrow, colors)
        else:
            self.highlightCode('return self.__find(n.NW, a, b)', callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            result = self._find(n.NW, x, y, code=code, wait=wait)
            self.canvas.restoreItems(nArrow, colors)
            
        self.cleanUp(callEnviron, sleepTime=wait / 10)
        return result

    _nearPointCode = '''
def __nearPoint(self, n={nVal}, a={x}, b={y}):
   if not n: return None
 
   if a == n.a and b == n.b: return n

   if   a >= n.a and b >  n.b:
      ans = self.__nearPoint(n.NE, a, b)
   elif a >  n.a and b <= n.b:
      ans = self.__nearPoint(n.SE, a, b)
   elif a <= n.a and b <  n.b: 
      ans = self.__nearPoint(n.SW, a, b)
   else:
      ans = self.__nearPoint(n.NW, a, b)   

   return ans if ans else n
'''
    _lastReferenceToN = re.compile(r'else (n)')
    
    def _nearPoint(self, n, x, y, code=_nearPointCode, wait=0.1):
        nVal = str(n)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=wait / 10)
        localVars = ()
        if code:
            nArrow = self.createLabeledArrow(
                n if n else self.noneCoords(), 'n', orientation=135)
            callEnviron |= set(nArrow)
            localVars += nArrow

        shortCircuit = False
        self.highlightCode('not n', callEnviron, wait=wait)
        if not n:
            self.highlightCode('return None', callEnviron)
            ans = None
            shortCircuit = True

        elif (self.highlightCode('a == n.a', callEnviron, wait=wait,
                                 returnValue=n.x == x) and
              self.highlightCode('b == n.b', callEnviron, wait=wait,
                                 returnValue=n.y == y)):
            self.highlightCode('return n', callEnviron, wait=wait)
            ans = n
            shortCircuit = True

        elif (self.highlightCode('a >= n.a', callEnviron, wait=wait,
                                 returnValue=x >= n.x) and
              self.highlightCode('b >  n.b', callEnviron, wait=wait,
                                 returnValue=y > n.y)):
            self.highlightCode(
                'ans = self.__nearPoint(n.NE, a, b)', callEnviron)
            colors = self.canvas.fadeItems(localVars)
            ans = self._nearPoint(n.NE, x, y, code=code, wait=wait)
            self.canvas.restoreItems(localVars, colors)
        elif (self.highlightCode('a >  n.a', callEnviron, wait=wait,
                                 returnValue=x > n.x) and
              self.highlightCode('b <= n.b', callEnviron, wait=wait,
                                 returnValue=y <=  n.y)):
            self.highlightCode(
                'ans = self.__nearPoint(n.SE, a, b)', callEnviron)
            colors = self.canvas.fadeItems(localVars)
            ans = self._nearPoint(n.SE, x, y, code=code, wait=wait)
            self.canvas.restoreItems(localVars, colors)
        elif (self.highlightCode('a <= n.a', callEnviron, wait=wait,
                                 returnValue=x <= n.x) and
              self.highlightCode('b <  n.b', callEnviron, wait=wait,
                                 returnValue=y <  n.y)):
            self.highlightCode(
                'ans = self.__nearPoint(n.SW, a, b)', callEnviron)
            colors = self.canvas.fadeItems(localVars)
            ans = self._nearPoint(n.SW, x, y, code=code, wait=wait)
            self.canvas.restoreItems(localVars, colors)
        else:
            self.highlightCode(
                'ans = self.__nearPoint(n.NW, a, b)', callEnviron)
            colors = self.canvas.fadeItems(localVars)
            ans = self._nearPoint(n.NW, x, y, code=code, wait=wait)
            self.canvas.restoreItems(localVars, colors)

        if not shortCircuit:
            ansArrow = self.createLabeledArrow(
                ans if ans else self.noneCoords(), 'ans', orientation=-135)
            callEnviron |= set(ansArrow)
            self.highlightCode(('ans', 6), callEnviron, wait=wait)
            self.highlightCode((('return ', 3),
                                ('ans', 5) if ans else self._lastReferenceToN),
                               callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)
        return ans if ans else n
        
    _nearestCode = '''
def __nearest(self, n={nVal},
       a={x}, b={y}, dist={dist:3.1f},
       cand={cand}, bounds={bounds}):
   if not n or dist == 0: return cand, dist
 
   fn = self.__distance
   newDist  = fn(a, b, n.a, n.b)
   if newDist < dist:
      cand = n  
      dist = newDist
 
   cBounds = CircleBounds(a, b, dist, fn)

   newB = bounds.adjusted(left = n.a, top = n.b)
   if cBounds.intersects(newB): 
      cand, dist = self.__nearest(
         n.SE, a, b, dist, cand, newB)
      cBounds.adjust(dist)

   newB = bounds.adjusted(left = n.a, bottom = n.b)
   if cBounds.intersects(newB): 
      cand, dist = self.__nearest(
         n.NE, a, b, dist, cand, newB) 
      cBounds.adjust(dist)
          
   newB = bounds.adjusted(right = n.a, top = n.b)  
   if cBounds.intersects(newB): 
      cand, dist = self.__nearest(
         n.SW, a, b, dist, cand, newB)
      cBounds.adjust(dist)
   
   newB = bounds.adjusted(right = n.a, bottom = n.b)
   if cBounds.intersects(newB): 
      cand, dist = self.__nearest(
         n.NW, a, b, dist, cand, newB) 

   return cand, dist
'''
    
    def _nearest(
            self, n, x, y, dist, cand, bounds, code=_nearestCode, wait=0.1):
        nVal = str(n)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=wait / 10)

        candArrowConfig = {'orientation': -135}
        localVars, faded = (), ()
        if code:
            nArrow = self.createLabeledArrow(
                n if n else self.noneCoords(), 'n', orientation=135)
            distance = self.canvas.create_text(
                *self.variableTextCoords(), anchor=SW, font=self.VARIABLE_FONT,
                text='dist = {:3.1f}'.format(dist), fill=self.VARIABLE_COLOR)
            candArrow = self.createLabeledArrow(
                cand if cand else self.noneCoords(), 'cand', **candArrowConfig)
            boundsText = self.canvas.create_text(
                *self.variableTextCoords(left=False), anchor=SE,
                text='bounds = {}'.format(bounds), font=self.VARIABLE_FONT,
                fill=self.BOUNDS_CONFIG['outline'], tags=('bounds', 'text'))
            boundsRect = self.canvas.create_hashed_rectangle(
                *self.canvasCoords(bounds._l, bounds._b),
                *self.canvasCoords(bounds._r, bounds._t),
                tags=('bounds', 'rect'),  **self.BOUNDS_CONFIG)
            self.canvas.copyItemHandlers(self.pointRegionRectangle, boundsRect)
            localVars += nArrow + candArrow + (distance, boundsText, boundsRect)
            faded += (Scrim.FADED_FILL,) * (len(localVars) - 1) + (
                Scrim.FADED_OUTLINE,)
            callEnviron |= set(localVars)
        
        if (self.highlightCode('not n', callEnviron, wait=wait,
                               returnValue=not n) or
            self.highlightCode('dist == 0', callEnviron, wait=wait,
                               returnValue=dist == 0)):
            self.highlightCode('return cand, dist', callEnviron)
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return cand, dist

        self.highlightCode('fn = self.__distance', callEnviron, wait=wait)
        if code:
            measure = self.createMeasure(x, y, n.a, n.b)
            callEnviron.add(measure)
        self.highlightCode('newDist  = fn(a, b, n.a, n.b)', callEnviron,
                           wait=wait)
        newDist = euclideanDistance(x, y, n.a, n.b)
        if code:
            self.dispose(callEnviron, measure)
            newDistText = self.canvas.create_text(
                *self.variableTextCoords(line=2), anchor=SW,
                font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR,
                text='newDist = {:3.1f}'.format(newDist))
            localVars += (newDistText,)
            faded += (Scrim.FADED_FILL,)
            callEnviron.add(newDistText)

        if self.highlightCode('newDist < dist', callEnviron, wait=wait,
                              returnValue=newDist < dist):
            cand = n
            dist = newDist
            if code:
                self.highlightCode('cand = n', callEnviron)
                self.moveItemsTo(
                    candArrow, self.labeledArrowCoords(cand, **candArrowConfig),
                    sleepTime=wait / 10)
                self.highlightCode('dist = newDist', callEnviron, wait=wait)
                self.canvas.itemConfig(
                    distance, text='dist = {:3.1f}'.format(dist))
        
        self.highlightCode('cBounds = CircleBounds(a, b, dist, fn)',
                           callEnviron, wait=wait)
        cBounds = CircleBounds(x, y, dist)
        if code:
            cBoundsText = self.canvas.create_text(
                *self.variableTextCoords(left=False, line=2), anchor=SE,
                text='cBounds = {}'.format(cBounds), tags=('cbounds', 'text'),
                fill=self.C_BOUNDS_CONFIG['outline'], font=self.VARIABLE_FONT)
            cBoundsRect = self.canvas.create_hashed_rectangle(
                *self.canvasCoords(cBounds._l, cBounds._b),
                *self.canvasCoords(cBounds._r, cBounds._t),
                tags=('cbounds', 'rect'), **self.C_BOUNDS_CONFIG)
            self.canvas.copyItemHandlers(self.pointRegionRectangle, cBoundsRect)
            localVars += (cBoundsText,)
            faded += (Scrim.FADED_FILL,)
            callEnviron |= set((cBoundsText, cBoundsRect))

        newBoundsText, newBoundsRect = None, None
        quadrants = {'SE': (('left', n.a), ('top', n.b)),
                     'NE': (('left', n.a), ('bottom', n.b)),
                     'SW': (('right', n.a), ('top', n.b)),
                     'NW': (('right', n.a), ('bottom', n.b))}
        count = 0
        for quadrant in quadrants:
            adjustment = quadrants[quadrant]
            keys = [e[0] for e in adjustment]
            self.highlightCode(
                'newB = bounds.adjusted({} = n.a, {} = n.b)'.format(*keys),
                callEnviron, wait=wait)
            newB = bounds.adjusted(**dict(adjustment))
            count += 1
            if code:
                if newBoundsText is None:
                    newBoundsText = self.canvas.create_text(
                        *self.variableTextCoords(left=False, line=3), anchor=SE,
                        text='newB = {}'.format(newB), tags=('newB', 'text'),
                        fill=self.NEW_BOUNDS_CONFIG['outline'],
                        font=self.VARIABLE_FONT)
                    newBoundsRect = self.canvas.create_hashed_rectangle(
                        *self.canvasCoords(newB._l, newB._b),
                        *self.canvasCoords(newB._r, newB._t),
                        tags=('newB', 'rect'), **self.NEW_BOUNDS_CONFIG)
                    self.canvas.copyItemHandlers(self.pointRegionRectangle,
                                                 newBoundsRect)
                    localVars += (newBoundsText,)
                    faded += (Scrim.FADED_FILL,)
                    callEnviron |= set((newBoundsText, newBoundsRect))
                else:
                    self.canvas.itemConfig(newBoundsText,
                                           text='newB = {}'.format(newB))
                    self.dispose(callEnviron, newBoundsRect)
                    newBoundsRect = self.canvas.create_hashed_rectangle(
                        *self.canvasCoords(newB._l, newB._b),
                        *self.canvasCoords(newB._r, newB._t),
                        tags=('newB', 'rect'), **self.NEW_BOUNDS_CONFIG)
                    self.canvas.copyItemHandlers(self.pointRegionRectangle,
                                                 newBoundsRect)
                    callEnviron.add(newBoundsRect)

            if self.highlightCode(
                    ('cBounds.intersects(newB)', count), callEnviron,
                    wait=wait, returnValue=cBounds.intersects(newB)):
                if code:
                    self.highlightCode(
                        (('cand, dist = self.__nearest(', count),
                         re.compile(' *n.{}, a, b, dist, cand, newB.'.format(
                             quadrant))),
                        callEnviron)
                    lvars = localVars + (cBoundsRect, newBoundsRect)
                    colors = self.canvas.fadeItems(
                        lvars, faded + (Scrim.FADED_OUTLINE,) * 2)
                nextCand, nextDist = self._nearest(
                    getattr(n, quadrant), x, y, dist, cand, newB, code=code,
                    wait=wait)
                if code:
                    self.canvas.restoreItems(lvars, colors)
                distanceChanged = nextDist != dist
                if distanceChanged:
                    dist = nextDist
                    if code:
                        self.canvas.itemConfig(
                            distance, text='dist = {:3.1f}'.format(dist))
                if nextCand is not cand:
                    cand = nextCand
                    if code:
                        self.moveItemsTo(
                            candArrow,
                            self.labeledArrowCoords(cand, **candArrowConfig),
                            sleepTime=wait / 10)

                if quadrant == 'NW':
                    continue
                self.highlightCode(('cBounds.adjust(dist)', count),
                                   callEnviron, wait=wait)
                if distanceChanged:
                    cBounds.adjust(dist)
                    if code:
                        self.dispose(callEnviron, cBoundsRect)
                        cBoundsRect = self.canvas.create_hashed_rectangle(
                            *self.canvasCoords(cBounds._l, cBounds._b),
                            *self.canvasCoords(cBounds._r, cBounds._t),
                            tags=('cbounds', 'rect'),
                            **self.C_BOUNDS_CONFIG)
                        self.canvas.copyItemHandlers(
                            self.pointRegionRectangle, cBoundsRect)
                        callEnviron.add(cBoundsRect)
        
        self.highlightCode(('return cand, dist', 2), callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)
        return cand, dist

    findNearestCode = '''
def findNearest(self, a={x}, b={y}):
   if not self.__root: return None

   ans  = self.__nearPoint(self.__root, a, b)
   dist = self.__distance(a, b, ans.a, ans.b)

   bounds =  Bounds()
   ans, dist = self.__nearest(
      self.__root, a, b, dist, ans, bounds)

   return ans.a, ans.b, ans.data, dist
'''
    _nearestCallPattern = re.compile(r'ans, dist =.*\n.* ans, bounds\)')
    
    def findNearest(self, x, y, start=True, code=findNearestCode, wait=0.1):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start,
            sleepTime=wait / 10)

        if code:
            queryPoint = self.createQueryPointItems(self.queryPointCoords(x, y))
            callEnviron |= set(queryPoint)
        localVars, faded = (), ()
        self.highlightCode('not self.__root', callEnviron)

        if not self.__root:
            self.highlightCode('return None', callEnviron)
            result = None
        else:
            self.highlightCode('ans  = self.__nearPoint(self.__root, a, b)',
                               callEnviron)
            ans = self._nearPoint(
                self.__root, x, y, code=self._nearPointCode if code else '',
                wait=wait if code else 0)
            ansArrowConfig = {'orientation': -135}
            if code:
                ansArrow = self.createLabeledArrow(ans, 'ans', **ansArrowConfig)
                measure = self.createMeasure(x, y, ans.a, ans.b)
                callEnviron |= set((measure, *ansArrow))
                localVars += ansArrow
                faded += (Scrim.FADED_FILL,) * len(ansArrow)

            self.highlightCode('dist = self.__distance(a, b, ans.a, ans.b)',
                               callEnviron, wait)
            dist = euclideanDistance(x, y, ans.a, ans.b)
            if code:
                distance = self.canvas.create_text(
                    *self.variableTextCoords(), font=self.VARIABLE_FONT,
                    text='dist = {:3.1f}'.format(dist), anchor=SW,
                    fill=self.VARIABLE_COLOR)
                callEnviron.add(distance)
                localVars += (distance,)
                faded += (Scrim.FADED_FILL,)
                self.dispose(callEnviron, measure)

            self.highlightCode('bounds =  Bounds()', callEnviron, wait=wait)
            bounds = Bounds()
            if code:
                boundsText = self.canvas.create_text(
                    *self.variableTextCoords(left=False), anchor=SE,
                    text='bounds = {}'.format(bounds), tags=('bounds', 'text'),
                    font=self.VARIABLE_FONT, fill=self.BOUNDS_CONFIG['outline'])
                boundsRect = self.canvas.create_hashed_rectangle(
                    *self.canvasCoords(bounds._l, bounds._b),
                    *self.canvasCoords(bounds._r, bounds._t),
                    tags=('bounds', 'rect'), **self.BOUNDS_CONFIG)
                self.canvas.copyItemHandlers(self.pointRegionRectangle,
                                             boundsRect)
                callEnviron |= set((boundsText, boundsRect))
                localVars += (boundsText, boundsRect)
                faded += (Scrim.FADED_FILL, Scrim.FADED_OUTLINE) 

            self.highlightCode(self._nearestCallPattern, callEnviron)
            colors = self.canvas.fadeItems(localVars, faded)
            newAns, newDist = self._nearest(
                self.__root, x, y, dist, ans, bounds, wait=wait if code else 0,
                code=self._nearestCode if code else '')
            self.canvas.restoreItems(localVars, colors)
            if newDist != dist:
                dist = newDist
                if code:
                    self.canvas.itemConfig(distance,
                                           text='dist = {:3.1f}'.format(dist))
            if newAns != ans:
                ans = newAns
                if code:
                    self.moveItemsTo(
                        ansArrow,
                        self.labeledArrowCoords(newAns, **ansArrowConfig),
                        sleepTime=wait / 10)
            
            self.highlightCode('return ans.a, ans.b, ans.data, dist',
                               callEnviron, wait=wait)
            result = (ans.a, ans.b, ans.data[0], dist)
            
        self.cleanUp(callEnviron)
        return result
    
    traverseExampleCode = '''
for a, b, data in quadtree.traverse():
   print(data)
'''
    
    traverseItemSeparator = ' '
    
    def traverseExample(self, code=traverseExampleCode, wait=0.1, start=True):
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)

        outBoxCoords = self.outputBoxCoords()
        outBoxCenter = BBoxCenter(outBoxCoords)
        self.outBox = OutputBox(self, outBoxCoords, outputFont=self.TEXT_FONT)
        callEnviron |= set(self.outBox.items())
        
        self.highlightCode('a, b, data in quadtree.traverse()', callEnviron)
        dataArrow = None
        localVars = ()
        colors = self.canvas.fadeItems(localVars)
        dataArrowConfig = {'orientation': -70, 'anchor': E}
        for a, b, data in self.traverse():
            self.canvas.restoreItems(localVars, colors)
            node = self._findNodeLabeled(data)
            if dataArrow is None:
                dataArrow = self.createLabeledArrow(node, 'a, b, data',
                                                    **dataArrowConfig)
                callEnviron |= set(dataArrow)
                localVars += dataArrow
            else:
                self.moveItemsTo(
                    dataArrow, self.labeledArrowCoords(node, **dataArrowConfig),
                    sleepTime=wait / 10)

            self.highlightCode('print(data)', callEnviron, wait=wait)
            dataItem = self.canvas.copyItem(node.items[3])
            callEnviron.add(dataItem)
            self.outBox.appendText(dataItem, sleepTime=wait / 10,
                                   separator=self.traverseItemSeparator)
            callEnviron.discard(dataItem)
            
            self.highlightCode('a, b, data in quadtree.traverse()', callEnviron)
            colors = self.canvas.fadeItems(localVars)
        
        self.canvas.restoreItems(localVars, colors)
        self.highlightCode((), callEnviron)
        self.cleanUp(callEnviron)

    traverseCode = '''
def traverse(self):
   s = [ ]
   if self.__root: s.append(self.__root)

   while len(s) > 0:
      n = s.pop()  
      yield n.a, n.b, n.data
        
      if n.NE: s.append(n.NE)
      if n.SE: s.append(n.SE)
      if n.SW: s.append(n.SW)
      if n.NW: s.append(n.NW)            
'''
    
    def traverse(self, code=traverseCode, wait=0.1):
        callEnviron = self.createCallEnvironment(code=code)
        self.highlightCode('s = [ ]', callEnviron, wait=wait)

        labelHeight = textHeight(self.VARIABLE_FONT, 's')
        pad = textHeight(self.TEXT_FONT, 'P0') // 2
        cellSize = (
            textWidth(self.TEXT_FONT, 'W' * self.maxArgWidth) + 2 * pad,
            3 * pad)
        self.traverseStack = Table(
            self,
            V(self.pointRegion[2:]) + V(pad, -(labelHeight + cellSize[1])),
            cellWidth=cellSize[0], cellHeight=cellSize[1], labelOffset=pad,
            label='s', cellBorderWidth=1, vertical=True, direction=-1,
            labelFont=self.VARIABLE_FONT, labelColor=self.VARIABLE_COLOR)
        callEnviron |= set(self.traverseStack.items())

        if self.highlightCode(
                'self.__root', callEnviron, wait=wait, returnValue=self.__root):
            self.highlightCode('s.append(self.__root)', callEnviron)
            self.stackPush(self.__root, callEnviron, wait=wait)

        nArrow = None
        childArrowConfig = self.traverseItemConfig.copy()
        self.highlightCode('len(s) > 0', callEnviron, wait=wait)
        while len(self.traverseStack) > 0:
            self.highlightCode('n = s.pop()', callEnviron)
            node, nArrow = self.stackPop(callEnviron, nArrow, wait=wait)
            
            self.highlightCode('yield n.a, n.b, n.data', callEnviron, wait=wait)
            for item in node.data:
                itemMap = self.yieldCallEnvironment(
                    callEnviron, sleepTime=wait / 10, moveItems=False)
                yield node.a, node.b, item
                self.resumeCallEnvironment(
                    callEnviron, itemMap, sleepTime=wait / 10)

            for child, orient, anchor in (
                    ('NE', -110, E), ('SE', -70, E),
                    ('SW',   70, W), ('NW', 110, W)):
                childName = 'n.' + child
                childNode = getattr(node, child)
                if self.highlightCode(childName, callEnviron, wait=wait,
                                      returnValue=childNode):
                    childArrow = self.createLabeledArrow(
                        childNode, childName, orientation=orient, anchor=anchor,
                        color=VisualizationApp.VARIABLE_COLOR)
                    callEnviron |= set(childArrow)
                    self.highlightCode(
                        's.append({})'.format(childName), callEnviron)
                    self.stackPush(childNode, callEnviron, wait=wait)
                    self.dispose(callEnviron, *childArrow)
                    
            self.highlightCode('len(s) > 0', callEnviron, wait=wait)
                
        self.highlightCode((), callEnviron)
        self.cleanUp(callEnviron)
        
    traverseItemConfig = {
        'color': VisualizationApp.VARIABLE_COLOR, 'orientation': 70,
        'anchor': W}

    def stackPush(
            self,
            node: 'A quadtree Node to push on traverse stack',
            callEnviron: 'Call environment for traverse iterator',
            wait: 'Total animation time' =0.1):
        stackHeight = len(self.traverseStack)
        cellCoords = self.traverseStack.cellCoords(stackHeight)
        cellCenter = BBoxCenter(cellCoords)
        nodeDataCopy = self.canvas.copyItem(node.items[3])
        callEnviron.add(nodeDataCopy)
        self.moveItemsLinearly(nodeDataCopy, cellCenter, sleepTime=wait / 10)
        self.traverseStack.append(drawnValue(node, nodeDataCopy))
        callEnviron |= set(self.traverseStack.items())
        
    def stackPop(self, callEnviron, nArrow, wait=0.1):
        if len(self.traverseStack) <= 0:
            raise Exception('Traverse stack is empty')
        top = self.traverseStack[-1]
        arrowCoords = self.labeledArrowCoords(
            top.val, **self.traverseItemConfig)
        if nArrow is None:
            nArrow = self.createLabeledArrow(
                arrowCoords, 'n', **self.traverseItemConfig)
            callEnviron |= set(nArrow)

        self.moveItemsLinearly(
            top.items + nArrow,
            (self.canvas.coords(top.val.items[3]), *arrowCoords),
            sleepTime=wait / 10)
        self.dispose(callEnviron, *top.items)
            
        self.traverseStack.pop()
        return top.val, nArrow
        
    def clickInsert(self):
        val = self.validArgument()
        if isinstance(val, tuple):
            x, y, d = val
            if self._findNodeLabeled(d):
                self.setMessage(
                    'Point labeled {} already in quadtree'.format(d))
                self.setArgumentHighlight(2, self.ERROR_HIGHLIGHT)
                return
            new = self.insert(int(x), int(y), d, start=self.startMode())
            msg = 'Point {} {}'.format(d, 'inserted' if new else 'updated')
            self.clearArguments()
        else:
            msg = val
        self.setMessage(msg)

    def clickFindExact(self):
        val = self.validArgument(nArgs=2)
        if isinstance(val, tuple):
            x, y, _ = val
            result = self.findExact(int(x), int(y), start=self.startMode())
            msg = ('Found {!r} at ({}, {})'.format(result, x, y) if result else
                   'No point at ({}, {})'.format(x, y))
            self.clearArguments()
        else:
            msg = val
        self.setMessage(msg)
        
    def clickFindNearest(self):
        val = self.validArgument(nArgs=2)
        if isinstance(val, tuple):
            x, y, _ = val
            result = self.findNearest(int(x), int(y), start=self.startMode())
            msg = ('Distance to {!r} at ({}, {}) is {:3.1f}'.format(
                result[2], result[0], result[1], result[3]) if result else
                   'No point found')
            self.clearArguments()
        else:
            msg = val
        self.setMessage(msg)

    def clickRandomFill(self):
        val = self.validArgument(nArgs=1)
        if isinstance(val, tuple):
            n, _, _ = val
            result = self.randomFill(int(n))
            msg = 'Added {} point{}'.format(result, '' if result == 1 else 's')
            self.clearArguments()
        else:
            msg = val
        self.setMessage(msg)
        
    def updateBoundaryDisplay(self):
        self.canvas.itemConfig(
            'boundary', state=NORMAL if self.showBoundaries.get() else HIDDEN)
        
    #allows only numbers for coords that are within the point region
    #everything aside from commas and spaces for data
    def validArgument(self, nArgs=3):
        x, y, d = self.getArguments()
        x, y, d = x.strip(), y.strip(), d.strip()
        msg = ''
        bbox = self.userBBox(self.pointRegion)
        if nArgs == 1 and not x.isdigit():
            msg = 'Number of points must be an integer'
        if nArgs > 1 and not (x.isdigit() and y.isdigit() and
                BBoxContains(bbox, (int(x), int(y)))):
            msg = '({}, {}) does not lie within {}'.format(x, y, bbox)
            for argIndex in (0, 1):
                self.setArgumentHighlight(argIndex, self.ERROR_HIGHLIGHT)
        if nArgs > 2 and not (0 < len(d) and len(d) <= self.maxArgWidth):
            if msg: msg += '\n'
            msg += 'Label must be between 1 and {} characters'.format(
                self.maxArgWidth)
            self.setArgumentHighlight(2, self.ERROR_HIGHLIGHT)
        if nArgs > 2 and ("," in d or " " in d):
            if msg: msg += '\n'
            msg += 'Label may not include commas or spaces'
            self.setArgumentHighlight(2, self.ERROR_HIGHLIGHT)
        return msg if msg else (x, y, d)

    def makeButtons(self):
        vcmd = (self.window.register(
            makeFilterValidate(self.maxArgWidth)), '%P')
        self.insertButton = self.addOperation(
            'Insert', lambda: self.clickInsert(), numArguments=3,
            argHelpText=('X coordinate', 'Y coordinate', 'Label'),
            helpText='Insert an item into the quadtree', validationCmd=vcmd)
        self.findExactButton = self.addOperation(
            'Find Exact', lambda: self.clickFindExact(), numArguments=2,
            argHelpText=('X coordinate', 'Y coordinate'),
            helpText='Find an item at a particular point', validationCmd=vcmd)
        self.findNearestButton = self.addOperation(
            'Find Nearest', lambda: self.clickFindNearest(), numArguments=2,
            argHelpText=('X coordinate', 'Y coordinate'),
            helpText='Find the nearest item to a particular point',
            validationCmd=vcmd)
        self.randomFillButton = self.addOperation(
            'Random Fill', lambda: self.clickRandomFill(), numArguments=1,
            argHelpText=('# of points',),
            helpText='Add N points in random positions', validationCmd=vcmd)
        self.addOperation(
            'New', lambda: self.new(), helpText='Create new, empty quadtree')
        self.addOperation(
            'Traverse', lambda: self.traverseExample(start=self.startMode()),
            helpText='Traverse quadtree items')
        self.showBoundariesCheckbutton = self.addOperation(
            'Show Boundaries',
            lambda: self.updateBoundaryDisplay(), buttonType=Checkbutton,
            variable=self.showBoundaries, cleanUpBefore=False, mutex=False,
            helpText='Toggle display of quadrant boundaries')
        self.addAnimationButtons()

    def enableButtons(self, enable=True):
        super().enableButtons(enable)
        widgetState(self.showBoundariesCheckbutton, NORMAL)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Visualize basic point quadtree operations',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-d', '--debug', default=False, action='store_true',
        help='Show debugging information.')
    parser.add_argument(
        '-r', '--random', default=None, type=int, metavar='N',
        help='Fill with N random points.')
    parser.add_argument(
        '-s', '--seed', default=None, 
        help='Seed the random generator with a string')
    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)
    
    quadtree = PointQuadtree()
    quadtree.DEBUG = args.debug
    
    if args.random:
        quadtree.randomFill(args.random)

    quadtree.runVisualization()
