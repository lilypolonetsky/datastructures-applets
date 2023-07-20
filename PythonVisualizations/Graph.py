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
    ADJ_MAT_HIGHLIGHT_PAD = 5
    HIGHLIGHTED_VERTEX_RADIUS = GraphBase.SELECTED_RADIUS + 2
    HIGHLIGHTED_VERTEX_WIDTH = 3
    HIGHLIGHTED_VERTEX_COLOR = 'chocolate2'
    HIGHLIGHTED_EDGE_WIDTH = 5
    HIGHLIGHTED_EDGE_COLOR = 'chocolate2'

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
        nVertConfig = {'level': 1, 'orientation': 10, 'anchor': SW}
        if code:
            nArrow = self.vertexTable.createLabeledArrow(
                n, 'n', see=True, **nArrowConfig)
            nVertArrow = self.createLabeledArrow(
                nLabel, 'n', see=True, **nVertConfig)
            callEnviron |= set(nArrow + nVertArrow)
            self.highlightCode('self.validIndex(n)', callEnviron, wait=wait)
            self.highlightCode('j in self.vertices()', callEnviron, wait=wait)
        
        jArrowConfig = {'level': 2, 'anchor': SE}
        jVertConfig = {'level': 1, 'orientation': 40, 'anchor': SW}
        jArrow, jVertArrow = None, None
        for j in self.vertexIndices():
            jLabel = self.vertexTable[j].val
            if code:
                if jArrow is None:
                    jArrow = self.vertexTable.createLabeledArrow(
                        j, 'j', see=True, **jArrowConfig)
                    jVertArrow = self.createLabeledArrow(
                        jLabel, 'j', see=True, **jVertConfig)
                    callEnviron |= set(jArrow + jVertArrow)
                else:
                    self.moveItemsTo(
                        jArrow + jVertArrow,
                        self.vertexTable.labeledArrowCoords(j, **jArrowConfig) +
                        self.labeledArrowCoords(jLabel, **jVertConfig),
                        sleepTime=wait / 10, see=True, expand=True)
                self.highlightCode('j != n', callEnviron, wait=wait)
                if j != n:
                    edgeEntry = self.adjMat[nLabel, jLabel][1] # Highlight adj
                    edgeEntry.grid(padx=self.ADJ_MAT_HIGHLIGHT_PAD, # mat edge
                                   pady=self.ADJ_MAT_HIGHLIGHT_PAD)
                    self.highlightCode('self.hasEdge(n, j)', callEnviron,
                                       wait=wait)
                    edgeEntry.grid(padx=0, pady=0)
                    
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
        nVertConfig = {'level': 1, 'orientation': 10, 'anchor': SW}
        if code:
            nArrow = self.vertexTable.createLabeledArrow(
                n, 'n', see=True, **nArrowConfig)
            nVertArrow = self.createLabeledArrow(
                nLabel, 'n', see=True, **nVertConfig)
            callEnviron |= set(nArrow + nVertArrow)
            localVars = nArrow + nVertArrow
        
            self.highlightCode('j in self.adjacentVertices(n)', callEnviron,
                               wait=wait)
            colors = self.canvas.fadeItems(localVars)
        
        jArrowConfig = {'level': 2, 'anchor': SE}
        jVertConfig = {'level': 1, 'orientation': 40, 'anchor': SW}
        jArrow, jVertArrow = None, None
        for j in self.adjacentVertices(
                n, code=self.adjacentVerticesCode if code else '', wait=wait):
            if code:
                self.canvas.restoreItems(localVars, colors)
                if jArrow is None:
                    jArrow = self.vertexTable.createLabeledArrow(
                        j, 'j', see=True, **jArrowConfig)
                    jVertArrow = self.createLabeledArrow(
                        self.vertexTable[j].val, 'j', see=True, **jVertConfig)
                    callEnviron |= set(jArrow + jVertArrow)
                    localVars += jArrow + jVertArrow
                else:
                    self.moveItemsTo(
                        jArrow + jVertArrow,
                        self.vertexTable.labeledArrowCoords(j, **jArrowConfig) +
                        self.labeledArrowCoords(self.vertexTable[j].val,
                                                **jVertConfig),
                        sleepTime=wait / 10, see=True, expand=True)
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
                colors = self.canvas.fadeItems(localVars)

        if code:
            self.canvas.restoreItems(localVars, colors)
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
        nArrow = self.vertexTable.createLabeledArrow(
            n, 'n', see=True, **nArrowConfig)
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
            cellWidth=self.VERTEX_RADIUS * 3 // 2, see=True if code else (),
            cellBorderWidth=1 if code else 0)
        callEnviron |= set(stack.items())

        if code:
            self.highlightCode('stack.push(n)', callEnviron, wait=wait)
            copyItems = tuple(self.canvas.copyItem(item)
                              for item in self.vertices[nLabel].items)
            callEnviron |= set(copyItems)
            self.moveItemsLinearly(
                copyItems, 
                (stack.cellCoords(len(stack)), stack.cellCenter(len(stack))),
                sleepTime=wait / 10, endFont=self.ADJACENCY_MATRIX_FONT,
                startFont=self.canvas.getItemFont(copyItems[1]), see=True,
                expand=True)
        stack.append(drawnValue(nLabel))
        if code:
            stack[-1].items = (
                self.canvas.create_rectangle(
                    *stack.cellCoords(len(stack) - 1),
                    fill=self.canvas_itemConfig(copyItems[0], 'fill'),
                    width=0),
                copyItems[1])
            self.canvas.tag_lower(*stack[-1].items)
            callEnviron |= set(stack[-1].items + stack.items())
            self.dispose(callEnviron, copyItems[0])

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
        visitArrowConfig = {'level': 1, 'orientation': -50, 'anchor': SE}
        jArrowConfig = {'level': 2, 'anchor': SE}
        jVertConfig = {'level': 1, 'orientation': 40, 'anchor': SW}
        vertArrow, adjArrow, jArrow, jVertArrow = None, None, None, None
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
                        len(stack) - 1, 'visit', see=True, **visitArrowConfig)
                    vertArrow = self.createLabeledArrow(
                        visitLabel, 'visit', see=True, **visitArrowConfig)
                    callEnviron |= set(visitArrow + vertArrow)
                    localVars += visitArrow + vertArrow
                else:
                    self.moveItemsTo(
                        visitArrow + vertArrow,
                        stack.labeledArrowCoords(len(stack) - 1, 
                                                 **visitArrowConfig) +
                        self.labeledArrowCoords(visit, **visitArrowConfig),
                        sleepTime=wait / 10, see=True, expand=True)

            adj = None
            if code:
                self.highlightCode('adj = None', callEnviron, wait=wait)
                if adjArrow is None:
                    adjArrow = self.createLabeledArrow(
                        lowerRight, 'adj', see=True, **adjArrowConfig)
                    callEnviron |= set(adjArrow)
                    localVars += adjArrow
                else:
                    self.moveItemsTo(
                        adjArrow, self.labeledArrowCoords(lowerRight,
                                                          **adjArrowConfig),
                        sleepTime=wait / 10, see=True, expand=True)
                self.highlightCode(self.innerLoopIterator, callEnviron,
                                   wait=wait)
                colors = self.canvas.fadeItems(localVars)

            for j in self.adjacentUnvisitedVertices(
                    visit, visited, wait=wait,
                    code=self.adjacentUnvisitedVerticesCode if code else ''):
                adj = j
                adjVertex = self.vertexTable[j].val
                if code:
                    self.canvas.restoreItems(localVars, colors)
                    if jArrow is None:
                        jArrow = self.vertexTable.createLabeledArrow(
                            j, 'j', see=True, **jArrowConfig)
                        jVertArrow = self.createLabeledArrow(
                            adjVertex, 'j', see=True, **jVertConfig)
                        callEnviron |= set(jArrow + jVertArrow)
                        localVars += jArrow + jVertArrow
                        colors = self.canvas.itemsColor(localVars)
                    else:
                        self.moveItemsTo(
                            jArrow + jVertArrow,
                            self.vertexTable.labeledArrowCoords(
                                j, **jArrowConfig) +
                            self.labeledArrowCoords(adjVertex, **jVertConfig),
                            sleepTime=wait / 10, see=True, expand=True)
                    self.highlightCode('adj = j', callEnviron, wait=wait)
                    self.moveItemsTo(
                        adjArrow, self.labeledArrowCoords(adjVertex,
                                                          **adjArrowConfig),
                        sleepTime=wait / 10, see=True, expand=True)
                    self.highlightCode('break', callEnviron, wait=wait)
                break

            if code:
                self.canvas.restoreItems(localVars, colors)
                self.highlightCode('adj is not None', callEnviron, wait=wait)
                if adj is not None:
                    self.highlightCode('stack.push(adj)', callEnviron,
                                       wait=wait)
            if adj is not None:
                stack.append(drawnValue(adjVertex))
                if code:
                    copyItems = tuple(self.canvas.copyItem(i)
                                      for i in self.vertices[adjVertex].items)
                    callEnviron |= set(copyItems + stack.items())
                    self.moveItemsLinearly(
                        copyItems,
                        (stack.cellCoords(len(stack) - 1),
                         stack.cellCenter(len(stack) - 1)),
                        sleepTime=wait / 10,
                        startFont=self.canvas.getItemFont(copyItems[1]),
                        endFont=self.ADJACENCY_MATRIX_FONT, see=True,
                        expand=True)
                    stack[-1].items = (
                        self.canvas.create_rectangle(
                            *stack.cellCoords(len(stack) - 1),
                            fill=self.canvas_itemConfig(copyItems[0], 'fill'),
                            width=0),
                        copyItems[1])
                    self.canvas.tag_lower(*stack[-1].items)
                    callEnviron |= set(stack[-1].items)
                    self.dispose(callEnviron, copyItems[0])
                    
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
                           gap=5, tags=('visited',), see=(), expand=True):
        visited = Table(
            self, (self.vertexTable.x0 + self.vertexTable.cellWidth + gap,
                   self.vertexTable.y0),
            *[drawnValue(initialValue) for k in range(size)],
            label='visited', labelAnchor=SW, vertical=True, 
            labelFont=self.vertexTable.labelFont, 
            cellWidth=self.vertexTable.cellHeight, see=see,
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
            if see:
                self.scrollToSee(
                    dValue.items + visited.items() +
                    (tuple(see) if isinstance(see, (list, tuple, set)) else ()),
                    expand=expand)
                
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
        nLabel = (n if isinstance(n, str) else
                  self.vertexTable[n].val if n < len(self.vertexTable) else
                  None)
        n = n if isinstance(n, int) else self.getVertexIndex(n)
        nVal = "{} ('{}')".format(n, nLabel)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()))

        nArrowConfig = {'level': 1, 'anchor': SE}
        nArrow = self.vertexTable.createLabeledArrow(
            n, 'n', see=True, **nArrowConfig)
        callEnviron |= set(nArrow)
        localVars = nArrow
        
        if code:
            self.highlightCode('self.validIndex(n)', callEnviron, wait=wait)
            self.highlightCode('visited = [False] * self.nVertices()',
                               callEnviron, wait=wait)
        visited = self.createVisitedTable(
            self.nVertices(), see=True, initialValue=False, visible=code)
        if code:
            callEnviron |= set(flat(*(dv.items for dv in visited)) +
                               visited.items())
            self.highlightCode('queue = Queue()', callEnviron, wait=wait)

        queue = Table(
            self, (50, self.graphRegion[3] + 20),
            label='queue', vertical=False, cellHeight=self.VERTEX_RADIUS,
            labelFont=(self.VARIABLE_FONT[0], -12),
            cellWidth=self.VERTEX_RADIUS * 3 // 2, see=True if code else (),
            cellBorderWidth=1 if code else 0)
        callEnviron |= set(queue.items())

        if code:
            self.highlightCode('queue.insert(n)', callEnviron, wait=wait)
            copyItems = tuple(self.canvas.copyItem(item)
                              for item in self.vertices[nLabel].items)
            callEnviron |= set(copyItems)
            self.moveItemsLinearly(
                copyItems, 
                (queue.cellCoords(len(queue)), queue.cellCenter(len(queue))),
                sleepTime=wait / 10, endFont=self.ADJACENCY_MATRIX_FONT,
                startFont=self.canvas.getItemFont(copyItems[1]), see=True,
                expand=True)
        queue.append(drawnValue(nLabel))
        if code:
            queue[-1].items = (
                self.canvas.create_rectangle(
                    *queue.cellCoords(len(queue) - 1),
                    fill=self.canvas_itemConfig(copyItems[0], 'fill'),
                    width=0),
                copyItems[1])
            self.canvas.tag_lower(*queue[-1].items)
            callEnviron |= set(queue[-1].items + queue.items())
            self.dispose(callEnviron, copyItems[0])

            self.highlightCode('visited[n] = True', callEnviron, wait=wait)

        visited[n].val = True
        if code:
            self.updateVisitedCells(visited, n)
            self.highlightCode('not queue.isEmpty()', callEnviron)

        visitArrow, visitArrowConfig = None, {'orientation': -50, 'anchor': SE}
        jArrowConfig = {'level': 2, 'anchor': SE}
        jVertConfig = {'orientation': 40, 'anchor': SW}
        jArrow, jVertArrow = None, None
        lowerRight = V(self.graphRegion[2:]) + V((self.VERTEX_RADIUS,) * 2)
        while len(queue) > 0:
            visitLabel = queue[0].val
            visit = self.getVertexIndex(visitLabel)
            if code:
                self.highlightCode('visit = queue.remove()', callEnviron,
                                   wait=wait)
                if visitArrow is None:
                    visitArrow = queue.createLabeledArrow(
                        0, 'visit', see=True, **visitArrowConfig)
                    callEnviron |= set(visitArrow)
                    localVars += visitArrow
                else:
                    self.moveItemsTo(
                        visitArrow,
                        queue.labeledArrowCoords(len(queue) - 1, 
                                                 **visitArrowConfig),
                        sleepTime=wait / 10, see=True, expand=True)
                    
            visitDValue = queue.pop(0)
            if code:
                for item in visitDValue.items:
                    self.canvas.tag_lower(
                        item, self.vertices[visitLabel].items[0])
                self.moveItemsLinearly(
                    visitArrow + visitDValue.items + 
                    flat(*(dv.items for dv in queue)),
                    self.labeledArrowCoords(visitLabel, **visitArrowConfig) +
                    tuple(self.canvas_coords(item) 
                          for item in self.vertices[visitLabel].items) +
                    flat(*((queue.cellCoords(j), queue.cellCenter(j)) for
                           j in range(len(queue)))),
                    sleepTime=wait / 10, see=True, expand=True)
                self.dispose(callEnviron, *visitDValue.items)

                self.highlightCode('yield visit', callEnviron)
                itemCoords = self.yieldCallEnvironment(callEnviron)
                
            yield visit
            if code:
                self.resumeCallEnvironment(callEnviron, itemCoords)
                self.highlightCode(self.innerLoopIterator, callEnviron,
                                   wait=wait)
                colors = self.canvas.fadeItems(localVars)

            for j in self.adjacentUnvisitedVertices(
                    visit, visited, wait=wait,
                    code=self.adjacentUnvisitedVerticesCode if code else ''):
                adjVertex = self.vertexTable[j].val
                if code:
                    self.canvas.restoreItems(localVars, colors)
                    if jArrow is None:
                        jArrow = self.vertexTable.createLabeledArrow(
                            j, 'j', see=True, **jArrowConfig)
                        jVertArrow = self.createLabeledArrow(
                            adjVertex, 'j', **jVertConfig)
                        callEnviron |= set(jArrow + jVertArrow)
                        localVars += jArrow + jVertArrow
                    else:
                        self.moveItemsTo(
                            jArrow + jVertArrow,
                            self.vertexTable.labeledArrowCoords(
                                j, **jArrowConfig) +
                            self.labeledArrowCoords(adjVertex, **jVertConfig),
                            sleepTime=wait / 10, see=True, expand=True)

                    self.highlightCode('queue.insert(j)', callEnviron,
                                       wait=wait)

                queue.append(drawnValue(adjVertex))
                if code:
                    copyItems = tuple(self.canvas.copyItem(i)
                                      for i in self.vertices[adjVertex].items)
                    callEnviron |= set(copyItems + queue.items())
                    self.moveItemsLinearly(
                        copyItems,
                        (queue.cellCoords(len(queue) - 1),
                         queue.cellCenter(len(queue) - 1)),
                        sleepTime=wait / 10,
                        startFont=self.canvas.getItemFont(copyItems[1]),
                        endFont=self.ADJACENCY_MATRIX_FONT, see=True,
                        expand=True)
                    queue[-1].items = (
                        self.canvas.create_rectangle(
                            *queue.cellCoords(len(queue) - 1),
                            fill=self.canvas_itemConfig(copyItems[0], 'fill'),
                            width=0),
                        copyItems[1])
                    self.canvas.tag_lower(*queue[-1].items)
                    callEnviron |= set(queue[-1].items)
                    self.dispose(callEnviron, copyItems[0])
                    
                    self.highlightCode(self.innerLoopIterator, callEnviron,
                                       wait=wait)
                    colors = self.canvas.fadeItems(localVars)

            if code:
                self.canvas.restoreItems(localVars, colors)
                self.highlightCode('not queue.isEmpty()', callEnviron, 
                                   wait=wait)

        if code:
            self.highlightCode((), callEnviron, wait=wait)
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
            outputFont=(self.VALUE_FONT[0], -16), see=True)
        callEnviron |= set(outputBox.items())
        
        iterator = (
            'vertex{vars} in graph.{order}First(start={startVal})'.format(
                **locals()))
        vertexArrow, vertexArrowConfig = None, {}
        vertexVertArrow = None
        vertexVertConfig = {'orientation': 30, 'anchor': SW}
        localVars, colors = (), ()
        self.highlightCode(iterator, callEnviron, wait=wait)

        for thing in (
                self.depthFirst if order == 'depth' else self.breadthFirst)(
                    startVertex, wait=wait):
            self.canvas.restoreItems(localVars, colors)
            vertex = thing[0] if order == 'depth' else thing
            vertexLabel = self.vertexTable[vertex].val
            path = thing[1] if order == 'depth' else ()
            edgesInPath = [
                self.edges[path[v].val, path[v + 1].val].items[0]
                for v in range(len(path) - 1)]
            if vertexArrow is None:
                vertexArrow = self.vertexTable.createLabeledArrow(
                    vertex, 'vertex', see=True, **vertexArrowConfig)
                vertexVertArrow = self.createLabeledArrow(
                    vertexLabel, 'vertex', see=True, **vertexVertConfig)
                callEnviron |= set(vertexArrow + vertexVertArrow)
                localVars += vertexArrow + vertexVertArrow
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
            self.highlightCode('print(graph.getVertex(vertex))', callEnviron,
                               wait=wait)
            copy = self.canvas.copyItem(self.vertices[vertexLabel].items[1])
            callEnviron.add(copy)
            outputBox.appendText(copy, sleepTime=wait / 10)

            self.highlightCode(iterator, callEnviron, wait=wait)
            for edge in edgesInPath:
                self.canvas.itemconfigure(
                    edge, width=self.EDGE_WIDTH, fill=self.EDGE_COLOR)
            colors = self.canvas.fadeItems(localVars)
            
        if code:
            self.highlightCode((), callEnviron, wait=wait)
        self.cleanUp(callEnviron)

    minimumSpanningTreeCode = '''
def minimumSpanningTree(self, n={nVal}):
   self.validIndex(n)
   tree = Graph()
   vMap = [None] * self.nVertices()
   for vertex, path in self.depthFirst(n):
      vMap[vertex] = tree.nVertices()
      tree.addVertex(self.getVertex(vertex))
      if len(path) > 1:
         tree.addEdge(vMap[path[-2]], vMap[path[-1]])
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
        self.highlightCode('tree = Graph()', callEnviron, wait=wait)
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
            *([None] * self.nVertices()),
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
            vMapIndex = 1 + self.nVertices() + len(treeVerts)
            vMapIndices = vMap.items()[vMapIndex:vMapIndex + 1]
            vMapArrow = self.createVMapArrow(
                vMap, len(treeVerts), vertex, see=vMapIndices)
            vMap[vertex] = drawnValue(len(treeVerts), *vMapArrow)
            callEnviron |= set(vMapArrow)
            localVars += vMapArrow
            faded += (Scrim.FADED_FILL,) * len(vMapArrow)

            self.highlightCode('tree.addVertex(self.getVertex(vertex))',
                               callEnviron, wait=wait)
            vertCoords = self.vertexCoords(vertexLabel)
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

    def createVMapArrow(self, vMap, index, vertex, see=()):
        indexCoords = vMap.arrayCellIndexCoords(index)
        tip = indexCoords
        base = vMap.cellCenter(vertex)
        arrow = self.canvas.create_line(*base, *tip, arrow=LAST)
        VdotRadius = V(3, 3)
        dot = self.canvas.create_oval(
            *(V(base) - VdotRadius), *(V(base) + VdotRadius),
            fill='red', width=0)
        if see:
            self.scrollToSee(
                (arrow, dot) +
                (tuple(see) if isinstance(see, (list, tuple, set)) else ()))
            
        return (arrow, dot)

    topologicalSortCode = '''
def sortVertsTopologically(
      self):
   vertsByDegree = [
      {} for j in range(
         min(self.nVertices(), self.nEdges() + 1))]
   inDegree = [0] * self.nVertices()
   for vertex in self.vertices():
      inDegree[vertex] = self.degree(vertex)[0]
      vertsByDegree[inDegree[vertex]][vertex] = 1
   result = []
   while len(vertsByDegree[0]) > 0:
      vertex, _ = vertsByDegree[0].popitem()
      result.append(vertex)
      for s in self.adjacentVertices(vertex):
         vertsByDegree[inDegree[s]].pop(s)
         inDegree[s] -= 1
         vertsByDegree[inDegree[s]][s] = 1
   if len(result) == self.nVertices():
      return result
   raise Exception('Cycle in graph, cannot sort') 
'''
    vertsByDegreeConstructor = re.compile(
        r'vertsByDegree = .*\n.*\n.*1\)\)\]')

    def topologicalSort(self, code=topologicalSortCode, start=True, wait=0.1):
        sortTags = 'TSort'
        callEnviron = self.createCallEnvironment(code=code,
                                                 startAnimations=start)
        localVars, faded = (), ()

        vertsByDegreeCoords = (
            textWidth(self.vertexTable.labelFont, '   vertsByDegree'),
            self.graphRegion[3] + 30)
        self.highlightCode('self.nVertices()', callEnviron, wait=wait)
        edgeCountLabel = self.canvas.create_text(
            *vertsByDegreeCoords, anchor=NW, text=str(self.nVertices()),
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR, tags=sortTags)
        callEnviron.add(edgeCountLabel)
        self.highlightCode('self.nEdges() + 1', callEnviron, wait=wait)
        self.canvas.itemConfig(
            edgeCountLabel,
            text='min({}, {})'.format(self.nVertices(), self.nEdges() + 1))
        self.highlightCode(
            'min(self.nVertices(), self.nEdges() + 1)', callEnviron, wait=wait)
        maxEdges = min(self.nVertices(), self.nEdges() + 1)
        self.canvas.itemConfig(edgeCountLabel, text=str(maxEdges))

        self.highlightCode(self.vertsByDegreeConstructor, callEnviron,
                           wait=wait)
        self.dispose(callEnviron, edgeCountLabel)
        vertsByDegreeLabel = self.canvas.create_text(
            *(V(vertsByDegreeCoords) + V(-15, 15)), anchor=E,
            text='vertsByDegree', font=self.vertexTable.labelFont,
            fill=self.VARIABLE_COLOR, tags=sortTags)
        callEnviron.add(edgeCountLabel)
        vertsByDegree = [
            Table(self,
                  (vertsByDegreeCoords[0] + j * self.vertexTable.cellWidth * 2,
                   vertsByDegreeCoords[1]),
                  label=str(j), labelAnchor=S, vertical=True, 
                  labelFont=self.vertexTable.labelFont, 
                  cellWidth=self.vertexTable.cellWidth,
                  cellHeight=self.vertexTable.cellHeight, see=True,
                  cellBorderWidth=self.vertexTable.cellBorderWidth)
            for j in range(maxEdges)]
        callEnviron |= set((vertsByDegreeLabel,
                            *flat(*(tbl.items() for tbl in vertsByDegree))))
        
        self.highlightCode('inDegree = [0] * self.nVertices()', callEnviron,
                           wait=wait)
        gap = 5
        inDegree = Table(
            self, (self.vertexTable.x0 + self.vertexTable.cellWidth + gap,
                   self.vertexTable.y0),
            *[drawnValue(0) for k in range(self.nVertices())],
            label='inDegree', labelAnchor=SW, vertical=True, 
            labelFont=self.vertexTable.labelFont, 
            cellWidth=self.vertexTable.cellHeight, see=True,
            cellHeight=self.vertexTable.cellHeight, cellBorderWidth=1)
        callEnviron |= set(inDegree.items())
        localVars += inDegree.items()
        faded = (Scrim.FADED_FILL, *((Scrim.FADED_OUTLINE,) * self.nVertices()))
        for j, dValue in enumerate(inDegree):
            dValue.items = (self.canvas.create_text(
                *inDegree.cellCenter(j), text='0', 
                font=self.ADJACENCY_MATRIX_FONT, tags=sortTags),)
            callEnviron |= set(dValue.items)
            localVars += dValue.items
            faded += (Scrim.FADED_FILL,)
            
        self.highlightCode('vertex in self.vertices()', callEnviron, wait=wait)
        vertexArrow, vertexArrowConfig = None, {}
        vertexVertArrow = None
        vertexVertConfig = {'orientation': 30, 'anchor': SW}
        sArrow, sArrowConfig = None, {}
        indegreeArrow, indegreeArrowConfig = None, {'orientation': 45}
        visible = self.visibleCanvas()
        for vertex in self.vertexIndices():
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
                
            self.highlightCode('inDegree[vertex] = self.degree(vertex)[0]',
                               callEnviron, wait=wait)
            colors = self.canvas.fadeItems(localVars, faded)
            inb, outb = self.degree(vertex)
            self.canvas.restoreItems(localVars, colors)
            self.moveItemsTo(
                (inb, outb),
                (inDegree.cellCenter(vertex), V(visible) - V(100, 100)),
                sleepTime=wait / 10, startFont=self.canvas.getItemFont(inb),
                endFont=self.ADJACENCY_MATRIX_FONT)
            nInb = self.canvas.itemConfig(inb, 'text')
            inDegree[vertex].val = int(nInb)
            self.canvas.itemConfig(inDegree[vertex].items[0], text=nInb)
            self.dispose(callEnviron, inb, outb)

            self.highlightCode('vertsByDegree[inDegree[vertex]][vertex] = 1',
                               callEnviron, wait=wait)
            copies = [self.canvas.copyItem(item)
                      for item in self.vertexTable[vertex].items]
            callEnviron |= set(copies)
            VbyDtable = vertsByDegree[inDegree[vertex].val]
            nVerts = len(VbyDtable)
            self.moveItemsTo(copies, (VbyDtable.cellCoords(nVerts),
                                      VbyDtable.cellCenter(nVerts)),
                             sleepTime=wait / 10, see=True, expand=True)
            VbyDtable.append(drawnValue(vertexLabel, *copies))
            callEnviron |= set(VbyDtable.items())
            
            self.highlightCode('vertex in self.vertices()', callEnviron,
                               wait=wait)
            
        self.highlightCode('result = []', callEnviron, wait=wait)
        result = []
        outputBox = OutputBox(
            self, bbox=(self.graphRegion[2] - 250, visible[3] - 40,
                        visible[2] - 10, visible[3] - 10), label='result',
            outputFont=(self.VALUE_FONT[0], -16), see=True)
        callEnviron |= set(outputBox.items())

        self.highlightCode('len(vertsByDegree[0]) > 0', callEnviron, wait=wait)
        while len(vertsByDegree[0]) > 0:
            self.highlightCode('vertex, _ = vertsByDegree[0].popitem()',
                               callEnviron, wait=wait)
            dValue = vertsByDegree[0].pop()
            vertexLabel = dValue.val
            self.dispose(callEnviron, *vertexArrow, dValue.items[0])
            self.canvas.tag_lower(dValue.items[1], 
                                  self.vertices[vertexLabel].items[0])
            self.moveItemsTo(
                dValue.items[1:] + vertexVertArrow,
                (self.vertexCoords(vertexLabel),
                 *self.labeledArrowCoords(vertexLabel, **vertexVertConfig)),
                sleepTime=wait / 10, see=True, expand=True)

            self.highlightCode('result.append(vertex)', callEnviron, wait=wait)
            outputBox.appendText(dValue.items[1], sleepTime=wait / 10)
            result.append(vertexLabel)

            self.highlightCode('s in self.adjacentVertices(vertex)',
                               callEnviron, wait=wait)
            colors = self.canvas.fadeItems(localVars, faded)
            for s in self.adjacentVertices(self.getVertexIndex(vertexLabel)):
                self.canvas.restoreItems(localVars, colors)
                sVertexLabel = self.vertexTable[s].val
                if sArrow is None:
                    sArrow = self.vertexTable.createLabeledArrow(
                        s, 's', see=True, **sArrowConfig)
                    callEnviron |= set(sArrow)
                    localVars += sArrow
                    faded += (Scrim.FADED_FILL,) * len(sArrow)
                else:
                    self.moveItemsTo(
                        sArrow,
                        self.vertexTable.labeledArrowCoords(s, **sArrowConfig),
                        sleepTime=wait / 10, see=True, expand=True)
                    
                self.highlightCode('vertsByDegree[inDegree[s]]',
                                   callEnviron, wait=wait / 10)
                VbyDtable = vertsByDegree[inDegree[s].val]
                if indegreeArrow is None:
                    indegreeArrow = VbyDtable.createLabeledArrow(
                            -0.5, '', see=True, **indegreeArrowConfig)
                    callEnviron |= set(indegreeArrow)
                else:
                    self.moveItemsTo(
                        indegreeArrow,
                        VbyDtable.labeledArrowCoords(
                            -0.5, **indegreeArrowConfig),
                        sleepTime=wait / 10, see=True, expand=True)
                
                self.highlightCode('vertsByDegree[inDegree[s]].pop(s)',
                                   callEnviron, wait=wait)
                itemIndex = [v.val for v in VbyDtable].index(
                    sVertexLabel)
                popValue = VbyDtable.pop(itemIndex)
                popLocation = len(VbyDtable) + 1
                popOffset = V(V(-1, 0, -1, 0) * (VbyDtable.cellWidth // 2))
                self.moveItemsOnCurve(
                    popValue.items +
                    flat(*(VbyDtable[j].items
                           for j in range(itemIndex, len(VbyDtable)))),
                    (V(VbyDtable.cellCoords(popLocation)) + popOffset,
                     V(VbyDtable.cellCenter(popLocation)) + popOffset) +
                    flat(*((VbyDtable.cellCoords(j), VbyDtable.cellCenter(j))
                           for j in range(itemIndex, len(VbyDtable)))),
                    sleepTime=wait / 10, see=True, expand=True)
                
                self.highlightCode('inDegree[s] -= 1', callEnviron, wait=wait)
                inDegree[s].val -= 1
                self.canvas.itemConfig(inDegree[s].items[0], 
                                       text=str(inDegree[s].val))
                VbyDtable = vertsByDegree[inDegree[s].val]
                self.moveItemsTo(indegreeArrow,
                                 VbyDtable.labeledArrowCoords(
                                     -0.5, **indegreeArrowConfig),
                                 sleepTime=wait / 10, see=True, expand=True)

                self.highlightCode('vertsByDegree[inDegree[s]][s] = 1',
                                   callEnviron, wait=wait)
                self.moveItemsTo(
                    popValue.items,
                    (VbyDtable.cellCoords(len(VbyDtable)),
                     VbyDtable.cellCenter(len(VbyDtable))),
                    sleepTime=wait / 10, see=True, expand=True)
                VbyDtable.append(popValue)
                callEnviron |= set(VbyDtable.items())
            
                self.highlightCode('s in self.adjacentVertices(vertex)',
                                   callEnviron, wait=wait)
                colors = self.canvas.fadeItems(localVars, faded)
                
            self.canvas.restoreItems(localVars, colors)
            self.highlightCode('len(vertsByDegree[0]) > 0', callEnviron,
                               wait=wait)
            
        self.highlightCode('len(result) == self.nVertices()', callEnviron,
                           wait=wait)
        if len(result) == self.nVertices():
            self.highlightCode('return result', callEnviron)
        else:
            self.highlightCode("raise Exception('Cycle in graph, cannot sort')",
                               callEnviron, color=self.EXCEPTION_HIGHLIGHT)

        self.cleanUp(callEnviron)
        return result if len(result) == self.nVertices() else None

    degreeCode = '''
def degree(self, n={nVal}):
   self.validIndex(n)
   inb, outb = 0, 0
   for j in self.vertices():
      if j != n:
         if self.hasEdge(j, n):
            inb += 1
         if self.hasEdge(n, j):
            outb += 1
   return (inb, outb)
'''
    
    def degree(self, n, code=degreeCode, wait=0.1):
        nLabel = self.vertexTable[n].val if n < len(self.vertexTable) else None
        nVal = "{} ('{}')".format(n, nLabel)
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))

        nArrowConfig = {'level': 1, 'anchor': SE}
        nVertConfig = {'level': 1, 'orientation': 10, 'anchor': SW}
        nArrow = self.vertexTable.createLabeledArrow(
            n, 'n', see=True, **nArrowConfig)
        nVertArrow = self.createLabeledArrow(
            nLabel, 'n', see=True, **nVertConfig)
        callEnviron |= set(nArrow + nVertArrow)
        self.highlightCode('self.validIndex(n)', callEnviron, wait=wait)
        self.highlightCode('inb, outb = 0, 0', callEnviron, wait=wait)
        inb, outb = 0, 0
        Voffset = V(50, 0)
        outVars = [
            (self.canvas.create_text(
                *(V(self.vertexTable.cellCenter(row)) + Voffset),
                text=name, font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR),
             self.canvas.create_text(
                 *(V(self.vertexTable.cellCenter(row + 1)) + Voffset),
                 text='0', font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR))
            for name, row in zip(('inb', 'outb'), (1, 4))]
        allOutVars = flat(*outVars)
        callEnviron |= set(allOutVars)
        self.scrollToSee(allOutVars, sleepTime=wait / 10)
            
        self.highlightCode('j in self.vertices()', callEnviron, wait=wait)
        jArrowConfig = {'level': 2, 'anchor': SE}
        jVertConfig = {'level': 1, 'orientation': 40, 'anchor': SW}
        jArrow, jVertArrow = None, None
        for j in self.vertexIndices():
            jLabel = self.vertexTable[j].val
            if jArrow is None:
                jArrow = self.vertexTable.createLabeledArrow(
                    j, 'j', see=True, **jArrowConfig)
                jVertArrow = self.createLabeledArrow(
                    jLabel, 'j', see=True, **jVertConfig)
                callEnviron |= set(jArrow + jVertArrow)
            else:
                self.moveItemsTo(
                    jArrow + jVertArrow,
                    self.vertexTable.labeledArrowCoords(j, **jArrowConfig) +
                    self.labeledArrowCoords(jLabel, **jVertConfig),
                    sleepTime=wait / 10, see=True, expand=True)
            self.highlightCode('j != n', callEnviron, wait=wait)
            if j != n:
                edge = (jLabel, nLabel)
                edgeEntry = self.adjMat[edge][1] # Highlight edge in
                edgeEntry.grid(padx=self.ADJ_MAT_HIGHLIGHT_PAD, # adj matrix
                               pady=self.ADJ_MAT_HIGHLIGHT_PAD)
                self.highlightCode('self.hasEdge(j, n)', callEnviron, wait=wait)
                if self.edgeWeight(*edge):
                    self.highlightCode('inb += 1', callEnviron, wait=wait)
                    inb += 1
                    self.canvas.itemConfig(outVars[0][1], text=str(inb))
                edgeEntry.grid(padx=0, pady=0)

                edge = (nLabel, jLabel)
                edgeEntry = self.adjMat[edge][1] # Highlight edge in
                edgeEntry.grid(padx=self.ADJ_MAT_HIGHLIGHT_PAD, # adj matrix
                               pady=self.ADJ_MAT_HIGHLIGHT_PAD)
                self.highlightCode('self.hasEdge(n, j)', callEnviron, wait=wait)
                if self.edgeWeight(*edge):
                    self.highlightCode('outb += 1', callEnviron, wait=wait)
                    outb += 1
                    self.canvas.itemConfig(outVars[1][1], text=str(outb))
                edgeEntry.grid(padx=0, pady=0)
                
            self.highlightCode('j in self.vertices()', callEnviron, wait=wait)

        self.highlightCode('return (inb, outb)', callEnviron)
        result = tuple(var[1] for var in outVars)
        callEnviron -= set(result)
        self.cleanUp(callEnviron)
        return result
    
    def enableButtons(self, enable=True):
        super().enableButtons(enable)
        for btn in (self.depthFirstTraverseButton, 
                    self.breadthFirstTraverseButton, self.MSTButton):
            widgetState( # can only traverse when start node selected
                btn,
                NORMAL if enable and self.selectedVertices[0] else DISABLED)
        widgetState(  # Can only sort directional graphs with 1+ edges
            self.sortButton,
            NORMAL if enable and self.nEdges() > 0 and
            not self.bidirectionalEdges.get() else DISABLED)

    def makeButtons(self, *args, **kwargs):
        '''Make buttons specific to unweighted graphs and aadd the
        animation control buttons'''
        vcmd = super().makeButtons(*args, **kwargs)
        self.depthFirstTraverseButton = self.addOperation(
            "Depth-first Traverse", lambda: self.clickTraverse('depth'),
            helpText='Traverse graph in depth-first order', state=DISABLED)
        self.breadthFirstTraverseButton = self.addOperation(
            "Breadth-first Traverse", lambda: self.clickTraverse('breadth'),
            helpText='Traverse graph in breadth-first order', state=DISABLED)
        self.MSTButton = self.addOperation(
            "Minimum Spanning Tree", self.clickMinimumSpanningTree,
            helpText='Compute a minimum spanning tree', state=DISABLED)
        self.sortButton = self.addOperation(
            "Topological Sort", self.clickTopologicalSort,
            helpText='Compute a toplogical sort of the vertices',
            state=DISABLED)
        self.addAnimationButtons()

    def clickTraverse(self, kind):
        if self.selectedVertices[0]:
            self.traverseExample(kind, self.selectedVertices[0][0],
                                 start=self.startMode())
        else:
            self.setMessage('Must select start vertex before traversal')

    def clickMinimumSpanningTree(self):
        if self.selectedVertices[0]:
            self.minimumSpanningTree(self.selectedVertices[0][0],
                                     start=self.startMode())
        else:
            self.setMessage('Must select start vertex for tree')

    def clickTopologicalSort(self):
        if self.bidirectionalEdges.get():
            self.setMessage('Edges must be directional to sort vertices')
        elif self.nEdges() == 0:
            self.setMessage('Must have at least 1 edge to sort vertices')
        else:
            result = self.topologicalSort(start=self.startMode())
            self.setMessage(
                'Sorted vertices: {}'.format(' '.join(result)) if result else
                'Cycle in graph.  Sorting impossble.')
            
if __name__ == '__main__':
    graph = Graph(weighted=False)
    graph.process_command_line_arguments(sys.argv[1:])
        
    graph.runVisualization()
