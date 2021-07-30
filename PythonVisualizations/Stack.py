from tkinter import *

try:
    from coordinates import *
    from drawnValue import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .coordinates import *
    from .drawnValue import *
    from .VisualizationApp import *

V = vector

class Stack(VisualizationApp):
    nextColor = 0
    MAX_ARG_WIDTH = 10
    MAX_CELL_HEIGHT = 40
    MAX_FONT_SIZE = 20
    MIN_FONT_SIZE = 9
    FONT_RATIO = 0.7
    CELL_HEIGHT = 40
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    STACK_X0 = 200

    def __init__(                       # Constructor
            self,
            title="Stack",              # Title of visualization window
            size=8,                     # Initial stack capacity
            maxArgWidth=MAX_ARG_WIDTH,  # Maximum string length for items
            numericIndexColor='gray40', # Color and font for numeric indices
            numericIndexFont=('Courier', -11), # by cells
            **kwargs):
        kwargs['title'] = title
        kwargs['maxArgWidth'] = maxArgWidth
        super().__init__(**kwargs)
        self.CELL_WIDTH = textWidth(
            self.VALUE_FONT, '▢' * (maxArgWidth + 2))
        self.size = size
        self.list = []
        self.numericIndexColor = numericIndexColor
        self.numericIndexFont = numericIndexFont

        self.buttons = self.makeButtons()
        self.display()

    def __str__(self):
        return str(self.list)

    def indexCoords(self, index):
        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        gap = 3 * abs(self.numericIndexFont[1])
        x0 = cell_coords[0] - gap - 50
        x1 = cell_coords[0] - gap
        y0 = cell_center[1]
        return x0, y0, x1, y0
        
    # Create an index arrow pointing at a cell with an optional name label
    def createIndex(self, index, name="__top"):
        arrowCoords = self.indexCoords(index)
        arrow = self.canvas.create_line(
            *arrowCoords, arrow="last", fill=self.VARIABLE_COLOR)
        if name:
            label = self.canvas.create_text(
                arrowCoords[0] - abs(self.VARIABLE_FONT[1]), arrowCoords[1],
                text=name, anchor=E, font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
            return (arrow, label)

        return (arrow,)

    # STACK FUNCTIONALITY

    pushCode = """
def push(self, item={val}):
   self.__top += 1
   self.__stackList[self.__top] = item
"""

    def push(self, val, code=pushCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)

        #move arrow up when new cell is inserted
        self.highlightCode('self.__top += 1', callEnviron)
        self.moveItemsBy(self.topIndex, (0, -self.CELL_HEIGHT), sleepTime=0.02)

        cellCoords = self.cellCoords(len(self.list))
        cellCenter = self.cellCenter(len(self.list))

        # create new cell and cell value display objects
        toPositions = (cellCoords, cellCenter)

        # determine the top left and bottom right positions
        canvasDims = widgetDimensions(self.canvas)
        left = int(self.cell0()[0] * 0.75)
        startPosition = [left, canvasDims[1],
                         left + self.CELL_WIDTH - self.CELL_BORDER,
                         canvasDims[1] + self.CELL_HEIGHT - self.CELL_BORDER]
        cellPair = self.createCellValue(startPosition, val)
        callEnviron |= set(cellPair)

        self.highlightCode('self.__stackList[self.__top] = item', callEnviron)
        yDelta = abs(cellCoords[1] - startPosition[1])
        self.moveItemsOnCurve(
            cellPair, toPositions, steps=max(10, yDelta // 4),
            startAngle=-75, sleepTime=0.01)

        # add a new DrawnValue with the new value, and display objects
        self.list.append(drawnValue(val, *cellPair))
        callEnviron ^= set(cellPair)

        # finish the animation
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    popCode = """
def pop(self):
   top = self.__stackList[self.__top]
   self.__stackList[self.__top] = None
   self.__top -= 1
   return top
"""

    def pop(self, code=popCode, start=True):

        # pop a DrawnValue from the list
        if len(self.list) == 0:
            return

        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)
        wait = 0.1

        self.highlightCode('top = self.__stackList[self.__top]', callEnviron)

        # move copies of item to be deleted to top area
        newItems = [self.canvas.copyItem(i) for i in self.list[-1].items]
        callEnviron |= set(newItems)

        itemPos = self.topBoxCoords()
        labelPos = ((itemPos[0] + itemPos[2]) / 2, 
                    itemPos[1] - self.CELL_HEIGHT / 2)

        topLabel = self.canvas.create_text(
                *labelPos, text="top", font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
        callEnviron.add(topLabel)

        self.moveItemsTo(
            newItems, (itemPos, (labelPos[0], itemPos[1]+self.CELL_HEIGHT//2)),
            sleepTime=wait/5)

        # clear stack cell
        self.highlightCode('self.__stackList[self.__top] = None', callEnviron)

        # Update internal data structure
        n = self.list.pop()
        callEnviron |= set(n.items)
        self.moveItemsOffCanvas(n.items, W, sleepTime=wait/5)

        # decrement index pointing to the last cell
        self.highlightCode('self.__top -= 1', callEnviron)
        self.moveItemsBy(self.topIndex, (0, (self.CELL_HEIGHT)), 
                         sleepTime=wait/5)

        self.highlightCode('return top', callEnviron)

        # Finish animation
        self.cleanUp(callEnviron)

        return n.val  # returns value displayed in the cell

    peekCode = """
def peek(self):
   if not self.isEmpty():
      return self.__stackList[self.__top]
"""

    # displays the top val of the stack in a small cell on the bottom right of the window
    def peek(self, code=peekCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)
        wait = 0.1

        self.highlightCode('not self.isEmpty()', callEnviron)

        if self.isEmpty():
            self.highlightCode([], callEnviron)
            self.cleanUp(callEnviron)
            return None

        self.highlightCode('return self.__stackList[self.__top]', callEnviron)

        # draw output box
        outputBox = self.canvas.create_rectangle(
            *self.outputBoxCoords(), fill=self.OPERATIONS_BG)
        callEnviron.add(outputBox)

        pos = len(self.list) - 1

        # calculate where the value will need to move to
        outputBoxCoords = self.canvas.coords(outputBox)
        midOutputBoxY = (outputBoxCoords[3] + outputBoxCoords[1]) // 2
        midOutputBoxX = (outputBoxCoords[0] + outputBoxCoords[2]) // 2

        # create the value to move to output box
        valueOutput = self.canvas.copyItem(self.list[pos].items[1])
        valueList = (valueOutput,)
        callEnviron.add(valueOutput)

        # move value to output box
        toPositions = (midOutputBoxX, midOutputBoxY)
        self.moveItemsTo(valueList, (toPositions,), sleepTime=wait/5)

        # make the value fit the output box
        newFont = (self.VALUE_FONT[0], -14)
        self.canvas.itemconfig(valueOutput, font=newFont)

        # Finish animation
        self.cleanUp(callEnviron)

        return self.list[pos].val
        
    def outputBoxCoords(self):
        x0, y0 = self.cell0()
        return (x0 + self.CELL_WIDTH * 3 // 2, y0 - 30,
                x0 + self.CELL_WIDTH * 5 // 2, y0)

    def topBoxCoords(self):
        outputBox = self.outputBoxCoords()
        return (outputBox[0], self.CELL_HEIGHT * 2,
                outputBox[2], self.CELL_HEIGHT * 3)

    isEmptyCode = """
def isEmpty(self):
    return self.__top < 0
    """

    def isEmpty(self, code=isEmptyCode):
        callEnviron = self.createCallEnvironment(code=code)
        
        callEnviron |= set(self.createIndex(-.5, name = "0"))
        self.highlightCode('return self.__top < 0', callEnviron)
        self.wait(0.3)
        
        self.cleanUp(callEnviron)
        return len(self.list) == 0

    __cell0 = None
    
    def cell0(self):
        if self.__cell0 is None: 
            canvasDims = widgetDimensions(self.canvas)
            self.__cell0 = (self.STACK_X0,
                            canvasDims[1] - self.CELL_HEIGHT - self.CELL_BORDER)
        return self.__cell0

    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        x0, y0 = self.cell0()
        return (x0, y0 - self.CELL_HEIGHT * (cell_index + 1),
                x0 + self.CELL_WIDTH - self.CELL_BORDER,
                y0 - self.CELL_HEIGHT * cell_index - self.CELL_BORDER)

    def cellCenter(self, index):  # Center point for array cell at index
        return BBoxCenter(self.cellCoords(index))

    def createArrayCell(self, index):  # Create a box representing an array cell
        cell_coords = self.cellCoords(index)
        half_border = self.CELL_BORDER // 2
        other_half = self.CELL_BORDER - half_border
        cell = V(cell_coords) + V(
            -half_border, -half_border, other_half, other_half)
        rect = self.canvas.create_rectangle(
            cell, fill=None, outline=self.CELL_BORDER_COLOR,
            width=self.CELL_BORDER)
        self.canvas.lower(rect)
        label = self.canvas.create_text(
            cell[0] - abs(self.numericIndexFont[1]), (cell[1] + cell[3]) // 2,
            text=str(index), 
            fill=self.numericIndexColor, font=self.numericIndexFont)
        self.canvas.lower(label)

        return rect, label

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
            valPos = BBoxCenter(rectPos)

        if color is None:
            # Take the next color from the palette
            color = drawnValue.palette[Stack.nextColor]
            Stack.nextColor = (Stack.nextColor + 1) % len(drawnValue.palette)
        cell_rect = self.canvas.create_rectangle(
            *rectPos, fill=color, outline='', width=0)
        cell_val = self.canvas.create_text(
            *valPos, text=str(key), font=self.VALUE_FONT, fill=self.VALUE_COLOR)
        handler = lambda e: self.setArgument(str(key))
        for item in (cell_rect, cell_val):
            self.canvas.tag_bind(item, '<Button>', handler)

        return cell_rect, cell_val

    newCode = '''
def __init__(self, max={newSize}):
   self.__stackList = [None] * max
   self.__top = -1
'''
    
    def display(self, newSize=None, code=newCode, start=True):
        self.canvas.delete("all")

        callEnviron, wait = None, 0
        if newSize is not None:
            wait = 0.1
            callEnviron = self.createCallEnvironment(
                code=code.format(**locals()), startAnimations=start)
            canvasDims = widgetDimensions(self.canvas)
            try:
                self.highlightCode(
                    'self.__stackList = [None] * max', callEnviron, wait=wait)
            except UserStop:
                wait = 0
            self.size = newSize
            self.CELL_HEIGHT = min(self.MAX_CELL_HEIGHT,
                                   canvasDims[1] // max(6, newSize + 2))
            self.VALUE_FONT = (self.VALUE_FONT[0], 
                               -int(self.CELL_HEIGHT * self.FONT_RATIO))
                
        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)
            if wait > 0:
                try:
                    self.wait(wait / 10)
                except UserStop:
                    wait = 0
        del self.list[:]
        
        # Make an arrow pointing to the top of the empty stack
        if callEnviron:
            try:
                self.highlightCode('self.__top = -1', callEnviron, wait=wait)
            except UserStop:
                wait = 0
        self.topIndex = self.createIndex(-1)

        if callEnviron:
            self.wait(wait / 10)
            self.highlightCode([], callEnviron)
            self.cleanUp(callEnviron)

    def fixCells(self):
        if self.topIndex:
            coords = self.indexCoords(len(self.list) - 1)
            self.canvas.coords(self.topIndex[0], *coords)
            if len(self.topIndex) > 1:
                self.canvas.coords(
                    self.topIndex[1], 
                    coords[0] - abs(self.VARIABLE_FONT[1]), coords[1])
        for i, dValue in enumerate(self.list):
            cell = self.cellCoords(i)
            center = self.cellCenter(i)
            for item, coords in zip(dValue.items, (cell, center)):
                self.canvas.coords(item, *coords)
                
    def cleanUp(self, *args, **kwargs): # Customize clean up for stack
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        if len(self.callStack) == 0:
            self.fixCells()
                
    def makeButtons(self, maxRows=4):
        width_vcmd = (self.window.register(makeWidthValidate(self.maxArgWidth)),
                      '%P')
        self.pushButton = self.addOperation(
            "Push", lambda: self.clickPush(), numArguments=1,
            argHelpText=['item'], validationCmd=width_vcmd,
            helpText='Push item on stack')
        newStackButton = self.addOperation(
            "New", lambda: self.clickNewStack(), numArguments=1,
            argHelpText=['number of items'], validationCmd=width_vcmd,
            helpText='Create stack to hold N items')

        popButton = self.addOperation(
            "Pop", lambda: self.clickPop(), helpText='Pop item from stack', 
            maxRows=maxRows)
        peekButton = self.addOperation(
            "Peek", lambda: self.clickPeek(), helpText='Peek at top stack item',
            maxRows=maxRows)
        self.addAnimationButtons(maxRows=maxRows)
        return [self.pushButton, popButton, peekButton, newStackButton]

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text:
            if len(entered_text) <= self.maxArgWidth:
                return entered_text
            else:
                self.setMessage("Error! {} value is too long".format(entered_text))

    # Button functions
    def clickPush(self):
        val = self.validArgument()
        if val is None:
            return
        else:
            if len(self.list) >= self.size:
                self.setMessage("Error! Stack is already full.")
            else:
                self.push(val, start=self.startMode())
                self.setMessage("Value {} pushed!".format(val))
        self.clearArgument()

    def clickPop(self):
        val = self.pop(start=self.startMode())
        if val is None:
            self.setMessage("Error! Stack is empty.")
        else:
            self.setMessage("Value {} popped!".format(val))

    def clickPeek(self):
        val = self.peek(start=self.startMode())
        
        self.setMessage(
            "Value {} is at the top of the stack!".format(val) if val else
            "Error! Stack is empty.")

    def clickNewStack(self):
        val = self.validArgument()
        if val is None:
            return
        if not val.isdigit():
            self.setMessage("New stack size must be a number")
            self.setArgumentHighlight(color=self.ERROR_HIGHLIGHT)
            return
        newSize = int(val)
        cell0 = self.cell0()
        maxCells = 10
        while (int((cell0[1] // (maxCells + 2)) * self.FONT_RATIO) > 
               self.MIN_FONT_SIZE):
            maxCells += 1

        if 1 <= newSize and newSize <= maxCells:
            self.display(newSize, start=self.startMode())
            self.setMessage("New stack of size {} created. ".format(newSize))
            self.clearArgument()
        else:
            self.setMessage(
                "Error! Stack size must be between 1 and {}.".format(maxCells))
            self.setArgumentHighlight(color=self.ERROR_HIGHLIGHT)

if __name__ == '__main__':
    stack = Stack()
    for arg in sys.argv[1:]:
        stack.setArgument(arg)
        stack.pushButton.invoke()
    stack.runVisualization()
