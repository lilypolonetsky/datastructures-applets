from tkinter import *

try:
    from tkUtilities import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .tkUtilities import *
    from .VisualizationApp import *

class Node(object):
    def __init__(self, x, y, d):
        self.x = x
        self.y = y
        self.data = [d] # might be more than one data at this coord
        self.dataObjects = [] #keeps track of text objects
        self.NE = self.SE = self.SW = self.NW = None
        self.countSpaces = 0
        #used for drawing intersecting lines
        self.horizontal_line = None
        self.vertical_line = None

class PointQuadtree(VisualizationApp):
    MAX_ARG_WIDTH = 4
    LINE_COLOR = 'SteelBlue4'
    TEXT_COLOR = 'red'
    ROOT_OUTLINE = 'yellow'
    TEXT_FONT = ("Helvetica", '10')
    CIRCLE_DIMEN = 8
    BUFFER_ZONE = (-10, -10, 50, 0)
    POINT_REGION_COLOR = 'LightSkyBlue1'

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
        self.direction = None #used in the draw lines function
        self.parent = None    #allows for creating coords of intersecting lines with recursion
        self.showTree = False
        self.rootOutline = None
        self.new()

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
        x, y = event.x, event.y
        self.setArguments(str(x), str(y))

    #creates new node in coordinates of double canvas mouse click
    #assigns a key according to node counter
    def createNode(self, event):
        x, y = event.x, event.y
        while self._findNodeLabeled('P{}'.format(self.COUNTER)):
            self.COUNTER += 1
        self.setArguments(str(x), str(y), 'P{}'.format(self.COUNTER))
        self.insertButton.invoke()

    #Assigns the designated graph-line coordinates to each node
    #If show graph checkbutton is clicked- draws the appropriate
    #horizontal and vertical lines
    def drawLine(self, n, parent, direction):
        if not self.direction:
            n.horizontal_line =2, n.y, self.canvas.winfo_width(), n.y
            n.vertical_line = n.x, 2, n.x, self.canvas.winfo_height()
            
        else:
            p_Hx0, p_Hy0, p_Hx1, p_Hy1 = parent.horizontal_line
            p_Vx0, p_Vy0, p_Vx1, p_Vy1 = parent.vertical_line
            S_vertical_line = n.x, parent.y, n.x, p_Vy1
            N_vertical_line = n.x, p_Vy0, n.x, parent.y
            W_horizontal_line = p_Hx0, n.y, parent.x, n.y
            E_horizontal_line = parent.x, n.y, p_Hx1 , n.y
            if self.direction == NE:
                n.horizontal_line = E_horizontal_line
                n.vertical_line = N_vertical_line
            elif self.direction== NW:
                n.horizontal_line = W_horizontal_line
                n.vertical_line = N_vertical_line
            elif self.direction == SW:
                n.horizontal_line = W_horizontal_line
                n.vertical_line = S_vertical_line
            elif self.direction == SE:
                n.horizontal_line = E_horizontal_line
                n.vertical_line = S_vertical_line
            self.direction = None
        if self.showTree == False: return
        return self.canvas.create_line(n.horizontal_line, fill = self.LINE_COLOR), self.canvas.create_line(n.vertical_line, fill = self.LINE_COLOR)

    #Switches the showTree attribute
    #deletes all the lines and root highlight if showTree is off
    #Otherwise draws all the lines at appropriate coordinates and the root highlight
    def graphLineDisplay(self):
        if self.showTree == True:
            self.showTree= False
            for i in self.lines: self.canvas.delete(i)
            self.lines = []
            self.canvas.delete(self.rootOutline)

        else:
            self.showTree= True
            for i in self.nodes:
                if i == self.__root:
                    self.rootOutline = self.canvas.create_oval((i.x - self.CIRCLE_DIMEN//2-2,
                                                                i.y- self.CIRCLE_DIMEN//2-2,
                                             i.x + self.CIRCLE_DIMEN//2+2,
                                             i.y + self.CIRCLE_DIMEN//2 +2),
                                            outline = self.ROOT_OUTLINE, width = 3)
                    self.canvas.lift(self.rootOutline)
                horiz = self.canvas.create_line(i.horizontal_line, fill = self.LINE_COLOR)
                vert = self.canvas.create_line(i.vertical_line, fill = self.LINE_COLOR)
                self.canvas.lower(horiz), self.canvas.lower(vert)
                self.lines.append(horiz), self.lines.append(vert)


    #wrapper method for insert
    def insert(self, x, y, d, start=True):
        callEnviron = self.createCallEnvironment(startAnimations=start)
        self.__root = self.__insert(self.__root, x, y, d)
        self.cleanUp(callEnviron)

    #creates a new node if none at designated coords
    #otherwise adds data to existing coordinate
    def __insert(self, n, x, y, d):
        callEnviron = self.createCallEnvironment()
        # return a new Node if we've reached None
        x = int(x)
        y = int(y)

        if not n:
            node = Node(x, y, d)
            self.nodes.append(node)
            node.countSpaces = 1


            if self.showTree == True:
                hor, ver = self.drawLine(node,self.parent, self.direction)
                self.lines.append(hor), self.lines.append(ver)
                if not self.__root: self.rootOutline = self.canvas.create_oval(
                (x - self.CIRCLE_DIMEN//2-2,
                y- self.CIRCLE_DIMEN//2-2, x + self.CIRCLE_DIMEN//2+2,
                y + self.CIRCLE_DIMEN//2 +2),
                outline = self.ROOT_OUTLINE, width = 3)

            else: self.drawLine(node,self.parent, self.direction)

            oval = self.canvas.create_oval(x - self.CIRCLE_DIMEN//2,
                                           y- self.CIRCLE_DIMEN//2,
                                           x + self.CIRCLE_DIMEN//2,
                                           y + self.CIRCLE_DIMEN//2, fill = "BLACK")
            text  = self.canvas.create_text(x-15, y - 12, text = d, fill = self.TEXT_COLOR, font = self.TEXT_FONT)
            self.points.append(oval)
            node.dataObjects = [text]

            self.COUNTER += 1 #keeps track of number of nodes inserted

            handler = lambda e: self.setArguments(str(x), str(y), str(d))
            self.canvas.tag_bind(oval, '<Button>', handler)

            self.cleanUp(callEnviron)
            return node

        # if the point to be inserted is identical to the current node,
        # add the data to the list of data, but don't recurse any further
        if n.x == x and n.y == y:
            n.data.append(d)
            key = d
            comma = self.canvas.create_text((x-3 + n.countSpaces), y - 12, fill = self.TEXT_COLOR,  text = ",", font = self.TEXT_FONT)
            n.countSpaces+= 25
            text  = self.canvas.create_text((x-15 + n.countSpaces), y - 12, fill = self.TEXT_COLOR,  text = key, font = self.TEXT_FONT)
            n.dataObjects.append(text), n.dataObjects.append(comma)
            self.COUNTER += 1
            self.cleanUp(callEnviron)
            return n


        # recurse down into the appropriate quadrant
        self.parent = n
        if   x >= n.x and y >= n.y:
            self.direction = SE
            n.SE = self.__insert(n.SE, x, y, d)
        elif x >= n.x and y <  n.y:
            self.direction = NE
            n.NE = self.__insert(n.NE, x, y, d)
        elif x <  n.x and y >= n.y:
            self.direction = SW
            n.SW = self.__insert(n.SW, x, y, d)
        else:
            self.direction = NW
            n.NW = self.__insert(n.NW, x, y, d)

        self.cleanUp(callEnviron)
        return n

    #clears canvas, and deletes all the nodes
    #with accompanying data and lines
    def new(self):
        self.canvas.delete('all')
        self.points = []
        self.lines= []
        self.nodes = []
        self.direction = None
        self.parent = None
        self.COUNTER = 0
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

    #allows only numbers for coords that are within canvas size
    #everything aside from commas and spaces for data
    def validArgument(self):
        x, y, d = self.getArguments()
        msg = ''
        if not (x.isdigit() and y.isdigit() and
                BBoxContains(self.pointRegion, (int(x), int(y)))):
            msg = "({}, {}) does not lie within {}".format(
                x, y, self.pointRegion)
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
            lambda: self.graphLineDisplay(), buttonType=Checkbutton,
            variable=self.showBoundaries,
            helpText='Toggle display of quadrant boundaries')
        self.addAnimationButtons()
        return [self.insertButton, newQuadtree, showBoundariesCheckbutton]

if __name__ == '__main__':
    quadtree = PointQuadtree()
    quadtree.runVisualization()
