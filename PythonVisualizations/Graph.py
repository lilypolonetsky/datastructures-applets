from tkinter import *
import random

try:
    from GraphBase import *
except ModuleNotFoundError:
    from .GraphBase import *

V = vector

class Graph(GraphBase):

    adjacentVerticesCode = '''
def adjacentVertices(self, n={nVal}):
   self.validIndex(n)
   for j in self.vertices():
      if j != n and self.hasEdge(n, j):
         yield j
'''
    
    def adjacentVertices(self, n, code=adjacentVerticesCode, wait=0.1):
        nVal = "{} ('{}')".format(self.getVertexIndex(n), n)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()))
            
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
        self.setMessage('DF Traverse TBD')

    def clickBreadthFirstTraverse(self):
        self.setMessage('BF Traverse TBD')
        
if __name__ == '__main__':
    graph = Graph(weighted=False)

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
