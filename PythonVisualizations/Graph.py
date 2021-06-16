from tkinter import *
import random

try:
    from GraphBase import *
except ModuleNotFoundError:
    from .GraphBase import *

V = vector

if __name__ == '__main__':
    graph = GraphBase()

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
