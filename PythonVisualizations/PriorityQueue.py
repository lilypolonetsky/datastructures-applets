import random
from tkinter import *

try:
    from drawnValue import *
    from SortingBase import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .SortingBase import *


class PriorityQueue(SortingBase):

    nextColor = 0

    def __init__(self, size=12, title="Priority Queue", **kwargs):
        super().__init__(size=size, title=title, **kwargs)

        self.nItems = None
        self.buttons = self.makeButtons()
        
        self.display()

    # ARRAY FUNCTIONALITY

    def insert(self, val):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        j = len(self.list) - 1  # Start at front

        indexJ = self.createIndex(j, 'j', level=-2)
        callEnviron |= set(indexJ)

        self.wait(0.2)
            
        self.list.append(drawnValue(None, None, None))
        while j >= 0 and val >= self.list[j].val:  # Move bigger items right

            self.assignElement(j, j+1, callEnviron)
            self.list[j+1].val = self.list[j].val
            j -= 1
            self.moveItemsBy(indexJ, (-self.CELL_SIZE, 0), sleepTime=0.02)  # Move "j" arrow
            
        # Location of the new cell in the array
        toPositions = (self.fillCoords(val, self.cellCoords(j+1)),
                       self.cellCenter(j+1))

        # Animate arrival of new value from operations panel area
        canvasDimensions = self.widgetDimensions(self.canvas)
        coords = self.cellCoords(0)
        delta = subtract_vector((canvasDimensions[0] // 2, canvasDimensions[1]),
                                coords[:2])
        startPosition = add_vector(coords, delta * 2)
        cellPair = self.createCellValue(startPosition, val)
        callEnviron |= set(cellPair)  # Mark new cell as temporary
        self.moveItemsTo(cellPair, toPositions, sleepTime=0.01)
        self.list[j+1] = drawnValue(val, *cellPair)
        callEnviron -= set(cellPair)  # New cell is no longer temporary

        self.moveItemsBy(self.nItems, (self.CELL_SIZE, 0), sleepTime=0.01)

        self.cleanUp(callEnviron) 

    def peek(self):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        # draw output box
        canvasDimensions = self.widgetDimensions(self.canvas)
        spacing = self.CELL_SIZE * 3 // 4
        padding = 10
        outputBox = self.canvas.create_rectangle(
            (canvasDimensions[0] - len(self.list) * spacing - padding) // 2,
            canvasDimensions[1] - self.CELL_SIZE - padding,
            (canvasDimensions[0] + len(self.list) * spacing + padding) // 2,
            canvasDimensions[1] - padding,
            fill=self.OPERATIONS_BG)
        callEnviron.add(outputBox)

        self.wait(0.3)

        # calculate where the value will need to move to
        outputBoxCoords = self.canvas.coords(outputBox)
        midOutputBox = (outputBoxCoords[3] + outputBoxCoords[1]) // 2

        # create the value to move to output box
        valueOutput = self.copyCanvasItem(self.list[-1].items[1])
        valueList = (valueOutput,)
        callEnviron.add(valueOutput)

        # move value to output box
        toPositions = (outputBoxCoords[0] + padding / 2 + (1 / 2) * spacing,
                       midOutputBox)
        self.moveItemsTo(valueList, (toPositions,), sleepTime=.02)

        # make the value 25% smaller
        newSize = (self.VALUE_FONT[0], int(self.VALUE_FONT[1] * .75))
        self.canvas.itemconfig(valueOutput, font=newSize)

        self.wait(0.3)
        self.cleanUp(callEnviron)
        
    def newArraySize(self, val):
        callEnviron = self.createCallEnvironment()                
        # Clear Array and reset size and list
        self.size = val
        self.list = []
        
        self.display()
        self.cleanUp(callEnviron)

    # delete the last element of the queue, or None if empty
    def remove(self):
        if len(self.list) == 0:
            self.setMessage('Array is empty!')
            return
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        self.wait(0.3)

        n = self.list.pop()
        callEnviron |= set(n.items)

        # Slide value rectangle up and off screen
        self.moveItemsOffCanvas(n.items, N, sleepTime=0.02)

        self.moveItemsBy(self.nItems, (-self.CELL_SIZE, 0), sleepTime=0.02)

        self.cleanUp(callEnviron)

    def fixPositions(self):     # Move canvas display items to exact coords
        for i, drawItem in enumerate(self.list):
            if drawItem:    # if i contains a cell...move the cells
                self.canvas.coords(drawItem.items[0], 
                                   *self.fillCoords(drawItem.val, 
                                                    self.cellCoords(i)))
                self.canvas.coords(drawItem.items[1], *self.cellCenter(i))

        # Move nItems index to position in array
        x = self.cellCenter(len(self.list))[0]
        # Use y coord from nItems index but x value from target location
        for item in self.nItems:
            coords = [x if i%2 == 0 else c
                      for i, c in enumerate(self.canvas.coords(item))]
            self.canvas.coords(item, *coords)
        
        self.window.update()

    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        if ((len(args) == 0 or args[0] is None) and # When cleaning up entire 
            kwargs.get('callEnviron', None) is None): # call stack,
            self.fixPositions()   # Restore cells to their coordinates in array

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        newSizeArrayButton = self.addOperation(
            "New", lambda: self.clickNew(), numArguments=1, validationCmd=vcmd)
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1, validationCmd=vcmd)
        deleteButton = self.addOperation(
            "Remove", lambda: self.clickRemove(), numArguments=0)
        peekButton = self.addOperation(
            "Peek", lambda: self.clickPeek(), numArguments=0)
        self.addAnimationButtons()
        return [insertButton, deleteButton, peekButton]

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val
    
    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            if len(self.list) >= self.size:
                self.setMessage("Error! Queue is already full.")
            else:
                self.insert(val)
                self.setMessage("Value {} inserted".format(val))
        self.clearArgument()
    
    def clickRemove(self):
        result = self.remove()
        self.clearArgument()

    def clickPeek(self):
        if len(self.list) <= 0: self.setMessage("Error! Queue is empty.")
        else:
            self.peek()
            self.setMessage("Value at front is {}".format(self.list[-1].val))

    def clickNew(self):
        val = self.validArgument()
        # If the number of cells desired wouldn't fit on the screen, error message
        if val is None or self.window.winfo_width() <= self.ARRAY_X0 + (val+1) * self.CELL_SIZE:
            self.setMessage("This array size is too big to display")
        elif val == 0:
            self.setMessage("This array size is too small")
        else:
            self.newArraySize(val)
        self.clearArgument()



if __name__ == '__main__':
    queue = PriorityQueue()
    queue.runVisualization()
