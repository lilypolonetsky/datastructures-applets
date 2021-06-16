from tkinter import *
import random

try:
    from VisualizationApp import *
    from coordinates import *
    from drawnValue import *
except ModuleNotFoundError:
    from .VisualizationApp import *
    from .coordinates import *
    from .drawnValue import *

V = vector

class Graph(VisualizationApp):
    MAX_VERTICES = 16
    VERTEX_RADIUS = 18
    vRadius = vector((VERTEX_RADIUS, VERTEX_RADIUS))
    VERTEX_FONT = ('Helvetica', -14)
    SELECTED_RADIUS = VERTEX_RADIUS * 6 // 5
    SELECTED_WIDTH = 2
    SELECTED_COLOR = 'white'
    SELECTED_OUTLINE = 'purple3'
    ADJACENCY_MATRIX_FONT = ('Helvetica', -12)
    ADJACENCY_MATRIX_BG = 'bisque'
    CANVAS_EXTERIOR = 'cyan'
    MATRIX_CELL_WIDTH = 20
    ACTIVE_VERTEX_OUTLINE_COLOR = 'blue'
    ACTIVE_VERTEX_OUTLINE_WIDTH = 1
    EDGE_COLOR = 'black'
    ACTIVE_EDGE_COLOR = 'blue'
    ACTIVE_EDGE_WIDTH = 3
    BAD_POSITION_TEXT_COLOR = 'red'
    DEFAULT_VERTEX_LABEL = 'A'
    nextColor = 0
    DEBUG = False
    
    def __init__(                    # Create a graph visualization application
            self, title="Graph", weighted=False, **kwargs):
        kwargs['title'] = title
        if 'canvasBounds' not in kwargs:
            kwargs['canvasBounds'] = (0, 0, kwargs.get('canvasWidth', 800),
                                      kwargs.get('canvasHeight', 400))
        super().__init__(**kwargs)
        self.weighted = weighted
        self.weightValidate = (self.window.register(numericValidate),
                               '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.buttons = self.makeButtons()
        self.createAdjacencyMatrixPanel()
        self.newGraph()
        self.canvas.bind('<Double-Button-1>', self.newVertexHandler(), add='+')
    
    def __str__(self):
        verts = self.nVertices()
        edges = self.nEdges()
        return '<Graph of {} vert{} and {} {}edge{}>'.format(
            verts, 'ex' if verts == 1 else 'ices', edges,
            'bidirectional ' if self.bidirectionalEdges.get() else '',
            '' if edges == 1 else 's')

    def nVerticess(self):
        return len(self.vertices)

    def nEdges(self):
        return len(self.edges) // (2 if self.bidirectionalEdges.get() else 1)

    def createAdjacencyMatrixPanel(self):
        self.canvasFrame['bg'] = self.CANVAS_EXTERIOR
        self.adjacencyMatrixPanel = Frame(
            self.canvasFrame, bg=self.ADJACENCY_MATRIX_BG)
        self.adjacencyMatrixPanel.pack(
            side=RIGHT, before=self.canvasVScroll, expand=False, fill=Y)
        controlbar = Frame(self.adjacencyMatrixPanel)
        controlbar.pack(side=TOP)
        panelTitle = Label(controlbar, text='Adjacency\nMatrix',
                           font=self.ADJACENCY_MATRIX_FONT)
        panelTitle.pack(side=LEFT)
        self.matrixExpose = Button(
            controlbar, text='X', font=self.ADJACENCY_MATRIX_FONT, 
            command=self.toggleAdjacencyMatrixDisplay)
        self.matrixExpose.pack(side=LEFT, expand=False, fill=Y)
        self.adjMatrixFrame = Frame(
            self.adjacencyMatrixPanel, bg=self.ADJACENCY_MATRIX_BG)
        self.adjMatrixFrame.pack(side=TOP, expand=FALSE, fill=None)

    def toggleAdjacencyMatrixDisplay(self):
        if self.adjMatrixFrame in self.adjacencyMatrixPanel.pack_slaves():
            self.matrixExpose['text'] = '+'
            self.adjMatrixFrame.pack_forget()
        else:
            self.matrixExpose['text'] = 'X'
            self.adjMatrixFrame.pack(side=TOP, expand=FALSE, fill=None)
        
    def newGraph(self):
        self.allowUserMoves = False
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
        self.selectedVertex = None
        self.dragItems = None
        self.nextID = 1
        self.display()
        self.setArgument(self.nextVertexLabel())
        
    def display(self):
        self.canvas.delete("all")
        self.allowUserMoves = True
        self.window.update()
        
    def createVertexItems(
            self, label, coords=None, color=None, tags=('vertex',)):
        if label in self.vertices:
            raise ValueError('Cannot duplicate vertex labeled {}'.format(label))
        if not label:
            raise ValueError('Cannot create unlabeled vertex')
        visibleCanvas = self.visibleCanvas()
        vr = V(self.SELECTED_RADIUS, self.SELECTED_RADIUS)
        region = (V(visibleCanvas[:2]) + vr) + (V(visibleCanvas[2:]) - vr)
        while coords is None:
            x = random.randrange(region[0], region[2])
            y = random.randrange(region[1], region[3])
            if all(distance2((x, y), self.canvas_coords(v.items[1])) >=
                   (2 * self.SELECTED_RADIUS) ** 2
                   for v in self.vertices.values()):
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
        self.canvas.tag_lower('vertex', 'edge')
        items = (shape, text)
        startMoveHandler = self.startMoveHandler(label)
        moveHandler = self.moveHandler(label)
        releaseHandler = self.releaseHandler(label)
        deleteHandler = self.deleteHandler(label)
        for item in items:
            self.canvas.tag_bind(item, '<Button-1>', startMoveHandler)
            self.canvas.tag_bind(item, '<B1-Motion>', moveHandler)
            self.canvas.tag_bind(item, '<ButtonRelease-1>', releaseHandler)
            self.canvas.tag_bind(item, '<Double-Button-1>', deleteHandler)
        return items

    def createEdgeItems(self, base, tip, weight=0, tags=('edge',),
                        removeRadius=VERTEX_RADIUS):
        p0, p1, p2, steps, weightCenter = self.edgeCoords(
            base, tip, removeRadius=removeRadius)
        line = self.canvas.create_line(
            *p0, *p1, *p2, width=1, fill=self.EDGE_COLOR,
            arrow=None if self.bidirectionalEdges.get() else LAST,
            activefill=self.ACTIVE_EDGE_COLOR, tags=tags + ('line',),
            activewidth=self.ACTIVE_EDGE_WIDTH, splinesteps=steps, smooth=True)
        weightText = self.canvas.create_text(
            *weightCenter,
            text='' if weight == 0 or not self.weighted else str(weight),
            font=self.VERTEX_FONT, fill=self.EDGE_COLOR, tags=tags + ('text',),
            activefill=self.ACTIVE_EDGE_COLOR)
        return (line, weightText)

    def edgeCoords(self, base, tip, removeRadius=VERTEX_RADIUS):
        midPoint = V(V(base) + V(tip)) / 2
        delta = V(tip) - V(base)
        offset = V(V(V(delta).rotate(-90)).unit()) * self.VERTEX_RADIUS
        inflection = midPoint if self.bidirectionalEdges.get() else V(
            midPoint) + V(offset)
        weightCenter = V(inflection) + V(V(offset) * 0.5)
        p0 = V(base) + V(V(V(V(inflection) - V(base)).unit()) * removeRadius)
        p1 = inflection
        p2 = V(tip) + V(V(V(V(inflection) - V(tip)).unit()) * removeRadius)
        steps = int(max(abs(delta[0]), abs(delta[1]), 5))
        return p0, p1, p2, steps, weightCenter
       
    def startMoveHandler(self, vertexLabel):
        def startHandler(event):
            if self.DEBUG:
                print('Entering startHandler on "{}" #{}'.format(
                    vertexLabel, event.serial))
            if not self.allowUserMoves or self.dragItems:
                if self.DEBUG:
                    print('Exiting startHandler #{} allowUserMoves = {} dragItems = {}"'.format(event.serial, self.allowUserMoves, self.dragItems))
                return
            self.enableButtons(False)
            vert = self.vertices[vertexLabel]
            self.setMessage('')
            moveVertex = event.state & SHIFT
            if moveVertex:
                copies = tuple(self.copyCanvasItem(i, includeBindings=False)
                               for i in vert.items)
                self.dragItems = copies
            else:
                self.selectVertex(vertexLabel)
                self.dragItems = self.createEdgeItems(
                    self.canvas_coords(vert.items[1]), (event.x, event.y),
                    weight=0, removeRadius=0)
            self.lastPos = (event.x, event.y)
            if self.DEBUG:
                print('Finished startHandler on "{}" #{}'.format(
                    vertexLabel, event.serial))
        return startHandler

    def moveHandler(self, vertexLabel):
        def mvHandler(event):
            if self.DEBUG:
                print('Entering mvHandler on "{}" #{}'.format(
                    vertexLabel, event.serial))
            if not (self.allowUserMoves and self.dragItems):
                if self.DEBUG:
                    print(('Exiting mvHandler #{} allowUserMoves = {} '
                           'dragItems = {}"').format(
                               event.serial, self.allowUserMoves,
                               self.dragItems))
                return
            self.enableButtons(False)
            delta = (event.x - self.lastPos[0], event.y - self.lastPos[1])
            self.lastPos = (event.x, event.y)
            dragItemType = self.canvas.type(self.dragItems[0])
            if dragItemType == 'oval':
                for item in self.dragItems:
                    self.canvas.move(item, *delta)

                newCenter = self.canvas_coords(self.dragItems[1])
                bad = self.badPosition(newCenter)
                self.canvas.itemconfigure(
                    self.dragItems[0], state=HIDDEN if bad else NORMAL)
                self.canvas.itemconfigure(
                    self.dragItems[1], 
                    fill=self.BAD_POSITION_TEXT_COLOR if bad else self.VALUE_COLOR)
            elif dragItemType == 'line':
                vert = self.vertices[vertexLabel]
                p0, p1, p2, steps, wc = self.edgeCoords(
                    self.canvas_coords(vert.items[1]), self.lastPos,
                    removeRadius=0)
                self.canvas.coords(self.dragItems[0], *p0, *p1, *p2)
                self.canvas.itemconfigure(self.dragItems[0], splinesteps=steps)
                self.canvas.coords(self.dragItems[1], *wc)
                toVert = self.findVertex(self.lastPos, 
                                         exclude=(vertexLabel,))
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
                    newCenter = self.canvas_coords(self.dragItems[1])
                    bad = self.badPosition(newCenter)
                    if bad:
                        if self.DEBUG:
                            print(('Release position is bad, '
                                   'ending #{}. Calling undoDrag').format(
                                       event.serial))
                        self.undoDrag(vertexLabel)
                    else:
                        delta = V(self.canvas_coords(self.dragItems[1])) - V(
                            self.canvas_coords(
                                self.vertices[vertexLabel].items[1]))
                        for item in self.vertices[vertexLabel].items:
                            self.canvas.move(item, *delta)
                        self.dispose({}, *self.dragItems)
                        self.dragItems = None
                        self.updateVertex(vertexLabel)
                        if self.DEBUG:
                            print('Finished release of vertex "{}"  #{}.'
                                  .format(vertexLabel, event.serial))
                elif dragItemType == 'line':
                    toVert = self.findVertex((event.x, event.y), 
                                             exclude=(vertexLabel,))
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
        self.allowUserMoves = False
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
            self.allowUserMoves = True
            if self.DEBUG:
                print('Unexpected end to undoing {} drag #{} for vertex "{}".'
                      .format(dragItemType, serial, vertexLabel))
            return
        wait = 30
        if dragItemType == 'oval':
            oldCenter = self.canvas_coords(
                self.vertices[vertexLabel].items[1])
            center = self.canvas_coords(self.dragItems[1])
            delta = V(V(V(oldCenter) - V(center)) * 0.2)
            if self.DEBUG:
                print('delta**2 = {:3.1f}'.format(delta.len2()))
            if delta.len2() <= endDistance:
                for item in self.dragItems:
                    self.canvas.delete(item)
                self.dragItems = None
                self.allowUserMoves = True
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
            edgeCoords = self.canvas_coords(self.dragItems[0])
            base, tip = edgeCoords[:2], edgeCoords[-2:]
            newTip = V(V(V(tip) * 8) + V(V(base) * 2)) / 10
            if self.DEBUG:
                print('distance**2 = {:3.1f}'.format(distance2(base, newTip)))
            if distance2(base, newTip) <= endDistance:
                for item in self.dragItems:
                    self.canvas.delete(item)
                self.dragItems = None
                self.allowUserMoves = True
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

    def selectVertex(self, vertexLabel, tags='selected'):
        if not (vertexLabel in self.vertices or vertexLabel is None):
            return
        radius = V((self.SELECTED_RADIUS, self.SELECTED_RADIUS))
        if self.selectedVertex:
            if vertexLabel is None:
                self.canvas.delete(self.selectedVertex[1])
                self.selectedVertex = None
            else:
                center = V(self.canvas.coords(
                    self.vertices[vertexLabel].items[1]))
                self.canvas.coords(self.selectedVertex[1],
                                   *(center - radius), *(center + radius))
                self.selectedVertex = (vertexLabel, self.selectedVertex[1])
        elif vertexLabel:
            center = V(self.canvas.coords(self.vertices[vertexLabel].items[1]))
            self.selectedVertex = (
                vertexLabel, 
                self.canvas.create_oval(
                    *(center - radius), *(center + radius),
                    fill=self.SELECTED_COLOR, outline=self.SELECTED_OUTLINE,
                    width=self.SELECTED_WIDTH, tags=tags))
            self.canvas.tag_lower(self.selectedVertex[1], 'vertex')
       
    def deleteHandler(self, vertexLabel):
        def delHandler(event):
            if self.DEBUG:
                print('Entered delHandler for "{}" #{}.'.format(
                    vertexLabel, event.serial))
            if not (vertexLabel in self.vertices and
                    (self.allowUserMoves or self.dragItems)):
                print(('Exit delHandler #{} on "{}" with allowUserMoves = {} '
                       'and dragItems = {}')
                      .format(event.serial, vertexLabel, self.allowUserMoves,
                              self.dragItems))
                return
            self.enableButtons(False)
            vert = self.deleteVertex(vertexLabel)
            self.enableButtons(True)
            self.setMessage('Deleted vertex {}'.format(vertexLabel))
            if self.DEBUG:
                print('Finished delHandler for "{}" #{}.'.format(
                    vertexLabel, event.serial))
        return delHandler
            
    def findVertex(self, point, exclude=()):
        for v in self.vertices:
            if v not in exclude:
                vert = self.vertices[v]
                center = self.canvas_coords(vert.items[1])
                if distance2(point, center) <= self.VERTEX_RADIUS **2:
                    return v
        
    def newVertexHandler(self):
        def newVertHandler(event):
            self.createVertex(self.getArgument(), coords=(event.x, event.y))
        return newVertHandler

    def badPosition(self, center, border=None):
        '''Check if a proposed vertex center would make it overlap other
        vertices or is outside the visible canvas minus a border.
        '''
        if border is None: border = self.VERTEX_RADIUS
        return (
            any(distance2(center, self.canvas_coords(v.items[1])) <
                (2 * self.SELECTED_RADIUS) ** 2 for v in self.vertices.values())
            or not BBoxContains(V(self.visibleCanvas()) + 
                                V(V(1, 1, -1, -1) * border),
                                center))
    
    def createVertex(self, label, color=None, coords=None, tags=('vertex',)):
        try:
            self.setMessage('')
            items = self.createVertexItems(
                label, color=color, coords=coords, tags=tags)
        except ValueError as e:
            self.setMessage(str(e))
            return
        newCenter = self.canvas_coords(items[1])
        bad = self.badPosition(newCenter)
        if bad:
            self.setMessage('Vertices must be visible and not overlap')
            self.dispose({}, *items)
        else:
            vert = drawnValue((label, self.nextID), *items)
            self.vertices[label] = vert
            vertColor = self.canvas_itemConfig(items[0], 'fill')
            columnLabel = Label(
                self.adjMatrixFrame, text=label, bg=vertColor,
                font=self.ADJACENCY_MATRIX_FONT)
            columnLabel.grid(row=0, column=self.nextID, sticky=(N, E, S, W))
            rowLabel = Label(
                self.adjMatrixFrame, text=label, bg=vertColor,
                font=self.ADJACENCY_MATRIX_FONT)
            rowLabel.grid(row=self.nextID, column=0, sticky=(N, E, S, W))
            for otherVert in self.vertices.values():
                if vert == otherVert:
                    frame = Frame(self.adjMatrixFrame, bg=vertColor)
                    frame.grid(row=self.nextID, column=self.nextID, 
                               sticky=(N, E, S, W))
                else:
                    otherVertColor = self.canvas_itemConfig(otherVert.items[0],
                                                            'fill')
                    entry = self.makeEdgeWeightEntry(
                        vertColor, (vert.val[0], otherVert.val[0]))
                    entry.grid(row=self.nextID, column=otherVert.val[1], 
                               sticky=(N, E, S, W))
                    entry = self.makeEdgeWeightEntry(
                        otherVertColor, (otherVert.val[0], vert.val[0]))
                    entry.grid(row=otherVert.val[1], column=self.nextID,
                               sticky=(N, E, S, W))
            self.nextID += 1
            self.setArgument(self.nextVertexLabel())

    def deleteVertex(self, vertexLabel):
        if not vertexLabel in self.vertices:
            raise ValueError('Cannot update non-existant vertex {}'.format(
                vertexLabel))
        if self.selectedVertex and self.selectedVertex[0] == vertexLabel:
            self.selectVertex(None)
        for edge in self.findEdges(vertexLabel):
            self.changeEdgeWeight(*edge, 0)
        vertex = self.vertices[vertexLabel]
        ID = vertex.val[1]
        adjMatrixWidgets = gridDict(self.adjMatrixFrame)
        for row, column in adjMatrixWidgets:
            if row == ID or (column == ID and row != ID):
                adjMatrixWidgets[row, column].grid_forget()
        self.dispose({}, *vertex.items)
        del self.vertices[vertexLabel]

    def makeEdgeWeightEntry(self, color, edge):
        if self.weighted:
            entry = Entry(self.adjMatrixFrame, bg=color,
                          font=self.ADJACENCY_MATRIX_FONT, width=2,
                          state=NORMAL,
                          takefocus=False, validate='key', 
                          validatecommand=self.weightValidate)
            def edgeWeightChange(event):
                self.changeEdgeWeight(*edge, self.getWeight(entry))
            entry.bind('<KeyRelease>', edgeWeightChange)
        else:
            def toggleEdge():
                entry = self.adjMat[edge]
                if entry:
                    self.enableButtons(False)
                    self.changeEdgeWeight(*edge, 0 if entry['text'] else 1)
                    self.enableButtons(True)
            entry = Button(self.adjMatrixFrame, bg=color,
                           text='', font=self.ADJACENCY_MATRIX_FONT,
                           state=NORMAL, takefocus=False, 
                           command=toggleEdge)
        self.adjMat[edge] = entry
        return entry

    def weight(self, weightEntry, newWeight=None):
        'Get or set the weight in a weight entry widget'
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
        
    def updateVertex(self, vertexLabel):
        if not vertexLabel in self.vertices:
            raise ValueError('Cannot update non-existant vertex {}'.format(
                vertexLabel))
        for edge in self.findEdges(vertexLabel):
            items = self.edges[edge].items
            p0, p1, p2, steps, wc = self.edgeCoords(
                self.canvas_coords(self.vertices[edge[0]].items[1]),
                self.canvas_coords(self.vertices[edge[1]].items[1]),
            )
            self.canvas.coords(items[0], *p0, *p1, *p2)
            self.canvas.itemconfigure(items[0], splinesteps=steps)
            self.canvas.coords(items[1], *wc)
        if self.selectedVertex and vertexLabel == self.selectedVertex[0]:
            self.selectVertex(vertexLabel)

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

    def changeEdgeWeight(self, fromVert, toVert, weight):
        edge = (fromVert, toVert)
        reverseEdge = (toVert, fromVert)
        edges = (edge, reverseEdge) if self.bidirectionalEdges.get() else (edge,)
        for ed in edges:
            if ed not in self.adjMat:
                raise Exception('Missing adjacency matrix entry {}->{}'.format(
                    *ed))
            self.weight(self.adjMat[ed], weight)

        if weight > 0:
            if edge not in self.edges:
                self.createEdge(fromVert, toVert, weight)
            else:
                self.canvas.itemconfigure(
                    self.edges[edge].items[1],
                    text=str(weight) if self.weighted else '')
        else:
            if edge in self.edges:
                self.dispose({}, *self.edges[edge].items)
                del self.edges[edge]
            if self.bidirectionalEdges.get() and reverseEdge in self.edges:
                self.dispose({}, *self.edges[reverseEdge].items)
                del self.edges[reverseEdge]
                    
    def createEdge(self, fromVert, toVert, weight=1, tags=('edge',)):
        edgeKey = (fromVert, toVert)
        centers = tuple(self.canvas_coords(self.vertices[v].items[1])
                        for v in edgeKey)
        self.edges[edgeKey] = drawnValue(
            edgeKey, *self.createEdgeItems(
                centers[0], centers[1], weight=weight, tags=tags))
        reverseEdge = (toVert, fromVert)
        if self.bidirectionalEdges.get():
            self.edges[reverseEdge] = self.edges[edgeKey]
        self.changeEdgeWeight(fromVert, toVert, weight)

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
            
    def makeButtons(self):
        vcmd = (self.window.register(
            makeFilterValidate(self.maxArgWidth)), '%P')
        self.newVertexButton = self.addOperation(
            "New Vertex", self.clickNewVertex, numArguments=1,
            validationCmd=vcmd, argHelpText=['vertex label'], 
            helpText='Create a new vertex with a label')
        self.randomFillButton = self.addOperation(
            "Random Fill", self.clickRandomFill, numArguments=1,
            validationCmd=vcmd, argHelpText=['# vertices'], 
            helpText='Fill with N random vertices')
        self.deleteVertexButton = self.addOperation(
            "Delete Vertex", self.clickDeleteVertex, numArguments=1,
            validationCmd=vcmd, argHelpText=['vertex label'], 
            helpText='Delete the labeled vertex')
        self.newGraphButton = self.addOperation(
            "New Graph", self.clickNewGraph,
            helpText='Create new, empty graph')
        self.bidirectionalEdges = IntVar()
        self.bidirectionalEdges.set(1)
        self.bidirectionalEdgesButton = self.addOperation(
            "Bidirectional", self.clickBidirectionalEdges,
            buttonType=Checkbutton, variable=self.bidirectionalEdges, 
            helpText='Use bidirectional edges')
        self.addAnimationButtons()

    def validArgument(self):
        text = self.getArgument()
        return text

    def enableButtons(self, enable=True):
        super().enableButtons(enable)
        for btn in [self.bidirectionalEdgesButton]: # Bidirectional edge status
            self.widgetState(               # can only change without edges
                btn,
                NORMAL if enable and self.nEdges() == 0 else DISABLED)
    
    # Button functions
    def clickNewVertex(self):
        val = self.validArgument()
        if val in self.vertices:
            self.setMessage('Cannot duplicate vertex {}'.format(val))
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
            return
        self.createVertex(val)
    
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
        for n in range(nVertices):
            self.createVertex(maxLabel)
            maxLabel = self.nextVertexLabel(maxLabel)
        
    def clickRandomFill(self):
        val = self.validArgument()
        if val and val.isdigit() and int(val) <= self.MAX_VERTICES:
            self.randomFill(int(val))
        else:
            self.setMessage('Number of vertices must be {} or less'.format(
                self.MAX_VERTICES))
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)

if __name__ == '__main__':
    graph = Graph()

    for arg in sys.argv[1:]:
        if len(arg) > 1 and arg[0] == '-':
            if arg == '-d':
                graph.DEBUG = True
            elif arg[1:].isdigit():
                graph.setArgument(arg[1:])
                graph.randomFillButton.invoke()
                graph.setArgument(
                    chr(ord(graph.DEFAULT_VERTEX_LABEL) + int(arg[1:])))
        else:
            graph.setArgument(arg)
            graph.newVertexButton.invoke()
        
    graph.runVisualization()
