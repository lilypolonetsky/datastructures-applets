import random
from tkinter import *

try:
    from drawnValue import *
    from VisualizationApp import *
    from SortingBase import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .VisualizationApp import *
    from .SortingBase import *
    
class Array(SortingBase):

    def __init__(self, title="Array", values=None, **kwargs):
        kwargs['title'] = title
        super().__init__(**kwargs)

        # Fill in initial array values with random integers
        # The display items representing these array cells are created later
        if values is None:
            for i in range(self.size - 1):
                self.list.append(drawnValue(random.randrange(self.valMax)))
        else:
            self.list = [drawnValue(val) for val in values]
        self.makeButtons()

        self.display()


    # Button functions
    def makeButtons(self, maxRows=3):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows,
            argHelpText=['item key'], helpText='Insert item in array')
        searchButton = self.addOperation(
            "Search", lambda: self.clickSearch(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows,
            argHelpText=['item key'], helpText='Search for item in array')
        deleteButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows,
            argHelpText=['item key'], helpText='Delete array item')
        newButton = self.addOperation(
            "New", lambda: self.clickNew(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows, 
            argHelpText=['number of cells'],
            helpText='Create new empty array')
        traverseButton = self.addOperation(
            "Traverse", lambda: self.traverse(), maxRows=maxRows,
            helpText='Traverse all array cells once')
        randomFillButton = self.addOperation(
            "Random Fill", lambda: self.randomFill(), maxRows=maxRows,
            helpText='Fill empty array cells with random keys')
        deleteRightmostButton = self.addOperation(
            "Delete Rightmost", lambda: self.deleteLast(), maxRows=maxRows,
            helpText='Delete last array item')
        self.addAnimationButtons(maxRows=maxRows)
        
    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage(
                "Input value must be an integer from 0 to {}".format(
                    self.valMax))
            self.setArgumentHighlight(color=self.ERROR_HIGHLIGHT)
        elif self.insert(val):
            self.setMessage("Value {} inserted".format(val))
            self.clearArgument()

if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    numArgs = [int(arg) for arg in sys.argv[1:] if arg.isdigit()]
    array = Array(values=numArgs if len(numArgs) > 0 else None)

    array.runVisualization()
