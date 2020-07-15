import time
from tkinter import *

try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

class Heap(VisualizationApp):
    nextColor = 0
    MAX_ARG_WIDTH = 8
    MAX_SIZE = 31
    CELL_WIDTH = 25
    CELL_HEIGHT = 12
    CELL_BORDER = 1
    CELL_BORDER_COLOR = 'black'
    HEAP_X0 = 50
    HEAP_Y0 = 30

    def __init__(self, size=2, maxArgWidth=MAX_ARG_WIDTH, title="Heap", **kwargs):
        super().__init__(title=title, maxArgWidth=maxArgWidth, **kwargs)
        self.size = size
        self.title = title
        self.list = []
        self.maxArgWidth = maxArgWidth
        self.buttons = self.makeButtons()
        self.display()
        self.indexDisplay = self.createIndex(len(self.list))

    def __str__(self):
        return str(self.list)
    
    # Create an index arrow to point at an indexed cell with an optional name label
    def createIndex(self, index, name=None):
        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        x0 = self.HEAP_X0 - self.CELL_WIDTH -5
        x1 = self.HEAP_X0 - self.CELL_WIDTH * 3 // 10
        y0 = y1 =cell_coords[-1] + self.CELL_HEIGHT // 2 
        if not name:
            label = "nItems" #labels the top of the Heap "top" with the pointer arrow
        else:
            label = name
        return self.drawArrow(
            x0, y0, x1, y1, self.VARIABLE_COLOR, self.SMALL_FONT, name=label)   
    
    # draw the actual arrow 
    def drawArrow(
            self, x0, y0, x1, y1, color, font, name=None):
        arrow = self.canvas.create_line(
            x0, y0, x1, y1, arrow="last", fill=color)
        if name:
            label = self.canvas.create_text(
                x0 - self.CELL_WIDTH / 2, y0 + (self.CELL_HEIGHT / 16) -3, text=name, anchor=SW,
                font=font, fill=color)

        return (arrow, label) if name else (arrow,) 

    def swap(self, a, b, aCellObjects=[], bCellObjects=[]):
        itemsA = [self.list[a].display_shape,
                  self.list[a].display_val] + aCellObjects
        itemsB = [self.list[b].display_shape,
                  self.list[b].display_val] + bCellObjects
        upDelta = (0, - self.CELL_HEIGHT * 4 // 3)
        downDelta = multiply_vector(upDelta, -1)
        if a == b:  # Swapping with self - just move up & down
            self.moveItemsBy(itemsA, upDelta, sleepTime=0.02)
            self.moveItemsBy(itemsA, downDelta, sleepTime=0.02)
            return

        # make a and b cells plus their associated items switch places
        self.moveItemsOnCurve(
            itemsA + itemsB, [self.canvas.coords(i) for i in itemsB + itemsA],
            sleepTime=0.05, startAngle=90 * 11 / (10 + abs(a - b)))

        # perform the actual cell swap operation in the list
        self.list[a], self.list[b] = self.list[b], self.list[a]    

    # HEAP FUNCTIONALITY

    def insert(self, val):
        callEnviron = self.createCallEnvironment() 
        self.startAnimations()       
        
        #If array needs to grow, add cells:
        if self.size < len(self.list) + 1:
            #making a tag for the array 
            arrayList = self.canvas.find_withtag("arrayCell")
            #making a tag for the copy of the array 
            for cell in arrayList:
                item = self.copyCanvasItem(cell)
                self.canvas.itemconfig(item, tags="newArrayCell")
            newArrayList = self.canvas.find_withtag("newArrayCell")
            newArrayList = list(newArrayList)
            boxes = list(newArrayList)
            callEnviron |= set(boxes)   
            #adding the values to the list of the copy of the array 
            for i in range(len(self.list)):
                newArrayList += [self.list[i].display_shape, self.list[i].display_val]
            self.moveItemsBy(newArrayList, (2*self.CELL_WIDTH, 0))          #moving the whole array over
            
            # Growing the the array 
            for i in range(self.size*2): 
                self.createArrayCell(i)            
            self.size *= 2
            #copying the values back into the larger array 
            copyVals = []
            for i in range(len(self.list)):
                copyVals += [self.list[i].display_shape, self.list[i].display_val]
            self.moveItemsBy(copyVals, (-2*self.CELL_WIDTH, 0))    
            #getting rid of the smaller array 
            

        #don't move arrow up if the first cell is being filled because it is already pointing there
        if len(self.list) >= 1:
            self.moveItemsBy(self.indexDisplay, (0, + (self.CELL_HEIGHT)))

        cellCoords = self.cellCoords2(len(self.list)) # Color box
        cellCenter = self.cellCenter2(len(self.list)) # Number in box

        # create new cell and cell value display objects
        cellCoords = add_vector(cellCoords, (0, 0, 0, self.CELL_BORDER))
        toPositions = (cellCoords, cellCenter)

        # determine the top left and bottom right positions
        startPosition = [self.HEAP_X0, 0, self.HEAP_X0, 0] #Color 
        startPosition = add_vector(startPosition, (0, 0, self.CELL_WIDTH, self.CELL_HEIGHT)) #color`
        cellPair = self.createCellValue(startPosition, val)
        callEnviron.add(cellPair)
        self.moveItemsTo(cellPair, toPositions, steps=self.CELL_HEIGHT, sleepTime=0.01)
    
        # add a new Drawable with the new value, color, and display objects
        d = drawable(
            val, self.canvas.itemconfigure(cellPair[0], 'fill')[-1], *cellPair)
        self.list.append(d)    #store item at the end of the list     
        
        if len(self.list) <= 0:            # heap condition.  The root node, i = 0,
            return         
        
        for i in range(len(self.list)-1, 0, -1):
            if self.list[i] < self.list[(i - 1) // 2]:  #if i is less than its parent 
                self.swap(i, (i-1)//2)
                    
        callEnviron.discard(cellPair)
        # finish the animation
        self.cleanUp(callEnviron)

    # lets user input an int argument that determines max size of the Heap
    def newArray(self):
        #gets rid of old elements in the list
        del self.list[:]
        self.size = 2
        self.display()

        #make a new arrow pointing to the top of the Heap
        self.indexDisplay = self.createIndex(len(self.list))

    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        return (self.HEAP_X0 + self.CELL_BORDER,  #width
                (self.HEAP_Y0 + self.CELL_HEIGHT * (cell_index + 1)) + self.CELL_BORDER,  #height
                self.HEAP_X0 + self.CELL_WIDTH - self.CELL_BORDER,
                self.HEAP_Y0 + self.CELL_HEIGHT * cell_index - self.CELL_BORDER) 
    
    def cellCoords2(self, cell_index):  # Get bounding rectangle for array cell
        return (self.HEAP_X0 + self.CELL_BORDER,  #width
                (self.HEAP_Y0 + self.CELL_HEIGHT * (cell_index + 1)),  #height
                self.HEAP_X0 + self.CELL_WIDTH - self.CELL_BORDER,
                self.HEAP_Y0 + self.CELL_HEIGHT * cell_index) 
    

    def cellCenter(self, index):  # Center point for array cell at index
        half_cell_x = (self.CELL_WIDTH - self.CELL_BORDER) // 2
        half_cell_y = (self.CELL_HEIGHT - self.CELL_BORDER) // 2

        return subtract_vector(self.cellCoords(index), (half_cell_x, half_cell_y))
    
    def cellCenter2(self, index):  # Center point for array cell at index
        half_cell_x = (self.CELL_WIDTH + self.CELL_BORDER) // 2
        half_cell_y = (self.CELL_HEIGHT - self.CELL_BORDER) // 2
        
        return add_vector(subtract_vector(self.cellCoords(index), (0, half_cell_y)), (half_cell_x, 0))    

    def createArrayCell(self, index):  # Create a box representing an array cell
        cell_coords = self.cellCoords(index)
        half_border = self.CELL_BORDER // 2
        arrayCoords = add_vector(cell_coords,
                                 (half_border-1, half_border-1,
                                  self.CELL_BORDER - half_border-1, self.CELL_BORDER - half_border))
        rect = self.canvas.create_rectangle(arrayCoords,
                                            fill=None, outline=self.CELL_BORDER_COLOR, width=self.CELL_BORDER, tags= "arrayCell")
        self.canvas.lower(rect)

        return rect

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
            color = drawable.palette[Heap.nextColor]
            Heap.nextColor = (Heap.nextColor + 1) % len(drawable.palette)
        cell_rect = self.canvas.create_rectangle(
            *rectPos, fill=color, outline='', width=0)
        cell_val = self.canvas.create_text(
            *valPos, text=str(key), font=self.SMALL_FONT, fill=self.VALUE_COLOR)
        handler = lambda e: self.setArgument(str(key))
        for item in (cell_rect, cell_val):
            self.canvas.tag_bind(item, '<Button>', handler)

        return cell_rect, cell_val

    def display(self):
        self.canvas.delete("all")

        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)

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

        # numArguments decides the side where the button appears in the operations grid
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1)
        newHeapButton = self.addOperation(
            "New", lambda: self.newArray())

        return [insertButton, newHeapButton]
    
    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val

    # Button functions
    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            if len(self.list) == self.MAX_SIZE:
                self.setMessage("Error! Heap is already full.")
            else:
                self.insert(val)
                self.setMessage("Value {} inserted!".format(val))
        self.clearArgument()
        
    def setButtonsStatus(self, state=NORMAL):
        for b in self.buttons:
            b['state'] = state


if __name__ == '__main__':
    # random.seed(3.14159)    # Use fixed seed for testing consistency
    HEAP = Heap()
    HEAP.runVisualization()