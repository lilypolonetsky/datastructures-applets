import time
from tkinter import *
import random 

try:
    from drawnValue import *
    from coordinates import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .coordinates import *
    from .VisualizationApp import *

V = vector

class Heap(VisualizationApp):
    nextColor = 0
    MAX_SIZE = 31
    CELL_WIDTH = 25
    CELL_HEIGHT = 12
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    ARRAY_X0 = 80
    ARRAY_Y0 = 18

    def __init__(self, size=2, valMax=99, title="Heap", **kwargs):
        super().__init__(title=title, **kwargs)
        self.size = size
        self.title = title
        self.list = []
        self.nItems = 0
        self.valMax = valMax
        self.arrayCopyDelta = (2 * self.CELL_WIDTH, 0)
        self.siftDelta = (3 * self.CELL_WIDTH, 0)
        self.buttons = self.makeButtons()
        self.display()

    def __str__(self):
        return str(self.list)
    
    # Create index arrow to point at an array cell with an optional name label
    def createArrayIndex(self, index, level=1, name='nItems'):
        return self.drawArrow(
            *self.arrayIndexCoords(index, level), self.VARIABLE_COLOR,
            self.SMALL_FONT, name=name)

    def arrayIndexCoords(self, index, level=1):
        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        level_spacing = abs(self.SMALL_FONT[1])
        if level > 0:
            x0 = self.ARRAY_X0 - self.CELL_WIDTH * 0.8 - level * level_spacing
            x1 = self.ARRAY_X0 - self.CELL_WIDTH * 0.3
        else:
            x0 = self.ARRAY_X0 + 1.8 * self.CELL_WIDTH - level * level_spacing
            x1 = self.ARRAY_X0 + self.CELL_WIDTH * 1.3
        y0 = y1 = cell_center[1]
        return x0, y0, x1, y1
    
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

    insertCode = '''
def insert(self, item={val}):
   if self.isFull():
      self._growHeap()
   self._arr[self._nItems] = item
   self._nItems += 1
   self._siftUp(self._nItems - 1)
'''
    
    def insert(self, val, code=insertCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        
        #If array needs to grow, add cells:
        self.highlightCode('self.isFull()', callEnviron, wait=wait)
        if self.size <= len(self.list):
            self.highlightCode('self._growHeap()', callEnviron)
            self._growHeap()

        # Create new item near top left corner
        startPosition = V(self.cellCoords(-1.4)) - V(self.siftDelta * 2)
        cellPair = self.createCellValue(startPosition, val)
        callEnviron |= set(cellPair)

        # Place it in the array
        self.highlightCode('self._arr[self._nItems] = item', callEnviron)
        toPositions = (self.cellCoords(len(self.list)), 
                       self.cellCenter(len(self.list)))
        self.moveItemsTo(cellPair, toPositions, sleepTime=wait / 10)
    
        # add a new drawnValue with the new value, color, and display objects
        d = drawnValue(val, *cellPair)
        self.list.append(d)    #store item at the end of the list
        callEnviron -= set(cellPair)
        self.nItems = len(self.list)
        
        # Move nItems index to one past inserted item
        self.highlightCode('self._nItems += 1', callEnviron)
        coords = self.arrayIndexCoords(self.nItems)
        self.moveItemsTo(self.nItemsIndex, (coords, coords[:2]), 
                         sleepTime=wait / 10)
            
        self.highlightCode('self._siftUp(self._nItems - 1)', callEnviron)
        self.siftUp(self.nItems - 1)  # Sift up new item
                    
        # finish the animation
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    growHeapCode = '''
def _growHeap(self):
   current = self._arr
   self._arr = [None] * 2 * len(self._arr)
   for i in range(self._nItems):
      self._arr[i] = current[i]
'''
    
    def _growHeap(self, code=growHeapCode):
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code)

        self.highlightCode('current = self._arr', callEnviron)
        callEnviron.add(self.canvas.create_text(
            *self.cellCenter(-1), text='_arr',
            anchor=S, font=self.SMALL_FONT, fill=self.VARIABLE_COLOR))
        callEnviron.add(self.canvas.create_text(
            *(V(self.cellCenter(-1)) + V(self.arrayCopyDelta)), text='current',
            anchor=S, font=self.SMALL_FONT, fill=self.VARIABLE_COLOR))
        cells = self.canvas.find_withtag("arrayCell")
        cells_and_values = list(cells)
        for v in self.list: # move current array cells and values over
            cells_and_values.extend(v.items)
        self.moveItemsBy(cells_and_values, self.arrayCopyDelta,
                         sleepTime=wait / 10)
            
        # Grow the the array 
        self.highlightCode('self._arr = [None] * 2 * len(self._arr)',
                           callEnviron)
        for i in range(self.size): 
            callEnviron.add(self.createArrayCell(i)) # Temporary
            if i + self.size < self.MAX_SIZE:
                self.createArrayCell(i + self.size) # Lasting
        self.size = min(self.size * 2, self.MAX_SIZE)
            
        #copying the values back into the larger array 
        self.highlightCode('i in range(self._nItems)', callEnviron,
                           wait=wait / 5)
        for v in self.list:
            self.highlightCode('self._arr[i] = current[i]', callEnviron)
            newValue = tuple(self.copyCanvasItem(i) for i in v.items)
            callEnviron |= set(newValue)
            self.moveItemsBy(newValue, V(self.arrayCopyDelta) * -1,
                             sleepTime=wait / 10)
            self.highlightCode('i in range(self._nItems)', callEnviron,
                               wait=wait / 5)

        # Move old cells back to original positions in one step
        # These are lasting and overlap the temporary ones just created
        self.moveItemsBy(cells_and_values, V(self.arrayCopyDelta) * -1, steps=1)
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    siftUpCode = '''
def _siftUp(self, i={i}):
   if i <= 0:
      return
   item = self._arr[i]
   itemkey = self._key(item)
   while 0 < i:
      parent = self.parent(i)
      if self._key(self._arr[parent]) < itemkey:
         self._arr[i] = self._arr[parent]
         i = parent
      else:
         break
   self._arr[i] = item
'''
    
    def siftUp(self, i, code=siftUpCode):
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))

        iIndex = self.createArrayIndex(i, name='i', level=-1)
        callEnviron |= set(iIndex)
        self.highlightCode('i <= 0', callEnviron, wait=wait)
        if i <= 0:
            self.highlightCode('return', callEnviron)
            self.cleanUp(callEnviron)
            return
        
        self.highlightCode('item = self._arr[i]', callEnviron, wait=wait)
        upItem = self.list[i].copy()
        copyItem = tuple(self.copyCanvasItem(i) for i in upItem.items)
        callEnviron |= set(copyItem)
        self.moveItemsBy(copyItem, self.siftDelta, sleepTime=wait / 10)

        self.highlightCode('itemkey = self._key(item)', callEnviron, wait=wait)
        copyItemCoords = [self.canvas.coords(item) for item in copyItem]
        itemLabel = self.canvas.create_text(
            *(V(copyItemCoords[1]) - V(0, self.CELL_HEIGHT)), text='itemkey',
            font=self.SMALL_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(itemLabel)

        parentIndex = None
        self.highlightCode('0 < i', callEnviron, wait=wait)
        while 0 < i:
            self.highlightCode('parent = self.parent(i)', callEnviron)
            parent = (i - 1) // 2
            if parentIndex is None:
                parentIndex = self.createArrayIndex(parent, name='parent')
                callEnviron |= set(parentIndex)
            else:
                parentCoords = self.arrayIndexCoords(parent)
                self.moveItemsTo(parentIndex, (parentCoords, parentCoords[:2]),
                                 sleepTime=wait / 10)

            self.highlightCode('self._key(self._arr[parent]) < itemkey',
                               callEnviron, wait=wait)
            if self.list[parent] < upItem: # if parent less than item sifting up
                self.highlightCode('self._arr[i] = self._arr[parent]',
                                   callEnviron)
                # move a copy of the parent down to node i
                copyVal = tuple(
                    self.copyCanvasItem(j) for j in self.list[parent].items)
                callEnviron |= set(copyVal)
                self.moveItemsOnCurve(
                    copyVal, (self.cellCoords(i), self.cellCenter(i)),
                    startAngle=-90 * 11 / (10 + i - parent),
                    sleepTime=wait / 10)
                for item in self.list[i].items:
                    self.canvas.delete(item)
                self.list[i].val = self.list[parent].val
                self.list[i].items = copyVal
                callEnviron -= set(copyVal)
                
                # Advance i to parent, move original item along with i Index
                self.highlightCode('i = parent', callEnviron)
                delta = self.cellCenter(parent)[1] - self.cellCenter(i)[1]
                self.moveItemsBy(iIndex + copyItem + (itemLabel,), (0, delta),
                                 sleepTime=wait / 10)
                i = parent
            else:
                self.highlightCode('break', callEnviron, wait=wait)
                break

            self.highlightCode('0 < i', callEnviron, wait=wait)
            
        # Move copied item into appropriate location
        self.highlightCode('self._arr[i] = item', callEnviron)
        self.moveItemsBy(copyItem, V(self.siftDelta) * -1,
                         sleepTime=wait / 10)
        for item in self.list[i].items:
            self.canvas.delete(item)
        self.list[i].val, self.list[i].items = upItem.val, copyItem
        callEnviron -= set(copyItem)

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
       
    def siftDown(self, i=0):  # Sift item i down to preserve heap condition
        firstLeaf = len(self.list) // 2 # Get index of first leaf
        if i >= firstLeaf: # If item i is at or below leaf level, 
            return         # it cannot be moved down
        wait = 0.1
        callEnviron = self.createCallEnvironment()
        
        downItem = self.list[i].copy()   # Store item at cell i
        copyItem = tuple(self.copyCanvasItem(i) for i in downItem.items)
        callEnviron |= set(copyItem)
        self.moveItemsBy(copyItem, self.siftDelta, sleepTime=wait / 10)
        
        # arrows
        iIndex = self.createArrayIndex(i, name='i', level=-1)
        maxChildIndex = self.createArrayIndex(
            2 * i + 1, name='maxChild', level=-2)
        callEnviron |= set(iIndex + maxChildIndex)
           
        itemkey = downItem.val # key
        while i < firstLeaf:  # While i above leaf level, find children
            left = (2*i)+1
            right = (2*i)+2
            maxi = left        # Assume left child has larger key
           
            if (right < len(self.list) and # If both children are present, and
                self.list[left].val < # left child has smaller key
                self.list[right].val): 
                maxi = right    # then use right child

            delta = self.cellCenter(maxi)[1] - self.canvas.coords(maxChildIndex[0])[1]  
            if delta != 0:      # Move child index pointer
                self.moveItemsBy(maxChildIndex, (0, delta), sleepTime=wait / 10)
                self.wait(wait)      # Pause for comparison
            
            if (itemkey <      # If item i's key is less
                self.list[maxi].val): # than max child's key,

                # move a copy of the child down to node i
                copyVal = tuple(
                    self.copyCanvasItem(j) for j in self.list[maxi].items)
                callEnviron |= set(copyVal)
                self.moveItemsOnCurve(
                    copyVal, (self.cellCoords(i), self.cellCenter(i)),
                    sleepTime=0.02)
                for item in self.list[i].items:
                    self.canvas.delete(item)
                self.list[i].val = self.list[maxi].val
                self.list[i].items = copyVal
                callEnviron -= set(copyVal)
                
                # Advance i to child, move original item along with i Index
                delta = self.cellCenter(maxi)[1] - self.cellCenter(i)[1]
                self.moveItemsBy(
                    iIndex + copyItem, (0, delta), sleepTime=wait / 10)
                i = maxi
                 
            else:              # If item i's key is greater than or equal
                break          # to larger child, then found position

        # Move copied item into appropriate location
        self.moveItemsBy(copyItem, V(self.siftDelta) * -1,
                         sleepTime=wait / 10)
        for item in self.list[i].items:
            self.canvas.delete(item)
        self.list[i].val, self.list[i].items = downItem.val, copyItem
        callEnviron -= set(copyItem)
        self.cleanUp(callEnviron)        

    def heapify(self, N = None):
        'Organize an array of N items to satisfy the heap condition'
        wait = 0.1
        callEnviron = self.createCallEnvironment()
        if N is None:            # If N is not supplied,
            N = len(self.list)   # then use number of items in list
        heapLo = N // 2          # The heap lies in the range [heapLo, N)
        while heapLo > 0:        # Heapify until the entire array is a heap
            heapLo -= 1           # Decrement heap's lower boundary
            self.siftDown(heapLo) # Sift down item at heapLo

        # Adjust nItems pointer to indicate heap condition is satisfied
        self.nItems = N
        coords = self.arrayIndexCoords(self.nItems)
        self.moveItemsTo(self.nItemsIndex, (coords, coords[:2]),
                         sleepTime=wait / 10)
        self.cleanUp(callEnviron)
              
    # lets user input an int argument that determines max size of the Heap
    def newArray(self):
        #gets rid of old elements in the list
        del self.list[:]
        self.size = 2
        self.display()

    def peek(self):
        wait = 0.1
        callEnviron = self.createCallEnvironment()

        # draw output box
        canvasDimensions = self.widgetDimensions(self.canvas)
        spacing = self.CELL_WIDTH * 3 // 4
        padding = 10
        boxSize = 1
        peekIndex = 0
        outputBox = self.canvas.create_rectangle(
            (self.ARRAY_X0 * 2 + padding),
            canvasDimensions[1] - self.CELL_WIDTH - padding,
            (self.ARRAY_X0 * 2 + boxSize * spacing + padding * 2),
            canvasDimensions[1] - padding,
            fill=self.OPERATIONS_BG)
        callEnviron.add(outputBox)

        outputBoxCoords = self.canvas.coords(outputBox)
        midOutputBox = (outputBoxCoords[3] + outputBoxCoords[1]) // 2
        # create the value to move to output box
        valueOutput = self.copyCanvasItem(self.list[peekIndex].items[1])
        callEnviron.add(valueOutput)

        # move value to output box
        toPosition = (outputBoxCoords[0] + padding / 2 +
                      (peekIndex + 1 / 2) * spacing,
                      midOutputBox)
        self.moveItemsTo(valueOutput, toPosition, sleepTime=wait / 10)
        # make the value 25% smaller
        newFont = (self.VALUE_FONT[0], self.VALUE_FONT[1] * 3 // 4)
        self.canvas.itemconfig(valueOutput, font=newFont)

        # add label to output box
        labelX = self.ARRAY_X0 * 2 + boxSize * spacing + padding * 5
        labelY = canvasDimensions[1] - padding * 2

        boxLabel = self.canvas.create_text(
            labelX, labelY, text="root", font=self.VARIABLE_FONT)
        callEnviron.add(boxLabel)

        # finish animation
        self.cleanUp(callEnviron)

    def removeMax(self):
        wait = 0.1
        callEnviron = self.createCallEnvironment()

        # remove first element from list
        n = self.list[0]

        # Move the first cell to display at the bottom of the screen
        items = n.items
        callEnviron |= set(items)

        # determine the coords of where to move the cell to on the bottom of the screen
        padding = 20
        canvasDimensions = self.widgetDimensions(self.canvas)
        cellCoords = (self.ARRAY_X0 + self.CELL_WIDTH + padding, canvasDimensions[1] - self.CELL_HEIGHT - padding,
                      self.ARRAY_X0 + self.CELL_WIDTH*2 + padding, canvasDimensions[1] - self.CELL_HEIGHT*2 - padding)
        cellCenter = (self.ARRAY_X0 + self.CELL_WIDTH + padding + self.CELL_WIDTH/2,
                      canvasDimensions[1] - self.CELL_HEIGHT - padding- self.CELL_HEIGHT/2)
        toPositions = cellCoords, cellCenter

        self.moveItemsTo(
            items, toPositions, steps=self.CELL_HEIGHT, sleepTime=wait / 10)

        if self.nItems < 1:
            self.setMessage("Heap requirement satisfied")

        # move bottom cell to top, and sift it down
        else:
            self.swapRoot()
            self.siftDown()
        
        # Finish animation
        self.cleanUp(callEnviron)

    def swapRoot(self):
        wait = 0.1
        callEnviron = self.createCallEnvironment()
        last = self.list[-1]
        items = last.items

        # move the last cell to the front of the heap
        cellCoords = self.cellCoords(0)
        cellCenter = self.cellCenter(0)
        toPositions = (cellCoords, cellCenter)
        startAngle = 90 * 50 / (50 + abs(cellCoords[0])) * (
            -1 if cellCoords[0] < 0 else 1)
        self.moveItemsOnCurve(items, toPositions, startAngle=startAngle,
                              sleepTime=wait / 10)
        self.list[0] = last

        self.list.pop()
        self.nItems = len(self.list)
        coords = self.arrayIndexCoords(self.nItems)
        self.moveItemsTo(self.nItemsIndex, (coords, coords[:2]),
                         sleepTime=wait / 10)
        
        # finish the animation
        self.cleanUp(callEnviron)
    
    def randomFill(self, val):
        self.size = max(self.size, val)
        
        self.list = [drawnValue(random.randrange(self.valMax + 1))
                     for i in range(val)]
        self.nItems = 1
        self.display()

    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        return V(
            self.ARRAY_X0, self.ARRAY_Y0, self.ARRAY_X0, self.ARRAY_Y0) + V(
                0, self.CELL_HEIGHT * cell_index,
                self.CELL_WIDTH - self.CELL_BORDER,
                self.CELL_HEIGHT * (cell_index + 1) - self.CELL_BORDER)

    def cellCenter(self, index):  # Center point for array cell at index
        half_cell_x = (self.CELL_WIDTH - self.CELL_BORDER) // 2
        half_cell_y = (self.CELL_HEIGHT - self.CELL_BORDER) // 2
        return V(self.cellCoords(index)) + V(half_cell_x, half_cell_y)

    def arrayCellCoords(self, index):
        cell_coords = self.cellCoords(index)
        half_border = self.CELL_BORDER // 2
        other_half = self.CELL_BORDER - half_border
        return V(cell_coords) + V(
            -half_border, -half_border, other_half, other_half)
        
    def createArrayCell(self, index):  # Create a box representing an array cell
        rect = self.canvas.create_rectangle(
            self.arrayCellCoords(index), fill=None, tags= "arrayCell",
            outline=self.CELL_BORDER_COLOR, width=self.CELL_BORDER)
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
        if isinstance(indexOrCoords, (int, float)):
            rectPos = self.cellCoords(indexOrCoords)
            valPos = self.cellCenter(indexOrCoords)
        else:
            rectPos = indexOrCoords
            valPos = divide_vector(add_vector(rectPos[:2], rectPos[2:]), 2)

        if color is None:
            # Take the next color from the palette
            color = drawnValue.palette[Heap.nextColor]
            Heap.nextColor = (Heap.nextColor + 1) % len(drawnValue.palette)
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
        self.nItemsIndex = self.createArrayIndex(self.nItems)

        # go through each drawnValue in the list
        for i, n in enumerate(self.list):
            # create display objects for the associated drawnValues
            n.items = self.createCellValue(i, n.val)

    def fixPositions(self):  # Move canvas display items to exact cell coords
        for i, dValue in enumerate(self.list):
            self.canvas.coords(dValue.items[0], *self.cellCoords(i))
            self.canvas.coords(dValue.items[1], *self.cellCenter(i))
            
        # Restore array cell borders in case they were moved
        for i, item in enumerate(self.canvas.find_withtag('arrayCell')):
            if i >= self.size: # Delete any extra cell borders
                self.canvas.delete(item)
            else:
                self.canvas.coords(item, *self.arrayCellCoords(i))
            
        # Restore nItems index to one past end of array
        coords = self.arrayIndexCoords(self.nItems)
        self.canvas.coords(self.nItemsIndex[0], coords)
        self.canvas.coords(self.nItemsIndex[1], coords[:2])

    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        if ((len(args) == 0 or args[0] is None) and # When cleaning up entire 
            kwargs.get('callEnviron', None) is None): # call stack,
            self.fixPositions()       # restore positions of all structures

    def makeButtons(self, maxRows=3):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd, argHelpText=['item'],
            helpText='Insert a new item in the heap')
        randomFillButton = self.addOperation(
            "Random Fill ", lambda: self.clickRandomFill(), numArguments=1,
            validationCmd=vcmd, argHelpText=['number of items'],
            helpText='Fill array with N random items')
        newHeapButton = self.addOperation(
            "New", lambda: self.clickNewArray(), maxRows=maxRows,
            helpText='Create empty heap')
        self.peekButton = self.addOperation(
            "Peek", lambda: self.clickPeek(), maxRows=maxRows,
            helpText='Peek at maximum item')
        self.removeMaxButton = self.addOperation(
            "Remove Max", lambda: self.clickRemoveMax(), maxRows=maxRows,
            helpText='Remove maximum item from heap')
        self.heapifyButton = self.addOperation(
            "Heapify", lambda: self.clickHeapify(), maxRows=maxRows,
            helpText='Organize items into heap')
        self.addAnimationButtons(maxRows=maxRows)
        self.enableButtons()
        return [self.insertButton, randomFillButton,
                newHeapButton, self.peekButton, self.removeMaxButton, 
                self.heapifyButton]

    def enableButtons(self, enable=True, **kwargs):
        super().enableButtons(enable, **kwargs)
        self.argumentChanged()
        isHeap = self.nItems >= len(self.list)
        self.widgetState(
            self.insertButton,
            NORMAL if self.widgetState(self.insertButton) == NORMAL 
            and isHeap and len(self.list) < self.MAX_SIZE else DISABLED)
        self.widgetState(
            self.peekButton, NORMAL if enable and self.nItems > 0 else DISABLED)
        self.widgetState(
            self.removeMaxButton, 
            NORMAL if enable and isHeap and self.nItems > 0 else DISABLED)
        self.widgetState(
            self.heapifyButton, 
            NORMAL if enable and self.nItems > 0 else DISABLED)
      
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
                self.insert(val, start=self.startMode())
                self.setMessage("Value {} inserted".format(val))
        self.clearArgument()
        
    def clickPeek(self):
        if len(self.list) <= 0:
            self.setMessage("Error! Heap is empty.")
        else:
            val = self.list[0].val
            self.peek()
            self.setMessage("{} is the root value!".format(val))
            
    def clickNewArray(self):
        self.newArray()

    def clickRemoveMax(self):
        if len(self.list) == 0:
            self.setMessage('Heap is empty!')

        else:
            val = self.list[0].val
            self.removeMax()
            self.setMessage("{} was removed!".format(val))


    def clickRandomFill(self):
        val = self.validArgument()
        if val is None or val < 1 or self.MAX_SIZE < val:
            self.setMessage(
                "Input value must be between 1 to {}.".format(self.MAX_SIZE))
        else:
            self.randomFill(val)

    def clickHeapify(self):
        self.heapify()


if __name__ == '__main__':
    numArgs = [int(arg) for arg in sys.argv[1:] if arg.isdigit()]
    HEAP = Heap()
    try:
        for arg in numArgs:
            HEAP.insert(arg)
            HEAP.cleanUp()
    except UserStop:
        HEAP.cleanUp()
    HEAP.runVisualization()
