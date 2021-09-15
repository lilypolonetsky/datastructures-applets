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
    def __init__(self, x, y, d, BBox):
        super().__init__((x, y, [d], None, None, None, None, BBox))

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

    #fills the x,y coordinates upon single canvas  mouse click
    def setXY(self, event):
        x, y = self.userCoords(event.x, event.y)
        self.setArguments(str(x), str(y))

    #creates new node in coordinates of double canvas mouse click
    def createNode(self, event):
        x, y = self.userCoords(event.x, event.y)
        n = sum(len(n.data) for n in self.nodes)
        while self._findNodeLabeled('P{}'.format(n)): n += 1
        self.setArguments(str(x), str(y), 'P{}'.format(n))
        self.insertButton.invoke()

    #wrapper method for insert
    def insert(self, x, y, d, start=True):
        callEnviron = self.createCallEnvironment(startAnimations=start)
        self.__root = self.__insert(self.__root, x, y, d,
                                    self.userBBox(self.pointRegion))
        self.cleanUp(callEnviron)

    #creates a new node if none at designated coords
    #otherwise adds data to existing coordinate
    def __insert(self, n, x, y, d, bbox):
        callEnviron = self.createCallEnvironment()

        x = int(x)
        y = int(y)

        if not n:        # return a new Node if we've reached an empty leaf
            n = Node(x, y, d, bbox)
            self.nodes.append(n)
            n.items = self.createPointItems(n, self.__root is None)
            if self.__root is None:
                self.__root = n

        # if the point to be inserted is identical to the current node,
        # add the data to the list of data
        elif n.x == x and n.y == y:
            n.data.append(d)
            self.canvas.itemConfig(n.items[3], text=', '.join(n.data))

        elif x >= n.x and y > n.y: # Otherwise, find correct quadrant
            n.NE = self.__insert(n.NE, x, y, d,
                                 (n.x, n.y, n.BBox[2], n.BBox[3]))
        elif x > n.x and y <=  n.y:
            n.SE = self.__insert(n.SE, x, y, d,
                                 (n.x, n.BBox[1], n.BBox[2], n.y))
        elif x <= n.x and y <  n.y:
            n.SW = self.__insert(n.SW, x, y, d,
                                 (n.BBox[0], n.BBox[1], n.x, n.y))
        else:
            n.NW = self.__insert(n.NW, x, y, d,
                                 (n.BBox[0], n.y, n.x, n.BBox[3]))

        self.cleanUp(callEnviron)
        return n

    def createPointItems(self, node, isRoot=False):
        R = self.CIRCLE_RADIUS
        ring = self.CIRCLE_RADIUS + 2
        nX, nY = self.canvasCoords(node.x, node.y)
        bbox = self.canvasBBox(node.BBox)
        items = (
            self.canvas.create_line(
                nX, bbox[1], nX, bbox[3],
                fill=self.LINE_COLOR, tags=('boundary', 'vertical')),
            self.canvas.create_line(
                bbox[0], nY, bbox[2], nY,
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
                nX - ring, nY - ring, nX + ring, nY + ring,
                outline=self.ROOT_OUTLINE, width=3),)
            self.canvas.tag_lower(items[-1])          

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
            for j in i.data:
                if label == j: return i

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
            self.insert(x, y, d, start=self.startMode())
            msg = "Point {} inserted".format(d)
            self.clearArguments()
        else:
            msg = val
        self.setMessage(msg)

    def changeBoundaryDisplay(self):
        self.canvas.itemConfig(
            'boundary', state=NORMAL if self.showBoundaries.get() else HIDDEN)
        
    #allows only numbers for coords that are within canvas size
    #everything aside from commas and spaces for data
    def validArgument(self):
        x, y, d = self.getArguments()
        msg = ''
        bbox = self.userBBox(self.pointRegion)
        if not (x.isdigit() and y.isdigit() and
                BBoxContains(bbox, (int(x), int(y)))):
            msg = "({}, {}) does not lie within {}".format(x, y, bbox)
            for argIndex in (0, 1):
                self.setArgumentHighlight(argIndex, self.ERROR_HIGHLIGHT)
        if not (0 < len(d) and len(d) <= self.maxArgWidth):
            if msg: msg += '\n'
            msg += 'Label must be between 1 and {} characters'.format(
                self.maxArgWidth)
            self.setArgumentHighlight(2, self.ERROR_HIGHLIGHT)
        if "," in d or " " in d:
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
        newQuadtree = self.addOperation(
            'New', lambda: self.new(), helpText='Create new, empty quadtree')
        showBoundariesCheckbutton = self.addOperation(
            'Show Boundaries',
            lambda: self.changeBoundaryDisplay(), buttonType=Checkbutton,
            variable=self.showBoundaries,
            helpText='Toggle display of quadrant boundaries')
        self.addAnimationButtons()
        return [self.insertButton, newQuadtree, showBoundariesCheckbutton]

if __name__ == '__main__':
    quadtree = PointQuadtree()
    quadtree.runVisualization()
