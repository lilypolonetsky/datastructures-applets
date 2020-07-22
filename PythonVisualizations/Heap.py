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
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    HEAP_X0 = 80
    HEAP_Y0 = 18

    def __init__(self, size=2, maxArgWidth=MAX_ARG_WIDTH, title="Heap", **kwargs):
        super().__init__(title=title, maxArgWidth=maxArgWidth, **kwargs)
        self.size = size
        self.title = title
        self.list = []
        self.maxArgWidth = maxArgWidth
        self.buttons = self.makeButtons()
        self.display()

    def __str__(self):
        return str(self.list)
    
    # Create an index arrow to point at an indexed cell with an optional name label
    def createIndex(self, index, level=1, name='nItems'):
        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        level_spacing = self.SMALL_FONT[1]
        if level > 0:
            x0 = self.HEAP_X0 - self.CELL_WIDTH * 0.8 - level * level_spacing
            x1 = self.HEAP_X0 - self.CELL_WIDTH * 0.3
        else:
            x0 = self.HEAP_X0 + 1.8 * self.CELL_WIDTH - level * level_spacing
            x1 = self.HEAP_X0 + self.CELL_WIDTH * 1.3
        y0 = y1 = cell_center[1]
        return self.drawArrow(
            x0, y0, x1, y1, self.VARIABLE_COLOR, self.SMALL_FONT, name=name)
    
    # draw the actual arrow 
    def drawArrow(
            self, x0, y0, x1, y1, color, font, name=None):
        arrow = self.canvas.create_line(
            x0, y0, x1, y1, arrow="last", fill=color)
        leftPointing = x1 < x0
        separation = 3 if leftPointing else -3
        if name:
            label = self.canvas.create_text(
                x0 + separation, y0, text=name, anchor=W if leftPointing else E,
                font=font, fill=color)

        return (arrow, label) if name else (arrow,) 

    # HEAP FUNCTIONALITY

    def insert(self, val):
        callEnviron = self.createCallEnvironment() 
        self.startAnimations()       
        
        #If array needs to grow, add cells:
        if self.size <= len(self.list):
            cells = list(self.canvas.find_withtag("arrayCell"))
            for v in self.list: # move current array cells and values over
                cells.append(v.display_shape)
                cells.append(v.display_val)
            self.moveItemsBy(cells, (2*self.CELL_WIDTH, 0),
                             sleepTime=0.02)
            
            # Grow the the array 
            self.size *= 2
            for i in range(self.size): 
                self.createArrayCell(i)            
            
            callEnviron |= set(cells) # Old cells are now temporary
            
            #copying the values back into the larger array 
            for v in self.list:
                newValue = (self.copyCanvasItem(v.display_shape),
                            self.copyCanvasItem(v.display_val))
                self.moveItemsBy(newValue, (-2*self.CELL_WIDTH, 0), 
                                 sleepTime=0.01)
                v.display_shape, v.display_val = newValue

            # Make old cells disapper
            for item in cells:
                self.canvas.delete(item)
                callEnviron.discard(item)

        self.moveItemsBy(self.indexDisplay, (0, self.CELL_HEIGHT),
                         sleepTime=0.02)

        cellCoords = self.cellCoords(len(self.list)) # Color box
        cellCenter = self.cellCenter(len(self.list)) # Number in box

        # create new cell and cell value display objects
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
        callEnviron.discard(cellPair)

        self.siftUp(len(self.list) - 1)  # Sift up new item
                    
        # finish the animation
        self.cleanUp(callEnviron)

    def siftUp(self, i):
        if i <= 0:
            return
        callEnviron = self.createCallEnvironment()
        item = self.list[i].copy()
        copyItem = (self.copyCanvasItem(item.display_shape),
                    self.copyCanvasItem(item.display_val))
        callEnviron |= set(copyItem)
        itemDelta = (3 * self.CELL_WIDTH, 0)
        self.moveItemsBy(copyItem, itemDelta, sleepTime=0.02)
        iIndex = self.createIndex(i, name='i', level=-1)
        parentIndex = self.createIndex((i - 1) // 2, name='parent', level=-2)
        callEnviron |= set(iIndex + parentIndex)
        while 0 < i:
            parent = (i - 1) // 2
            delta = self.cellCenter(parent)[1] - self.canvas.coords(
                parentIndex[0])[1]
            if delta != 0:      # Move parent index pointer
                self.moveItemsBy(parentIndex, (0, delta), sleepTime=0.01)

            self.wait(0.2)      # Pause for comparison
            if self.list[parent] < item: # if parent less than item sifting up
                # move a copy of the parent down to node i
                copyVal = (self.copyCanvasItem(self.list[parent].display_shape),
                           self.copyCanvasItem(self.list[parent].display_val))
                callEnviron |= set(copyVal)
                self.moveItemsOnCurve(
                    copyVal, (self.cellCoords(i), self.cellCenter(i)),
                    startAngle=-90 * 11 / (10 + i - parent),
                    sleepTime=0.02)
                self.list[i].val = self.list[parent].val
                self.list[i].color = self.list[parent].color
                self.canvas.delete(self.list[i].display_shape)
                self.canvas.delete(self.list[i].display_val)
                self.list[i].display_shape, self.list[i].display_val = copyVal
                callEnviron -= set(copyVal)
            else:
                break

            # Advance i to parent, move original item along with i Index
            delta = self.cellCenter(parent)[1] - self.cellCenter(i)[1]
            self.moveItemsBy(iIndex + copyItem, (0, delta), sleepTime=0.01)
            i = parent

        # Move copied item into appropriate location
        self.moveItemsBy(copyItem, multiply_vector(itemDelta, -1),
                         sleepTime=0.01)
        self.canvas.delete(self.list[i].display_shape)
        self.canvas.delete(self.list[i].display_val)
        self.list[i].val, self.list[i].color = item.val, item.color
        self.list[i].display_shape, self.list[i].display_val = copyItem
        callEnviron -= set(copyItem)
        self.cleanUp(callEnviron)
        
    # lets user input an int argument that determines max size of the Heap
    def newArray(self):
        #gets rid of old elements in the list
        del self.list[:]
        self.size = 2
        self.display()

    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        return (self.HEAP_X0, 
                self.HEAP_Y0 + self.CELL_HEIGHT * cell_index,
                self.HEAP_X0 + self.CELL_WIDTH - self.CELL_BORDER,
                self.HEAP_Y0 + self.CELL_HEIGHT * (cell_index + 1) - self.CELL_BORDER) 

    def cellCenter(self, index):  # Center point for array cell at index
        half_cell_x = (self.CELL_WIDTH - self.CELL_BORDER) // 2
        half_cell_y = (self.CELL_HEIGHT - self.CELL_BORDER) // 2
        return add_vector(self.cellCoords(index), (half_cell_x, half_cell_y))

    def createArrayCell(self, index):  # Create a box representing an array cell
        cell_coords = self.cellCoords(index)
        half_border = self.CELL_BORDER // 2
        other_half = self.CELL_BORDER - half_border
        arrayCoords = add_vector(
            cell_coords, (-half_border, -half_border, other_half, other_half))
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

        #make a new arrow pointing to the top of the Heap
        self.indexDisplay = self.createIndex(len(self.list))

        # go through each Drawable in the list
        for i, n in enumerate(self.list):
            # create display objects for the associated Drawables
            n.display_shape, n.display_val = self.createCellValue(
                i, n.val, n.color)
            n.color = self.canvas.itemconfigure(n.display_shape, 'fill')

        self.window.update()


    def fixCells(self):  # Move canvas display items to exact cell coords
        for i, drawItem in enumerate(self.list):
            self.canvas.coords(drawItem.display_shape, *self.cellCoords(i))
            self.canvas.coords(drawItem.display_val, *self.cellCenter(i))

    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        self.fixCells()       # Restore cells to their coordinates in array

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # numArguments decides the side where the button appears in the operations grid
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1, validationCmd=vcmd)
        newHeapButton = self.addOperation( 
            "New", lambda: self.newArray())
        self.addAnimationButtons()

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
            if len(self.list) >= self.MAX_SIZE:
                self.setMessage("Error! Heap is already full.")
            else:
                self.insert(val)
                self.setMessage("Value {} inserted".format(val))
        self.clearArgument()

if __name__ == '__main__':
    # random.seed(3.14159)    # Use fixed seed for testing consistency
    HEAP = Heap()
    HEAP.runVisualization()
