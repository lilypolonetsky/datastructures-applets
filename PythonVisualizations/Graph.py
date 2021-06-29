from tkinter import *
import re

try:
    from GraphBase import *
    from TableDisplay import *
    from OutputBox import *
except ModuleNotFoundError:
    from .GraphBase import *
    from .TableDisplay import *
    from .OutputBox import *

V = vector

class Graph(GraphBase):
    VISITED_SYMBOLS = {False: 'F' , 0: 'F', True: 'T', 1: 'T'}
    VISITED_COLORS = {False: 'light coral' , 0: 'light coral' , 
                      True: 'green3', 1: 'green3'}
    VISITED_HIGHLIGHT_COLOR = 'yellow'

    def vertexIndices(self):
      return range(self.nVertices()) # Same as range up to nVertices

    adjacentVerticesCode = '''
def adjacentVertices(self, n={nVal}):
   self.validIndex(n)
   for j in self.vertices():
      if j != n and self.hasEdge(n, j):
         yield j
'''
    
    def adjacentVertices(self, n, code=adjacentVerticesCode, wait=0.1):
        nLabel = self.vertexTable[n].val if n < len(self.vertexTable) else None
        nVal = "{} ('{}')".format(n, nLabel)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()))

        nArrowConfig = {'level': 1, 'anchor': SE}
        if code:
            nArrow = self.vertexTable.createLabeledArrow(n, 'n', **nArrowConfig)
            callEnviron |= set(nArrow)
            self.highlightCode('self.validIndex(n)', callEnviron, wait=wait)
            self.highlightCode('j in self.vertices()', callEnviron, wait=wait)
        
        jArrowConfig = {'level': 2, 'anchor': SE}
        jArrow = None
        for j in self.vertexIndices():
            if code:
                if jArrow is None:
                    jArrow = self.vertexTable.createLabeledArrow(
                        j, 'j', **jArrowConfig)
                    callEnviron |= set(jArrow)
                else:
                    self.moveItemsTo(
                        jArrow,
                        self.vertexTable.labeledArrowCoords(j, **jArrowConfig),
                        sleepTime=wait / 10)
                self.highlightCode('j != n', callEnviron, wait=wait)
                if j != n:
                    self.highlightCode('self.hasEdge(n, j)', callEnviron,
                                       wait=wait)
            jLabel = self.vertexTable[j].val
            if j != n and self.edgeWeight(nLabel, jLabel):
                if code:
                    self.highlightCode('yield j', callEnviron)
                    itemCoords = self.yieldCallEnvironment(callEnviron)
                yield j
                if code:
                    self.resumeCallEnvironment(callEnviron, itemCoords)
                    
            if code:
                self.highlightCode('j in self.vertices()', callEnviron,
                                   wait=wait)

        if code:
            self.highlightCode((), callEnviron)
        self.cleanUp(callEnviron)

    adjacentUnvisitedVerticesCode = '''
def adjacentUnvisitedVertices(
      self, n={nVal}, visited, markVisits={markVisits}):
   for j in self.adjacentVertices(n):
      if not visited[j]:
         if markVisits:
            visited[j] = True
         yield j
'''

    def adjacentUnvisitedVertices(
            self, n, visited, markVisits=True,
            code=adjacentUnvisitedVerticesCode, wait=0.1):
        nLabel = self.vertexTable[n].val if n < len(self.vertexTable) else None
        nVal = "{} ('{}')".format(n, nLabel)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()))

        nArrowConfig = {'level': 1, 'anchor': SE}
        if code:
            nArrow = self.vertexTable.createLabeledArrow(n, 'n', **nArrowConfig)
            callEnviron |= set(nArrow)
            localVars = nArrow
        
            self.highlightCode('j in self.adjacentVertices(n)', callEnviron,
                               wait=wait)
            colors = self.fadeNonLocalItems(localVars)
        
        jArrowConfig = {'level': 2, 'anchor': SE}
        jArrow = None
        for j in self.adjacentVertices(
                n, code=self.adjacentVerticesCode if code else '', wait=wait):
            if code:
                self.restoreLocalItems(localVars, colors)
                if jArrow is None:
                    jArrow = self.vertexTable.createLabeledArrow(
                        j, 'j', **jArrowConfig)
                    callEnviron |= set(jArrow)
                    localVars += jArrow
                else:
                    self.moveItemsTo(
                        jArrow,
                        self.vertexTable.labeledArrowCoords(j, **jArrowConfig),
                        sleepTime=wait / 10)
                self.canvas.itemconfigure(visited[j].items[0], width=2)
                self.highlightCode('not visited[j]', callEnviron, wait=wait)
                self.canvas.itemconfigure(visited[j].items[0], width=0)
                if not visited[j].val:
                    self.highlightCode(('markVisits', 2), callEnviron,
                                       wait=wait)
                    
            if not visited[j].val:
                if markVisits:
                    if code:
                        self.highlightCode('visited[j] = True', callEnviron, 
                                           wait=wait)
                    visited[j].val = True
                    if code:
                        self.updateVisitedCells(visited, j)
                
                if code:
                    self.highlightCode('yield j', callEnviron)
                    itemCoords = self.yieldCallEnvironment(callEnviron)
                yield j
                if code:
                    self.resumeCallEnvironment(callEnviron, itemCoords)
                    
            if code:
                self.highlightCode('j in self.adjacentVertices(n)', callEnviron,
                                   wait=wait)
                colors = self.fadeNonLocalItems(localVars)

        if code:
            self.restoreLocalItems(localVars, colors)
            self.highlightCode((), callEnviron)
        self.cleanUp(callEnviron)

    depthFirstCode = '''
def depthFirst(self, n={nVal}):
   self.validIndex(n)
   visited = [False] * self.nVertices()
   stack = Stack()
   stack.push(n)
   visited[n] = True
   yield (n, stack)
   while not stack.isEmpty():
      visit = stack.peek()
      adj = None
      for j in self.adjacentUnvisitedVertices(
         visit, visited):
         adj = j
         break
      if adj is not None:
         stack.push(adj)
         yield (adj, stack)
      else:
         stack.pop()
'''
    innerLoopIterator = re.compile(
        r'j in self.adjacentUnvisitedVertices.\n.* visited\)')

    def depthFirst(self, n, code=depthFirstCode, wait=0.1):
        nLabel = (n if isinstance(n, str) else
                  self.vertexTable[n].val if n < len(self.vertexTable) else
                  None)
        n = n if isinstance(n, int) else self.getVertexIndex(n)
        nVal = "{} ('{}')".format(n, nLabel)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()))

        nArrowConfig = {'level': 1, 'anchor': SE}
        nArrow = self.vertexTable.createLabeledArrow(n, 'n', **nArrowConfig)
        callEnviron |= set(nArrow)
        localVars = nArrow
        
        if code:
            self.highlightCode('self.validIndex(n)', callEnviron, wait=wait)
            self.highlightCode('visited = [False] * self.nVertices()',
                               callEnviron, wait=wait)
        visited = self.createVisitedTable(
            self.nVertices(), initialValue=False, visible=code)
        if code:
            callEnviron |= set(flat(*(dv.items for dv in visited)) +
                               visited.items())
            self.highlightCode('stack = Stack()', callEnviron, wait=wait)

        stack = Table(
            self, (50, self.graphRegion[3] + 20),
            label='stack', vertical=False, cellHeight=self.VERTEX_RADIUS,
            labelFont=(self.VARIABLE_FONT[0], -12),
            cellWidth=self.VERTEX_RADIUS * 3 // 2,
            cellBorderWidth=1 if code else 0)
        callEnviron |= set(stack.items())

        if code:
            self.highlightCode('stack.push(n)', callEnviron, wait=wait)
            copyItems = tuple(self.copyCanvasItem(item)
                              for item in self.vertexTable[n].items)
            callEnviron |= set(copyItems)
            self.moveItemsLinearly(
                copyItems, 
                (stack.cellCoords(len(stack)), stack.cellCenter(len(stack))),
                sleepTime=wait / 10)
        stack.append(drawnValue(nLabel))
        if code:
            stack[-1].items = copyItems
            callEnviron |= set(stack[-1].items + stack.items())

            self.highlightCode('visited[n] = True', callEnviron, wait=wait)

        visited[n].val = True
        if code:
            self.updateVisitedCells(visited, n)
            self.highlightCode('yield (n, stack)', callEnviron)
            itemCoords = self.yieldCallEnvironment(callEnviron)
        yield n, stack
        if code:
            self.resumeCallEnvironment(callEnviron, itemCoords)
            self.highlightCode('not stack.isEmpty()', callEnviron)

        visitArrow = None
        visitArrowConfig = {'level': 1, 'orientation': -30, 'anchor': SE}
        jArrowConfig = {'level': 2, 'anchor': SE}
        vertArrow, adjArrow, jArrow = None, None, None
        adjArrowConfig = {'level': 1, 'orientation': -30, 'anchor': SW}
        lowerRight = V(self.graphRegion[2:]) + V((self.VERTEX_RADIUS,) * 2)
        while len(stack) > 0:
            visitLabel = stack[-1].val
            visit = self.getVertexIndex(visitLabel)
            if code:
                self.highlightCode('visit = stack.peek()', callEnviron,
                                   wait=wait)
                if visitArrow is None:
                    visitArrow = stack.createLabeledArrow(
                        len(stack) - 1, 'visit', **visitArrowConfig)
                    vertArrow = self.createLabeledArrow(
                        visitLabel, 'visit', **visitArrowConfig)
                    callEnviron |= set(visitArrow + vertArrow)
                    localVars += visitArrow + vertArrow
                else:
                    self.moveItemsTo(
                        visitArrow + vertArrow,
                        stack.labeledArrowCoords(len(stack) - 1, 
                                                 **visitArrowConfig) +
                        self.labeledArrowCoords(visit, **visitArrowConfig),
                        sleepTime=wait / 10)

            adj = None
            if code:
                self.highlightCode('adj = None', callEnviron, wait=wait)
                if adjArrow is None:
                    adjArrow = self.createLabeledArrow(
                        lowerRight, 'adj', **adjArrowConfig)
                    callEnviron |= set(adjArrow)
                    localVars += adjArrow
                else:
                    self.moveItemsTo(
                        adjArrow, self.labeledArrowCoords(lowerRight,
                                                          **adjArrowConfig),
                        sleepTime=wait / 10)
                self.highlightCode(self.innerLoopIterator, callEnviron,
                                   wait=wait)
                colors = self.fadeNonLocalItems(localVars)

            for j in self.adjacentUnvisitedVertices(
                    visit, visited, wait=wait,
                    code=self.adjacentUnvisitedVerticesCode if code else ''):
                adj = j
                adjVertex = self.vertexTable[j].val
                if code:
                    self.restoreLocalItems(localVars, colors)
                    if jArrow is None:
                        jArrow = self.vertexTable.createLabeledArrow(
                            j, 'j', **jArrowConfig)
                        callEnviron |= set(jArrow)
                        localVars += jArrow
                        colors += tuple(self.canvas_itemConfig(i, 'fill')
                                        for i in jArrow)
                    else:
                        self.moveItemsTo(
                            jArrow, self.vertexTable.labeledArrowCoords(
                                j, **jArrowConfig),
                            sleepTime=wait / 10)
                    self.highlightCode('adj = j', callEnviron, wait=wait)
                    self.moveItemsTo(
                        adjArrow, self.labeledArrowCoords(adjVertex,
                                                          **adjArrowConfig),
                        sleepTime=wait / 10)
                    self.highlightCode('break', callEnviron, wait=wait)
                break

            if code:
                self.restoreLocalItems(localVars, colors)
                self.highlightCode('adj is not None', callEnviron, wait=wait)
                if adj is not None:
                    self.highlightCode('stack.push(adj)', callEnviron,
                                       wait=wait)
            if adj is not None:
                stack.append(drawnValue(adjVertex))
                if code:
                    copyItems = tuple(self.copyCanvasItem(i)
                                      for i in self.vertexTable[adj].items)
                    callEnviron |= set(copyItems + stack.items())
                    self.moveItemsLinearly(
                        copyItems,
                        (stack.cellCoords(len(stack) - 1),
                         stack.cellCenter(len(stack) - 1)),
                        sleepTime=wait / 10)
                    stack[-1].items = copyItems
                    self.highlightCode('yield (adj, stack)', callEnviron)
                    itemCoords = self.yieldCallEnvironment(callEnviron)
                yield adj, stack
                if code:
                    self.resumeCallEnvironment(callEnviron, itemCoords)
                    
            else:
                if code:
                    self.highlightCode('stack.pop()', callEnviron, wait=wait)
                    self.moveItemsOffCanvas(
                        stack[-1].items, edge=S, sleepTime=wait / 10)
                    self.dispose(callEnviron, stack[-1].items)
                stack.pop()

            if code:
                self.highlightCode('not stack.isEmpty()', callEnviron)

        if code:
            self.highlightCode((), callEnviron)
        self.cleanUp(callEnviron)

    def createVisitedTable(self, size, initialValue=False, visible=True,
                           gap=5, tags=('visited',)):
        visited = Table(
            self, (self.vertexTable.x0 + self.vertexTable.cellWidth + gap,
                   self.vertexTable.y0),
            *[drawnValue(initialValue) for k in range(size)],
            label='visited', labelAnchor=SW, vertical=True, 
            labelFont=self.vertexTable.labelFont, 
            cellWidth=self.vertexTable.cellHeight,
            cellHeight=self.vertexTable.cellHeight, cellBorderWidth=1)
        if visible:
            for j, dValue in enumerate(visited):
                dValue.items = (
                    self.canvas.create_rectangle(
                        *visited.cellCoords(j), 
                        fill=self.VISITED_COLORS[initialValue], width=0,
                        outline=self.VISITED_HIGHLIGHT_COLOR, tags=tags),
                    self.canvas.create_text(
                        *visited.cellCenter(j),
                        text=self.VISITED_SYMBOLS[initialValue], 
                        font=self.ADJACENCY_MATRIX_FONT, tags=tags))
        return visited

    def updateVisitedCells(self, visited, index=None):
        for v in visited[0 if index is None else index:
                         len(visited) if index is None else index + 1]:
            self.canvas.itemconfigure(
                v.items[0], fill=self.VISITED_COLORS[v.val])
            self.canvas.itemconfigure(
                v.items[1], text=self.VISITED_SYMBOLS[v.val])
            
    breadthFirstCode = '''
def breadthFirst(self, n={nVal}):
   self.validIndex(n)
   visited = [False] * self.nVertices()
   queue = Queue()
   queue.insert(n)
   visited[n] = True
   while not queue.isEmpty():
      visit = queue.remove()
      yield visit
      for j in self.adjacentUnvisitedVertices(
            visit, visited):
         queue.insert(j)
'''

    def breadthFirst(self, n, code=breadthFirstCode, wait=0.1):
        nLabel = self.vertexTable[n].val if n < len(self.vertexTable) else None
        nVal = "{} ('{}')".format(n, nLabel)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()))

        nArrowConfig = {'level': 1, 'anchor': SE}
        nArrow = self.vertexTable.createLabeledArrow(n, 'n', **nArrowConfig)
        callEnviron |= set(nArrow)
        
        if code:
            self.highlightCode('self.validIndex(n)', callEnviron, wait=wait)
        self.cleanUp(callEnviron)

    traverseExampleCode = '''
for vertex{vars} in graph.{order}First(start={startVal}):
   print(graph.getVertex(vertex))
'''
    
    def traverseExample(self, order, startVertex, code=traverseExampleCode,
                        start=True, wait=0.1):
        orderings = ('breadth', 'depth')
        if order not in orderings:
            raise ValueError('Traverse order must be in {}'.format(orderings))
        startVal = "{} ('{}')".format(
            self.getVertexIndex(startVertex), startVertex)
        vars = '' if order == 'breadth' else ', stack'
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)

        visible = self.visibleCanvas()
        outputBox = OutputBox(
            self, bbox=(self.graphRegion[2] - 250, visible[3] - 40,
                        self.graphRegion[2], visible[3] - 10),
            outputFont=(self.VALUE_FONT[0], -16))
        callEnviron |= set(outputBox.items())
        
        iterator = (
            'vertex{vars} in graph.{order}First(start={startVal})'.format(
                **locals()))
        vertexArrow, vertexArrowConfig, localVars, colors = None, {}, (), {}
        self.highlightCode(iterator, callEnviron, wait=wait)

        for thing in (
                self.depthFirst if order == 'depth' else self.breadthFirst)(
                    startVertex, wait=wait):
            self.restoreLocalItems(localVars, colors)
            vertex = thing[0] if order == 'depth' else thing
            vertexLabel = self.vertexTable[vertex].val
            path = thing[1] if order == 'depth' else ()
            edgesInPath = [
                self.edges[path[v].val, path[v + 1].val].items[0]
                for v in range(len(path) - 1)]
            if vertexArrow is None:
                vertexArrow = self.vertexTable.createLabeledArrow(
                    vertex, 'vertex', **vertexArrowConfig)
                callEnviron |= set(vertexArrow)
                localVars += vertexArrow
            else:
                self.moveItemsTo(
                    vertexArrow, 
                    self.vertexTable.labeledArrowCoords(
                        vertex, **vertexArrowConfig), sleepTime=wait / 10)
            for edge in edgesInPath:
                self.canvas.itemconfigure(
                    edge, width=self.ACTIVE_EDGE_WIDTH,
                    fill=self.ACTIVE_EDGE_COLOR)
            self.highlightCode('print(graph.getVertex(vertex))', callEnviron,
                               wait=wait)
            copy = self.copyCanvasItem(self.vertices[vertexLabel].items[1])
            callEnviron.add(copy)
            outputBox.appendText(copy, sleepTime=wait / 10)

            self.highlightCode(iterator, callEnviron, wait=wait)
            for edge in edgesInPath:
                self.canvas.itemconfigure(
                    edge, width=self.EDGE_WIDTH, fill=self.EDGE_COLOR)
            colors = self.fadeNonLocalItems(localVars)
            
        if code:
            self.highlightCode((), callEnviron, wait=wait)
        self.cleanUp(callEnviron)
    
    def enableButtons(self, enable=True):
        super().enableButtons(enable)
        for btn in (self.depthFirstTraverseButton, 
                    self.breadthFirstTraverseButton):
            self.widgetState( # can only traverse when start node selected
                btn,
                NORMAL if enable and self.selectedVertex else DISABLED)

    def makeButtons(self, *args, **kwargs):
        '''Make buttons specific to unweighted graphs and aadd the
        animation control buttons'''
        vcmd = super().makeButtons(*args, **kwargs)
        self.depthFirstTraverseButton = self.addOperation(
            "Depth-first Traverse", self.clickDepthFirstTraverse,
            helpText='Traverse graph in depth-first order', state=DISABLED)
        self.breadthFirstTraverseButton = self.addOperation(
            "Breadth-first Traverse", self.clickBreadthFirstTraverse,
            helpText='Traverse graph in breadth-first order', state=DISABLED)
        self.addAnimationButtons()

    def clickDepthFirstTraverse(self):
        if self.selectedVertex:
            self.traverseExample('depth', self.selectedVertex[0],
                                 start=self.startMode())
        else:
            self.setMessage('Must select start vertex before traversal')

    def clickBreadthFirstTraverse(self):
        if self.selectedVertex:
            self.setMessage('BF Traverse TBD')
            # self.traverseExample('breadth', self.selectedVertex[0],
            #                      start=self.startMode())
        else:
            self.setMessage('Must select start vertex before traversal')
        
if __name__ == '__main__':
    graph = Graph(weighted=False)
    edgePattern = re.compile(r'(\w+)-(\w+)')

    edges = []
    for arg in sys.argv[1:]:
        edgeMatch = edgePattern.match(arg)
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
            edges.append((edgeMatch.group(1), edgeMatch.group(2)))
        else:
            graph.setArgument(arg)
            graph.newVertexButton.invoke()
    for fromVert, toVert in edges:
        graph.createEdge(fromVert, toVert, 1)
        
    graph.runVisualization()
