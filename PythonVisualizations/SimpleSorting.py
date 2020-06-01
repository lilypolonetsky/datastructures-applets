import random
import time
from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

CELL_SIZE = 50
CELL_BORDER = 2
CELL_BORDER_COLOR = 'black'
ARRAY_X0 = 100
ARRAY_Y0 = 100
FONT_SIZE = 20
VALUE_FONT = ('Helvetica', FONT_SIZE)
VALUE_COLOR = 'black'
FOUND_COLOR = 'brown4'

class SimpleArraySort(VisualizationApp):
    nextColor = 0

    def __init__(self, size=10, title="Simple Sorting", **kwargs):
        super().__init__(title=title, **kwargs)
        self.size = size
        self.title = title
        self.list = []           # Internal array of drawable cell values

        self.buttons = self.makeButtons()
        for i in range(size):
            self.list.append(drawable(random.randrange(30)))
        self.display()
        
    def __str__(self):
        return str(self.list)

    # ANIMATION METHODS
    def assignElement(self, fromIndex, toIndex, steps=10, sleepTime=0.01):
        fromItem = self.list[fromIndex]
        toItem = self.list[toIndex]
        
        # get positions of "to" cell in array
        toPositions = (self.cellCoords(toIndex), self.cellCenter(toIndex))

        # create new display objects as copies of the "from" cell and value
        newCell = self.copyCanvasItem(fromItem.display_shape)
        newCellVal = self.copyCanvasItem(fromItem.display_val)

        # Move copies to the desired location
        self.moveItemsTo((newCell, newCellVal), toPositions, steps=steps,
                         sleepTime=sleepTime)
        
        # delete the original "to" display value and the new display shape
        self.canvas.delete(self.list[toIndex].display_val)
        self.canvas.delete(self.list[toIndex].display_shape)

        # update value and display value in "to" position in the list
        self.list[toIndex].display_val = newCellVal
        self.list[toIndex].val = self.list[fromIndex].val
        self.list[toIndex].display_shape = newCell
        self.list[toIndex].color = self.list[fromIndex].color

        # update the window
        self.window.update()

    def assignToTemp(self, index, varName="temp", existing=None):
        """Assign indexed cell to a temporary variable named varName.
        Animate value moving to the temporary variable above the array.
        Return a drawable for the new temporary value and a text item for
        its name.  The existing name item can be passed to avoid creating
        a new one and for moving the value to that location
        """
        fromDraw = self.list[index]
        fromCell = fromDraw.display_shape
        fromCellVal = fromDraw.display_val
        posCell = self.canvas.coords(fromCell)
        posCellVal = self.canvas.coords(fromCellVal)

        shape = self.copyCanvasItem(fromCell)
        val = self.copyCanvasItem(fromCellVal)
        if existing:
            tempPos = self.canvas.coords(existing)
            templabel = existing
        else:
            posLabel = subtract_vector(posCellVal, (0, CELL_SIZE * 2))
            templabel = self.canvas.create_text(
                *posLabel, text=varName, font=VARIABLE_FONT, 
                fill=VARIABLE_COLOR)

        delta = (tempPos[0] - posCellVal[0] if existing else 0, 
                 - CELL_SIZE * 4 // 3)
        self.moveItemsBy((shape, val), delta, sleepTime=0.02)

        return drawable(fromDraw.val, fromDraw.color, shape, val), templabel

    def assignFromTemp(self, index, temp, templabel):

        toCellCoords = self.cellCoords(index)
        toCellCenter = self.cellCenter(index)
        tempCellCoords = self.canvas.coords(temp.display_shape)
        deltaX = toCellCoords[0] - tempCellCoords[0]
        startAngle = 90 * 500 / (500 + abs(deltaX)) * (-1 if deltaX < 0 else 1)
                           
        self.moveItemsOnCurve(
            (temp.display_shape, temp.display_val),
            (toCellCoords, toCellCenter), sleepTime=0.04, startAngle=startAngle)
        
        if templabel:
            self.canvas.delete(templabel)
        self.canvas.delete(self.list[index].display_shape)
        self.canvas.delete(self.list[index].display_val)
        self.list[index] = temp

    def swap(self, a, b, aCellObjects = [], bCellObjects = []):
        itemsA = [self.list[a].display_shape, 
                  self.list[a].display_val] + aCellObjects
        itemsB = [self.list[b].display_shape, 
                  self.list[b].display_val] + bCellObjects
        upDelta = (0, - CELL_SIZE * 4 // 3)
        downDelta = multiply_vector(upDelta, -1)
        if a == b:         # Swapping with self - just move up & down
            self.moveItemsBy(itemsA, upDelta, sleepTime=0.02)
            self.moveItemsBy(itemsA, downDelta, sleepTime=0.02)
            return

        # make a and b cells plus their associated items switch places
        self.moveItemsOnCurve(
            itemsA + itemsB, [self.canvas.coords(i) for i in itemsB + itemsA],
            sleepTime=0.05, startAngle=90 * 11/(10 + abs(a - b)))

        # perform the actual cell swap operation in the list
        self.list[a], self.list[b] = self.list[b], self.list[a]

    def createIndex(         # Create an index arrow to point at an indexed
            self, index,     # cell
            name=None,       # with an optional name label
            level=1,         # at a particular level away from the cells
            color=VARIABLE_COLOR): # (negative are below)
        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        level_spacing = VARIABLE_FONT[1] 
        x = cell_center[0]
        if level > 0:
            y0 = cell_coords[1] - CELL_SIZE * 3 // 5 - level * level_spacing
            y1 = cell_coords[1] - CELL_SIZE * 3 // 10
        else:
            y0 = cell_coords[3] + CELL_SIZE * 3 // 5 - level * level_spacing
            y1 = cell_coords[3] + CELL_SIZE * 3 // 10
        arrow = self.canvas.create_line(
            x, y0, x, y1, arrow="last", fill=color)
        if name:
            label = self.canvas.create_text(
                x + 2, y0, text=name, anchor=SW if level > 0 else NW,
                font=VARIABLE_FONT, fill=color)
        return (arrow, label) if name else (arrow, )

    insertCode = """
def insert(self, item):
   self.__a[self.__nItems] = item
   self.__nItems += 1
"""
    insertCodeSnippets = {
        'item_assignment': ('2.3', '2.end'),
        'nitem_increment': ('3.3', '3.end'),
    }
    
    def insert(self, val):
        self.startAnimations()
        self.cleanUp()
        self.showCode(self.insertCode.strip())
        self.createCodeTags(self.insertCodeSnippets)
        
        # If array needs to grow, add cells:
        while self.size < len(self.list) + 1:
            self.size += 1
            self.createArrayCell(len(self.list))

        # draw an index pointing to the last cell
        self.highlightCodeTags('item_assignment')
        indexDisplay = self.createIndex(len(self.list), 'nItems')
        self.cleanup |= set(indexDisplay)

        # create new cell and cell value display objects
        toPositions = (self.cellCoords(len(self.list)), 
                       self.cellCenter(len(self.list)))

        # Animate arrival of new value from operations panel area
        canvasDimensions = self.widgetDimensions(self.canvas)
        startPosition = add_vector(
            [canvasDimensions[0] // 2 - CELL_SIZE, canvasDimensions[1]] * 2,
            (0, 0) + (CELL_SIZE - CELL_BORDER,) * 2)
        cellPair = self.createCellValue(startPosition, val)
        self.moveItemsTo(cellPair, toPositions, steps=CELL_SIZE, sleepTime=0.01)

        # add a new Drawable with the new value, color, and display objects
        self.list.append(drawable(
            val, self.canvas.itemconfigure(cellPair[0], 'fill'), *cellPair))

        # advance index for next insert
        self.highlightCodeTags('nitem_increment')
        self.moveItemsBy(indexDisplay, (CELL_SIZE, 0), sleepTime=0.01)

        self.highlightCodeTags([])
        self.stopAnimations()

    def removeFromEnd(self):
        self.cleanUp()
        
        # pop an Element from the list
        if len(self.list) == 0:
            self.setMessage('Array is empty!')
            return
        n = self.list.pop()

        # delete the associated display objects
        self.canvas.delete(n.display_shape)
        self.canvas.delete(n.display_val)

        # update window
        self.window.update()

    def cellCoords(self, cell_index): # Get bounding rectangle for array cell
        return (ARRAY_X0 + CELL_SIZE * cell_index, ARRAY_Y0, # at index
                ARRAY_X0 + CELL_SIZE * (cell_index + 1) - CELL_BORDER,
                ARRAY_Y0 + CELL_SIZE - CELL_BORDER)

    def cellCenter(self, cell_index): # Center point for array cell at index
        half_cell = (CELL_SIZE - CELL_BORDER) // 2
        return add_vector(self.cellCoords(cell_index), (half_cell, half_cell))

    def createArrayCell(self, index): # Create a box representing an array cell
        cell_coords = self.cellCoords(index)
        half_border = CELL_BORDER // 2
        rect = self.canvas.create_rectangle(
            *add_vector(cell_coords, 
                        (-half_border, -half_border,
                         CELL_BORDER - half_border, CELL_BORDER - half_border)),
            fill=None, outline=CELL_BORDER_COLOR, width=CELL_BORDER)
        self.canvas.lower(rect)
        return rect

    def createCellValue(self, indexOrCoords, key, color=None):
        """Create new canvas items to represent a cell value.  A square
        is created filled with a particular color with a text key centered
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
            color = drawable.palette[SimpleArraySort.nextColor]
            SimpleArraySort.nextColor = (SimpleArraySort.nextColor + 1) % len(drawable.palette)

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

        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)
        
        # go through each Drawable in the list
        for i, n in enumerate(self.list):
            # create display objects for the associated Drawables
            n.display_shape, n.display_val = self.createCellValue(
                i, n.val, n.color)
            n.color = self.canvas.itemconfigure(n.display_shape, 'fill')

        self.window.update()

    findCode = """
def find(self, item):
   for j in range(self.__nItems):
      if self.__a[j] == item:
         return j
   return -1
"""
    findCodeSnippets = {
        'outer_loop_increment': ('2.7', '2.32'),
        'key_comparison': ('3.9', '3.28'),
        'key_found': ('4.9', '4.end'),
        'key_not_found': ('5.3', '5.end'),
    }
    
    def find(self, val):
        self.startAnimations()
        self.cleanUp()
        self.showCode(self.findCode.strip())
        self.createCodeTags(self.findCodeSnippets)

        # draw an index for variable j pointing to the first cell
        indexDisplay = self.createIndex(0, 'j')
        self.cleanup |= set(indexDisplay)

        # go through each Drawable in the list
        for i in range(len(self.list)):
            n = self.list[i]

            # if the value is found
            self.highlightCodeTags('key_comparison')
            self.window.update()
            if self.wait(0.1):
                break
            if n.val == val:
                # get the position of the displayed cell and val
                self.highlightCodeTags('key_found')
                posShape = self.canvas.coords(n.display_shape)
                
                # Highlight the found element with a circle
                self.cleanup.add(self.canvas.create_oval(
                    *add_vector(
                        posShape,
                        (CELL_BORDER, CELL_BORDER, -CELL_BORDER, -CELL_BORDER)),
                    outline=FOUND_COLOR))

                # update the display
                self.window.update()
                self.wait(0.1)
                
                # Animation stops
                self.highlightCodeTags([])
                self.stopAnimations()
                return i

            # if not found, then move the index over one cell
            self.highlightCodeTags('outer_loop_increment')
            self.moveItemsBy(indexDisplay, (CELL_SIZE, 0), sleepTime=0.01)
            if self.wait(0.01):
                break

        # Key not found
        self.highlightCodeTags('key_not_found')
        self.window.update()
        self.wait(0.1)
        
        # Animation stops
        self.highlightCodeTags([])
        self.stopAnimations()
        return None

    def shuffle(self):
        self.startAnimations()
        self.cleanUp()

        y = ARRAY_Y0
        for i in range(len(self.list)):
            newI = random.randint(0, len(self.list)-1)
            self.list[i], self.list[newI] = self.list[newI], self.list[i]

        times = 0

        # Scramble positions
        canvasDimensions = self.widgetDimensions(self.canvas)
        DX = CELL_SIZE * 3 / 5
        DY = DX
        while times < len(self.list)*2:
            down = max(0, 5 - times) * CELL_SIZE // 5
            for i in range(len(self.list)):
                if self.wait(0.01):
                    break
                bBox = self.canvas.coords(self.list[i].display_shape)
                shuffleY = random.randint(
                    max(down - DY, -bBox[1]), 
                    min(down + DY, canvasDimensions[1] - bBox[3]))
                shuffleX = random.randint(
                    max(-DX, -bBox[0]), min(DX, canvasDimensions[0] - bBox[2]))
                self.moveItemsBy(
                    (self.list[i].display_shape, self.list[i].display_val),
                    (shuffleX, shuffleY),
                    steps=1, sleepTime=0)
            times += 1
            if self.wait(0.01):
                break
            self.window.update()

        # Animate return of values to their array cells
        self.stopMergeSort()

        # Animation stops
        self.stopAnimations()

    insertionSortCode = """
def insertionSort(self):
   for outer in range(1, self.__nItems):
      temp = self.__a[outer]
      inner = outer
      while inner > 0 and temp < self.__a[inner-1]:
         self.__a[inner] = self.__a[inner-1]
         inner -= 1
      self.__a[inner] = temp
"""
    insertionSortCodeSnippets = {
        'outer_loop_increment': ('2.7', '2.39'),
        'temp_assignment': ('3.6', '3.end'),
        'inner_assignment': ('4.6', '4.end'),
        'inner_loop_test': ('5.12', '5.50'),
        'inner_loop_assignment': ('6.9', '6.end'),
        'inner_loop_decrement': ('7.9', '7.end'),
        'outer_loop_assignment': ('8.6', '8.end'),
    }
    
    # SORTING METHODS
    def insertionSort(self):
        self.startAnimations()
        self.cleanUp()
        self.showCode(SimpleArraySort.insertionSortCode.strip())
        self.createCodeTags(self.insertionSortCodeSnippets)
        n = len(self.list)

        # make an index arrow for the outer loop
        outer = 1
        outerIndex = self.createIndex(outer, "outer", level=-2)
        self.cleanup |= set(outerIndex)
        self.highlightCodeTags('outer_loop_increment')

        # make an index arrow that points to the next cell to check
        innerIndex = self.createIndex(outer, "inner", level=-1)
        self.cleanup |= set(innerIndex)
        tempVal, label = None, None

        # All items beyond the outer index have not been sorted
        while outer < len(self.list):
            self.highlightCodeTags('outer_loop_increment')

            # Store item at outer index in temporary mark variable
            temp = self.list[outer].val
            self.highlightCodeTags('temp_assignment')
            if tempVal:
                tempVal, _ = self.assignToTemp(
                    outer, varName="temp", existing=label)
            else:
                tempVal, label = self.assignToTemp(outer, varName="temp")
                self.cleanup.add(label)
            self.cleanup.add(tempVal.display_shape)
            self.cleanup.add(tempVal.display_val)

            # Inner loop starts at marked temporary item
            inner = outer 

            # Move inner index arrow to point at cell to check
            self.highlightCodeTags('inner_assignment')
            centerX0 = self.cellCenter(inner)[0]
            deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
            if deltaX != 0:
                self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=0.02)
                
            # Loop down until we find an item less than or equal to the mark
            while inner > 0 and temp < self.list[inner - 1].val:
                self.highlightCodeTags('inner_loop_test')
                if self.wait(0.05):
                    break

                # Shift cells right that are greater than mark
                self.highlightCodeTags('inner_loop_assignment')
                self.assignElement(inner - 1, inner)

                # Move inner index arrow to point at next cell to check
                inner -= 1
                self.highlightCodeTags('inner_loop_decrement')
                centerX0 = self.cellCenter(inner)[0]
                deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
                if deltaX != 0:
                    self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=0.02)

            # Delay to show discovery of insertion point for mark
            if self.wait(0.1):
                break
            
            # Copy marked temporary value to insetion point
            self.highlightCodeTags('outer_loop_assignment')
            self.assignFromTemp(inner, tempVal, None)

            # Take it out of the cleanup set since it should persist
            for item in (tempVal.display_shape, tempVal.display_val):
                if item in self.cleanup:
                    self.cleanup.remove(item)

            # Advance outer loop
            outer += 1
            self.highlightCodeTags('outer_loop_increment')
            self.moveItemsBy(outerIndex, (CELL_SIZE, 0), sleepTime=0.02)
            if self.wait(0.01):
                break

        self.highlightCodeTags([])
        self.fixCells()

        # Animation stops
        self.stopAnimations()

    bubbleSortCode = """
def bubbleSort(self):
   for last in range(self.__nItems-1, 0, -1):
      for inner in range(last):
         if self.__a[inner] > self.__a[inner+1]:
            self.swap(inner, inner+1)
"""
    bubbleSortCodeSnippets = {
        'outer_loop_increment': ('2.7', '2.44'),
        'inner_loop_increment': ('3.10', '3.30'),
        'inner_loop_comparison': ('4.12', '4.47'),
        'inner_loop_swap': ('5.12', '5.end'),
    }
    
    def bubbleSort(self):
        self.startAnimations()
        self.cleanUp()
        self.showCode(SimpleArraySort.bubbleSortCode.strip())
        self.createCodeTags(self.bubbleSortCodeSnippets)
        n = len(self.list)

        # make an index arrow that points to last unsorted element
        last = n - 1
        lastIndex = self.createIndex(last, "last", level=2)
        self.cleanup |= set(lastIndex)
        self.highlightCodeTags('outer_loop_increment')

        # make an index arrow that points to the next cell to check
        innerIndex = self.createIndex(0, "inner", level=1)
        self.cleanup |= set(innerIndex)
        
        # While unsorted cells remain
        while last > 0:
            for inner in range(last):
                # Move inner index arrow to cell to check
                self.highlightCodeTags('inner_loop_increment')
                centerX0 = self.cellCenter(inner)[0]
                deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
                if deltaX != 0:
                    self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=0.02)
                    
                # Compare cell value at inner index with the next value
                self.highlightCodeTags('inner_loop_comparison')
                self.window.update()
                if self.wait(0.2):
                    break
                if self.list[inner].val > self.list[inner+1].val:
                    self.highlightCodeTags('inner_loop_swap')
                    self.swap(inner, inner+1)

            if self.wait(0.01):
                break

            # move last index one lower
            last -= 1
            self.highlightCodeTags('outer_loop_increment')
            self.moveItemsBy(lastIndex, (-CELL_SIZE, 0), sleepTime=0.05)

        # Animation stops
        self.highlightCodeTags([])
        self.stopAnimations()

    selectionSortCode = """
def selectionSort(self):
   for outer in range(self.__nItems-1):
      min = outer
      for inner in range(outer+1, self.__nItems):
         if self.__a[inner] < self.__a[min]:
            min = inner
      self.swap(outer, min)
"""
    selectionSortCodeSnippets = {
        'outer_loop_increment': ('2.7', '2.44'),
        'outer_min_assignment': ('3.6', '3.end'),
        'inner_loop_increment': ('4.10', '4.48'),
        'inner_loop_comparison': ('5.12', '5.43'),
        'inner_min_assignment': ('6.12', '6.end'),
        'outer_loop_swap': ('7.6', '7.end'),
    }
    
    def selectionSort(self):
        self.startAnimations()
        self.cleanUp()
        self.showCode(SimpleArraySort.selectionSortCode.strip())
        self.createCodeTags(self.selectionSortCodeSnippets)
        n = len(self.list)

        # make an index arrow for the outer loop
        outer = 0
        outerIndex = self.createIndex(outer, "outer", level=3)
        self.cleanup |= set(outerIndex)
        self.highlightCodeTags('outer_loop_increment')

        # make an index arrow that points to the next cell to check
        innerIndex = self.createIndex(outer+1, "inner", level=1)
        self.cleanup |= set(innerIndex)
        minIndex = None

        # All items beyond the outer index have not been sorted
        while outer < len(self.list) - 1:

            min_idx = outer
            self.highlightCodeTags('outer_min_assignment')
            if minIndex:
                self.moveItemsBy(
                    minIndex,
                    (self.cellCenter(outer)[0] - 
                     self.canvas.coords(minIndex[0])[0], 0), sleepTime=0.02)
            else:
                minIndex = self.createIndex(outer, "min", level=2)
                if self.wait(0.1):
                    break
                self.cleanup |= set(minIndex)
            
            # Find the minimum element in remaining
            # unsorted array
            for inner in range(outer + 1, len(self.list)):
                
                # Move inner index arrow to point at cell to check
                self.highlightCodeTags('inner_loop_increment')
                centerX0 = self.cellCenter(inner)[0]
                deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
                if deltaX != 0:
                    self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=0.02)

                self.highlightCodeTags('inner_loop_comparison')
                self.window.update()
                if self.wait(0.2):
                    break
                if self.list[inner].val < self.list[min_idx].val:
                    min_idx = inner
                    self.highlightCodeTags('inner_min_assignment')
                    self.moveItemsBy(
                        minIndex,
                        (self.canvas.coords(innerIndex[0])[0] -
                         self.canvas.coords(minIndex[0])[0], 0), sleepTime=0.02)

            if self.wait(0.01):
                break

            # Swap the found minimum element with the one indexed by outer
            self.highlightCodeTags('outer_loop_swap')
            self.swap(outer, min_idx)
            
            # move outer index one higher
            outer += 1
            self.highlightCodeTags('outer_loop_increment')
            self.moveItemsBy(outerIndex, (CELL_SIZE, 0), sleepTime=0.05)

        self.fixCells()

        # Animation stops
        self.highlightCodeTags([])
        self.stopAnimations()
        
    def stopMergeSort(self, toX=ARRAY_X0, toY=ARRAY_Y0):
        # bring all cells up to original position

        dy = -2
        dx = [0] * len(self.list)
        done = [False] * len(self.list)
        doneCount = 0

        # calculate dx for each node to move it back to original position
        for i in range(len(self.list)):
            fromX = self.canvas.coords(self.list[i].display_shape)[0]
            fromY = self.canvas.coords(self.list[i].display_shape)[1]
            if toY < fromY:
                dx[i] = dy * ((toX + CELL_SIZE * i) - fromX) / (toY - fromY)
            else:
                done[i] = True
                doneCount += 1

        # while all of the elements have not yet been returned to the original position
        while doneCount < len(self.list):
            for i in range(len(self.list)):
                # move the done elements up by dy and corresponding dx
                if not done[i]:
                    self.canvas.move(self.list[i].display_shape, dx[i], dy)
                    self.canvas.move(self.list[i].display_val, dx[i], dy)

                    # when the cell is in the correct position, mark it as done
                    if self.canvas.coords(self.list[i].display_shape)[1] <= toY:
                        doneCount += 1
                        done[i] = True

            self.window.update()
            if self.wait(0.01):
                break

        self.fixCells()
        
    def fixCells(self):       # Move canvas display items to exact cell coords
        for i, drawItem in enumerate(self.list):
            self.canvas.coords(drawItem.display_shape, *self.cellCoords(i))
            self.canvas.coords(drawItem.display_val, *self.cellCenter(i))
        self.window.update()

    def cleanUp(self):        # Customize clean up for sorting
        super().cleanUp()     # Do the VisualizationApp clean up
        self.fixCells()       # Restore cells to their coordinates in array
        
    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        bubbleSortButton = self.addOperation(
            "Bubble Sort", lambda: self.bubbleSort())
        selectionSortButton = self.addOperation(
            "Selection Sort", lambda: self.selectionSort())
        insertionSortButton = self.addOperation(
            "Insertion Sort", lambda: self.insertionSort())
        deleteButton = self.addOperation(
            "Delete Rightmost", lambda: self.removeFromEnd())
        shuffleButton = self.addOperation(
            "Shuffle", lambda: self.shuffle())
        self.addAnimationButtons()
        findButton = self.addOperation(
            "Find", lambda: self.clickFind(), numArguments=1,
            validationCmd=vcmd)
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd)
        buttons = [bubbleSortButton, selectionSortButton, insertionSortButton,
                   shuffleButton, findButton, insertButton, deleteButton]
        return buttons # Buttons managed by play/pause/stop controls

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val

    # Button functions
    def clickFind(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            result = self.find(val)
            if result != None:
                msg = "Found {}!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()

    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            self.insert(val)
            self.setMessage("Value {} inserted".format(val))
        self.clearArgument()

    def enableButtons(self, enable=True):
        for btn in self.buttons:
            btn.config(state=NORMAL if enable else DISABLED)
            
    def startAnimations(self):
        self.enableButtons(enable=False)
        super().startAnimations()
            
    def stopAnimations(self):
        super().stopAnimations()
        self.enableButtons(enable=True)
        self.argumentChanged()
                    
if __name__ == '__main__':
    random.seed(3.14159)    # Use fixed seed for testing consistency
    array = SimpleArraySort()

    array.runVisualization()

'''
To Do:
- make it look pretty
- animate insert and delete
- delete/insert at index?
- label arrows for sorts (inner, outer, etc.)
- implement shell sort, radix sort, quick sort
'''
