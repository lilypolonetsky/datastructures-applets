from tkinter import *
import random

try:
    from coordinates import *
    from drawnValue import *
    from TableDisplay import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .coordinates import *
    from .drawnValue import *
    from .TableDisplay import *
    from .VisualizationApp import *

V = vector

class GraphBase(VisualizationApp):
    MAX_VERTICES = 14
    VERTEX_RADIUS = 18
    MAX_VERTEX_LABEL_WIDTH = 2
    vRadius = vector((VERTEX_RADIUS, VERTEX_RADIUS))
    VERTEX_FONT = ('Helvetica', -14)
    SELECTED_RADIUS = VERTEX_RADIUS * 6 // 5
    SELECTED_WIDTH = 2
    SELECTED_COLOR = 'white'
    SELECTED_OUTLINE = 'purple3'
    ADJACENCY_MATRIX_FONT = ('Helvetica', -12)
    ADJACENCY_MATRIX_BG = 'red3'
    GRAPH_REGION_BACKGROUND = 'old lace'
    MATRIX_CELL_WIDTH = 20
    ACTIVE_VERTEX_OUTLINE_COLOR = 'blue'
    ACTIVE_VERTEX_OUTLINE_WIDTH = 1
    EDGE_WIDTH = 1
    EDGE_COLOR = 'black'
    ACTIVE_EDGE_COLOR = 'blue'
    ACTIVE_EDGE_WIDTH = 3
    BAD_POSITION_TEXT_COLOR = 'red'
    DEFAULT_VERTEX_LABEL = 'A'
    nextColor = 0
    DEBUG = False
    
    def __init__(                    # Create a graph visualization application
            self, title="Graph", graphRegion=None, weighted=False, **kwargs):
        kwargs['title'] = title
        kwargs['maxArgWidth'] = self.MAX_VERTEX_LABEL_WIDTH
        if 'canvasBounds' not in kwargs:
            kwargs['canvasBounds'] = (0, 0, kwargs.get('canvasWidth', 800),
                                      kwargs.get('canvasHeight', 400))
        super().__init__(**kwargs)
        if graphRegion is None:
            graphRegion = V(self.canvasBounds) - V(-45, -30, 150, 100)
        self.graphRegion = graphRegion
        self.weighted = weighted
        self.weightValidate = (self.window.register(numericValidate),
                               '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.createAdjacencyMatrixPanel()
        self.buttons = self.makeButtons()
        self.newGraph()
        self.window.bind('<Configure>', self.reconfigureHandler())
        mapHandler = self.mapHandler()
        for event in ('<Map>', '<Unmap>'):
            self.window.bind(event, mapHandler)
    
    def __str__(self):
        verts = self.nVertices()
        edges = self.nEdges()
        return '<Graph of {} vert{} and {} {}edge{}>'.format(
            verts, 'ex' if verts == 1 else 'ices', edges,
            'bidirectional ' if self.bidirectionalEdges.get() else '',
            '' if edges == 1 else 's')

    def reconfigureHandler(self):
        def reconfigHandler(event):
            if event.widget == self.window:
                self.positionAdjacencyMatrix()
        return reconfigHandler

    def mapHandler(self):
        def map_handler(event):
            if event.widget == self.window:
                if event.type == EventType.Map:
                    self.adjacencyMatrixPanel.deiconify()
                    self.positionAdjacencyMatrix()
                elif event.type == EventType.Unmap:
                    self.adjacencyMatrixPanel.withdraw()
        return map_handler
    
    def nVertices(self):
        return len(self.vertices)

    def nEdges(self):
        return len(self.edges) // (2 if self.bidirectionalEdges.get() else 1)

    def createAdjacencyMatrixPanel(
            self, suffix=' Adjacency Matrix', anchor=SE):
        newTitle = self.title + suffix
        self.adjacencyMatrixPanel = Toplevel()
        self.adjacencyMatrixPanel.title(newTitle)
        self.adjMatControlBar = Frame(self.adjacencyMatrixPanel)
        self.adjMatControlBar.pack(side=TOP)
        panelTitle = Label(self.adjMatControlBar, text='Adjacency\nMatrix',
                           font=self.ADJACENCY_MATRIX_FONT)
        panelTitle.pack(side=LEFT)
        self.createAdjacencyMatrixControlImages()
        self.matrixExpose = Button(
            self.adjMatControlBar, image=self.adjMatControlImages['collapse'],
            command=self.toggleAdjacencyMatrixDisplay, takefocus=False,
            width=20)
        buttonImage(self.matrixExpose, self.adjMatControlImages['collapse'])
        self.matrixExpose.pack(side=LEFT, expand=False, fill=Y)
        self.buttonPadX = int(self.window.winfo_fpixels(
            self.matrixExpose['padx']))
        self.adjMatrixFrame = Frame(
            self.adjacencyMatrixPanel, bg=self.ADJACENCY_MATRIX_BG)
        self.adjMatrixFrame.pack(side=TOP, expand=FALSE, fill=None)

        self.adjacencyMatrixPanel.transient(self.window)
        self.adjacencyMatrixPanel.overrideredirect(True)
        if hasattr(self.window, 'title'):  # If top window is exposed
            self.positionAdjacencyMatrix(anchor=anchor)
        else:                              # otherwise hide until it is exposed
            self.adjacencyMatrixAnchor = anchor
            self.adjacencyMatrixPanel.withdraw()

    def createAdjacencyMatrixControlImages(self, height=None):
        if height is None:
            height = abs(self.CONTROLS_FONT[1])
        targetSize = (height, height)
        names = ('collapse', 'uncollapse')
        self.adjMatControlImages = dict(
            (name, getPhotoImage(name + '-symbol.png', targetSize))
            for name in names)
        return self.adjMatControlImages
            
    def toggleAdjacencyMatrixDisplay(self):
        if self.adjMatrixFrame in self.adjacencyMatrixPanel.pack_slaves():
            buttonImage(self.matrixExpose,
                        self.adjMatControlImages['uncollapse'])
            self.adjMatrixFrame.pack_forget()
        else:
            buttonImage(self.matrixExpose, self.adjMatControlImages['collapse'])
            self.adjMatrixFrame.pack(side=TOP, expand=FALSE, fill=None)
        self.positionAdjacencyMatrix()

    def positionAdjacencyMatrix(self, anchor=None):
        if anchor is None: anchor = self.adjacencyMatrixAnchor
        self.adjacencyMatrixAnchor = anchor
        self.window.update_idletasks()
        shown = (
            self.adjMatrixFrame
            if self.adjMatrixFrame in self.adjacencyMatrixPanel.pack_slaves()
            else self.adjMatControlBar)
        w, h = max(80, shown.winfo_reqwidth()), max(10, shown.winfo_reqheight())
        winW, winH, x0, y0 = widgetGeometry(self.window.winfo_toplevel())
        canW, canH = widgetDimensions(self.canvas)
        x = x0 + max(0, (0 if W in anchor else canW - w if E in anchor else
                         int(canW - w) // 2))
        y = y0 + max(0, (0 if N in anchor else canH - h if S in anchor else
                         int(canH - h) // 2))
        self.adjacencyMatrixPanel.wm_geometry('+{}+{}'.format(x, y))
        
    def newGraph(self):
        # The vertices hash maps vertex labels to the drawnValue representing
        # the vertex.  The drawnValue's val attribute is (label, ID) where
        # ID is unique integer ID used for the adjacency grid rows & columns
        self.vertices = {}

        # The adjMat hash maps vertex label pairs to the weight widget
        # in the adjacency matrix panel.  
        self.adjMat = {}

        # The edges hash maps vertex label pairs to the drawnValue representing
        # the arrow and text items in the canvas for the edge.  The drawnValue's
        # val attribute is the vertex label pair
        self.edges = {}

        for cell in self.adjMatrixFrame.grid_slaves():
            cell.grid_forget()
        self.adjMatrix00 = Frame(self.adjMatrixFrame, bg='white')
        self.adjMatrix00.grid(row=0, column=0, sticky=(N, E, S, W))
        self.selectedVertex = None
        self.dragItems = None
        self.nextID = 1
        self.display()
        self.setArgument(self.nextVertexLabel())
        
    def display(self):
        self.canvas.delete("all")
        self.graphRegionRectangle = self.canvas.create_rectangle(
            *self.graphRegion, fill=self.GRAPH_REGION_BACKGROUND, outline='')
        self.canvas.tag_bind(self.graphRegionRectangle, '<Double-Button-1>',
                             self.newVertexHandler())
        self.vertexTable = Table(
            self, (self.graphRegion[2] + 50, 40), label='_vertices',
            vertical=True, cellHeight=self.VERTEX_RADIUS, labelAnchor=SE,
            labelFont=(self.VARIABLE_FONT[0], -12),
            cellWidth=self.VERTEX_RADIUS * 3 // 2, cellBorderWidth=1)
        self.window.update_idletasks()
        
    def createVertexItems(
            self, label, coords=None, color=None, tags=('vertex',)):
        if label in self.vertices:
            raise ValueError('Cannot duplicate vertex labeled {}'.format(label))
        if not label:
            raise ValueError('Cannot create unlabeled vertex')
        visibleCanvas = self.visibleCanvas()
        border = V(1, 1, -1, -1) * self.SELECTED_RADIUS
        region = V(self.graphRegion) + V(border)
        while coords is None:
            x = random.randrange(region[0], region[2])
            y = random.randrange(region[1], region[3])
            if not self.badPosition((x, y)):
                coords = (x, y)
        if color is None:
            color = drawnValue.palette[self.nextColor]
            self.nextColor = (1 + self.nextColor) % len(drawnValue.palette)
        vr = V(self.VERTEX_RADIUS, self.VERTEX_RADIUS)
        shape = self.canvas.create_oval(
            *(V(coords) - self.vRadius), *(V(coords) + self.vRadius),
            tags=tags + ('shape', label), outline='', width=1, fill=color,
            activeoutline=self.ACTIVE_VERTEX_OUTLINE_COLOR,
            activewidth=self.ACTIVE_VERTEX_OUTLINE_WIDTH)
        text = self.canvas.create_text(
            *coords, text=label, tags=tags + ('text', label),
            font=self.VERTEX_FONT, fill=self.VALUE_COLOR,
            activefill=self.ACTIVE_VERTEX_OUTLINE_COLOR)
        if self.nEdges():
            self.canvas.tag_lower('vertex', 'edge')
        items = (shape, text)
        startMoveHandler = self.startMoveHandler(label)
        moveHandler = self.moveHandler(label)
        releaseHandler = self.releaseHandler(label)
        deleteHandler = self.deleteVertexHandler(label)
        for item in items:
            self.canvas.tag_bind(item, '<Button-1>', startMoveHandler)
            self.canvas.tag_bind(item, '<B1-Motion>', moveHandler)
            self.canvas.tag_bind(item, '<ButtonRelease-1>', releaseHandler)
            self.canvas.tag_bind(item, '<Double-Button-1>', deleteHandler)
        return items

    def createEdgeItems(self, base, tip, weight=0, tags=('edge',),
                        removeRadius=VERTEX_RADIUS, edgePair=None):
        p0, p1, p2, steps, weightCenter = self.edgeCoords(
            base, tip, removeRadius=removeRadius)
        line = self.canvas.create_line(
            *p0, *p1, *p2, width=self.EDGE_WIDTH, fill=self.EDGE_COLOR,
            arrow=None if self.bidirectionalEdges.get() else LAST,
            activefill=self.ACTIVE_EDGE_COLOR, tags=tags + ('line',),
            activewidth=self.ACTIVE_EDGE_WIDTH, splinesteps=steps, smooth=True)
        weightText = self.canvas.create_window(
            *weightCenter, state=HIDDEN if weight == 0 else NORMAL,
            tags=tags + ('weightWindow',),
            window=self.createEdgeWeightEntry(self.GRAPH_REGION_BACKGROUND,
                                              edgePair, weight, self.canvas)
        ) if self.weighted else self.canvas.create_text(
            *weightCenter,
            text='' if weight == 0 or not self.weighted else str(weight),
            font=self.VERTEX_FONT, fill=self.EDGE_COLOR, tags=tags + ('text',),
            activefill=self.ACTIVE_EDGE_COLOR)
        self.canvas.tag_lower(line, 'vertex')
        if edgePair:
            self.canvas.tag_bind(line, '<Double-Button-1>', 
                                 self.deleteEdgeHandler(edgePair))
        return (line, weightText)

    def edgeCoords(self, base, tip, removeRadius=VERTEX_RADIUS):
        midPoint = V(V(base) + V(tip)) / 2
        delta = V(tip) - V(base)
        offset = V(V(V(delta).rotate(-90)).unit()) * self.VERTEX_RADIUS
        inflection = midPoint if self.bidirectionalEdges.get() else V(
            midPoint) + V(offset)
        weightCenter = V(inflection) + V(offset)
        p0 = V(base) + V(V(V(V(inflection) - V(base)).unit()) * removeRadius)
        p1 = inflection
        p2 = V(tip) + V(V(V(V(inflection) - V(tip)).unit()) * removeRadius)
        steps = int(max(abs(delta[0]), abs(delta[1]), 5))
        return p0, p1, p2, steps, weightCenter

    def vertexCoords(self, vertexLabel):
        return self.canvas.coords(self.vertices[vertexLabel].items[1])
    
    def createLabeledArrow(
            self, vertexOrCoords, label, color=None, font=None,
            width=1, anchor=None, tags=('arrow',), **kwargs):
        if color is None: color = 'black'
        if font is None: font = self.VARIABLE_FONT
        coords = (self.labeledArrowCoords(vertexOrCoords, **kwargs)
                  if isinstance(vertexOrCoords, (int, str)) or
                  (isinstance(vertexOrCoords, (list, tuple)) and
                   len(vertexOrCoords) == 2 and
                   isinstance(vertexOrCoords[0], (int, float)))
                  else vertexOrCoords)
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
            self, vertexOrCoords, level=1, orientation=0, offset=5, **kwargs):
        center = (self.vertexCoords(vertexOrCoords)
                  if isinstance(vertexOrCoords, str) else
                  self.vertexCoords(self.vertexTable[vertexOrCoords].val)
                  if isinstance(vertexOrCoords, int) and 
                  vertexOrCoords < len(self.vertexTable) else
                  vertexOrCoords)
        Vrad = V(V(0, self.VERTEX_RADIUS + offset).rotate(orientation))
        tip = V(center) - Vrad
        Vdelta = V(
            V(0, abs(level) * abs(self.VARIABLE_FONT[1])).rotate(orientation))
        base = V(tip) - Vdelta
        return base + tip, base
       
    def startMoveHandler(self, vertexLabel):
        def startHandler(event):
            moveVertex = event.state & SHIFT
            if self.DEBUG:
                print('Entering startHandler {} "{}" #{}'.format(
                    'to move' if moveVertex else 'to add edge to',
                    vertexLabel, event.serial))
            if self.dragItems:
                if self.DEBUG:
                    print('Exiting startHandler #{} dragItems = {}"'.format(
                        event.serial, self.dragItems))
                return
            if self.operationMutex.locked():
                self.setMessage(
                    'Cannot {} vertex during other operation'.format(
                        'move' if moveVertex else 'add edge to'))
                return
            vert = self.vertices[vertexLabel]
            self.setMessage('')
            self.cleanUp()
            if moveVertex:
                copies = tuple(self.canvas.copyItem(i, includeBindings=False)
                               for i in vert.items + (vert.items[0],))
                self.canvas.itemConfig(
                    copies[-1], state=HIDDEN, fill='', width=2,
                    outline=self.BAD_POSITION_TEXT_COLOR)
                self.dragItems = copies
            else:
                self.selectVertex(vertexLabel)
                self.dragItems = self.createEdgeItems(
                    self.vertexCoords(vertexLabel), (event.x, event.y),
                    weight=0, removeRadius=0)
            self.lastPos = (event.x, event.y)
            self.enableButtons()
            if self.DEBUG:
                print('Finished startHandler on "{}" #{}'.format(
                    vertexLabel, event.serial))
        return startHandler

    def moveHandler(self, vertexLabel):
        def mvHandler(event):
            if self.DEBUG:
                print('Entering mvHandler on "{}" #{}'.format(
                    vertexLabel, event.serial))
            if not self.dragItems:
                if self.DEBUG:
                    print(('Exiting mvHandler #{} dragItems = {}"').format(
                        event.serial, self.dragItems))
                return
            self.enableButtons(False)
            delta = (event.x - self.lastPos[0], event.y - self.lastPos[1])
            self.lastPos = (event.x, event.y)
            dragItemType = self.canvas.type(self.dragItems[0])
            if dragItemType == 'oval':
                for item in self.dragItems:
                    self.canvas.move(item, *delta)

                newCenter = self.canvas.coords(self.dragItems[1])
                bad = self.badPosition(newCenter, ignore=(vertexLabel,))
                self.canvas.itemconfigure(
                    self.dragItems[0], state=HIDDEN if bad else NORMAL)
                self.canvas.itemconfigure(
                    self.dragItems[1], 
                    fill=self.BAD_POSITION_TEXT_COLOR if bad else self.VALUE_COLOR)
                self.canvas.itemconfigure(
                    self.dragItems[2], state=NORMAL if bad else HIDDEN)
                if not bad:
                    for orig, copy in zip(self.vertices[vertexLabel].items,
                                          self.dragItems[:2]):
                        self.canvas.coords(orig, self.canvas.coords(copy))
                    self.updateVertex(vertexLabel)
            elif dragItemType == 'line':
                p0, p1, p2, steps, wc = self.edgeCoords(
                    self.vertexCoords(vertexLabel), self.lastPos,
                    removeRadius=0)
                self.canvas.coords(self.dragItems[0], *p0, *p1, *p2)
                self.canvas.itemconfigure(self.dragItems[0], splinesteps=steps)
                self.canvas.coords(self.dragItems[1], *wc)
                toVert = self.findVertex(
                    self.lastPos, exclude=self.vertexPlusAdjacent(vertexLabel))
                if toVert:
                    self.canvas.itemconfigure(
                        self.vertices[toVert].items[0],
                        outline=self.ACTIVE_VERTEX_OUTLINE_COLOR)
                    self.canvas.itemconfigure(
                        self.vertices[toVert].items[1],
                        fill=self.ACTIVE_VERTEX_OUTLINE_COLOR)
                else:
                    self.restoreVertexAppearance()
            else:
                raise Exception('Dragging items of type {} not supported'.
                                format(dragItemType))
            if self.DEBUG:
                print('Finished mvHandler on "{}" #{}'.format(
                    vertexLabel, event.serial))
                    
        return mvHandler

    def restoreVertexAppearance(self, tags=('vertex',)):
        for tag in tags:
            for item in self.canvas.find_withtag(tag):
                if self.canvas.type(item) == 'oval':
                    self.canvas.itemconfigure(item, outline='', state=NORMAL)
                elif self.canvas.type(item) == 'text':
                    self.canvas.itemconfigure(item, fill=self.VALUE_COLOR, 
                                              state=NORMAL)

    def releaseHandler(self, vertexLabel):
        def relHandler(event):
            if self.DEBUG:
                print('Entering reHandler on "{}" #{}'.format(
                    vertexLabel, event.serial))
            if self.dragItems:
                dragItemType = self.canvas.type(self.dragItems[0])
                if dragItemType == 'oval':
                    newCenter = self.canvas.coords(self.dragItems[1])
                    bad = self.badPosition(newCenter, ignore=(vertexLabel,))
                    if bad:
                        if self.DEBUG:
                            print(('Release position is bad, '
                                   'ending #{}. Calling undoDrag').format(
                                       event.serial))
                        self.undoDrag(vertexLabel)
                    else:
                        delta = V(self.canvas.coords(self.dragItems[1])) - V(
                            self.vertexCoords(vertexLabel))
                        for item in self.vertices[vertexLabel].items:
                            self.canvas.move(item, *delta)
                        self.dispose({}, *self.dragItems)
                        self.dragItems = None
                        self.updateVertex(vertexLabel)
                        if self.DEBUG:
                            print('Finished release of vertex "{}"  #{}.'
                                  .format(vertexLabel, event.serial))
                elif dragItemType == 'line':
                    toVert = self.findVertex(
                        (event.x, event.y), 
                        exclude=self.vertexPlusAdjacent(vertexLabel))
                    self.restoreVertexAppearance()
                    if toVert:
                        if self.DEBUG:
                            print('Release new edge to "{}"  #{}.'.format(
                                toVert, event.serial))
                        self.dispose({}, *self.dragItems)
                        self.dragItems = None
                        self.createEdge(vertexLabel, toVert, 1)
                    else:
                        if self.DEBUG:
                            print(('Released edge connects "{}" to nothing, '
                                   'ending #{}. Calling undoDrag').format(
                                       vertexLabel, event.serial))
                        self.undoDrag(vertexLabel)
                else:
                    raise Exception('Dragging items of type {} not supported'.
                                    format(dragItemType))
            self.enableButtons(True)
        return relHandler

    def undoDrag(self, vertexLabel, after=None, endDistance=16, serial=0):
        if not self.dragItems:
            return
        dragItemType = self.canvas.type(self.dragItems[0])
        if self.DEBUG:
            print('Entered undoDrag #{} moving {} for vertex "{}" & after={}'
                  .format(serial, dragItemType, vertexLabel, after),
                  end=' ')
        if not (dragItemType in ('line', 'oval') and 
                vertexLabel in self.vertices):
            if self.dragItems:
                self.dispose({}, *self.dragItems)
            self.dragItems = None
            if self.DEBUG:
                print('Unexpected end to undoing {} drag #{} for vertex "{}".'
                      .format(dragItemType, serial, vertexLabel))
            return
        wait = 30
        if dragItemType == 'oval':
            oldCenter = self.vertexCoords(vertexLabel)
            center = self.canvas.coords(self.dragItems[1])
            delta = V(V(V(oldCenter) - V(center)) * 0.2)
            if self.DEBUG:
                print('delta**2 = {:3.1f}'.format(delta.len2()))
            if delta.len2() <= endDistance:
                for item in self.dragItems:
                    self.canvas.delete(item)
                self.dragItems = None
                if self.DEBUG:
                    print('Finished undoing {} drag #{}.'.format(
                        dragItemType, serial))
                if callable(after):
                    if self.DEBUG:
                        print('Calling after...')
                    after()
            else:
                for item in self.dragItems:
                    self.canvas.move(item, *delta)
                self.undoDragRequest = self.canvas.after(
                    wait, 
                    lambda: self.undoDrag(vertexLabel, after, endDistance, serial))
        elif dragItemType == 'line':
            edgeCoords = self.canvas.coords(self.dragItems[0])
            base, tip = edgeCoords[:2], edgeCoords[-2:]
            newTip = V(V(V(tip) * 8) + V(V(base) * 2)) / 10
            if self.DEBUG:
                print('distance**2 = {:3.1f}'.format(distance2(base, newTip)))
            if distance2(base, newTip) <= endDistance:
                for item in self.dragItems:
                    self.canvas.delete(item)
                self.dragItems = None
                if self.DEBUG:
                    print('Finished undoing {} drag #{}.'.format(
                        dragItemType, serial))
                if callable(after):
                    if self.DEBUG:
                        print('Calling after...')
                    after()
            else:
                p0, p1, p2, steps, wc = self.edgeCoords(
                    base, newTip, removeRadius=0)
                self.canvas.coords(self.dragItems[0], *p0, *p1, *p2)
                self.canvas.itemconfigure(self.dragItems[0], splinesteps=steps)
                self.canvas.coords(self.dragItems[1], *wc)
                if self.DEBUG:
                    print('Scheduling more undoing of {} drag #{} after {} ms.'
                          .format(dragItemType, serial, wait))
                self.undoDragRequest = self.canvas.after(
                    wait,
                    lambda: self.undoDrag(vertexLabel, after, endDistance, serial))

    def selectVertex(self, vertexLabel, tags='selected', checkMutex=True):
        if not (vertexLabel in self.vertices or vertexLabel is None):
            return
        if checkMutex:
            if not self.operationMutex.acquire(blocking=False):
                if vertexLabel != (self.selectedVertex[0]
                                   if self.selectedVertex else None):
                    self.setMessage(
                        'Cannot {}select vertex during operation'.format(
                            'de' if vertexLabel is None else ''))
                return
            self.cleanUp()
        Vradius = V((self.SELECTED_RADIUS, self.SELECTED_RADIUS))
        if self.selectedVertex:
            if vertexLabel is None:
                self.canvas.delete(self.selectedVertex[1])
                self.selectedVertex = None
            else:
                Vcenter = V(self.vertexCoords(vertexLabel))
                self.canvas.coords(self.selectedVertex[1],
                                   *(Vcenter - Vradius), *(Vcenter + Vradius))
                self.selectedVertex = (vertexLabel, self.selectedVertex[1])
        elif vertexLabel:
            Vcenter = V(self.canvas.coords(self.vertices[vertexLabel].items[1]))
            self.selectedVertex = (
                vertexLabel, 
                self.canvas.create_oval(
                    *(Vcenter - Vradius), *(Vcenter + Vradius),
                    fill=self.SELECTED_COLOR, outline=self.SELECTED_OUTLINE,
                    width=self.SELECTED_WIDTH, tags=tags))
            self.canvas.tag_lower(self.selectedVertex[1], 'vertex')
        if checkMutex and self.operationMutex.locked():
            self.operationMutex.release()
       
    def deleteVertexHandler(self, vertexLabel):
        def delVertHandler(event):
            if self.DEBUG:
                print('Entered delVertHandler for "{}" #{}.'.format(
                    vertexLabel, event.serial))
            if not (vertexLabel in self.vertices and self.dragItems):
                if self.DEBUG:
                    print(('Exit delVertHandler #{} on "{}" with '
                           'dragItems = {}')
                          .format(event.serial, vertexLabel, self.dragItems))
                return
            if self.deleteVertex(vertexLabel):
                self.setMessage('Deleted vertex {}'.format(vertexLabel))
            self.enableButtons()
            if self.DEBUG:
                print('Finished delVertHandler for "{}" #{}.'.format(
                    vertexLabel, event.serial))
        return delVertHandler

    def deleteEdgeHandler(self, edge):
        def delEdgeHandler(event):
            if self.DEBUG:
                print('Entered delEdgeHandler for {} #{}.'.format(
                    edge, event.serial))
            if not (edge in self.edges):
                if self.DEBUG:
                    print('Exit delEdgeHandler #{} on {}'
                          .format(event.serial, edge))
                return
            if self.deleteEdge(*edge):
                self.setMessage('Deleted edge {}'.format(edge))
            self.enableButtons()
            if self.DEBUG:
                print('Finished delEdgeHandler for {} #{}.'.format(
                    edge, event.serial))
        return delEdgeHandler
    
    def findVertex(self, point, exclude=()):
        for v in self.vertices:
            if v not in exclude:
                if (distance2(point, self.vertexCoords(v)) <=
                    self.VERTEX_RADIUS ** 2):
                    return v

    def vertexPlusAdjacent(self, vert):
        return (vert, *(v for v in self.vertices if self.edgeWeight(vert, v)))
        
    def newVertexHandler(self):
        def newVertHandler(event):
            if self.nVertices() < self.MAX_VERTICES:
                self.createVertex(self.getArgument(), 
                                  coords=(self.canvas.canvasx(event.x),
                                          self.canvas.canvasy(event.y)))
            else:
                self.setMessage('Maximum number of vertices = {}'.format(
                    self.MAX_VERTICES))
            self.enableButtons()
        return newVertHandler

    def badPosition(self, center, border=None, ignore=()):
        '''Check if a proposed vertex center would make it overlap other
        vertices or is outside the visible canvas minus a border or is
        on the line segment bewtween any pair of connected vertices.
        '''
        if border is None: border = self.VERTEX_RADIUS
        return (
            not BBoxContains(
                V(self.graphRegion) + V(V(1, 1, -1, -1) * border), center) or
            any(distance2(center, self.canvas.coords(v.items[1])) <
                (2 * self.SELECTED_RADIUS) ** 2 for v in self.vertices.values()
                if v.val[0] not in ignore) or
            (self.bidirectionalEdges.get() and
             any(collinearBetween(self.vertexCoords(self.vertexTable[j].val),
                                  center,
                                  self.vertexCoords(self.vertexTable[k].val),
                                  1e-4)
                 for j in range(len(self.vertexTable))
                 for k in range(j + 1, len(self.vertexTable))
                 if self.edgeWeight(self.vertexTable[j].val,
                                    self.vertexTable[k].val) > 0)))
    
    def createVertex(self, label, color=None, coords=None, tags=('vertex',)):
        if not self.operationMutex.acquire(blocking=False):
            self.setMessage('Cannot create vertex during other operation')
            return
        if self.nVertices() >= self.MAX_VERTICES:
            self.setMessage('Already have max Number of vertices {}'.format(
                self.MAX_VERTICES))
            if self.operationMutex.locked():
                self.operationMutex.release()
            return
        try:
            self.cleanUp()
            self.setMessage('')
            items = self.createVertexItems(
                label, color=color, coords=coords, tags=tags)
        except ValueError as e:
            self.setMessage(str(e))
            self.operationMutex.release()
            return
        newCenter = self.canvas.coords(items[1])
        if self.badPosition(newCenter):
            self.setMessage('Vertices must be visible and not overlap')
            self.dispose({}, *items)
            self.operationMutex.release()
            return
        
        vert = drawnValue((label, self.nextID), *items)
        self.vertices[label] = vert
        vertColor = self.canvas_itemConfig(items[0], 'fill')

        self.vertexTable.append(
            drawnValue(label,
                       self.canvas.create_rectangle(
                           *self.vertexTable.cellCoords(len(self.vertexTable)),
                           fill=vertColor, outline='', width=1,
                           tags='vertexTableItem'),
                       self.canvas.create_text(
                           *self.vertexTable.cellCenter(len(self.vertexTable)),
                           text=label, font=self.ADJACENCY_MATRIX_FONT,
                           fill=self.VALUE_COLOR, tags='vertexTableItem')))
        for item in self.vertexTable[-1].items:
            self.canvas.tag_bind(item, '<Button-1>',
                                 lambda e: self.setArgument(label))

        columnLabel = Label(
            self.adjMatrixFrame, text=label, bg=vertColor,
            font=self.ADJACENCY_MATRIX_FONT)
        columnLabel.grid(row=0, column=self.nextID, sticky=(N, E, S, W))
        rowLabel = Label(
            self.adjMatrixFrame, text=label, bg=vertColor,
            font=self.ADJACENCY_MATRIX_FONT)
        rowLabel.grid(row=self.nextID, column=0, sticky=(N, E, S, W))
        maxWidth = textWidth(self.ADJACENCY_MATRIX_FONT, label)
        columnIDs = [vert.val[1]]
        for otherVert in self.vertices.values():
            if vert == otherVert:
                frame = Frame(self.adjMatrixFrame, bg=vertColor)
                frame.grid(row=self.nextID, column=self.nextID, 
                               sticky=(N, E, S, W))
            else:
                otherVertColor = self.canvas_itemConfig(otherVert.items[0], 
                                                        'fill')
                entry = self.createEdgeWeightEntry(
                    vertColor, (vert.val[0], otherVert.val[0]), None)
                entry.grid(row=self.nextID, column=otherVert.val[1], 
                           sticky=(N, E, S, W))
                self.adjMat[vert.val[0], otherVert.val[0]] = [0, entry]
                entry = self.createEdgeWeightEntry(
                    otherVertColor, (otherVert.val[0], vert.val[0]), None)
                entry.grid(row=otherVert.val[1], column=self.nextID,
                           sticky=(N, E, S, W))
                self.adjMat[otherVert.val[0], vert.val[0]] = [0, entry]
                maxWidth = max(maxWidth, textWidth(self.ADJACENCY_MATRIX_FONT,
                                                   otherVert.val[0]))
                columnIDs.append(otherVert.val[1])
        self.nextID += 1
        self.setArgument(self.nextVertexLabel())
        for ID in columnIDs:
            self.adjMatrixFrame.columnconfigure(
                ID, minsize=maxWidth + self.buttonPadX)
        self.positionAdjacencyMatrix()
        self.operationMutex.release()
        return True

    def deleteVertex(self, vertexLabel):
        if not vertexLabel in self.vertices:
            raise ValueError('Cannot update non-existant vertex {}'.format(
                vertexLabel))
        if not self.operationMutex.acquire(blocking=False):
            self.setMessage('Cannot delete vertex during other operation')
            return
        self.cleanUp()
        if self.selectedVertex and self.selectedVertex[0] == vertexLabel:
            self.selectVertex(None, checkMutex=False)
        for edge in self.findEdges(vertexLabel):
            self.edgeWeight(*edge, 0)
        vertex = self.vertices[vertexLabel]
        ID = vertex.val[1]
        self.adjMatrixFrame.columnconfigure(ID, minsize=0)
        adjMatrixWidgets = gridDict(self.adjMatrixFrame)
        for row, column in adjMatrixWidgets:
            if row == ID or (column == ID and row != ID):
                adjMatrixWidgets[row, column].grid_forget()
        tableIndex = self.getVertexIndex(vertexLabel)
        self.dispose({}, *vertex.items, *self.vertexTable[tableIndex].items)
        del self.vertexTable[tableIndex]
        for dValue in self.vertexTable[tableIndex:]:
            for item in dValue.items:
                self.canvas.move(item, 0, - self.vertexTable.cellHeight)
        del self.vertices[vertexLabel]
        self.positionAdjacencyMatrix()
        self.operationMutex.release()
        return True

    def deleteEdge(self, fromVert, toVert):
        if not self.operationMutex.acquire(blocking=False):
            self.setMessage('Cannot delete edge during other operation')
            return
        self.cleanUp()
        self.edgeWeight(fromVert, toVert, 0)        
        self.operationMutex.release()
        return True
    
    def getVertexIndex(self, label):
        return [dv.val for dv in self.vertexTable].index(label)

    def createEdgeWeightEntry(self, color, edge, weight=None, parent=None):
        if self.weighted:
            entry = Entry(parent or self.adjMatrixFrame, bg=color,
                          font=self.ADJACENCY_MATRIX_FONT, width=2,
                          state=NORMAL,
                          takefocus=False, validate='key', 
                          validatecommand=self.weightValidate)
            self.weight(entry, weight)
            def edgeWeightChange(event):
                if not (isinstance(edge, tuple) and len(edge) == 2):
                    if self.DEBUG:
                        print('Attempt to change weight of empty edge')
                    return
                if not self.operationMutex.acquire(blocking=False):
                    self.setMessage('Cannot change edge during other operation')
                    self.weight(entry, self.edgeWeight(*edge))
                    return
                self.cleanUp()
                self.edgeWeight(*edge, self.weight(entry))
                self.operationMutex.release()
                self.enableButtons()
            entry.bind('<KeyRelease>', edgeWeightChange)
        else:
            entry = Button(self.adjMatrixFrame, bg=color,
                           text='', font=self.ADJACENCY_MATRIX_FONT,
                           state=NORMAL, takefocus=False)
            def toggleEdge():
                if not self.operationMutex.acquire(blocking=False):
                    self.setMessage('Cannot change edge during other operation')
                    return
                self.cleanUp()
                self.edgeWeight(*edge, 0 if entry['text'] else 1)
                self.operationMutex.release()
                self.enableButtons()
            entry['command'] = toggleEdge
            
        return entry

    def weight(self, weightEntry, newWeight=None):
        'Get or set the weight in a weight entry widget'
        if isinstance(weightEntry, str):
            try:
                weightEntry = self.window.nametowidget(weightEntry)
            except KeyError:
                raise ValueError('String "{}" is not a recognized widget'.
                                 format(weightEntry))
        if isinstance(weightEntry, Entry):
            text = weightEntry.get() 
            if newWeight is None:
                return int(text) if text else 0
            if (newWeight > 0 and str(newWeight) != text) or text != '':
                state = weightEntry['state']
                weightEntry['state'] = NORMAL
                weightEntry.delete(0, END)
                if newWeight:
                    weightEntry.insert(0, str(newWeight))
                weightEntry['state'] = state
        elif isinstance(weightEntry, Button):
            text = weightEntry['text']
            if newWeight is None:
                return int(text) if text else 0
            if (newWeight > 0 and str(newWeight) != text) or text != '':
                weightEntry['text'] = '' if newWeight == 0 else str(newWeight)
        else:
            raise ValueError('Cannot set weight in widget of type {}'.format(
                type(weightEntry)))
                
    def updateVertex(self, vertexLabel):
        if not vertexLabel in self.vertices:
            raise ValueError('Cannot update non-existant vertex {}'.format(
                vertexLabel))
        for edge in self.findEdges(vertexLabel):
            items = self.edges[edge].items
            p0, p1, p2, steps, wc = self.edgeCoords(
                self.vertexCoords(edge[0]), self.vertexCoords(edge[1]))
            self.canvas.coords(items[0], *p0, *p1, *p2)
            self.canvas.itemConfig(items[0], splinesteps=steps)
            self.canvas.coords(items[1], *wc)
        if self.selectedVertex and vertexLabel == self.selectedVertex[0]:
            self.selectVertex(vertexLabel, checkMutex=False)

    def findEdges(self, vertex, inbound=True, outbound=True, unique=None):
        '''Find edges incident to a vertex, possibly filtering by direction.
        Return only correctly oriented edge if unique is specified which
        defaults to state of bidirectionalEdges.
        '''
        if unique is None: unique = self.bidirectionalEdges.get()
        return [
            edge for edge in self.edges if
            (inbound and edge[1] == vertex or outbound and edge[0] == vertex)
            and (not unique or self.edges[edge].val == edge)]

    def edgeWeight(self, fromVert, toVert, weight=None):
        'Get or set the weight of the edge from one vertex to another'
        if fromVert == toVert:  # Cannot have edge with same vertex at both ends
            if weight is None:
                return 0
            return
        edge = (fromVert, toVert)
        revEdge = (toVert, fromVert)
        edges = (edge, revEdge) if (
            self.bidirectionalEdges.get() and weight is not None) else (edge,)
        for ed in edges:
            if ed not in self.adjMat and (weight is None or weight == 0):
                raise Exception('Missing adjacency matrix entry {}->{}'.format(
                    *ed))
            self.weight(self.adjMat[ed][1], weight)  # Set weight in adj matrix
        if weight is None:   # When no weight provided, return existing weight
            return self.adjMat[edge][0]

        if weight > 0:         # For new/updated edges, update canvas display
            if edge not in self.edges:
                self.createEdge(fromVert, toVert, weight, checkMutex=False)
            elif self.weighted:
                self.weight(self.canvas.itemConfig(self.edges[edge].items[1],
                                                   'window'),
                            weight)
        else:                  # weight == 0 means edge is deleted
            if edge in self.edges:
                self.dispose({}, *self.edges[edge].items)
                del self.edges[edge]
            if self.bidirectionalEdges.get() and revEdge in self.edges:
                self.dispose({}, *self.edges[revEdge].items)
                del self.edges[revEdge]
        self.positionAdjacencyMatrix()
        self.adjMat[edge][0] = weight
        if self.bidirectionalEdges.get():                    
            self.adjMat[revEdge][0] = weight
            
    def createEdge(
            self, fromVert, toVert, weight=1, tags=('edge',), checkMutex=True):
        edgeKey = (fromVert, toVert)
        if fromVert == toVert or edgeKey in self.edges and isinstance(
                self.edge[edgeKey], drawnValue):
            return
        centers = tuple(self.vertexCoords(v) for v in edgeKey)
        if checkMutex and not self.operationMutex.acquire(blocking=False):
            self.setMessage('Cannot create edge during other operation')
            return
        self.cleanUp()
        self.edges[edgeKey] = drawnValue(
            edgeKey, *self.createEdgeItems(
                centers[0], centers[1], weight=weight, tags=tags,
                edgePair=edgeKey))
        if self.bidirectionalEdges.get():
            self.edges[toVert, fromVert] = self.edges[edgeKey]
        self.edgeWeight(fromVert, toVert, weight)
        if checkMutex and self.operationMutex.locked():
            self.operationMutex.release()
        return True

    def nextVertexLabel(self, label=None):
        if label is None:
            label = self.getArgument()
        if label == '':
            label = self.DEFAULT_VERTEX_LABEL
        while label in self.vertices:
            previous = label
            if label.isalpha():
                for i in range(len(label) - 1, -1, -1):
                    nextAlpha = chr(ord(label[i]) + 1)
                    if nextAlpha.isalpha():
                        label = label[:i] + nextAlpha + (
                            'a' if nextAlpha.islower() else 'A') * (
                                len(label) - 1 - i)
                        break
                if previous == label:
                    if len(label) == self.maxArgWidth:
                        return ''
                    lower = label[0].islower()
                    label = ('a' if lower else 'A') * (len(label) + 1)
            elif label.isdigit():
                fmt = '{{:0{}d}}'.format(len(label))
                label = fmt.format(int(label) + 1)
                if len(label) > self.maxArgWidth:
                    return ''
            else:
                label = ''
        return label
            
    def makeButtons(self, bidirectional=None):
        '''Make buttons common to weighted and unweighted graphs without
        the animation control buttons.  If bidirectional is None, a button
        to control the kind of edges is created, ottherwise, the kind of
        edges is set to the truth value provided'''
        vcmd = (self.window.register(
            makeFilterValidate(self.maxArgWidth)), '%P')
        self.newVertexButton = self.addOperation(
            "New Vertex", self.clickNewVertex, numArguments=1, mutex=False,
            validationCmd=vcmd, argHelpText=['vertex label'], 
            helpText='Create a new vertex with a label')
        self.randomFillButton = self.addOperation(
            "Random Fill", self.clickRandomFill, numArguments=1, mutex=False,
            validationCmd=vcmd, argHelpText=['# vertices'], 
            helpText='Fill with N random vertices')
        self.deleteVertexButton = self.addOperation(
            "Delete Vertex", self.clickDeleteVertex, numArguments=1,
            validationCmd=vcmd, argHelpText=['vertex label'], mutex=False, 
            helpText='Delete the labeled vertex')
        self.newGraphButton = self.addOperation(
            "New Graph", self.clickNewGraph,
            helpText='Create new, empty graph')
        self.bidirectionalEdges = IntVar()
        self.bidirectionalEdges.set(
            1 if bidirectional is None or bidirectional else 0)
        self.bidirectionalEdgesButton = self.addOperation(
            "Bidirectional", self.clickBidirectionalEdges,
            buttonType=Checkbutton, variable=self.bidirectionalEdges, 
            helpText='Use bidirectional edges') if bidirectional is None else None
        return vcmd

    def validArgument(self):
        text = self.getArgument()
        return text

    def enableButtons(self, enable=True):
        super().enableButtons(enable)
        if self.bidirectionalEdgesButton: # Bidirectional edge status
            widgetState(                  # can only change without edges
                self.bidirectionalEdgesButton,
                NORMAL if enable and self.nEdges() == 0 else DISABLED)
        for btn in (self.newVertexButton, self.randomFillButton):
            widgetState(
                btn,
                NORMAL if enable and self.nVertices() < self.MAX_VERTICES and
                self.getArgument(0) else DISABLED)
        widgetState(
            self.deleteVertexButton,
            NORMAL if enable and self.nVertices() > 0 and
            self.getArgument(0) else DISABLED)
    
    # Button functions
    def clickNewVertex(self):
        val = self.validArgument()
        if val in self.vertices:
            self.setMessage('Cannot duplicate vertex {}'.format(val))
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
            return
        if not self.createVertex(val):
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
    
    def clickDeleteVertex(self):
        val = self.validArgument()
        if val not in self.vertices:
            self.setMessage('No vertex labeled {}'.format(val))
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
            return
        self.deleteVertex(val)
        self.clearArgument()

    def clickNewGraph(self):
        self.newGraph()
    
    def clickBidirectionalEdges(self):
        return

    def randomFill(self, nVertices):
        maxLabel = (self.DEFAULT_VERTEX_LABEL if len(self.vertices) == 0 else
                    self.nextVertexLabel(max(v for v in self.vertices)))
        for n in range(min(nVertices, self.MAX_VERTICES - self.nVertices())):
            if not self.createVertex(maxLabel):
                break
            maxLabel = self.nextVertexLabel(maxLabel)
        
    def clickRandomFill(self):
        val = self.validArgument()
        if (val and val.isdigit() and
            int(val) <= self.MAX_VERTICES - self.nVertices()):
            self.randomFill(int(val))
        elif self.MAX_VERTICES <= self.nVertices():
            self.setMessage('Already have max Number of vertices {}'.format(
                self.MAX_VERTICES))
        else:
            self.setMessage('Number of vertices must be {} or less'.format(
                self.MAX_VERTICES - self.nVertices()))
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)

if __name__ == '__main__':
    graph = GraphBase(weighted=any(':' in arg for arg in sys.argv[1:]))
    edgePattern = re.compile(r'(\w+)-(\w+)(:([1-9][0-9]?))?')

    edges = []
    for arg in sys.argv[1:]:
        edgeMatch = edgePattern.fullmatch(arg)
        if len(arg) > 1 and arg[0] == '-':
            if arg == '-d':
                graph.DEBUG = True
            elif arg == '-b':
                graph.bidirectionalEdges.set(1)
            elif arg == '-B':
                graph.bidirectionalEdges.set(0)
            elif arg[1:].isdigit():
                graph.setArgument(arg[1:])
                graph.randomFillButton.invoke()
                graph.setArgument(
                    chr(ord(graph.DEFAULT_VERTEX_LABEL) + int(arg[1:])))
        elif edgeMatch and all(edgeMatch.group(i) in sys.argv[1:] 
                               for i in (1, 2)):
            edges.append((edgeMatch.group(1), edgeMatch.group(2),
                          int(edgeMatch.group(4)) if edgeMatch.group(4) else 1))
        else:
            graph.setArgument(arg)
            graph.newVertexButton.invoke()
    for fromVert, toVert, weight in edges:
        graph.createEdge(fromVert, toVert, weight)
        
    graph.runVisualization()
