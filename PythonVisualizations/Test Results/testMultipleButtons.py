# NOTE TO WINDOWS DEVELOPERS
#
# VisualizationApp.py is in this test directory as a symbolic link to
# the version in the parent directory.  Unless you've taken special
# steps to get your Windows system to support symbolic links and for
# git to correctly copy them onto your working copy, the statement
# below to import VisualizationApp will not work.  To run this
# program, copy it to the same directory as VisualizationApp.py.
# On macOS and Linux, the symbolic links should work with the git
# and GitHub Desktop clients using their default settings.

from VisualizationApp import *
import sys
from tkinter import *

__doc__ = '''
USAGE:

Run this program with optional arguments:
  python3 testMultipleButtons.py [numArguments [useCheckButtons ['helpText']]]

* The button that makes other buttons will make them depend on a certain
  number of arguments, numArguments, which defaults to 1

* The buttons will be created as normal Buttons, unless useCheckButtons
  is something that evaluates as True in Python (e.g. 1 or True).

* The helpText is displayed initially to explain the purpose of the text
  entry areas.  It disappears when clicked or a value is entered in one of
  of the entry areas. 
'''

# Default values for number of args for operations, checkbuttons, and help text
nArgs = 1
checkbuttons = False
help='Click to enter argument'

# Parse arguments
try:
   if len(sys.argv) > 1: # Use command line argument if provided
      nArgs = int(sys.argv[1])
      if len(sys.argv) > 2: #
         checkbuttons = eval(sys.argv[2])
         if len(sys.argv) > 3:
            help = ' '.join(sys.argv[3:])
except:
   print('Error parsing arguments\n', __doc__)
   sys.exit(-1)
   
app = VisualizationApp()

buttons = []
def addOperationWithArg():
   opName = 'Operation {}'.format(len(buttons) + 1)
   buttons.append(app.addOperation(
      opName,
      lambda: app.setMessage('{} invoked with args {}'.format(
         opName, app.getArguments())),
      buttonType=Checkbutton if checkbuttons else Button,
      numArguments=nArgs, helpText=help))
   
app.addOperation('Create {} with {} argument{}'.format(
   'Checkbutton' if checkbuttons else 'Button',
   nArgs, '' if nArgs == 1 else 's'),
                 addOperationWithArg)

app.runVisualization()
