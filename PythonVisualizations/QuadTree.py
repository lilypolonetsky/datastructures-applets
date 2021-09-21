from tkinter import *

try:
    from tkUtilities import *
    from drawnValue import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .tkUtilities import *
    from .drawnValue import *
    from .VisualizationApp import *

class Node(drawnValue):
    fields = ('x', 'y', 'data', 'NE', 'SE', 'SW', 'NW', 'BBox')
    findex = dict((field, i) for i, field in enumerate(fields))
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
    TEXT_FONT = ("Helvetica", '10')
    CIRCLE_RADIUS = 4
    BUFFER_ZONE = (-10, -20, 50, 0)
    POINT_REGION_COLOR = 'cyan'
    POINT_COLOR = 'black'
    CROSSHAIR_SIZE = 15
    CROSSHAIR_COLOR = 'blue'
    CROSSHAIR_FONT = (VisualizationApp.VARIABLE_FONT[0], -10)

    def __init__(self, maxArgWidth=MAX_ARG_WIDTH, title="Point Quadtree",
                 pointRegion=None, **kwargs):
        if 'canvasBounds' not in kwargs:
            kwargs['canvasBounds'] = (0, 0, kwargs.get('canvasWidth', 800),
                                      kwargs.get('canvasHeight', 400))
        super().__init__(title=title, maxArgWidth = maxArgWidth, **kwargs)
        if pointRegion is None:
            pointRegion = V(self.canvasBounds) - V(self.BUFFER_ZONE)
        self.pointRegion = pointRegion
        self.showBoundaries = IntVar()
        self.showBoundaries.set(1)
        self.buttons = self.makeButtons()
        self.new()

    def canvasCoords(self, userX, userY):
        return self.pointRegion[0] + userX, self.pointRegion[3] - userY
    
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

    #fills the x,y coordinates upon single canvas  mouse click
    def setXY(self, event):
        x, y = self.userCoords(event.x, event.y)
        self.setArguments(str(x), str(y))

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
        
    insertCode = '''
def insert(self, a={x}, b={y}, data={data!r}):
   self.__root = self.__insert(self.__root, a, b, data)   
'''
    
    #wrapper method for insert
    def insert(self, x, y, data, start=True, code=insertCode, wait=0.1):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start,
            sleepTime=wait / 10)

        if code:
            crosshair = self.createCrosshairItems(*self.crosshairCoords(x, y))
            callEnviron |= set(crosshair)
            self.highlightCode(
                'self.__root = self.__insert(self.__root, a, b, data)',
                callEnviron)
        self.__root = self.__insert(self.__root, x, y, data,
                                    self.userBBox(self.pointRegion), wait=wait)
        self.canvas.itemConfig('root', state=NORMAL)
        if code:
            self.dispose(callEnviron, *crosshair)
            self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)

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
            return n

        # if the point to be inserted is identical to the current node,
        # add the data to the list of data
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
            return n

        elif (self.highlightCode('a >= n.a', callEnviron, wait=wait,
                                 returnValue=x >= n.x) and
              self.highlightCode('b >  n.b', callEnviron, wait=wait,
                                 returnValue=y > n.y)):
            self.highlightCode('n.NE = self.__insert(n.NE, a, b, data)',
                               callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            n.NE = self.__insert(n.NE, x, y, data,
                                 (n.x, n.y, n.BBox[2], n.BBox[3]))
            self.canvas.restoreItems(nArrow, colors)
        elif (self.highlightCode('a >  n.a', callEnviron, wait=wait,
                                 returnValue=x > n.x) and
              self.highlightCode('b <= n.b', callEnviron, wait=wait,
                                 returnValue=y <=  n.y)):
            self.highlightCode('n.SE = self.__insert(n.SE, a, b, data)',
                               callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            n.SE = self.__insert(n.SE, x, y, data,
                                 (n.x, n.BBox[1], n.BBox[2], n.y))
            self.canvas.restoreItems(nArrow, colors)
        elif (self.highlightCode('a <= n.a', callEnviron, wait=wait,
                                 returnValue=x <= n.x) and
              self.highlightCode('b <  n.b', callEnviron, wait=wait,
                                 returnValue=y <  n.y)):
            self.highlightCode('n.SW = self.__insert(n.SW, a, b, data)',
                               callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            n.SW = self.__insert(n.SW, x, y, data,
                                 (n.BBox[0], n.BBox[1], n.x, n.y))
            self.canvas.restoreItems(nArrow, colors)
        else:
            self.highlightCode('n.NW = self.__insert(n.NW, a, b, data)',
                               callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            n.NW = self.__insert(n.NW, x, y, data,
                                 (n.BBox[0], n.y, n.x, n.BBox[3]))
            self.canvas.restoreItems(nArrow, colors)
            
        self.highlightCode(('return n', 2), callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)
        self.updateBoundaryDisplay()
        return n

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
                nX - R * 3, nY - R * 2, text=', '.join(node.data),
                anchor=SW, fill=self.TEXT_COLOR, font=self.TEXT_FONT,
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
            self.canvas.tag_bind(item, '<Button>', self.setXY)
            self.canvas.tag_bind(item, '<Double-Button-1>', self.createNode)
        return items

    #clears canvas, and deletes all the nodes
    #with accompanying data and lines
    def new(self):
        self.canvas.delete('all')
        self.points = []
        self.lines= []
        self.nodes = []
        self.direction = None
        self.parent = None
        self.__root = None
        self.display()

    def _findNodeLabeled(self, label):
        for i in self.nodes:
            if label in i.data: return i

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
        
    #does not allow a data point to be re-used
    def clickInsert(self):
        val = self.validArgument()
        if isinstance(val, tuple):
            x, y, d = val
            if self._findNodeLabeled(d):
                self.setMessage(
                    'Point labeled {} already in quadtree'.format(d))
                self.setArgumentHighlight(2, self.ERROR_HIGHLIGHT)
                return
            existing = self.findExact(int(x), int(y), code='')
            self.insert(int(x), int(y), d, start=self.startMode())
            msg = 'Point {} {}'.format(d, 'updated' if existing else 'inserted')
            self.clearArguments()
        else:
            msg = val
        self.setMessage(msg)

    def clickFindExact(self):
        val = self.validArgument(nArgs=2)
        if isinstance(val, tuple):
            x, y, d = val
            result = self.findExact(int(x), int(y), start=self.startMode())
            msg = ('Found {!r} at ({}, {})'.format(result, x, y) if result else
                   'No point at ({}, {})'.format(x, y))
            self.clearArguments()
        else:
            msg = val
        self.setMessage(msg)
        
    def updateBoundaryDisplay(self):
        self.canvas.itemConfig(
            'boundary', state=NORMAL if self.showBoundaries.get() else HIDDEN)
        
    #allows only numbers for coords that are within canvas size
    #everything aside from commas and spaces for data
    def validArgument(self, nArgs=3):
        x, y, d = self.getArguments()
        msg = ''
        bbox = self.userBBox(self.pointRegion)
        if not (x.isdigit() and y.isdigit() and
                BBoxContains(bbox, (int(x), int(y)))):
            msg = "({}, {}) does not lie within {}".format(x, y, bbox)
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
        newQuadtree = self.addOperation(
            'New', lambda: self.new(), helpText='Create new, empty quadtree')
        showBoundariesCheckbutton = self.addOperation(
            'Show Boundaries',
            lambda: self.updateBoundaryDisplay(), buttonType=Checkbutton,
            variable=self.showBoundaries,
            helpText='Toggle display of quadrant boundaries')
        self.addAnimationButtons()
        return [self.insertButton, newQuadtree, showBoundariesCheckbutton]

if __name__ == '__main__':
    quadtree = PointQuadtree()
    quadtree.runVisualization()
