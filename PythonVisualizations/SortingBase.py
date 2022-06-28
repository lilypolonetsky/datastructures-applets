import random
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

class SortingBase(VisualizationApp):
    CELL_SIZE = 50
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    ARRAY_X0 = 80
    ARRAY_Y0 = 80
    FOUND_COLOR = 'brown4'
    nextColor = 0
    CELL_WIDTH = CELL_SIZE
    CELL_HEIGHT = CELL_SIZE * 5 // 2
    CELL_MIN_WIDTH = 18
    
    def __init__(self, size=10, maxCells=100, valMax=99, **kwargs):
        super().__init__(**kwargs)
        self.size = size
        self.maxCells = maxCells
        self.valMax = valMax
        self.showValues = True
        self.nItems = None

        self.list = []  # Internal array of drawnValue cell values
        
        self.display()
        
    def __str__(self):
        return str(self.list)
    
    # ANIMATION METHODS
    def assignElement(
            self, fromIndex, toIndex, callEnviron, steps=10, sleepTime=0.01,
            startAngle=0):
        
        fromValue = self.list[fromIndex]
        toValue = (self.list[toIndex] if toIndex < len(self.list) 
                   else drawnValue(0))

        # create new display objects as copies of the "from" cell and value
        copyItems = [self.canvas.copyItem(i) for i in fromValue.items 
                     if i is not None]
        callEnviron |= set(copyItems)

        # get positions of "to" cell in array
        toPositions = (self.fillCoords(fromValue.val, 
                                       self.currentCellCoords(toIndex)),
                       self.currentCellCenter(toIndex))[:len(copyItems)]
                
        # Move copies to the desired location
        if startAngle == 0:                            # move items linearly
            self.moveItemsTo(copyItems, toPositions,
                             steps=steps, sleepTime=sleepTime)
        else:                                          # move items on curve
            self.moveItemsOnCurve(
                copyItems, toPositions, startAngle=startAngle, 
                steps=steps, sleepTime=sleepTime)

        # delete the original "to" display value and the new display shape
        self.dispose(callEnviron, *toValue.items)

        # update value and display value in "to" position in the list
        toValue.val = fromValue.val
        toValue.items = tuple(copyItems)
        callEnviron -= set(copyItems)
        if toIndex == len(self.list):  # If to localtion is a new cell,
            self.list.append(toValue)  # append it

    def tempCoords(self, index):  # Determine coordinates for a temporary var
        cellCoords = self.currentCellCoords(index) # aligned below an array
        canvasDims = widgetDimensions(self.canvas) # cell
        bottom = min(canvasDims[1] - 1,
                     cellCoords[3] + int(self.CELL_HEIGHT * 1.7))
        return V(cellCoords) + V((0, bottom - cellCoords[3]) * 2)

    def tempLabelCoords(self, index, font=None):
        if font is None:
            font = self.VARIABLE_FONT
        tempPos = self.tempCoords(index)
        return (tempPos[0] + tempPos[2]) // 2, tempPos[1] - abs(font[1])
    
    def assignToTemp(self, index, callEnviron, varName="temp", existing=None,
                     sleepTime=0.02, tempCoords=None):
        """Assign indexed cell to a temporary variable named varName.
        Animate value moving to the temporary variable below the array.
        Return a drawnValue for the new temporary value and a text item for
        its name label.  The existing label can be passed to avoid creating
        a new one with an optional set of coordinates for the label position.
        The indexed value (and optionally the temp label) are moved along a
        straight path to their locations
        """
        fromValue = self.list[index]
        posCell = self.canvas.coords(fromValue.items[0])
        cellXCenter = (posCell[0] + posCell[2]) // 2

        copyItems = [self.canvas.copyItem(i) for i in fromValue.items 
                     if i is not None]
        callEnviron |= set(copyItems)
        
        tempPos = self.tempCoords(index)
        if existing:
            tempLabelPos = tempCoords if tempCoords else self.canvas.coords(existing)
            tempLabel = existing
        else:
            tempLabelPos = tempCoords if tempCoords else self.tempLabelCoords(
                index)
            tempLabel = self.canvas.create_text(
                *tempLabelPos, text=varName, font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
            callEnviron.add(tempLabel)

        delta = (tempLabelPos[0] - cellXCenter, tempPos[1] - posCell[1])
        newCoords = [V(self.canvas.coords(i)) + V(delta * 2)
                     for i in copyItems] + [tempLabelPos]
        self.moveItemsTo(copyItems + [tempLabel], newCoords,
                         sleepTime=sleepTime)

        return drawnValue(fromValue.val, *copyItems), tempLabel

    def assignFromTemp(self, index, temp, templabel, delete=True,
                       sleepTime=0.04):
        """Assign a temporary drawnValue to the indexed array cell by
        moving it into position on top of the array cell
        Delete the temporary label if requested.
        """

        toCellCoords = self.fillCoords(temp.val, self.currentCellCoords(index))
        toCellCenter = self.currentCellCenter(index)
        tempCellCoords = self.canvas.coords(temp.items[0])
        deltaX = toCellCoords[0] - tempCellCoords[0]
        startAngle = 45 * 500 / (500 + abs(deltaX)) * (-1 if deltaX < 0 else 1)

        self.moveItemsOnCurve(
            temp.items, (toCellCoords, toCellCenter)[:len(temp.items)],
            sleepTime=sleepTime, startAngle=startAngle)

        if delete:
            if templabel:
                self.canvas.delete(templabel)
        if index == len(self.list):
            self.list.append(temp)
        else:
            for item in self.list[index].items:
                if item is not None:
                    self.canvas.delete(item)
            self.list[index] = temp
        
    def swap(self, a, b, aCellObjects=[], bCellObjects=[]):
        '''Swap items at indices a & b of the array bundled with any extra 
        canvas items
        '''
        A, B = self.list[a], self.list[b]
        itemsA = A.items + tuple(aCellObjects)
        itemsB = B.items + tuple(bCellObjects)
        coordsA = self.fillCoords(B.val, self.cellCoords(a))
        coordsB = self.fillCoords(A.val, self.cellCoords(b))
        if a == b:  # Swapping with self - just move up & down
            delta = (0, (coordsA[3] - coordsA[1]) * 3 // 4)
            self.moveItemsBy(itemsA, delta, sleepTime=0.02)
            self.moveItemsBy(itemsA, V(delta) * -1, sleepTime=0.02)
            return
    
        # make a and b cells plus their associated items switch places
        self.moveItemsOnCurve(
            [i for i in itemsA + itemsB if i is not None], 
            [coordsA if i == A.items[0] else
             coordsB if i == B.items[0] else self.canvas.coords(i)
             for i in itemsB + itemsA if i is not None],
            sleepTime=0.05, startAngle=90 * 11 / (10 + abs(a - b)))
    
        # perform the actual cell swap operation in the list
        self.list[a], self.list[b] = self.list[b], self.list[a]   

    def indexCoords(self, index, level=1):
        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        level_space = abs(self.VARIABLE_FONT[1])
        space = self.CELL_SIZE * 1 // 10
        x = cell_center[0]
        if level > 0:
            y0 = cell_coords[1] - space - level * level_space
            y1 = cell_coords[1] - space
        else:
            y0 = cell_coords[3] + space - level * level_space
            y1 = cell_coords[3] + space
        return x, y0, x, y1
        
    def createIndex(  # Create an index arrow to point at an indexed
            self, index,  # cell
            name=None,  # with an optional name label
            level=1,  # at a particular level away from the cells
            color=None):  # (negative are below)
        if not color: color = self.VARIABLE_COLOR

        x0, y0, x1, y1 = self.indexCoords(index, level)
        arrow = self.canvas.create_line(x0, y0, x0, y1, arrow=LAST, fill=color)
        if name:
            label = self.canvas.create_text(
                x0, y0, text=name, anchor=SW if level > 0 else NW,
                font=self.VARIABLE_FONT, fill=color)
        return (arrow, label) if name else (arrow,)  

    def computeCellWidth(self, nCells=None):
        if nCells is None:
            nCells = self.size
        canvasDims = widgetDimensions(self.canvas)
        return max(self.CELL_MIN_WIDTH,
                   min(self.CELL_SIZE,
                       (canvasDims[0] - self.ARRAY_X0) // (nCells + 1)))
    
    def canShowValues(self, width=None):
        if width is None:
            width = self.CELL_WIDTH
        return (self.CELL_BORDER +
                textWidth(self.VALUE_FONT, str(self.valMax))) < width

    # ARRAY FUNCTIONALITY
    newCode = '''
def __init__(self, initialSize={val}):
   self.__a = [None] * initialSize
   self.__nItems = 0
'''
    
    def new(self, val, code=newCode, start=True):
        canvasDims = widgetDimensions(self.canvas)
        maxCells = min(
            self.maxCells, 
            (canvasDims[0] - self.ARRAY_X0) // self.CELL_MIN_WIDTH - 1)
        if val > maxCells:
            self.setMessage('Too many cells; must be {} or less'.format(
                maxCells))
            return
        elif val < 1:
            self.setMessage('Too few cells; must be 1 or more')
            return

        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        self.canvas.delete('all')
        
        self.size = val
        self.highlightCode('self.__a = [None] * initialSize', callEnviron, 
                           wait=0.1)
        self.list = []
        self.CELL_WIDTH = self.computeCellWidth()
        self.showValues = self.canShowValues()

        self.display(showNItems=False)
        self.wait(0.1)

        self.highlightCode('self.__nItems = 0', callEnviron, wait=0.1)
        self.display()
        self.wait(0.1)

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        return True

    insertCode = """
def insert(self, item={val}):
   self.__a[self.__nItems] = item
   self.__nItems += 1
"""

    def insert(self, val, allowGrowth=False, code=insertCode, start=True):
        canvasDims = widgetDimensions(self.canvas)
        # Check if inserted cell will be off of the canvas
        offCanvas = canvasDims[0] <= self.cellCoords(len(self.list))[2]

        if (len(self.list) >= self.size and not allowGrowth or
            len(self.list) >= self.maxCells or
            self.CELL_WIDTH == self.CELL_MIN_WIDTH and offCanvas):
            self.setMessage('Array is full')
            return False
        
        # Inserting when there is no room on the canvas
        redraw = offCanvas
        if offCanvas:
            self.CELL_WIDTH = self.computeCellWidth(len(self.list) + 1)
            self.showValues = self.canShowValues()
        if self.size < len(self.list) + 1:
            self.size = len(self.list) + 1
            redraw = True
        if redraw:
            self.display()
        
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)

        self.highlightCode('self.__a[self.__nItems] = item', callEnviron)

        # create new cell and cell value display objects
        toPositions = (self.fillCoords(val, self.cellCoords(len(self.list))),
                       self.cellCenter(len(self.list)))

        # Animate arrival of new value from operations panel area
        startPosition = self.newValueCoords()
        cellPair = self.createCellValue(startPosition, val)

        if len(cellPair) == 1 or cellPair[1] is None:
            cellPair, toPositions = cellPair[:1], toPositions[:1]
        callEnviron |= set(cellPair)
        self.moveItemsTo(cellPair, toPositions, sleepTime=0.01)

        # add a new drawnValue with the new value, and display objects
        self.list.append(drawnValue(val, *cellPair))
        callEnviron ^= set(cellPair) # Remove new cell from temp call environ

        # advance nItems index
        self.highlightCode('self.__nItems += 1', callEnviron)
        self.moveItemsBy(self.nItems, (self.CELL_WIDTH, 0), sleepTime=0.01)

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        return True
       
    def randomFill(self):
        callEnviron = self.createCallEnvironment()        

        toFill = self.size - len(self.list)
        if toFill > 0:
            self.list.extend([
                drawnValue(random.randrange(self.valMax)) 
                for i in range(toFill)])
        else:
            self.setMessage('Array is already full')
        
        self.display(showNItems=self.nItems)
        self.cleanUp(callEnviron)
    
    def linearFill(self, increasing=True):
        callEnviron = self.createCallEnvironment()        

        toFill = self.size - len(self.list)
        if toFill > 0:
            self.list.extend([
                drawnValue(
                    int((i if increasing else max(1, toFill - 1) - i) *
                        self.valMax / max(1, toFill - 1)))
                for i in range(toFill)])
        else:
            self.setMessage('Array is already full')
        self.display(showNItems=self.nItems)
        self.cleanUp(callEnviron)
        
    getCode = """
def get(self, n={n}):
   if 0 <= n and n < self.__nItems:
      return self.__a[n]
"""

    def get(self, n, code=getCode):
        wait=0.1
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))
        self.highlightCode('0 <= n', callEnviron, wait=wait)
        result = None
        if 0 <= n:
            self.highlightCode('n < self.__nItems', callEnviron, wait=wait)
            if n < len(self.list):
                self.highlightCode('return self.__a[n]', callEnviron, wait=wait)
                result = self.list[n]
            else:
                self.highlightCode([], callEnviron)
        else:
            self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        return result
    
    searchCode = """
def search(self, item={item}):
   return self.get(self.find(item))
"""

    def search(self, item, code=searchCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        self.highlightCode('self.find(item)', callEnviron)
        n = self.find(item)
        callEnviron |= set(self.createIndex(n, '', level=2))
        if n > -1:
            callEnviron.add(self.createFoundCircle(n))
        self.highlightCode('self.get(self.find(item))', callEnviron)
        result = self.get(n)
        self.highlightCode('return self.get(self.find(item))', callEnviron)
        self.wait(0.2)
        self.cleanUp(callEnviron)
        return result

    findCode = """
def find(self, item={val}):
   for j in range(self.nItems):
      if self.__a[j] == item:
         return j
   return -1
"""

    def find(self, val, code=findCode):
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))
       
        # draw an index for variable j pointing to the first cell
        indexDisplay = self.createIndex(0, 'j')
        callEnviron |= set(indexDisplay)

        # show that we are starting the loop
        self.highlightCode('j in range(self.nItems)', callEnviron)

        # go through each drawnValue in the list
        for j, n in enumerate(self.list):
            # Test if the value is found
            self.highlightCode('self.__a[j] == item', callEnviron, wait=0.1)
            if n.val == val:
                self.highlightCode('return j', callEnviron)

                # Highlight the found element with a circle
                callEnviron.add(self.createFoundCircle(j))

                # update the display and pause to show circle
                self.wait(0.1)

                # Animation stops
                self.highlightCode([], callEnviron)
                self.cleanUp(callEnviron)
                return j

            # if not found, then move the index over one cell
            self.highlightCode('j in range(self.nItems)', callEnviron)
            self.moveItemsBy(indexDisplay, (self.CELL_WIDTH, 0), sleepTime=0.01)
            self.wait(0.1)

        # key not found
        self.highlightCode('return -1', callEnviron)
        self.wait(0.1)

        # Animation stops
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        return -1
    
    deleteCode = """
def delete(self, item={val}):
   for j in range(self.__nItems):
      if self.__a[j] == item:
         self.__nItems -= 1
         for k in range(j, self.__nItems):
            self.__a[k] = self.__a[k+1]
         return True
   return False
"""
        
    def delete(self, val, code=deleteCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)

        # draw an index for variable j pointing to the first cell
        Jindex = self.createIndex(0, 'j', level=2)
        callEnviron |= set(Jindex)

        # show that we are starting the loop
        self.highlightCode('j in range(self.__nItems)', callEnviron, wait=0.1)
        
        # go through each drawnValue in the list
        # look for val to be deleted
        for j, n in enumerate(self.list):

            # Test if the value is found
            self.highlightCode('self.__a[j] == item', callEnviron, wait=0.1)
            if n.val == val:

                # Highlight the found element with a circle
                foundCircle = self.createFoundCircle(j)
                callEnviron.add(foundCircle)

                # Pause to show circle
                self.wait(0.3)

                # decrement nItems
                self.highlightCode('self.__nItems -= 1', callEnviron)

                # Move nItems pointer
                self.moveItemsBy(
                    self.nItems, (-self.CELL_WIDTH, 0), sleepTime=0.01)

                # Slide value rectangle with found circle up and off screen
                self.moveItemsOffCanvas(
                    n.items + (foundCircle,), N, sleepTime=0.02)

                self.highlightCode('k in range(j, self.__nItems)', 
                                   callEnviron, wait=0.1)

                # Create an index for shifting the cells
                kIndex = self.createIndex(j, 'k')
                callEnviron |= set(kIndex)
                    
                # Slide values from right to left to fill gap
                for k in range(j, len(self.list) -1):
                    self.highlightCode('self.__a[k] = self.__a[k+1]',
                                       callEnviron)
                    self.assignElement(k + 1, k, callEnviron)
                    self.moveItemsBy(
                        kIndex, (self.CELL_WIDTH, 0), sleepTime=0.01)

                    self.highlightCode('k in range(j, self.__nItems)', 
                                       callEnviron, wait=0.1)
                
                # remove the last item in the list
                n = self.list.pop()
                # delete the associated display objects
                for item in n.items:
                    if item is not None:
                        self.canvas.delete(item)
                
                # update window
                self.highlightCode('return True', callEnviron)
                self.wait(0.3)

                self.highlightCode([], callEnviron)
                self.cleanUp(callEnviron)
                return True

            # if not found, then move the index over one cell
            self.highlightCode('j in range(self.__nItems)', callEnviron)
            self.moveItemsBy(
                Jindex, (self.CELL_WIDTH, 0), sleepTime=0.01)
        
        # key not found
        self.highlightCode('return False', callEnviron, wait=0.3)

        # Animation stops
        self.cleanUp(callEnviron)
        return None

    deleteLastCode = '''
def deleteLast(self):
   self.__nItems -= 1
   self.__a[self.__nItems] = None
'''

    def deleteLast(self, code=deleteLastCode, start=True):
        if len(self.list) == 0:
            self.setMessage('Array is empty!')
            return
    
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)
        
        #move nItems pointer
        self.highlightCode('self.__nItems -= 1', callEnviron)
        self.moveItemsBy(self.nItems, (-self.CELL_WIDTH, 0), sleepTime=0.01)

        # pop an Element from the list
        n = self.list.pop()
        callEnviron |= set(n.items)
    
        # Slide value rectangle up and off screen
        self.highlightCode('self.__a[self.__nItems] = None', callEnviron)
        self.moveItemsOffCanvas(n.items, N, sleepTime=0.02)

        # Finish animation
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        
    traverseCode = """
def traverse(self, function=print):
   for j in range(self.nItems):
      function(self.__a[j])
"""

    def traverse(self, code=traverseCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        
        # draw an index pointing to the first cell
        indexDisplay = self.createIndex(0, 'j')
        callEnviron |= set(indexDisplay)

        # draw output box
        canvasDimensions = widgetDimensions(self.canvas)
        outputFont = (self.VALUE_FONT[0], int(self.VALUE_FONT[1] * .75))
        spacing = self.outputBoxSpacing(outputFont)
        padding = 10
        outputBoxCoords = self.outputBoxCoords(outputFont, padding=padding)
        midOutputBox = (outputBoxCoords[3] + outputBoxCoords[1]) // 2
        outputBox = self.canvas.create_rectangle(
            *outputBoxCoords, fill=self.OPERATIONS_BG)
        callEnviron.add(outputBox)

        self.highlightCode('j in range(self.nItems)', callEnviron)
        self.wait(0.3)
        for j, n in enumerate(self.list):
            # create the value to move to output box
            valueOutput = (
                self.canvas.copyItem(n.items[1]) 
                if len(n.items) > 1 and n.items[1] else
                self.canvas.create_text(
                    *self.cellCenter(j), text=n.val, font=outputFont))
            callEnviron.add(valueOutput)

            # move value to output box
            self.highlightCode('function(self.__a[j])', callEnviron)
            toPositions = (outputBoxCoords[0] + padding/2 + (j + 1/2)*spacing, 
                           midOutputBox)
            self.moveItemsTo((valueOutput,), (toPositions,), sleepTime=.02)

            # Make sure the final value is in the output font
            self.canvas.itemconfig(valueOutput, font=outputFont)

            # move the index pointer over
            self.highlightCode('j in range(self.nItems)', callEnviron)
            self.moveItemsBy(indexDisplay, (self.CELL_WIDTH, 0), sleepTime=0.03)

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    def outputBoxSpacing(self, outputFont):
        return textWidth(outputFont, str(self.valMax) + '  ')
    
    def outputBoxCoords(self, outputFont, padding=10, N=None):
        '''Coordinates for an output box in lower right of canvas with enough
        space to hold n values, defaulting to current array length'''
        if N is None:
            N = len(self.list)
        spacing = self.outputBoxSpacing(outputFont)
        canvasDims = widgetDimensions(self.canvas)
        left = max(0, canvasDims[0] - N * spacing - padding) // 2
        return (left, canvasDims[1] - abs(outputFont[1]) * 3 - padding,
                left + N * spacing + padding, canvasDims[1] - padding)
       
    def isSorted(self):
        return all(self.list[i-1] <= self.list[i] 
                   for i in range(1, len(self.list)))
        
    def cellCoords(self, index): # Get bounding rectangle for indexed array cell
        return (self.ARRAY_X0 + self.CELL_WIDTH * index, self.ARRAY_Y0,
                self.ARRAY_X0 + self.CELL_WIDTH * (index + 1) - self.CELL_BORDER,
                self.ARRAY_Y0 + self.CELL_HEIGHT - self.CELL_BORDER)    
    
    def cellCenter(self, cell_index):  # Center point for array cell at index
        x1, y1, x2, y2 = self.cellCoords(cell_index)
        return (x1 + x2) // 2, (y1 + y2) // 2

    def newValueCoords(self):
        cell0 = self.cellCoords(0)   # Shift cell 0 coords off canvans
        canvasDims = widgetDimensions(self.canvas)
        upperOpsDims = widgetDimensions(self.operationsUpper)
        lowerOpsDims = widgetDimensions(self.operationsLower)
        return V(cell0) + V(
            (max(upperOpsDims[0], lowerOpsDims[0]) // 2 - cell0[0],
             canvasDims[1] - cell0[1]) * 2)

    def cellTag(self, index): # Tag name for a particular cell in an array
        return "cell-{}".format(index)

    def arrayCellDelta(self):
        half_border = self.CELL_BORDER // 2
        return (-half_border, -half_border,
                self.CELL_BORDER - half_border, self.CELL_BORDER - half_border)
    
    def arrayCellCoords(self, index):
        cell_coords = self.cellCoords(index)
        return V(cell_coords) + V(self.arrayCellDelta())

    def currentCellCoords(self, index):
        '''Compute coords from current array cell position.  For indices
        beyond ends of array, use the closest array cell and adjust by the
        cell width horizontally.
        '''
        closest = max(0, min(len(self.arrayCells) - 1, index))
        return V(V(self.canvas.coords(self.arrayCells[closest])) +
                 V(((index - closest) * self.CELL_WIDTH, 0) * 2)) - V(
                     self.arrayCellDelta())

    def currentCellCenter(self, index):
        x1, y1, x2, y2 = self.currentCellCoords(index)
        return (x1 + x2) // 2, (y1 + y2) // 2
    
    def createArrayCell(     # Create a box representing an array cell
            self, index, tags=["arrayBox"], color=None, width=None):
        if color is None: color = self.CELL_BORDER_COLOR
        if width is None: width = self.CELL_BORDER
        rect = self.canvas.create_rectangle(
            *self.arrayCellCoords(index), fill=None, outline=color,
            width=width, tags=tags + [self.cellTag(index)])
        self.canvas.lower(rect)
        return rect        
    
    def createCellValue(self, indexOrCoords, key, color=None):
        """Create new canvas items to represent a cell value.  A rectangle is
        created filled with a particular color behind an optional text key.
        The position of the cell can either be an integer index in the Array or
        the bounding box coordinates of the rectangle.  If color is not
        supplied, the next color in the palette is used.  An event handler is
        set up to update the VisualizationApp argument with the cell's value
        if clicked with any button.  Returns a tuple, (rectangle, text), of
        canvas items, which may be 1-tuple if self.showValues is False.
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
            color = drawnValue.palette[SortingBase.nextColor]
            SortingBase.nextColor = (SortingBase.nextColor + 1) % len(
                drawnValue.palette)
      
        newCoords = self.fillCoords(key, rectPos)
    
        cell = (self.canvas.create_rectangle(
            *newCoords, fill=color, outline='', width=0),)
        if self.showValues:
            cell += (self.canvas.create_text(
                *valPos, text=str(key), font=self.VALUE_FONT,
                fill=self.VALUE_COLOR, tags="cellVal"), )
        handler = lambda e: self.setArgument(str(key))
        for item in cell:
            self.canvas.tag_bind(item, '<Button>', handler)

        return cell
    
    # get the whole box coords and return how much will get filled 
    def fillCoords(self, val, rectPos, valMin=0, valMax=None):
        if valMax is None:
            valMax = self.valMax
        x1, y1, x2, y2 = rectPos 
        midY = (y1 + y2) // 2
        # proportion of what is filled
        prop = (val - valMin) / (valMax - valMin)
        y2 = round(midY + prop * (y2-midY))
        
        return (x1, y1, x2, y2)
    
    def createFoundCircle(self, index):
        return self.canvas.create_oval(
            *(V(self.cellCoords(index)) + V(V(1, 1, -1, -1) * self.CELL_BORDER)),
            outline=self.FOUND_COLOR)
    
    def redrawArrayCells(self, tag="arrayBox"):
        self.canvas.delete(tag)
        self.arrayCells = [self.createArrayCell(i) for i in range(self.size)]
    
    def display(self, showNItems=True):
        # Save any current drawn value colors
        colors = [dValue.color(self.canvas) for dValue in self.list]
        self.canvas.delete("all")
    
        self.arrayCells = [self.createArrayCell(i) for i in range(self.size)]
    
        # go through each drawnValue in the list
        for i, n in enumerate(self.list):
            # re-create display objects
            n.items = self.createCellValue(i, n.val, color=colors[i])

        # draw an index pointing to the last item in the list
        self.nItems = self.createIndex(
            len(self.list), 'nItems', level = -1, color = 'black'
        ) if showNItems else None
    
        self.window.update()

    def toTarget(         # Return the 2-D vector between the indexed item's
            self, index): # current position and its normal position in array
        return V(self.cellCoords(index)) - V(
            self.canvas.coords(self.list[index].items[0])[:2])
    
    def shuffle(self, steps=20):
        callEnviron = self.createCallEnvironment()

        nItems = len(self.list)    
        random.shuffle(self.list)  # Randomly move items internally in array

        coords0 = self.cellCoords(0) # Get the height of a cell
        canvasDims = widgetDimensions(self.canvas)
        height = int(coords0[3] - coords0[1])
        vSpace = canvasDims[1] - coords0[3]
        
        velocity = [ # Initial velocity is mostly down and towards destination
            (random.randint(int(dx / 3) - 1, 1) if dx < 0 else
             random.randint(-1, int(dx / 3) + 1),
             random.randint(int(height * 1 / 5), (height + vSpace) // 3))
            for dx, dy in [self.toTarget(i) for i in range(nItems)]]
        
        for step in range(steps):
            stepsToGo = steps - step
            jitter = max(1, int(stepsToGo * 2 / 3))
            half = max(1, jitter // 2)
            for i in range(nItems):
                for item in self.list[i].items: # Get drawnValue items
                    if item is not None: # If not None, move it by velocity
                        self.canvas.move(item, *velocity[i])
                velocity[i] = V(  # Change velocity to move towards
                    V(V(velocity[i]) * 0.8) + # target location and add
                    V(V(self.toTarget(i)) / stepsToGo)) + V(
                        (random.randint(-jitter, jitter), # some random jitter
                         random.randint(-half, half)))
            self.wait(0.05)

        # Ensure all items get to new positions
        self.fixCells()

        # Animation stops
        self.cleanUp(callEnviron)
    
    def fixCells(self):  # Move canvas display items to exact cell coords
        for index, ac in enumerate(self.arrayCells):
            self.canvas.coords(ac, self.arrayCellCoords(index))
        for i, dValue in enumerate(self.list):
            for item, coords in zip(dValue.items,
                                    (self.fillCoords(dValue.val,
                                                     self.cellCoords(i)),
                                     self.cellCenter(i))):
                if item is not None:
                    self.canvas.coords(item, *coords)
        if self.nItems:
            indexCoords = self.indexCoords(len(self.list), level=-1)
            for item in self.nItems:
                if item is not None:
                    nCoords = len(self.canvas.coords(item))
                    self.canvas.coords(item, *indexCoords[:nCoords]) 
        
    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        if len(self.callStack) == 0: # When call stack is empty
            self.fixCells()
        
    def makeButtons(self, maxRows=4):
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
            "Traverse", 
            lambda: self.traverse(start=self.startMode()), maxRows=maxRows,
            helpText='Traverse all array cells once')
        randomFillButton = self.addOperation(
            "Random Fill", lambda: self.randomFill(), maxRows=maxRows,
            helpText='Fill empty array cells with random keys')
        increasingFillButton = self.addOperation(
            "Increasing Fill", lambda: self.linearFill(), maxRows=maxRows,
            helpText='Fill empty array cells with increasing keys')
        decreasingFillButton = self.addOperation(
            "Decreasing Fill", lambda: self.linearFill(False), maxRows=maxRows,
            helpText='Fill empty array cells with decreasing keys')
        deleteRightmostButton = self.addOperation(
            "Delete Rightmost", 
            lambda: self.deleteLast(start=self.startMode()), maxRows=maxRows,
            helpText='Delete last array item')
        shuffleButton = self.addOperation(
            "Shuffle", lambda: self.shuffle(), maxRows=maxRows,
            helpText='Shuffle position of all items')
        buttons = [btn for btn in self.opButtons]
        return buttons, vcmd  # Buttons managed by play/pause/stop controls    
    
    def validArgument(self, valMax=None):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if valMax is None:
                valMax = self.valMax
            if val <= valMax:
                return val
    
    # Button functions
    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage(
                "Input value must be an integer from 0 to {}".format(
                    self.valMax))
            self.setArgumentHighlight(color=self.ERROR_HIGHLIGHT)
        elif self.insert(val, allowGrowth=True, start=self.startMode()):
            self.setMessage("Value {} inserted".format(val))
            self.clearArgument()
     
    def clickSearch(self):
        val = self.validArgument()
        if val is None:
            self.setMessage(
                "Input value must be an integer from 0 to {}".format(
                    self.valMax))
            self.setArgumentHighlight(color=self.ERROR_HIGHLIGHT)
        else:
            found = self.search(val, start=self.startMode())
            self.setMessage(
                "Value {} {}found".format(val, "" if found else "not "))
            self.clearArgument() 
     
    def clickDelete(self):
        val = self.validArgument()
        if val is None:
            self.setMessage(
                "Input value must be an integer from 0 to {}".format(
                    self.valMax))
            self.setArgumentHighlight(color=self.ERROR_HIGHLIGHT)
        else:
            result = self.delete(val, start=self.startMode())
            msg = "Value {} {}".format(
                val, "deleted" if result else "not found")
            self.setMessage(msg)
        self.clearArgument()

    def clickNew(self):
        val = self.validArgument(valMax=1000)
        if val is None:
            self.setMessage('Invalid array size')
            self.clearArgument()
            return
        # If new succeeds, clear the argument
        if self.new(val, start=self.startMode()):
            self.clearArgument()
