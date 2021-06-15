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
    OVERLAP_OUTLINE_COLOR = 'red'
    OVERLAP_TEXT_COLOR = 'red'
    DEFAULT_VERTEX_LABEL = 'A'
    nextColor = 0
    
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
            *(V(coords) - vr), *(V(coords) + vr), fill=color,
            tags=tags + ('shape', label), outline='', width=1,
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
        for item in items:
            self.canvas.tag_bind(item, '<Button-1>', startMoveHandler)
            self.canvas.tag_bind(item, '<B1-Motion>', moveHandler)
            self.canvas.tag_bind(item, '<ButtonRelease-1>', releaseHandler)
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
            if not self.allowUserMoves or self.dragItems:
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
        return startHandler

    def moveHandler(self, vertexLabel):
        def mvHandler(event):
            if not self.dragItems or not self.allowUserMoves:
                return
            self.enableButtons(False)
            delta = (event.x - self.lastPos[0], event.y - self.lastPos[1])
            self.lastPos = (event.x, event.y)
            moveVertex = self.canvas.type(self.dragItems[0]) != 'line'
            if moveVertex:
                for item in self.dragItems:
                    self.canvas.move(item, *delta)

                newCenter = self.canvas_coords(self.dragItems[1])
                overlap = any(
                    distance2(newCenter, self.canvas_coords(v.items[1])) <
                    (2 * self.SELECTED_RADIUS) ** 2
                    for v in self.vertices.values() if v.val[0] != vertexLabel)
                self.canvas.itemconfigure(
                    self.dragItems[0], state=HIDDEN if overlap else NORMAL)
                self.canvas.itemconfigure(
                    self.dragItems[1], 
                    fill= self.OVERLAP_TEXT_COLOR if overlap else
                    self.VALUE_COLOR)
            else:
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
            if self.dragItems:
                moveVertex = self.canvas.type(self.dragItems[0]) != 'line'
                if moveVertex:
                    newCenter = self.canvas_coords(self.dragItems[1])
                    overlap = any(
                        distance2(newCenter, self.canvas_coords(v.items[1])) <
                        (2 * self.SELECTED_RADIUS) ** 2
                        for v in self.vertices.values() 
                        if v.val[0] != vertexLabel)
                    if overlap:
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
                else:
                    toVert = self.findVertex((event.x, event.y), 
                                             exclude=(vertexLabel,))
                    self.restoreVertexAppearance()
                    if toVert:
                        self.dispose({}, *self.dragItems)
                        self.dragItems = None
                        self.createEdge(vertexLabel, toVert, 1)
                    else:
                        self.undoDrag(vertexLabel)
            self.enableButtons(True)
        return relHandler

    def undoDrag(self, vertexLabel):
        if self.dragItems:
            self.allowUserMoves = False
            moveVertex = self.canvas.type(self.dragItems[0]) != 'line'
            wait = 40
            if moveVertex:
                oldCenter = self.canvas_coords(
                    self.vertices[vertexLabel].items[1])
                center = self.canvas_coords(self.dragItems[1])
                delta = V(V(V(oldCenter) - V(center)) * 0.1)
                if delta.len2() <= 1:
                    for item in self.dragItems:
                        self.canvas.delete(item)
                    self.dragItems = None
                    self.allowUserMoves = True
                else:
                    for item in self.dragItems:
                        self.canvas.move(item, *delta)
                    self.undoDragRequest = self.canvas.after(
                        wait, lambda: self.undoDrag(vertexLabel))
            else:
                edge = self.canvas_coords(self.dragItems[0])
                base, tip = edge[:2], edge[-2:]
                newTip = V(V(V(tip) * 9) + V(base)) / 10
                if distance2(base, newTip) <= 1:
                    for item in self.dragItems:
                        self.canvas.delete(item)
                    self.dragItems = None
                    self.allowUserMoves = True
                else:
                    p0, p1, p2, steps, wc = self.edgeCoords(
                        base, newTip, removeRadius=0)
                    self.canvas.coords(self.dragItems[0], *p0, *p1, *p2)
                    self.canvas.itemconfigure(self.dragItems[0],
                                              splinesteps=steps)
                    self.canvas.coords(self.dragItems[1], *wc)
                    self.undoDragRequest = self.canvas.after(
                        wait, lambda: self.undoDrag(vertexLabel))

    def selectVertex(self, vertexLabel, tags='selected'):
        if not (vertexLabel in self.vertices or vertexLabel is None):
            return
        radius = V((self.SELECTED_RADIUS, self.SELECTED_RADIUS))
        if self.selectedVertex:
            if vertexLabel is None:
                self.canvas.delete(self.selectedVertex)
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

    def createVertex(self, label, color=None, coords=None, tags=('vertex',)):
        try:
            self.setMessage('')
            items = self.createVertexItems(
                label, color=color, coords=coords, tags=tags)
        except ValueError as e:
            self.setMessage(str(e))
            return
        newCenter = self.canvas_coords(items[1])
        overlap = any(
            distance2(newCenter, self.canvas_coords(v.items[1])) <
            (2 * self.SELECTED_RADIUS) ** 2 for v in self.vertices.values())
        if overlap:
            self.setMessage('Vertices may not overlap')
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
            other = 1 if edge[0] == vertexLabel else 0
            p0, p1, p2, steps, wc = self.edgeCoords(
                self.canvas_coords(self.vertices[edge[1 - other]].items[1]),
                self.canvas_coords(self.vertices[edge[other]].items[1]),
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
        return [edge for edge in self.edges if
                inbound and edge[1] == vertex or outbound and edge[0] == vertex
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
        self.newVertexButton = self.addOperation(
            "Random Fill", self.clickRandomFill, numArguments=1,
            validationCmd=vcmd, argHelpText=['# vertices'], 
            helpText='Fill with N random vertices')
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
        graph.setArgument(arg)
        graph.newVertexButton.invoke()
        
    graph.runVisualization()
