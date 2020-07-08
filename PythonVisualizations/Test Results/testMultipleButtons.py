from VisualizationApp import *
import sys

# Default number of args for operations and help text
nArgs = 1
help='Click to enter argument'
if len(sys.argv) > 1: # Use command line argument if provided
   nArgs = int(sys.argv[1])
   if len(sys.argv) > 2: #
      help = sys.argv[2]
   
app = VisualizationApp()

buttons = []
def addOperationWithArg():
   opName = 'Operation {}'.format(len(buttons) + 1)
   buttons.append(app.addOperation(
      opName, 
      lambda: app.setMessage('{} invoked with args {}'.format(
         opName, app.getArguments())), 
      numArguments=nArgs, helpText=help))
   
app.addOperation('Create operation with {} argument{}'.format(
   nArgs, '' if nArgs == 1 else 's'),
                 addOperationWithArg)

app.runVisualization()
