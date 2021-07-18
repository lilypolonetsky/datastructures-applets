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

        self.setMessage('MST TBD')
            
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
