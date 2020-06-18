import time
from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

CELL_SIZE = 40
CELL_BORDER = 2
CELL_BORDER_COLOR = 'black'
STACK_X0 = 300
STACK_Y0 =  400
FONT_SIZE = 20
VALUE_FONT = ('Helvetica', FONT_SIZE)
VALUE_COLOR = 'black'



# possible issues: 
# when you enter an invalid number the operations grid moves slightly to the right (and then moves back when a valid number is entered)
#  the cell_size was changed from 50 to 40 to show the entire stack vertically

class Stack(VisualizationApp):
    nextColor = 0

    def __init__(self, size=10, title="Stack", **kwargs):
        super().__init__(title=title, **kwargs)
        self.size = size
        self.title = title
        self.list = []
        self.buttons = self.makeButtons()

  

    def __str__(self):
        return str(self.list)

    # STACK FUNCTIONALITY

   
    def push(self, val):
        self.cleanUp()
      
        # create new cell and cell value display objects
        toPositions = (self.cellCoords(len(self.list)), 
                       self.cellCenter(len(self.list)))

        # Animate arrival of new value from operations panel area
        canvasDimensions = self.widgetDimensions(self.canvas)
        #determine the top left and bottom right positions
        startPosition = [STACK_X0 ,0,STACK_X0 ,0]
        startPosition = add_vector(startPosition, (0, 0, CELL_SIZE, CELL_SIZE))
        cellPair = self.createCellValue(startPosition, val)
        self.moveItemsTo(cellPair, toPositions, steps=CELL_SIZE, sleepTime=0.01)

        # add a new Drawable with the new value, color, and display objects
        d = drawable(
            val, self.canvas.itemconfigure(cellPair[0], 'fill'), *cellPair)
        self.list.append(d)

        # update window
        self.window.update()

    

    def pop(self):
        self.cleanUp()
        # pop a Drawable from the list
        if len(self.list) == 0:
            self.setMessage('Stack is empty!')
            return
        n = self.list.pop()

        # delete the associated display objects
        items = (n.display_shape, n.display_val)
        #self.moveItemsOffCanvas(items, N, sleepTime=0.02) ## alternative method to moveItemsBy
        self.moveItemsBy(items, delta=(0,-400),steps=CELL_SIZE, sleepTime = .01)
        self.canvas.delete(n.display_shape)
        self.canvas.delete(n.display_val)

        # update window
        self.window.update()
        
        return n.val # returns value displayed in the cell


       
    def cellCoords(self, cell_index): # Get bounding rectangle for array cell
        return (STACK_X0 ,
                STACK_Y0 - CELL_SIZE * (cell_index +1), 
                STACK_X0 + CELL_SIZE - CELL_BORDER,
                STACK_Y0 - CELL_SIZE * cell_index + CELL_BORDER)    

    def cellCenter(self, index): # Center point for array cell at index
        half_cell = (CELL_SIZE - CELL_BORDER) // 2
        return add_vector(self.cellCoords(index), (half_cell, half_cell))


    def createCellValue(self, indexOrCoords, key, color=None):
        """Create new canvas items to represent a cell value.  A square
        is created filled with a particular color with an text key centered
        inside.  The position of the cell can either be an integer index in
        the Array or the bounding box coordinates of the square.  If color
        is not supplied, the next color in the palette is used.
        An event handler is set up to update the VisualizationApp argument
        with the cell's value if clicked with any button.
        Returns the tuple, (square, text), of canvas items
        """
        # Determine position and color of cell
        if isinstance(indexOrCoords, int):
            rectPos = self.cellCoords(indexOrCoords)
            valPos = self.cellCenter(indexOrCoords)
        else:
            rectPos = indexOrCoords
            valPos = divide_vector(add_vector(rectPos[:2], rectPos[2:]), 2)
        if color is None:
            # Take the next color from the palette
            color = drawable.palette[Stack.nextColor]
            Stack.nextColor = (Stack.nextColor + 1) % len(drawable.palette)

        cell_rect = self.canvas.create_rectangle(
            *rectPos, fill=color, outline='', width=0)
        cell_val = self.canvas.create_text(
            *valPos, text=str(key), font=VALUE_FONT, fill=VALUE_COLOR)
        handler = lambda e: self.setArgument(str(key))
        for item in (cell_rect, cell_val):
            self.canvas.tag_bind(item, '<Button>', handler)

        return cell_rect, cell_val

    def display(self):
        self.canvas.delete("all")

        # go through each Drawable in the list
        for i, n in enumerate(self.list):
            # create display objects for the associated Drawables
            n.display_shape, n.display_val = self.createCellValue(
                i, n.val, n.color)
            n.color = self.canvas.itemconfigure(n.display_shape, 'fill')

        self.window.update()



    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        #numArguments decides the side where the button appears in the operations grid
        pushButton = self.addOperation(
            "Push", lambda: self.clickPush(), numArguments=1,
            validationCmd=vcmd)
        popButton = self.addOperation(
            "Pop", lambda: self.clickPop())        
      
        return [pushButton, popButton]
           
    

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val
    
    # Button functions

    def clickPush(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            if len(self.list) >= self.size:
                self.setMessage("Error! Stack is already full.")
            else:
                self.setButtonsStatus(DISABLED)
                self.push(val)
                self.setButtonsStatus(NORMAL)
                self.setMessage("Value {} pushed!".format(val))
                
        self.clearArgument()
        
    
    def clickPop(self):
        self.setButtonsStatus(DISABLED)
        val = self.pop()
        self.setButtonsStatus(NORMAL)
        self.setMessage("Value {} popped!".format(val))
        
    def setButtonsStatus(self, state= NORMAL):
        for b in self.buttons:
            b['state'] = state
    
       

if __name__ == '__main__':
    #random.seed(3.14159)    # Use fixed seed for testing consistency
    stack = Stack()
    stack.setButtonsStatus(DISABLED)
    for i in range(10):
        stack.push(i+1)
    stack.setButtonsStatus(NORMAL)
    

    stack.runVisualization()

