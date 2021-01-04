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

    def __init__(self, title="Array", **kwargs):
        kwargs['title'] = title
        super().__init__(**kwargs)

        # Fill in initial array values with random integers
        # The display items representing these array cells are created later
        for i in range(self.size - 1):
            self.list.append(drawnValue(random.randrange(self.valMax)))
        self.display()

        self.buttons = self.makeButtons()

    # Button functions
    def makeButtons(self, maxRows=4):
        buttons, vcmd = super().makeButtons(maxRows=maxRows)
        self.addAnimationButtons()
        return buttons
        
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
    array = Array()

    array.runVisualization()
