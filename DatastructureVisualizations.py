__doc__ = '''
Program to show data structure visualizations in a single application.
'''

import sys, os

try:
    if not hasattr(sys, 'path'): sys.path = []
    if (sys.argv and os.path.exists(sys.argv[0]) and
        os.path.dirname(sys.argv[0])):
        sys.path.append(os.path.dirname(sys.argv[0]))
    if (__file__ and os.path.exists(__file__) and
        os.path.dirname(__file__) and
        os.path.dirname(__file__) not in sys.path):
        sys.path.append(os.path.dirname(__file__))
except:
    pass

from PythonVisualizations import runAllVisualizationsMenu

if __name__ == '__main__':
    dirname = None
    for path in sys.path:
        if os.path.isdir(os.path.join(path, 'PythonVisualizations')):
            dirname = os.path.join(path, 'PythonVisualizations')
    runAllVisualizationsMenu.showVisualizations(
        runAllVisualizationsMenu.findVisualizations([dirname]))
