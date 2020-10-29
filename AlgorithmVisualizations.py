#! /usr/bin/env python3
__doc__ = """
Program to show algorithm visualizations in a nested tabbed Tk notebook.
"""

from PythonVisualizations import runAllVisualizationsMenu

if __name__ == '__main__':
    runAllVisualizationsMenu.showVisualizations(
        runAllVisualizationsMenu.findVisualizations(['PythonVisualizations']))
