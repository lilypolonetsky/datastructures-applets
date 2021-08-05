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

class Queue(VisualizationApp):
    WIDTH = 800
    HEIGHT = 400
    CELL_SIZE = 50
    ARRAY_X0 = 100
    ARRAY_Y0 = 100
    nextColor = 0
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    MAX_CELLS = 12

    def __init__(              # Create a circular Queue visualization
            self, center=None, # centered at these coords (or canvas center)
            outerRadius=0.9,   # w/ outer and inner radius specified as either
            innerRadius=0.5,   # a fraction of the height or in pixels
            size=10,           # with a particular number of cells
            maxArgWidth=6,     # Maximum width of keys/values to show
            frontIndexColor='blue', # Colors for index displays or '' for none
            rearIndexColor='dark green',
            valueColor='black', 
            valueFont=('Helvetica', 16),
            variableColor='brown3',
            variableFont=('Courier', 14),
            numericIndexColor='gray40', # Color and font for numeric indices in
            numericIndexFont=('Courier', 11), # in cells and covered by values 
            title="Queue",
            **kwargs):
        kwargs['title'] = title
        kwargs['maxArgWidth'] = maxArgWidth
        super().__init__(**kwargs)
        self.list = [None]*size
        self.size = size
        self.nItems = 0
        self.front = 1  # when Queue is empty, front is one more than rear
        self.rear = 0
        self.frontIndexColor = frontIndexColor
        self.rearIndexColor = rearIndexColor
        self.valueColor = valueColor
        self.valueFont = valueFont
        self.variableColor = variableColor
        self.variableFont = variableFont
        self.numericIndexColor = numericIndexColor
        self.numericIndexFont = numericIndexFont
        if center is None:
            center = V(widgetDimensions(self.canvas)) / 2
        self.center = tuple(map(int, center))
        minDimension = min(*self.center)
        self.innerRadius = (innerRadius * minDimension if innerRadius <= 1 else
                            innerRadius)
        self.outerRadius = (outerRadius * minDimension if outerRadius <= 1 else
                            outerRadius)
        self.textRadius = (self.innerRadius + self.outerRadius) / 2
        self.makeButtons()
        self.display()

    def __str__(self):
        return str([d.val for d in self.list])
    
    # ANIMATION METHODS
    def createIndex(  # Create an arrow to point at a particuar cell
            self,     # cell with an optional name label
            index=-1,
            name=None,
            color=None,
            level=1): # Level controls arrow length to avoid overlapping labels
        if color == '':  # No color means no index created
            return tuple()
        elif color is None:
            color = self.variableColor
        arrow_coords = self.arrowCoords(index, level)
        arrow = self.canvas.create_line(
            *arrow_coords, arrow="last", fill=color)
        if name:
            label = self.canvas.create_text(
                arrow_coords[0], arrow_coords[1], text=name, 
                anchor=self.labelAnchor(arrow_coords, level),
                font=self.variableFont, fill=color)
        return (arrow, label) if name else (arrow,)

    # Arrow endpoint coordinates to point at cell
    # Level 1 is nearest inside inner radius, Level 2 is close to center
    # Negative levels are inside the array cell and is used for positioning the
    # numeric indices
    def arrowCoords(self, cellIndex, level=1):
        angle = (cellIndex + 0.5) * -self.sliceAngle
        tip = V(self.innerRadius * 0.95, 0).rotate(angle)
        back = V(self.innerRadius - self.variableFont[1] * level * 2.8,
                 0).rotate(angle)
        return (V(self.center) + V(back)) + (V(self.center) + V(tip))

    # Anchor for index label indexed on horizontal-vertical (0 or 1), then
    # (xSign, ySign, level % 2)
    anchors = [
        {(+1, +1, 0): SE, (-1, +1, 0): SW,
         (+1, +1, 1): NE, (-1, +1, 1): NW,
         (+1, -1, 0): SE, (-1, -1, 0): SW,
         (+1, -1, 1): NE, (-1, -1, 1): NW,
        },
        {(+1, +1, 0): SW, (-1, +1, 0): SW,
         (+1, +1, 1): SE, (-1, +1, 1): SE,
         (+1, -1, 0): NW, (-1, -1, 0): NW,
         (+1, -1, 1): NE, (-1, -1, 1): NE,
        },
        ]
    
    def labelAnchor(self, arrowCoords, level):
        return 'center'
    
    def moveIndexTo(
            self, indexItems, cellIndex, level, steps=10, sleepTime=0.02):
        '''Move an index arrow and optional label to the point at the cell
        indexed by cellIndex from its current position'''
        newArrowCoords = self.arrowCoords(cellIndex, level)
        self.moveItemsLinearly(indexItems, [newArrowCoords, newArrowCoords[:2]],
                         steps=steps, sleepTime=sleepTime)

    def sliceRange(self, index):
        index %= self.size
        return (self.sliceAngle * index, self.sliceAngle)

    def outerCoords(self):
        outer = (self.outerRadius, ) * 2
        return (V(self.center) - V(outer)) + (V(self.center) + V(outer))

    def innerCoords(self):
        inner = (self.innerRadius, ) * 2
        return (V(self.center) - V(inner)) + (V(self.center) + V(inner))

    def outputBoxFontAndPadding(self, font=None):
        if font is None:
            font = (self.VALUE_FONT[0], -self.VALUE_FONT[1] * 3 // 4)
        pad = abs(font[1]) // 2
        return font, pad
        
    def outputBoxCoords(self, nItems=1, font=None):
        canvasDims = widgetDimensions(self.canvas)
        font, pad = self.outputBoxFontAndPadding(font)
        lineHeight = textHeight(font)
        lineWidth = textWidth(font, '▢' * self.maxArgWidth) + pad * 2
        y1 = self.center[1] + self.outerRadius
        y0 = y1 - lineHeight * nItems - pad * 2
        x0 = canvasDims[0] - lineHeight - lineWidth
        return x0, y0, x0 + lineWidth, y1 

    def createOutputBox(self, nItems=1, label=None, font=None):
        font, pad = self.outputBoxFontAndPadding(font)
        coords = self.outputBoxCoords(nItems, font)
        items = (
            self.canvas.create_rectangle(*coords, fill=self.OPERATIONS_BG),)
        if label:
            items += (self.canvas.create_text(
                (coords[0] + coords[2]) // 2, coords[1] - pad, text=label,
                font=self.VARIABLE_FONT, fill = self.VARIABLE_COLOR),)
        return items

    def outputBoxLineCoords(self, line=0, font=None):
        font, pad = self.outputBoxFontAndPadding(font)
        boxCoords = self.outputBoxCoords(line + 1, font)
        lineHeight = textHeight(font)
        return ((boxCoords[0] + boxCoords[2]) // 2, 
                boxCoords[3] - pad - lineHeight // 2)
        
    def newCellValue(self, index, value, color=None):
        if color is None:
            color = drawnValue.palette[self.nextColor]
            # increment nextColor
            self.nextColor = (self.nextColor + 1) % len(drawnValue.palette)

        sliceRange = self.sliceRange(index)
        arc = self.canvas.create_arc(
            *self.outerCoords(), start=sliceRange[0], extent = sliceRange[1],
            fill=color, width=0, outline='', style=PIESLICE,
            tags='value background')
        self.canvas.tag_lower(arc, 'cell')
        cover = self.canvas.create_arc(
            *self.innerCoords(), start=sliceRange[0], extent = sliceRange[1],
            fill=self.canvas.itemConfig(self.sliceCover, 'fill'),
            width=0, outline='', style=PIESLICE, tags='value background')
        self.canvas.tag_lower(cover, 'cell')
        textDelta = V((self.innerRadius + self.outerRadius) / 2, 0).rotate(
            (index + 0.5) * -self.sliceAngle)
        text = self.canvas.create_text(
            *(V(self.center) + V(textDelta)), text=value,
            font=self.valueFont, fill=self.valueColor)
        return (arc, text, cover)

    isEmptyCode = '''
def isEmpty(self): return self.__nItems == 0
'''

    def isEmpty(self, code=isEmptyCode):
        callEnviron = self.createCallEnvironment(code=code)
        self.highlightCode('return self.__nItems == 0', callEnviron, wait=0.1)
        self.cleanUp(callEnviron)
        return self.nItems == 0

    isFullCode = '''
def isFull(self): return self.__nItems == self.__maxSize
'''

    def isFull(self, code=isFullCode):
        callEnviron = self.createCallEnvironment(code=code)
        self.highlightCode('return self.__nItems == self.__maxSize',
                           callEnviron, wait=0.1)
        self.cleanUp(callEnviron)
        return self.nItems >= self.size
    
    insertCode = '''
def insert(self, item={val!r}):
   if self.isFull():
      raise Exception("Queue overflow")
   self.__rear += 1
   if self.__rear == self.__maxSize:
      self.__rear = 0
   self.__que[self.__rear] = item
   self.__nItems += 1
   return True
'''
    
    # insert item at rear of queue   
    def insertRear(self, val, code=insertCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        wait = 0.1

        self.highlightCode('self.isFull()', callEnviron, wait=wait)
        if self.isFull():
            self.highlightCode(
                'raise Exception("Queue overflow")', callEnviron, wait=wait,
                color=self.EXCEPTION_HIGHLIGHT)
            self.cleanUp(callEnviron)
            return False

        # increment rear
        self.highlightCode('self.__rear += 1', callEnviron, wait=wait)
        nextRear = (self.rear + 1) % self.size
        if self.rearArrow:
            self.moveIndexTo(self.rearArrow, nextRear, self.rearLevel)
        
        # deal with wraparound
        self.highlightCode(
            'self.__rear == self.__maxSize', callEnviron, wait=wait)
        if nextRear == 0:
            self.highlightCode('self.__rear = 0', callEnviron, wait=wait)

        # insert the item
        self.highlightCode(
            'self.__que[self.__rear] = item', callEnviron, wait=wait)

        # create new cell and cell value display objects
        # Start drawing new one at rear
        cellValue = self.newCellValue(nextRear, val)
        callEnviron |= set(cellValue)

        # Show nItems being incremented
        self.highlightCode('self.__nItems += 1', callEnviron)
        self.updateNItems(self.nItems + 1)
        self.rear = nextRear
        self.list[self.rear] = drawnValue(val, *cellValue)
        callEnviron -= set(cellValue)
        self.wait(wait)

        # update window
        self.highlightCode('return True', callEnviron, wait=wait)
        self.cleanUp(callEnviron)
        return True

    removeFrontCode = '''
def remove(self):
   if self.isEmpty():
      raise Exception("Queue underflow")
   front = self.__que[self.__front]
   self.__que[self.__front] = None
   self.__front += 1
   if self.__front == self.__maxSize:
      self.__front = 0
   self.__nItems -= 1
   return front
'''
    
    # remove the front element of the queue, or None if empty
    def removeFront(self, code=removeFrontCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        wait = 0.1

        self.highlightCode('self.isEmpty()', callEnviron, wait=wait)
        if self.isEmpty():
            self.highlightCode(
                'raise Exception("Queue underflow")',
                callEnviron, wait=wait, color=self.EXCEPTION_HIGHLIGHT)
            self.cleanUp(callEnviron)
            return None

        outFont, pad = self.outputBoxFontAndPadding()
        box = self.createOutputBox(1, 'front')
        callEnviron |= set(box)
        self.highlightCode(
            'front = self.__que[self.__front]', callEnviron, wait=wait)
            
        #get the value at front
        n = self.list[self.front]
        val = self.canvas.copyItem(n.items[1])
        callEnviron.add(val)
        self.moveItemsTo(val, self.outputBoxLineCoords(), sleepTime=0.01)
        self.canvas.itemconfigure(val, font=outFont)

        # set front value to None so it will be garbage collected
        self.highlightCode('self.__que[self.__front] = None', callEnviron)
        quadrant = [E, N, W, S][
            ((self.front + self.size // 4) * 4 // self.size) % 4]
        callEnviron |= set(n.items)
        self.moveItemsOffCanvas(n.items, quadrant, sleepTime=0.01)
        self.list[self.front] = None
        for i in n.items:
            self.canvas.delete(i)
        
        #increment front
        self.highlightCode('self.__front += 1', callEnviron)
        newFront = (self.front + 1) % self.size
        if self.frontArrow:
            self.moveIndexTo(self.frontArrow, newFront, self.frontLevel)
        self.highlightCode(
            'self.__front == self.__maxSize', callEnviron, wait=wait)
        if newFront == 0:
            self.highlightCode('self.__front = 0', callEnviron, wait=wait)
        self.front = newFront
        
        # decrement number of items
        self.highlightCode('self.__nItems -= 1', callEnviron, wait=wait)
        self.updateNItems(self.nItems - 1)

        self.highlightCode('return front', callEnviron, wait=wait)
        self.cleanUp(callEnviron)
        return n.val

    peekCode = '''
def peek(self):
   return None if self.isEmpty() else self.__que[self.__front]
'''
    
    def peek(self, code=peekCode, start=True):
        callEnviron = self.createCallEnvironment(
            code.format(**locals()), startAnimations=start)
        wait = 0.1

        self.highlightCode('self.isEmpty()', callEnviron, wait=wait)
        if self.isEmpty():
            self.highlightCode('return None', callEnviron, wait=wait)
            self.cleanUp(callEnviron)
            return None

        # create the output box
        self.highlightCode(['return', 'self.__que[self.__front]'], callEnviron)
        font, pad = self.outputBoxFontAndPadding()
        outputBox = self.createOutputBox()
        callEnviron |= set(outputBox)

        # calculate where the value will need to move to
        peekValCoords = self.outputBoxLineCoords()

        # create the value to move to output box
        valueOutput = self.canvas.copyItem(self.list[self.front].items[1])
        callEnviron.add(valueOutput)

        # move value to output box and use its font
        self.moveItemsTo(valueOutput, peekValCoords, sleepTime=.02)
        self.canvas.itemconfig(valueOutput, font=font)

        self.cleanUp(callEnviron)
        return self.list[self.front].val

    newCode = '''
def __init__(self, size={newSize}):
   self.__maxSize = size
   self.__que = [None] * size
   self.__front = 1
   self.__rear = 0
   self.__nItems = 0
'''
    def display(self, newSize=None, code=newCode, start=True):
        callEnviron, wait = None, 0
        if newSize is not None:
            callEnviron = self.createCallEnvironment(
                code.format(**locals()), startAnimations=start)

        self.canvas.delete("all")
        if callEnviron:
            wait = 0.1
            try:
                sizeRequest = self.canvas.create_text(
                    *(V(widgetDimensions(self.canvas)) / 2),
                    text=str(newSize), 
                    font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
                callEnviron.add(sizeRequest)
                self.highlightCode(
                    'self.__maxSize = size', callEnviron, wait=wait)
                self.highlightCode(
                    'self.__que = [None] * size', callEnviron, wait=wait)
            except UserStop:
                wait = 0
            self.size = newSize
            self.list = [None] * self.size
            self.canvas.delete(sizeRequest)
            callEnviron.discard(sizeRequest)
        self.createCells(self.size, wait/10)  # Draw grid of cells

        self.front = 1
        self.frontLevel = 2
        if callEnviron and wait:
            try:
                self.highlightCode('self.__front = 1', callEnviron, wait=wait)
            except UserStop:
                wait = 0
        self.frontArrow = self.createIndex(
            self.front, "_front", level=self.frontLevel,
            color=self.frontIndexColor)
            
        self.rear = 0
        self.rearLevel = 1
        if callEnviron and wait:
            try:
                self.highlightCode('self.__rear = 0', callEnviron, wait=wait)
            except UserStop:
                wait = 0
        self.rearArrow = self.createIndex(
            self.rear, "_rear", level=self.rearLevel,
            color=self.rearIndexColor)

        self.nItems = 0
        if callEnviron and wait:
            try:
                self.highlightCode('self.__nItems = 0', callEnviron, wait=wait)
            except UserStop:
                wait = 0
        self.nItemsDisplay = self.canvas.create_text(
            self.center[0] - self.outerRadius, 
            self.center[1] - self.outerRadius,
            text='_nItems: {}'.format(self.nItems), anchor=NW,
            font=self.variableFont, fill=self.variableColor)
        
        if callEnviron:
            self.highlightCode([], callEnviron)
            self.cleanUp(callEnviron)

    def updateNItems(self, newNItems):
        self.nItems = newNItems
        self.canvas.itemconfigure(
            self.nItemsDisplay, text='nItems: {}'.format(self.nItems))

# Button functions
    def clickNew(self):
        entered_text = self.getArgument()
        if not (entered_text.isdigit() and 1 < int(entered_text) and
                int(entered_text) <= self.MAX_CELLS):
            self.setMessage('New queue must have 2 - {} cells'.format(
                self.MAX_CELLS))
            return
        self.display(newSize=int(entered_text), start=self.startMode())
        
    def clickInsertRear(self):
        entered_text = self.getArgument()
        if entered_text:
            if self.insertRear(entered_text, start=self.startMode()):
                self.setMessage('Value {} inserted'.format(repr(entered_text)))
                self.clearArgument()
            else:
                self.setMessage('Queue is full!')

    def clickPeek(self):
        val = self.peek(start=self.startMode())
        self.setMessage(
            "Value {} is at the front of the queue".format(repr(val)) if val
            else "Queue is empty")

    def clickRemove(self):
        front = self.removeFront(start=self.startMode())
        self.setMessage('Value {} removed'.format(repr(front)) if front else
                        'Queue is empty!')

    def makeButtons(self, maxRows=4):
        vcmd = (self.window.register(makeWidthValidate(self.maxArgWidth)), '%P')
        self.insertButton = self.addOperation(
            "Insert", lambda: self.clickInsertRear(), numArguments=1,
            validationCmd=vcmd, argHelpText=['item'],
            helpText='Insert item at rear of queue')
        self.newButton = self.addOperation(
            "New", lambda: self.clickNew(), numArguments=1, validationCmd=vcmd,
            argHelpText=['number of items'], 
            helpText='Create queue to hold N items')

        self.removeButton = self.addOperation(
            "Remove", lambda: self.clickRemove(), maxRows=maxRows,
            helpText='Remove item at front of queue')
        self.peekButton = self.addOperation(
            "Peek", lambda: self.clickPeek(), maxRows=maxRows,
            helpText='Peek at front of queue item')
        self.addAnimationButtons(maxRows=maxRows)

    def createCells(self, nCells, wait=0): # Create array cells in a circle
        self.sliceAngle = 360 / nCells
                    
        self.sliceCover = self.canvas.create_oval(
            *self.innerCoords(), fill=self.DEFAULT_BG, width=self.CELL_BORDER,
            outline=self.CELL_BORDER_COLOR, tags='cover')

        self.slices, self.numericIndices = [], []
        for sliceI in range(nCells):
            self.slices.append(self.canvas.create_arc(
                *self.outerCoords(),
                start=self.sliceAngle * sliceI, extent = self.sliceAngle,
                fill='', width=self.CELL_BORDER, outline=self.CELL_BORDER_COLOR,
                style=PIESLICE, tags='cell'))
            self.canvas.tag_lower(self.slices[-1], 'cover')
            if self.numericIndexColor and self.numericIndexFont:
                self.numericIndices.append(self.canvas.create_text(
                    *self.arrowCoords(sliceI, -0.3)[:2], text=str(sliceI),
                    font=self.numericIndexFont, fill=self.numericIndexColor))
            if wait:
                try:
                    self.wait(wait)
                except UserStop:
                    wait = 0

    def restoreIndices(self):
        if self.frontArrow:
            arrowCoords = self.arrowCoords(self.front, self.frontLevel)
            self.canvas.coords(self.frontArrow[0], *arrowCoords)
            self.canvas.coords(self.frontArrow[1], *arrowCoords[:2])
        if self.rearArrow:
            arrowCoords = self.arrowCoords(self.rear, self.rearLevel)
            self.canvas.coords(self.rearArrow[0], *arrowCoords)
            self.canvas.coords(self.rearArrow[1], *arrowCoords[:2])
        self.updateNItems(self.nItems)
        
    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        if len(self.callStack) == 0:
            self.restoreIndices()

if __name__ == '__main__':
    queue = Queue()
    for arg in sys.argv[1:]:
        queue.setArgument(arg)
        queue.insertButton.invoke()
        
    queue.runVisualization()
