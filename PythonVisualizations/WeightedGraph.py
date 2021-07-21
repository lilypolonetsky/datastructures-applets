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
    def __init__(self, title='Weighted Graph', **kwargs):
        super().__init__(title=title, weighted=True)
        
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
        nArrow = self.vertexTable.createLabeledArrow(
            n, 'n', see=True, **nArrowConfig)
        callEnviron |= set(nArrow)
        localVars, faded = nArrow, (Scrim.FADED_FILL,) * len(nArrow)
        
        self.highlightCode('self.validIndex(n)', callEnviron, wait=wait)
        self.highlightCode('tree = WeightedGraph()', callEnviron, wait=wait)
        treeLabelAnchor = (70, self.graphRegion[3] + 60)
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
        
        self.highlightCode('vMap = [None] * self.nVertices()', callEnviron,
                           wait=wait)
        vMap = Table(
            self, (self.vertexTable.x0 + self.vertexTable.cellWidth + 5,
                   self.vertexTable.y0),
            *[drawnValue(None) for k in range(self.nVertices())],
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
        
        vertexArrow, vertexArrowConfig = None, {}
        vertexVertArrow = None
        vertexVertConfig = {'orientation': 30, 'anchor': SW}
        self.highlightCode('vertex, path in self.depthFirst(n)', callEnviron,
                           wait=wait)
        colors = self.canvas.fadeItems(localVars, faded)
        for vertex, path in self.depthFirst(n):
            self.canvas.restoreItems(localVars, colors, top=False)
            vertexLabel = self.vertexTable[vertex].val
            edgesInPath = [
                self.edges[path[v].val, path[v + 1].val].items[0]
                for v in range(len(path) - 1)]
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
            for edge in edgesInPath:
                self.canvas.itemconfigure(
                    edge, width=self.ACTIVE_EDGE_WIDTH,
                    fill=self.ACTIVE_EDGE_COLOR)

            self.highlightCode('vMap[vertex] = tree.nVertices()', callEnviron,
                               wait=wait)
            vMapArrow = self.createVMapArrow(vMap, len(treeVerts), vertex,
                                             see=True)
            vMap[len(treeVerts)] = drawnValue(vertexLabel, *vMapArrow)
            callEnviron |= set(vMapArrow)
            localVars += vMapArrow
            faded += (Scrim.FADED_FILL,) * len(vMapArrow)

            self.highlightCode('tree.addVertex(self.getVertex(vertex))',
                               callEnviron, wait=wait)
            vertCoords = self.canvas.coords(self.vertices[vertexLabel].items[1])
            if len(treeVerts) == 0:
                inflection = V(treeLabelAnchor) + V(300, 0)
                tipCoords = self.labeledArrowCoords(
                    vertexLabel,
                    orientation=V(V(inflection) - V(vertCoords)).orient2d() +
                    90)[0][2:]
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
            self.canvas.tag_lower(treeVertHighlight,
                                  self.vertices[vertexLabel].items[0])
            copies = tuple(self.canvas.copyItem(item) 
                           for item in self.vertexTable[vertex].items)
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
            
            self.highlightCode('len(path) > 1', callEnviron, wait=wait)
            if len(path) > 1:
                self.highlightCode(
                    'tree.addEdge(vMap[path[-2]], vMap[path[-1]])', callEnviron,
                    wait=wait)
                coords = self.canvas.coords(edgesInPath[-1])
                delta = V(coords[:2]) - V(coords[-2:])
                treeEdgeHighlight = self.canvas.create_line(
                    *coords, smooth=True, tags=MSTtags,
                    splinesteps=int(max(abs(delta[0]), abs(delta[1]), 5)),
                    fill=self.HIGHLIGHTED_EDGE_COLOR,
                    width=self.HIGHLIGHTED_EDGE_WIDTH)
                self.canvas.lower(treeEdgeHighlight, edgesInPath[-1])
                callEnviron.add(treeEdgeHighlight)
                localVars, faded = (*localVars, treeEdgeHighlight), (
                    *faded, Scrim.FADED_FILL)
                treeEdges.append(drawnValue(edgesInPath[-1], treeEdgeHighlight))
                
            self.highlightCode(
                'vertex, path in self.depthFirst(n)', callEnviron, wait=wait)
            for edge in edgesInPath:
                self.canvas.itemConfig(
                    edge, width=self.EDGE_WIDTH, fill=self.EDGE_COLOR)
            colors = self.canvas.fadeItems(localVars, faded)
            
        self.canvas.restoreItems(localVars, colors, top=False)
            
        self.highlightCode('return tree', callEnviron, wait=wait)
        self.cleanUp(callEnviron)
    
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
