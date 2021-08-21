from tkinter import *
import re, math

try:
    from Graph import *
    from TableDisplay import *
    from OutputBox import *
except ModuleNotFoundError:
    from .Graph import *
    from .TableDisplay import *
    from .OutputBox import *

V = vector

def replaceInfinity(formatSpec, *values, **kwargs):
    newValues = ('∞' if val == math.inf else '-∞' if val == - math.inf else val
                 for val in values)
    for key in kwargs:
        if kwargs[key] == math.inf:
            kwargs[key] = '∞'
        elif kwargs[key] == - math.inf:
            kwargs[key] = '-∞'
    return formatSpec.format(*newValues, **kwargs)
    
class WeightedGraph(Graph):
    EDGE_PRIORITY_QUEUE_COLOR = 'misty rose'
    
    def __init__(self, title='Weighted Graph', **kwargs):
        super().__init__(
            title=title, weighted=True, selectableVertices=2, **kwargs)
        
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
                        text=str(w), font=self.VERTEX_FONT)
                    toMove = (*vertLabels, weightLabel)
                    callEnviron |= set(toMove)
                    insertAt = self.edgeInsertPosition(edges, w)
                    PQcoords = edges.cellAndCenters(insertAt, rows=2)
                    newCoords=(PQcoords[1], PQcoords[1], PQcoords[2])
                    toMove += flat(*(ed.items for ed in edges[insertAt:]))
                    newCoords += flat(*[
                        edges.cellAndCenters(j, rows=2)
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
            edgeLabelCoords = self.edgeLabelCoords(edge, nVertsBBox)
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
                nVertsBBox, callEnviron, wait, edgeLabelCoords, edgeLabelAnchor)
                    
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
                    edge, w, edgeLabel, wLabel, highlightedEdge, edges, dValue,
                    nVertsBBox, callEnviron, wait)

                self.highlightCode('not edges.isEmpty()', callEnviron,
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
    
    def createEdgePriorityQueueEntry(
            self, edges, edge, weight, insertAt, tags='edgePQ'):
        coords = edges.cellAndCenters(insertAt, rows=2)
        rect = self.canvas.create_rectangle(
            *coords[0], fill=self.EDGE_PRIORITY_QUEUE_COLOR,
            outline='', width=0, tags=tags)
        text1 = self.canvas.create_text(
            *coords[1], text='{}-{}'.format(*edge, weight),
            font=self.ADJACENCY_MATRIX_FONT, tags=tags)
        text2 = self.canvas.create_text(
            *coords[2], text=str(weight), font=self.ADJACENCY_MATRIX_FONT,
            tags=tags)
        return drawnValue((edge, weight), rect, text1, text2)

    def updateEdgeAndWeightFromQueue(
            self, edge, weight, edgeLabel, weightLabel, highlightedEdge, edges,
            dValue, nVertsBBox, callEnviron, wait, edgeLabelCoords=None,
            edgeLabelAnchor=None):
        if edgeLabelCoords is None:
            edgeLabelCoords = self.edgeLabelCoords(edge, nVertsBBox)
        if edgeLabelAnchor is None:
            edgeLabelAnchor = NE if edge is None else CENTER
        self.canvas.changeAnchor(edgeLabelAnchor, edgeLabel)
        toMove = [edgeLabel]
        moveTo = [edgeLabelCoords]
        toDispose = []
        if edge is not None:
            queueFrontCoords = edges.cellAndCenters(0, rows=2)
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
            moveTo += list(flat(*(edges.cellAndCenters(j, rows=2)
                                  for j in range(len(edges)))))
        self.moveItemsLinearly(toMove, moveTo, sleepTime=wait / 10)
        self.canvas.coords(
            highlightedEdge,
            self.canvas.coords(highlightedEdge)[:2] * 2 if edge is None else
            self.vertexCoords(edge[0]) + self.vertexCoords(edge[1]))
        self.canvas.itemConfig(weightLabel, text='w = {}'.format(weight))
        self.dispose(callEnviron, *toDispose)

    def edgeLabelCoords(self, edge, nVertsBBox):
        'Position of the edge variable label in minimum spanning tree algorithm'
        return ((nVertsBBox[0], nVertsBBox[3] + 5) if edge is None else
                self.edgeCoords(
                    *(self.vertexCoords(edge[j])
                      for j in ((1, 0) if edge == self.edges[edge].val else
                                (0, 1))))[-1])

    shortestPathCode = '''
def shortestPath(self, start={startVal}, end={endVal}):
   visited = {{}}
   costs = {{start: (0, start)}}
   while end not in visited:
      nextVert, cost = None, math.inf
      for vertex in costs:
         if (vertex not in visited and
             costs[vertex][0] <= cost):
            nextVert, cost = vertex, costs[vertex][0]
      if nextVert is None:
         break
      visited[nextVert] = 1
      for adj in self.adjacentVertices(nextVert):
         if adj not in visited:
            pathCost = (
               self.edgeWeight(nextVert, adj) +
               costs[nextVert][0])
            if (adj not in costs or
                costs[adj][0] > pathCost):
               costs[adj] = (pathCost, nextVert)
   path = []
   while end in visited:
      path.append(end)
      if end == start:
         break
      end = costs[end][1]
   return list(reversed(path))
'''
    pathCostAssignPattern = re.compile(
        r'pathCost = .*\n.*\n.*costs\[nextVert\]\[0\]\)')
    
    def shortestPath(self, start, end, code=shortestPathCode,
                     startAnimations=True, wait=0.1):
        SPtags = 'SP'
        startVert = (start if isinstance(start, str) else
                     self.vertexTable[start].val
                     if start < len(self.vertexTable) else None)
        start = (start if isinstance(start, int) else
                 self.getVertexIndex(start))
        startVal = "{} ('{}')".format(start, startVert)
        endVert = (end if isinstance(end, str) else
                     self.vertexTable[end].val
                     if end < len(self.vertexTable) else None)
        end = (end if isinstance(end, int) else self.getVertexIndex(end))
        endVal = "{} ('{}')".format(end, endVert)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=startAnimations)

        startArrowConfig, endArrowConfig = {'anchor': SE},  {'anchor': NE}
        vertArrowConfig = {'orientation': 10, 'anchor': SW}
        startArrow = self.vertexTable.createLabeledArrow(
            start, 'start', **startArrowConfig)
        startVertArrow = self.createLabeledArrow(
            startVert, 'start', **vertArrowConfig)
        endArrow = self.vertexTable.createLabeledArrow(
            end, 'end', **endArrowConfig)
        endVertArrow = self.createLabeledArrow(
            endVert, 'end', **vertArrowConfig)
        arrows = startArrow + startVertArrow + endArrow + endVertArrow
        callEnviron |= set(arrows)
        localVars = arrows
        faded = (Scrim.FADED_FILL,) * len(arrows)

        self.highlightCode('visited = {}', callEnviron, wait=wait)
        visited = self.createVisitedTable(self.nVertices(), visible=False)
        localVars += visited.items()
        faded += (Scrim.FADED_FILL,
                  *((Scrim.FADED_OUTLINE,) * (len(visited.items()) - 1)))
        
        self.highlightCode('costs = {start: (0, start)}', callEnviron,
                           wait=wait)
        costs = Table(
            self, (70, self.graphRegion[3] + 40),
            label='costs', labelAnchor=E, vertical=False,
            labelFont=self.VARIABLE_FONT, 
            cellWidth=self.VERTEX_RADIUS * 3, cellHeight=self.VERTEX_RADIUS * 2,
            see=True, cellBorderWidth=self.vertexTable.cellBorderWidth)
        localVars += costs.items()
        faded += (Scrim.FADED_FILL,) * len(costs.items())
        costs.append(drawnValue(
            (startVert, 0, startVert),
            *self.createCostsTableEntry(
                costs, startVert, (0, startVert),
                color=self.canvas.itemConfig(self.vertices[startVert].items[0],
                                             'fill'))))
        costVertices = (startVert,)
        callEnviron |= set(costs.items() + costs[0].items)
        localVars += (costs.items()[-1], *costs[0].items)
        faded += (Scrim.FADED_OUTLINE,
                  *((Scrim.FADED_FILL,) * len(costs[0].items)))

        nextVertArrow, costsNextVertArrow = None, None
        nextVertArrowConfig = {'orientation': 60}
        nextVertNoneCoords = (-self.VERTEX_RADIUS,
                              (self.graphRegion[1] + self.graphRegion[3]) // 2)
        vertexArrow, vertexArrowConfig = None, {'level': 2}
        vertexArrow2, vertexArrow2Config = None, {'level': -1}
        adjArrow, costsAdjArrow, adjArrowConfig = None, None, {
            'orientation': -60, 'level': 2}
        costLabelCoords = V(self.graphRegion[2:]) + V(50, 15)
        pathCostLabelCoords = V(costLabelCoords) + V(0, 15)
        pathCostLabel = None
        self.highlightCode('end not in visited', callEnviron, wait=wait)
        while not visited[end].val:
            self.highlightCode('nextVert, cost = None, math.inf', callEnviron,
                               wait=wait)
            nextVert, cost = None, math.inf
            if nextVertArrow is None:
                nextVertArrow = self.createLabeledArrow(
                    nextVertNoneCoords, 'nextVert', **nextVertArrowConfig)
                costsNextVertArrow = self.createLabeledArrow(
                    nextVertNoneCoords, 'nextVert', **nextVertArrowConfig)
                costLabel = self.canvas.create_text(
                    *costLabelCoords, anchor=E,
                    text=replaceInfinity('cost = {}', cost),
                    tags=SPtags, fill=self.VARIABLE_COLOR,
                    font=self.VARIABLE_FONT)
                items = (costLabel, *nextVertArrow, *costsNextVertArrow)
                callEnviron |= set(items)
                localVars += items
                faded += (Scrim.FADED_FILL,) * len(items)
            else:
                arrowCoords = self.labeledArrowCoords(nextVertNoneCoords,
                                                      **nextVertArrowConfig)
                self.moveItemsTo(nextVertArrow + costsNextVertArrow,
                                 arrowCoords + arrowCoords,
                                 sleepTime=wait / 10)
                self.canvas.itemConfig(costLabel,
                                       text=replaceInfinity('cost = {}', cost))

            self.highlightCode('vertex in costs', callEnviron, wait=wait)
            for costIndex in range(len(costs)):
                vertex = costs[costIndex].val[0]
                vertexIndex = self.getVertexIndex(vertex)
                if vertexArrow is None:
                    vertexArrow = costs.createLabeledArrow(
                        costIndex, 'vertex', **vertexArrowConfig)
                    vertexArrow2 = visited.createLabeledArrow(
                        vertexIndex, 'vertex', **vertexArrow2Config)
                    arrows = vertexArrow + vertexArrow2
                    callEnviron |= set(arrows)
                    localVars += arrows
                    faded += (Scrim.FADED_FILL,) * len(arrows)
                else:
                    self.moveItemsTo(
                        vertexArrow + vertexArrow2,
                        costs.labeledArrowCoords(costIndex, **vertexArrowConfig)
                        + visited.labeledArrowCoords(
                            vertexIndex, **vertexArrow2Config),
                        sleepTime=wait / 10)

                self.highlightCode('vertex not in visited', callEnviron,
                                   wait=wait)
                if not visited[vertexIndex].val:
                    self.highlightCode('costs[vertex][0] <= cost', callEnviron,
                                       wait=wait)
                if (not visited[vertexIndex].val and
                    costs[costIndex].val[1] < cost):
                    self.highlightCode(
                        'nextVert, cost = vertex, costs[vertex][0]',
                        callEnviron, wait=wait)
                    nextVert, nextVertIndex = vertex, vertexIndex
                    cost = costs[costIndex].val[1]
                    costCopy = self.canvas.copyItem(costs[costIndex].items[2])
                    callEnviron.add(costCopy)
                    self.canvas.itemConfig(costCopy, text=str(cost),
                                           anchor=E)
                    self.moveItemsTo(
                        (costCopy, *nextVertArrow, *costsNextVertArrow),
                        (self.canvas.coords(costLabel),
                         *(self.labeledArrowCoords(self.vertexCoords(nextVert),
                                                   **nextVertArrowConfig) +
                           costs.labeledArrowCoords(costIndex,
                                                    **nextVertArrowConfig))),
                        sleepTime=wait / 10)
                    self.dispose(callEnviron, costCopy)
                    self.canvas.itemConfig(
                        costLabel, text=replaceInfinity('cost = {}', cost))

                self.highlightCode('vertex in costs', callEnviron, wait=wait)

            self.moveItemsTo(
                vertexArrow + vertexArrow2,
                costs.labeledArrowCoords(len(costs), **vertexArrowConfig) +
                visited.labeledArrowCoords(len(visited), **vertexArrow2Config),
                sleepTime=wait / 10)

            self.highlightCode('nextVert is None', callEnviron, wait=wait)
            if nextVert is None:
                self.highlightCode('break', callEnviron, wait=wait)
                break
            
            self.highlightCode('visited[nextVert] = 1', callEnviron, wait=wait)
            visited[nextVertIndex] = drawnValue(
                True,
                self.canvas.create_text(
                    *visited.cellCenter(nextVertIndex), text='1',
                    font=self.ADJACENCY_MATRIX_FONT, tags=SPtags))
            callEnviron |= set(visited[nextVertIndex].items)
            localVars += visited[nextVertIndex].items
            faded += (Scrim.FADED_FILL,)

            self.highlightCode('adj in self.adjacentVertices(nextVert)',
                               callEnviron, wait=wait)
            colors = self.canvas.fadeItems(localVars, faded)
            for adj in self.adjacentVertices(nextVertIndex):
                self.canvas.restoreItems(localVars, colors, top=False)
                adjVertex = self.vertexTable[adj].val
                costVertices = [c.val[0] for c in costs]
                adjVertexInCosts = adjVertex in costVertices
                adjVertexIndexInCosts = (
                    costVertices.index(adjVertex) if adjVertexInCosts else
                    len(costs))
                if adjArrow is None:
                    adjArrow = self.createLabeledArrow(adj, 'adj',
                                                       **adjArrowConfig)
                    costsAdjArrow = (
                        costs.createLabeledArrow(adjVertexIndexInCosts, 'adj',
                                                 **adjArrowConfig)
                        if adjVertexInCosts else
                        self.createLabeledArrow(adj, 'adj', **adjArrowConfig))
                    arrows = adjArrow + costsAdjArrow
                    callEnviron |= set(arrows)
                    localVars += arrows
                    faded += (Scrim.FADED_FILL,) * len(arrows)
                else:
                    self.moveItemsTo(
                        adjArrow + costsAdjArrow,
                        self.labeledArrowCoords(adj, **adjArrowConfig) +
                        (costs.labeledArrowCoords(adjVertexIndexInCosts,
                                                  **adjArrowConfig)
                         if adjVertexInCosts else
                         self.labeledArrowCoords(adj, **adjArrowConfig)),
                        sleepTime=wait / 10)
                    
                self.highlightCode('adj not in visited', callEnviron, wait=wait)
                if not visited[adj].val:
                    self.highlightCode(self.pathCostAssignPattern, callEnviron,
                                       wait=wait)
                    costIndex = costVertices.index(nextVert)
                    edge = (nextVert, adjVertex)
                    edgeWeight = self.edgeWeight(*edge)
                    cost = costs[costIndex].val[1]
                    pathCost = edgeWeight + cost
                    edgeWeightCopy = self.canvas.create_text(
                        *self.canvas.coords(self.edges[edge].items[1]),
                        anchor=E, text=str(edgeWeight), tags=SPtags,
                        font=self.ADJACENCY_MATRIX_FONT)
                    costCopy = self.canvas.copyItem(costs[costIndex].items[2])
                    self.canvas.itemConfig(costCopy, text=str(cost), anchor=E)
                    callEnviron |= set((edgeWeightCopy, costCopy))
                    self.moveItemsTo(
                        (edgeWeightCopy, costCopy), (pathCostLabelCoords,) * 2,
                        sleepTime=wait / 10)
                    if pathCostLabel is None:
                        pathCostLabel = self.canvas.create_text(
                            *pathCostLabelCoords, anchor=E,
                            text='pathCost = {}'.format(pathCost), tags=SPtags,
                            fill=self.VARIABLE_COLOR, font=self.VARIABLE_FONT)
                        callEnviron.add(pathCostLabel)
                        localVars += (pathCostLabel,)
                        faded += (Scrim.FADED_FILL,)
                    else:
                        self.canvas.itemConfig(
                            pathCostLabel, text='pathCost = {}'.format(pathCost))
                    self.dispose(callEnviron, edgeWeightCopy, costCopy)
                    
                    self.highlightCode('adj not in costs', callEnviron,
                                       wait=wait)
                    if adjVertex in costVertices:
                        self.highlightCode('costs[adj][0] > pathCost',
                                           callEnviron, wait=wait)
                    if (not adjVertexInCosts or
                        costs[adjVertexIndexInCosts].val[1] > pathCost):
                        self.highlightCode('costs[adj] = (pathCost, nextVert)',
                                           callEnviron, wait=wait)
                        pathCostCopy = self.canvas.create_text(
                            *pathCostLabelCoords, anchor=E, text=str(pathCost),
                            font=self.ADJACENCY_MATRIX_FONT)
                        nextVertCopy = self.canvas.create_text(
                            *self.vertexCoords(nextVert), anchor=W,
                            text=' {}'.format(nextVert),
                            font=self.ADJACENCY_MATRIX_FONT)
                        toMove = (pathCostCopy, nextVertCopy)
                        costCellCoords = costs.cellAndCenters(
                            adjVertexIndexInCosts, rows=2)
                        moveTo = (costCellCoords[2],) * 2
                        if not adjVertexInCosts:
                            toMove += (self.canvas.copyItem(
                                self.vertices[adjVertex].items[1]),)
                            moveTo += (costCellCoords[1],)
                        callEnviron |= set(toMove)
                        self.moveItemsTo(toMove, moveTo, sleepTime=wait / 10)
                        costTuple = (pathCost, nextVert)
                        if adjVertexInCosts:
                            self.canvas.itemConfig(
                                costs[adjVertexIndexInCosts].items[2],
                                text=str(costTuple))
                            costs[adjVertexIndexInCosts].val = (
                                adjVertex, *costTuple)
                        else:
                            costs.append(drawnValue(
                                (adjVertex, *costTuple),
                                *self.createCostsTableEntry(
                                    costs, adjVertex, costTuple,
                                    color=self.canvas.itemConfig(
                                        self.vertices[adjVertex].items[0],
                                        'fill'))))
                            newItems = (costs.items()[-1], *costs[-1].items)
                            callEnviron |= set(newItems)
                            localVars += newItems
                            faded += (Scrim.FADED_OUTLINE,
                                      *((Scrim.FADED_FILL,) *
                                        len(costs[-1].items)))
                        self.dispose(callEnviron, *toMove)

                self.highlightCode('adj in self.adjacentVertices(nextVert)',
                                   callEnviron, wait=wait)
                colors = self.canvas.fadeItems(localVars, faded)
            
            self.canvas.restoreItems(localVars, colors, top=False)
            
            self.highlightCode('end not in visited', callEnviron, wait=wait)
            
        self.highlightCode('path = []', callEnviron, wait=wait)
        self.dispose(callEnviron,
                     *costsNextVertArrow, *nextVertArrow,
                     *(adjArrow if adjArrow else ()))
        path = Table(
            self, (costs.x0, costs.y0 + costs.cellHeight + 5),
            label='path', labelAnchor=E, vertical=False,
            labelFont=self.VARIABLE_FONT, cellWidth=self.vertexTable.cellWidth,
            cellHeight=self.vertexTable.cellHeight, see=True,
            cellBorderWidth=self.vertexTable.cellBorderWidth)

        self.highlightCode('end in visited', callEnviron, wait=wait)
        endIndexInCosts = (
            costVertices.index(endVert) if endVert in costVertices else -1)
        if costsAdjArrow:
            self.canvas.itemConfig(costsAdjArrow[1], text='end')
            self.moveItemsTo(
                costsAdjArrow,
                costs.labeledArrowCoords(endIndexInCosts, **adjArrowConfig),
                sleepTime=0, steps=1)
        else:
            costs.createLabeledArrow(endIndexInCosts, 'end', **adjArrowConfig)
        while visited[end].val:
            self.highlightCode('path.append(end)', callEnviron, wait=wait)
            copies = tuple(self.canvas.copyItem(i)
                           for i in self.vertexTable[end].items)
            callEnviron |= set(copies)
            self.moveItemsTo(copies, path.cellAndCenters(len(path)),
                             sleepTime=wait / 10)
            path.append(drawnValue(endVert, *copies))
            callEnviron |= set(path.items())
            if len(path) > 1:
                edge = tuple(d.val for d in path[-2:])
                treeEdgeHighlight = self.canvas.create_line(
                    *self.canvas.coords(self.edges[edge].items[0]),
                    fill=self.HIGHLIGHTED_EDGE_COLOR, tags=SPtags,
                    width=self.HIGHLIGHTED_EDGE_WIDTH)
                self.canvas.lower(treeEdgeHighlight, 'edge')
                callEnviron.add(treeEdgeHighlight)
            
            self.highlightCode('end == start', callEnviron, wait=wait)
            if end == start:
                self.highlightCode(('break', 2), callEnviron, wait=wait)
                break
            
            self.highlightCode('end = costs[end][1]', callEnviron, wait=wait)
            endVert = costs[endIndexInCosts].val[2]
            end = self.getVertexIndex(endVert)
            endIndexInCosts = costVertices.index(endVert)
            self.moveItemsTo(
                endArrow + endVertArrow + costsAdjArrow,
                self.vertexTable.labeledArrowCoords(end, **endArrowConfig) +
                self.labeledArrowCoords(endVert, **vertArrowConfig) +
                costs.labeledArrowCoords(endIndexInCosts, **adjArrowConfig),
                sleepTime=wait / 10)

            self.highlightCode('end in visited', callEnviron, wait=wait)
        
        self.highlightCode('list(reversed(path))', callEnviron, wait=wait)
        self.cleanUp(callEnviron)
        return [d.val for d in reversed(path)]

    def createCostsTableEntry(
            self, costs, vertex, values, color='white', index=None,
            tags='costs'):
        if index is None: index = len(costs)
        coords = self.costsTableCoords(costs, index)
        rect = self.canvas.create_rectangle(
            *coords[0], outline='', width=0, fill=color, tags=tags)
        vertLabel = self.canvas.create_text(
            *coords[1], text=vertex, font=self.ADJACENCY_MATRIX_FONT, tags=tags)
        valuesLabel = self.canvas.create_text(
            *coords[2], text=str(values), font=self.ADJACENCY_MATRIX_FONT,
            tags=tags)
        return rect, vertLabel, valuesLabel

    def costsTableCoords(self, costs, index):
        coords = costs.cellAndCenters(index, rows=2)
        center = costs.cellCenter(index)
        return (*coords[0][:3], center[1]), coords[1], coords[2]
        
        
    def enableButtons(self, enable=True):
        super(type(self).__bases__[0], self).enableButtons( # Grandparent
            enable)
        for btn in (self.depthFirstTraverseButton, 
                    self.breadthFirstTraverseButton, self.MSTButton):
            widgetState( # these operations need 1 selected vertex
                btn,
                NORMAL if enable and self.selectedVertices[0] else DISABLED)
        for btn in (self.shortestPathButton,):
            widgetState( # these operations need 2 selected vertices
                btn,
                NORMAL if enable and all(self.selectedVertices[:2]) else
                DISABLED)

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
        self.shortestPathButton = self.addOperation(
            "Shortest Path", self.clickShortestPath,
            helpText='Find the shortest path connecting 2 vertices',
            state=DISABLED)
        self.addAnimationButtons()

    def clickShortestPath(self):
        if all(self.selectedVertices):
            path = self.shortestPath(self.selectedVertices[0][0],
                                     self.selectedVertices[1][0],
                                     startAnimations=self.startMode())
            self.setMessage('Shortest path: ' + ' '.join(path) if path else
                            'No path found')
        else:
            self.setMessage('Must select start and end vertices to find path')
            
if __name__ == '__main__':
    graph = WeightedGraph()
    graph.process_command_line_arguments(sys.argv[1:])
        
    graph.runVisualization()
