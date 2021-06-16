from tkinter import *
import random

try:
    from GraphBase import *
except ModuleNotFoundError:
    from .GraphBase import *

V = vector

class Graph(GraphBase):

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
