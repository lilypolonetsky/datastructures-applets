#! /usr/bin/env python3
__doc__ = """
Program to show algorithm visualizations in a nested tabbed Tk notebook.
"""

from PythonVisualizations import runAllVisualizations

if __name__ == '__main__':
    runAllVisualizations.showVisualizations(
        runAllVisualizations.findVisualizations('./PythonVisualizations'))
