from tkinter import *
import re

try:
    from Graph import *
    from TableDisplay import *
    from OutputBox import *
except ModuleNotFoundError:
    from .Graph import *
    from .TableDisplay import *
    from .OutputBox import *

V = vector

class WeightedGraph(Graph):
    EDGE_PRIORITY_QUEUE_COLOR = 'misty rose'
    
    def __init__(self, title='Weighted Graph', **kwargs):
        super().__init__(title=title, weighted=True, **kwargs)
        
    minimumSpanningTreeCode = '''
def minimumSpanningTree(self, n={nVal}):
   self.validIndex(n)
   tree = WeightedGraph()
   nVerts = self.nVertices()
   vMap = [None] * nVerts
   edges = Heap(key=weight, descending=False)
   vMap[n] = 0
   tree.addVertex(self.getVertex(n))
   while tree.nVertices() < nVerts:
      for vertex in self.adjacentVertices(n):
         if vMap[vertex] is None:
            edges.insert(
               ((n, vertex), self.edgeWeight(n, vertex)))
      edge, w = (
         (None, 0) if edges.isEmpty() else edges.remove())
      while (not edges.isEmpty() and
             vMap[edge[1]] is not None):
         edge, w = edges.remove()
      if (edge is None or
          vMap[edge[1]] is not None):
         break
      n = edge[1]
      vMap[n] = tree.nVertices()
      tree.addVertex(self.getVertex(n))
      tree.addEdge(vMap[edge[0]], vMap[edge[1]], w)
   return tree
'''

    edgesInsertPattern = re.compile(
        r'edges.insert\(\n.* self.edgeWeight\(n, vertex\)\)\)')

    edgeExtractionPattern = re.compile(
        r'edge, w = \(\n.* else edges.remove\(\)\)')

    def minimumSpanningTree(
            self, n, code=minimumSpanningTreeCode, start=True, wait=0.1):
        MSTtags = 'MST'
        nLabel = (n if isinstance(n, str) else
                  self.vertexTable[n].val if n < len(self.vertexTable) else
                  None)
        n = n if isinstance(n, int) else self.getVertexIndex(n)
        nVal = "{} ('{}')".format(n, nLabel)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)

        nArrowConfig = {'level': 1, 'anchor': SE}
        nVertConfig = {'level': 1, 'orientation': 10, 'anchor': SW}
        nArrow = self.vertexTable.createLabeledArrow(n, 'n', **nArrowConfig)
        nVertArrow = self.createLabeledArrow(nLabel, 'n', **nVertConfig)
        callEnviron |= set(nArrow + nVertArrow)
        localVars = nArrow + nVertArrow
        faded = (Scrim.FADED_FILL,) * len(nArrow + nVertArrow)
        
        self.highlightCode('self.validIndex(n)', callEnviron, wait=wait)
        self.highlightCode('tree = WeightedGraph()', callEnviron, wait=wait)
        treeLabelAnchor = (70, self.graphRegion[3] + 10)
        treeLabel = self.canvas.create_text(
            *treeLabelAnchor, text='tree', anchor=E,
            fill=self.VARIABLE_COLOR, font=self.VARIABLE_FONT)
        callEnviron.add(treeLabel)
        localVars, faded = (*localVars, treeLabel), (*faded, Scrim.FADED_FILL)
        treeVerts = Table(
            self, V(treeLabelAnchor) + V(5, 15), vertical=False,
            label='vertices', cellHeight=self.VERTEX_RADIUS,
            labelFont=(self.VARIABLE_FONT[0], -12), see=True,
            cellWidth=self.VERTEX_RADIUS * 3 // 2, cellBorderWidth=1)
        localVars += treeVerts.items()
        callEnviron |= set(treeVerts.items())
        faded += (Scrim.FADED_FILL,) * len(treeVerts.items())
        treeEdges = []
        
        self.highlightCode('nVerts = self.nVertices()', callEnviron, wait=wait)
        nVerts = self.nVertices()
        nVertsLabel = self.canvas.create_text(
            self.graphRegion[2], treeLabelAnchor[1], anchor=E,
            text='nVerts = {}'.format(nVerts),
            fill=self.VARIABLE_COLOR, font=self.VARIABLE_FONT)
        callEnviron.add(nVertsLabel)
        localVars, faded = (*localVars, nVertsLabel), (*faded, Scrim.FADED_FILL)
        nVertsBBox = self.canvas.bbox(nVertsLabel)
        
        self.highlightCode('vMap = [None] * nVerts', callEnviron, wait=wait)
        vMap = Table(
            self, (self.vertexTable.x0 + self.vertexTable.cellWidth + 5,
                   self.vertexTable.y0),
            *([None] * nVerts),
            label='vMap', labelAnchor=S, vertical=True, 
            labelFont=self.vertexTable.labelFont, 
            cellWidth=15, cellHeight=self.vertexTable.cellHeight, see=True,
            cellBorderWidth=self.vertexTable.cellBorderWidth,
            indicesFont=self.vertexTable.labelFont, indicesAnchor=W,
            indicesOffset=30)
        callEnviron |= set(vMap.items())
        localVars += vMap.items()
        faded += (Scrim.FADED_FILL,
                 *((Scrim.FADED_OUTLINE,) * (len(vMap.items()) - 1)))
        
        self.highlightCode('edges = Heap(key=weight, descending=False)',
                           callEnviron, wait=wait)
        edges = Table(
            self, V(treeLabelAnchor) + V(0, 40),
            label='edges', labelAnchor=E, vertical=False,
            labelFont=self.VARIABLE_FONT, 
            cellWidth=self.VERTEX_RADIUS * 3, cellHeight=self.VERTEX_RADIUS * 2,
            see=True, cellBorderWidth=self.vertexTable.cellBorderWidth)
        callEnviron |= set(edges.items())
        localVars += edges.items()
        faded += (Scrim.FADED_FILL,
                 *((Scrim.FADED_OUTLINE,) * (len(edges.items()) - 1)))

        self.highlightCode('vMap[n] = 0', callEnviron, wait=wait)
        vMapArrow = self.createVMapArrow(vMap, 0, n, see=True)
        vMap[n] = drawnValue(0, *vMapArrow)
        callEnviron |= set(vMapArrow)
        localVars += vMapArrow
        faded += (Scrim.FADED_FILL,) * len(vMapArrow)
        
        self.highlightCode('tree.addVertex(self.getVertex(n))', callEnviron,
                           wait=wait)
        vertCoords = self.vertexCoords(nLabel)
        inflection = V(treeLabelAnchor) + V(300, 0)
        tipCoords = self.labeledArrowCoords(
            nLabel,
            orientation=V(V(inflection) - V(vertCoords)).orient2d() + 90)[0][2:]
        treeArrow = self.canvas.create_line(
            *treeLabelAnchor, *inflection, *tipCoords,
            arrow=LAST, fill=self.HIGHLIGHTED_EDGE_COLOR, smooth=True,
            splinesteps=abs(int(tipCoords[1] - treeLabelAnchor[1])))
        callEnviron.add(treeArrow)
        localVars, faded = (*localVars, treeArrow), (
            *faded, Scrim.FADED_FILL)
        
        vRad = V((self.HIGHLIGHTED_VERTEX_RADIUS, ) * 2)
        treeVertHighlight = self.canvas.create_oval(
            *(V(vertCoords) - vRad), *(V(vertCoords) + vRad),
            fill='', outline=self.HIGHLIGHTED_VERTEX_COLOR,
            width=self.HIGHLIGHTED_VERTEX_WIDTH, tags=MSTtags)
        self.canvas.tag_lower(treeVertHighlight, 'vertex')
        copies = tuple(self.canvas.copyItem(item) 
                       for item in self.vertexTable[n].items)
        newItems = (treeVertHighlight, *copies)
        callEnviron |= set(newItems)
        localVars, faded = localVars + newItems, faded + (
            Scrim.FADED_FILL,) * len(newItems)
        self.moveItemsLinearly(
            copies, (treeVerts.cellCoords(len(treeVerts)),
                     treeVerts.cellCenter(len(treeVerts))),
            startFont=self.canvas.getItemFont(copies[1]),
            endFont=self.ADJACENCY_MATRIX_FONT, sleepTime=wait / 10,
            see=True, expand=True)
            
        treeVerts.append(drawnValue(nLabel, newItems))
        callEnviron.add(treeVerts.items()[-1])
        localVars, faded = (*localVars, treeVerts.items()[-1]), (
            *faded, Scrim.FADED_OUTLINE)

        vertexArrow, vertexArrowConfig = None, {}
        vertexVertArrow = None
        vertexVertConfig = {'orientation': 30, 'anchor': SW}
        edgeLabel, wLabel = None, None
        highlightedEdge = self.canvas.create_line(
            *vertCoords, *vertCoords, tags=MSTtags,
            fill=self.ACTIVE_EDGE_COLOR, width=self.HIGHLIGHTED_EDGE_WIDTH)
        self.canvas.tag_lower(highlightedEdge, 'edge')
        callEnviron.add(highlightedEdge)
        localVars, faded = (*localVars, highlightedEdge), (
            *faded, Scrim.FADED_FILL)

        self.highlightCode('tree.nVertices() < nVerts', callEnviron, wait=wait)
        while len(treeVerts) < nVerts:
            self.highlightCode('vertex in self.adjacentVertices(n)',
                               callEnviron, wait=wait)
            colors = self.canvas.fadeItems(localVars, faded)
            for vertex in self.adjacentVertices(n):
                self.canvas.restoreItems(localVars, colors, top=False)
                vertexLabel = self.vertexTable[vertex].val

                if vertexArrow is None:
                    vertexArrow = self.vertexTable.createLabeledArrow(
                        vertex, 'vertex', see=True, **vertexArrowConfig)
                    vertexVertArrow = self.createLabeledArrow(
                        vertexLabel, 'vertex', see=True, **vertexVertConfig)
                    arrows = vertexArrow + vertexVertArrow
                    callEnviron |= set(arrows)
                    localVars += arrows
                    faded += (Scrim.FADED_FILL,) * len(arrows)
                else:
                    self.moveItemsTo(
                        vertexArrow + vertexVertArrow, 
                        self.vertexTable.labeledArrowCoords(
                            vertex, **vertexArrowConfig) +
                        self.labeledArrowCoords(vertexLabel, **vertexVertConfig),
                        sleepTime=wait / 10, see=True, expand=True)

                self.highlightCode('vMap[vertex] is None', callEnviron,
                                   wait=wait)
                if vMap[vertex] is None:
                    self.highlightCode(self.edgesInsertPattern, callEnviron,
                                       wait=wait)
                    edge = (nLabel, vertexLabel)
                    w = self.edgeWeight(nLabel, vertexLabel)
                    vertLabels = tuple(
                        self.canvas.copyItem(self.vertices[v].items[1])
                        for v in edge)
                    for j in (0, 1):
                        self.canvas.itemConfig(
                            vertLabels[j],
                            text=(' {}' if j else '{} ').format(
                                self.canvas.itemConfig(vertLabels[j], 'text')),
                            anchor=W if j else E)
                    weightLabel = self.canvas.create_text(
                        *self.canvas.coords(self.edges[edge].items[1]),
                        text=str(weight), font=self.VERTEX_FONT)
                    toMove = (*vertLabels, weightLabel)
                    callEnviron |= set(toMove)
                    insertAt = self.edgeInsertPosition(edges, w)
                    PQcoords = self.edgePriorityQueueCoords(edges, insertAt)
                    newCoords=(PQcoords[1], PQcoords[1], PQcoords[2])
                    toMove += flat(*(ed.items for ed in edges[insertAt:]))
                    newCoords += flat(*[
                        self.edgePriorityQueueCoords(edges, j)
                        for j in range(insertAt + 1, len(edges) + 1)])
                    self.moveItemsLinearly(
                        toMove, newCoords, sleepTime=wait / 10)
                    edges[insertAt:insertAt] = [
                        self.createEdgePriorityQueueEntry(
                            edges, edge, w, insertAt)]
                    newItems = (edges.items()[-1], *edges[insertAt].items)
                    callEnviron |= set(newItems)
                    self.dispose(callEnviron, *toMove[:3])
                    localVars += newItems
                    faded += (
                        Scrim.FADED_OUTLINE,
                        *((Scrim.FADED_FILL,) * len(edges[insertAt].items)))
                    
                self.highlightCode('vertex in self.adjacentVertices(n)',
                                   callEnviron, wait=wait)
                colors = self.canvas.fadeItems(localVars, faded)
                
            self.canvas.restoreItems(localVars, colors, top=False)
            self.highlightCode('edges.isEmpty()', callEnviron, wait=wait)
            self.highlightCode(
                ('edge, w = (',
                 '(None, 0)' if len(edges) == 0 else 'edges.remove()'),
                callEnviron, wait=wait)
            dValue = None if len(edges) == 0 else edges.pop(0)
            edge, w = (None, 0) if dValue is None else dValue.val
            edgeLabelCoords = (
                (nVertsBBox[0], nVertsBBox[3] + 5) if edge is None else
                self.edgeCoords(
                    *(self.canvas.coords(self.vertices[edge[j]].items[1])
                      for j in (0, 1)))[-1])
            edgeLabelAnchor = NE if edge is None else CENTER
            if edgeLabel is None:
                wLabel = self.canvas.create_text(
                    nVertsBBox[2], nVertsBBox[3] + 5, anchor=NE,
                    text='w = {}'.format(w), font=self.VARIABLE_FONT,
                    fill=self.VARIABLE_COLOR)
                edgeLabel = self.canvas.create_text(
                    *edgeLabelCoords, anchor=edgeLabelAnchor, text='edge',
                    font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
                callEnviron |= set((wLabel, edgeLabel))
                localVars += (wLabel, edgeLabel)
                faded += (Scrim.FADED_FILL,) * 2
            self.updateEdgeAndWeightFromQueue(
                edge, w, edgeLabel, wLabel, highlightedEdge, edges, dValue,
                callEnviron, wait, edgeLabelCoords, edgeLabelAnchor)
                    
            self.highlightCode('not edges.isEmpty()', callEnviron, wait=wait)
            if len(edges) > 0:
                self.highlightCode('vMap[edge[1]] is not None', callEnviron,
                                   wait=wait)
            while (len(edges) > 0 and
                   vMap[self.getVertexIndex(edge[1])] is not None):
                self.highlightCode('edge, w = edges.remove()', callEnviron,
                                   wait=wait)
                
                dValue = edges.pop(0)
                edge, w = dValue.val
                self.updateEdgeAndWeightFromQueue(
                    edge, w, edgeLabel, wLabel, highligtedEdge, edges, dValue,
                    callEnviron, wait)

                self.highlightCode('not edges.isEmpty() TBD', callEnviron,
                                   wait=wait)
                if len(edges) > 0:
                    self.highlightCode('vMap[edge[1]] is not None', callEnviron,
                                       wait=wait)
                
            self.highlightCode('edge is None', callEnviron, wait=wait)
            if edge is not None:
                self.highlightCode(('vMap[edge[1]] is not None', 2),
                                   callEnviron, wait=wait)
            if edge is None or vMap[self.getVertexIndex(edge[1])] is not None:
                self.highlightCode('break', callEnviron, wait=wait)
                break
                
            self.highlightCode('n = edge[1]', callEnviron, wait=wait)
            nLabel = edge[1]
            n = self.getVertexIndex(nLabel)
            self.moveItemsTo(
                nArrow + nVertArrow,
                self.vertexTable.labeledArrowCoords(n, **nArrowConfig) +
                self.labeledArrowCoords(nLabel, **nVertConfig),
                sleepTime=wait / 10)

            self.highlightCode('vMap[n] = tree.nVertices()', callEnviron,
                               wait=wait)
            vMapArrow = self.createVMapArrow(vMap, len(treeVerts), n)
            vMap[n] = drawnValue(len(treeVerts), *vMapArrow)
            callEnviron |= set(vMapArrow)
            localVars += vMapArrow
            faded += (Scrim.FADED_FILL,) * len(vMapArrow)

            self.highlightCode(('tree.addVertex(self.getVertex(n))', 2),
                               callEnviron, wait=wait)
            vertCoords = self.vertexCoords(nLabel)
            treeVertHighlight = self.canvas.create_oval(
                *(V(vertCoords) - vRad), *(V(vertCoords) + vRad),
                fill='', outline=self.HIGHLIGHTED_VERTEX_COLOR,
                width=self.HIGHLIGHTED_VERTEX_WIDTH, tags=MSTtags)
            self.canvas.tag_lower(treeVertHighlight, 'vertex')
            copies = tuple(self.canvas.copyItem(item) 
                           for item in self.vertexTable[n].items)
            newItems = (treeVertHighlight, *copies)
            callEnviron |= set(newItems)
            localVars, faded = localVars + newItems, faded + (
                Scrim.FADED_FILL,) * len(newItems)
            self.moveItemsLinearly(
                copies, (treeVerts.cellCoords(len(treeVerts)),
                         treeVerts.cellCenter(len(treeVerts))),
                startFont=self.canvas.getItemFont(copies[1]),
                endFont=self.ADJACENCY_MATRIX_FONT, sleepTime=wait / 10,
                see=True, expand=True)
            
            treeVerts.append(drawnValue(vertexLabel, newItems))
            callEnviron.add(treeVerts.items()[-1])
            localVars, faded = (*localVars, treeVerts.items()[-1]), (
                *faded, Scrim.FADED_OUTLINE)
            
            self.highlightCode(
                'tree.addEdge(vMap[edge[0]], vMap[edge[1]], w)', callEnviron,
                wait=wait)
            coords = self.canvas.coords(self.edges[edge].items[0])
            delta = V(coords[:2]) - V(coords[-2:])
            treeEdgeHighlight = self.canvas.create_line(
                *coords, smooth=True, tags=MSTtags,
                splinesteps=int(max(abs(delta[0]), abs(delta[1]), 5)),
                fill=self.HIGHLIGHTED_EDGE_COLOR,
                width=self.HIGHLIGHTED_EDGE_WIDTH)
            self.canvas.lower(treeEdgeHighlight, 'edge')
            callEnviron.add(treeEdgeHighlight)
            localVars, faded = (*localVars, treeEdgeHighlight), (
                *faded, Scrim.FADED_FILL)
            treeEdges.append(
                drawnValue(self.edges[edge].items[0], treeEdgeHighlight))
                
            self.highlightCode('tree.nVertices() < nVerts', callEnviron,
                               wait=wait)
            
        self.highlightCode('return tree', callEnviron, wait=wait)
        self.cleanUp(callEnviron)

    def edgeInsertPosition(self, edges, weight):
        lo, hi = 0, len(edges) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if edges[mid].val[1] == weight:
                return mid
            elif edges[mid].val[1] < weight:
                lo = mid + 1
            else:
                hi = mid - 1
        return lo

    def edgePriorityQueueCoords(self, edges, index):
        Vy = V(0, textHeight(self.ADJACENCY_MATRIX_FONT) // 2)
        Vcenter = V(edges.cellCenter(index))
        return edges.cellCoords(index), Vcenter - Vy, Vcenter + Vy
    
    def createEdgePriorityQueueEntry(self, edges, edge, weight, insertAt):
        coords = self.edgePriorityQueueCoords(edges, insertAt)
        rect = self.canvas.create_rectangle(
            *coords[0], fill=self.EDGE_PRIORITY_QUEUE_COLOR,
            outline='', width=0, tags='edgePQ')
        text1 = self.canvas.create_text(
            *coords[1], text='{}-{}'.format(*edge, weight),
            font=self.ADJACENCY_MATRIX_FONT)
        text2 = self.canvas.create_text(
            *coords[2], text=str(weight), font=self.ADJACENCY_MATRIX_FONT)
        return drawnValue((edge, weight), rect, text1, text2)

    def updateEdgeAndWeightFromQueue(
            self, edge, weight, edgeLabel, weightLabel, highlightedEdge, edges,
            dValue, callEnviron, wait, edgeLabelCoords=None,
            edgeLabelAnchor=None):
        if edgeLabelCoords is None:
            edgeLabelCoords = (
                (nVertsBBox[0], nVertsBBox[3] + 5) if edge is None else
                self.edgeCoords(
                    *(self.canvas.coords(self.vertices[edge[j]].items[1])
                      for j in (0, 1)))[-1])
        if edgeLabelAnchor is None:
            edgeLabelAnchor = NE if edge is None else CENTER
        self.canvas.changeAnchor(edgeLabelAnchor, edgeLabel)
        toMove = [edgeLabel]
        moveTo = [edgeLabelCoords]
        if edge is not None:
            queueFrontCoords = self.edgePriorityQueueCoords(edges, 0)
            toMove += [self.canvas.create_text(
                *queueFrontCoords[1], text=(' {}' if i else '{} ').format(v),
                anchor=W if i else E, font=self.ADJACENCY_MATRIX_FONT)
                       for i, v in enumerate(edge)]
            moveTo += [self.vertexCoords(v) for v in edge]
            callEnviron |= set(toMove[-2:])
            self.dispose(callEnviron, *dValue.items[:2])
            toMove.append(dValue.items[2])
            moveTo.append(self.canvas.coords(weightLabel))
            toDispose = toMove[1:]
            toMove += list(flat(*(dv.items for dv in edges)))
            moveTo += list(flat(*(self.edgePriorityQueueCoords(edges, j)
                                  for j in range(len(edges)))))
        self.moveItemsLinearly(toMove, moveTo, sleepTime=wait / 10)
        self.canvas.coords(
            highlightedEdge,
            self.canvas.coords(highlightedEdge)[:2] * 2 if edge is None else
            self.vertexCoords(edge[0]) + self.vertexCoords(edge[1]))
        self.canvas.itemConfig(weightLabel, text='w = {}'.format(weight))
        self.dispose(callEnviron, *toDispose)
    
    def enableButtons(self, enable=True):
        super(type(self).__bases__[0], self).enableButtons( # Grandparent
            enable)
        for btn in (self.depthFirstTraverseButton, 
                    self.breadthFirstTraverseButton, self.MSTButton):
            widgetState( # can only traverse when start node selected
                btn,
                NORMAL if enable and self.selectedVertex else DISABLED)

    def makeButtons(self, *args, **kwargs):
        '''Make buttons specific to unweighted graphs and aadd the
        animation control buttons'''
        vcmd = super(type(self).__bases__[0], self).makeButtons( # Grandparent
            *args, bidirectional=True, **kwargs)
        self.depthFirstTraverseButton = self.addOperation(
            "Depth-first Traverse", lambda: self.clickTraverse('depth'),
            helpText='Traverse graph in depth-first order', state=DISABLED)
        self.breadthFirstTraverseButton = self.addOperation(
            "Breadth-first Traverse", lambda: self.clickTraverse('breadth'),
            helpText='Traverse graph in breadth-first order', state=DISABLED)
        self.MSTButton = self.addOperation(
            "Minimum Spanning Tree", self.clickMinimumSpanningTree,
            helpText='Compute a minimum spanning tree', state=DISABLED)
        self.addAnimationButtons()
            
if __name__ == '__main__':
    graph = WeightedGraph()
    edgePattern = re.compile(r'(\w+)-(\w+)(:([1-9][0-9]?))?')

    edges = []
    for arg in sys.argv[1:]:
        edgeMatch = edgePattern.fullmatch(arg)
        if len(arg) > 1 and arg[0] == '-':
            if arg == '-d':
                graph.DEBUG = True
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
