import random
import time
from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *
 

class SortingBase(VisualizationApp):
    CELL_SIZE = 50
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    ARRAY_X0 = 100
    ARRAY_Y0 = 100
    FOUND_COLOR = 'brown4'
    nextColor = 0
    CELL_WIDTH = CELL_SIZE
    CELL_MIN_WIDTH = 20
    
    def __init__(self, size=10, maxCells=100, valMax=99, **kwargs):
        super().__init__(**kwargs)
        self.size = size
        self.maxCells = maxCells
        self.valMax = valMax
        self.changeSize = False 

        self.list = []  # Internal array of drawable cell values
        
        self.display()
        
    def __str__(self):
        return str(self.list) 
    
    # ANIMATION METHODS
    def assignElement(self, fromIndex, toIndex, callEnviron, steps=10, sleepTime=0.01):
        
        fromItem = self.list[fromIndex]
        toItem = self.list[toIndex]

        # get positions of "to" cell in array
        toPositions = (self.fillCoords(fromItem.val, self.cellCoords(toIndex)),
                       self.cellCenter(toIndex))
                
        # create new display objects as copies of the "from" cell and value
        newCell = self.copyCanvasItem(fromItem.display_shape)
        items = (newCell,)
        if fromItem.display_val:
            items += (self.copyCanvasItem(fromItem.display_val),)
        callEnviron |= set(items)

        # Move copies to the desired location
        self.moveItemsTo(items, toPositions, steps=steps,
                         sleepTime=sleepTime)

        # delete the original "to" display value and the new display shape
        self.canvas.delete(self.list[toIndex].display_val)
        self.canvas.delete(self.list[toIndex].display_shape)

        # update value and display value in "to" position in the list
        toItem.val = fromItem.val
        toItem.color = fromItem.color
        toItem.display_shape = items[0]
        toItem.display_val = items[1] if len(items) > 1 else None
        
        callEnviron -= set(items)
        
        # update the window
        self.window.update()  
        
    def swap(self, a, b, aCellObjects=[], bCellObjects=[]):
        itemsA = [self.list[a].display_shape] + aCellObjects 
        itemsB = [self.list[b].display_shape] + bCellObjects
        if not self.changeSize:
            itemsA.append(self.list[a].display_val)
            itemsB.append(self.list[b].display_val)            
        #itemsA = [self.list[a].display_shape,
                  #self.list[a].display_val] + aCellObjects
        #itemsB = [self.list[b].display_shape,
                  #self.list[b].display_val] + bCellObjects
        upDelta = (0, - self.CELL_SIZE * 4 // 3)
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

    def indexCoords(self, index, level=1):
        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        level_space = abs(self.VARIABLE_FONT[1])
        x = cell_center[0]
        if level > 0:
            y0 = cell_coords[1] - self.CELL_SIZE * 3 // 5 - level * level_space
            y1 = cell_coords[1] - self.CELL_SIZE * 3 // 10
        else:
            y0 = cell_coords[3] + self.CELL_SIZE * 3 // 5 - level * level_space
            y1 = cell_coords[3] + self.CELL_SIZE * 3 // 10
        return x, y0, x, y1
        
    def createIndex(  # Create an index arrow to point at an indexed
            self, index,  # cell
            name=None,  # with an optional name label
            level=1,  # at a particular level away from the cells
            color=None):  # (negative are below)
        if not color: color = self.VARIABLE_COLOR

        x0, y0, x1, y1 = self.indexCoords(index, level)
        arrow = self.canvas.create_line(
            x0, y0, x0, y1, arrow="last", fill=color)
        if name:
            label = self.canvas.create_text(
                x0, y0, text=name, anchor=SW if level > 0 else NW,
                font=self.VARIABLE_FONT, fill=color)
        return (arrow, label) if name else (arrow,)  

    # ARRAY FUNCTIONALITY
    def new(self, val):
        canvasDims = self.widgetDimensions(self.canvas)
        maxCells = min(self.maxCells, 
                       (canvasDims[0] - self.ARRAY_X0) // self.CELL_MIN_WIDTH)
        if val > maxCells:
            self.setMessage('Too many cells; must be {} or less'.format(
                maxCells))
            return
        elif val < 1:
            self.setMessage('Too few cells; must be 1 or more')
            return
            
        self.size = val
        self.list = []
        self.changeSize = (self.size + 2) * self.CELL_SIZE > canvasDims[0]
        self.CELL_WIDTH = self.CELL_MIN_WIDTH if self.changeSize else self.CELL_SIZE
        self.display()
        
        return True

    def insert(self, val, allowGrowth=False):
        canvasDims = self.widgetDimensions(self.canvas)
        # Check if inserted cell will be off of the canvas
        offCanvas = canvasDims[0] <= self.cellCoords(len(self.list))[2]

        if (len(self.list) >= self.size and not allowGrowth or
            len(self.list) >= self.maxCells or
            self.CELL_WIDTH == self.CELL_MIN_WIDTH and offCanvas):
            self.setMessage('Array is full')
            return False
        
        self.startAnimations()
        callEnviron = self.createCallEnvironment()
        
        # Inserting when there is no room on the canvas
        redraw = False
        if offCanvas and not self.changeSize:
            self.changeSize = True 
            self.CELL_WIDTH = self.CELL_MIN_WIDTH
            redraw = True
        if self.size < len(self.list) + 1:
            self.size = len(self.list) + 1
            redraw = True
        if redraw:
            self.display()
            
        # create new cell and cell value display objects
        toPositions = (self.fillCoords(val, self.cellCoords(len(self.list))),
                       self.cellCenter(len(self.list)))

        # Animate arrival of new value from operations panel area
        startPosition = add_vector(
            [canvasDims[0] // 2 - self.CELL_WIDTH, canvasDims[1]] * 2,
            (0, 0) + (self.CELL_WIDTH - self.CELL_BORDER, 
                      2.5*self.CELL_SIZE - self.CELL_BORDER))
        
        cellPair = self.createCellValue(startPosition, val)

        if len(cellPair) == 1 or cellPair[1] is None:
            cellPair, toPositions = cellPair[:1], toPositions[:1]

        callEnviron |= set(cellPair)
        self.moveItemsTo(cellPair, toPositions, sleepTime=0.01)

        # add a new Drawable with the new value, color, and display objects
        self.list.append(drawable(
            val, self.canvas.itemconfigure(cellPair[0], 'fill')[-1], *cellPair))
        callEnviron ^= set(cellPair) # Remove new cell from temp call environment

        # advance nItems index
        self.moveItemsBy(self.nItems, (self.CELL_WIDTH, 0), sleepTime=0.01)

        self.cleanUp(callEnviron)
        return True
       
    def randomFill(self):
        callEnviron = self.createCallEnvironment()        

        self.list=[drawable(random.randrange(90)) for i in range(self.size)]
        
        self.display()         
        self.cleanUp(callEnviron)      
        
    def delete(self, val):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()

        # draw an index for variable j pointing to the first cell
        indexDisplay = self.createIndex(0, 'j')
        callEnviron |= set(indexDisplay)
        
        # go through each Drawable in the list
        # look for val to be deleted
        for j in range(len(self.list)):
            n = self.list[j]

            self.wait(0.1)
            
            if n.val == val:
                # get the position of the displayed cell
                cellShape = self.cellCoords(j)

                # Highlight the found element with a circle
                foundCircle = self.canvas.create_oval(
                    *add_vector(
                        cellShape,
                        multiply_vector((1, 1, -1, -1), self.CELL_BORDER)),
                    outline=self.FOUND_COLOR)
                callEnviron.add(foundCircle)

                # update the display
                self.wait(0.3)

                # remove the found circle
                callEnviron.remove(foundCircle)
                self.canvas.delete(foundCircle)

                # Slide value rectangle up and off screen
                items = (n.display_shape, n.display_val) if not self.changeSize else (n.display_shape,)
                self.moveItemsOffCanvas(items, N, sleepTime=0.02)

                #move nItems pointer
                self.moveItemsBy(self.nItems, (-self.CELL_WIDTH, 0),
                                 sleepTime=0.01)

                # Create an index for shifting the cells
                kIndex = self.createIndex(j, 'k')
                callEnviron |= set(kIndex)
            
                # Slide values from right to left to fill gap
                for k in range(j+1, len(self.list)):
                    self.assignElement(k, k - 1, callEnviron)
                    self.moveItemsBy(kIndex, (self.CELL_WIDTH, 0),
                                     sleepTime=0.01)
                    self.wait(0.1)

                # remove the last item in the list
                n = self.list.pop()
                # delete the associated display objects
                self.canvas.delete(n.display_shape)
                self.canvas.delete(n.display_val)
                
                # update window
                self.wait(0.3)

                self.cleanUp(callEnviron)
                return True

            # if not found, then move the index over one cell
            self.moveItemsBy(indexDisplay, (self.CELL_WIDTH, 0), sleepTime=0.01)

        # Animation stops
        self.cleanUp(callEnviron)
        return None

    def removeFromEnd(self):
        if len(self.list) == 0:
            self.setMessage('Array is empty!')
            return
    
        self.startAnimations()
        callEnviron = self.createCallEnvironment()

        #move nItems pointer
        self.moveItemsBy(self.nItems, (-self.CELL_WIDTH, 0), sleepTime=0.01)
        
        # pop an Element from the list
        n = self.list.pop()
        
        # Slide value rectangle up and off screen
        if not self.changeSize:
            items = (n.display_shape, n.display_val)
        else:
            items = (n.display_shape, )
        callEnviron |= set(items)
        self.moveItemsOffCanvas(items, N, sleepTime=0.02)
    
        # Finish animation
        self.cleanUp(callEnviron)

    def isSorted(self):
        return all(self.list[i-1] <= self.list[i] 
                   for i in range(1, len(self.list)))
        
    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        return (self.ARRAY_X0 + self.CELL_WIDTH * cell_index, self.ARRAY_Y0,  # at index
                self.ARRAY_X0 + self.CELL_WIDTH * (cell_index + 1) - self.CELL_BORDER,
                self.ARRAY_Y0 + 2.5*self.CELL_SIZE - self.CELL_BORDER)    
    
    def cellCenter(self, cell_index):  # Center point for array cell at index
        x1, y1, x2, y2 = self.cellCoords(cell_index)
        midX = (x1 + x2) // 2 
        midY = (y1 + y2) // 2
        return midX, midY    
    
    def createArrayCell(self, index):  # Create a box representing an array cell
        cell_coords = self.cellCoords(index)
        half_border = self.CELL_BORDER // 2
        rect = self.canvas.create_rectangle(
            *add_vector(cell_coords,
                        (-half_border, -half_border,
                         self.CELL_BORDER - half_border, self.CELL_BORDER - half_border)),
            fill=None, outline=self.CELL_BORDER_COLOR, width=self.CELL_BORDER, tags="arrayBox")
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
            color = drawable.palette[SortingBase.nextColor]
            SortingBase.nextColor = (SortingBase.nextColor + 1) % len(drawable.palette)
      
        newCoords = self.fillCoords(key, rectPos)
    
        cell = (self.canvas.create_rectangle(
            *newCoords, fill=color, outline='', width=0),)
        valWidth = self.textWidth(self.VALUE_FONT, str(self.valMax))
        if valWidth < self.CELL_WIDTH:
            cell += (self.canvas.create_text(
                *valPos, text=str(key), font=self.VALUE_FONT,
                fill=self.VALUE_COLOR, tags="cellVal"), )
        handler = lambda e: self.setArgument(str(key))
        for item in cell:
            self.canvas.tag_bind(item, '<Button>', handler)

        return cell if len(cell) == 2 else (cell[0], None)
    
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
    
    def redrawArrayCells(self):        
        self.canvas.delete("arrayBox")
        for i in range(len(self.list)):
            self.createArrayCell(i)    
    
    def display(self):
        self.canvas.delete("all")
    
        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)

        # draw an index pointing to the last item in the list
        self.nItems = self.createIndex(
            len(self.list), 'nItems', level = -1, color = 'black')
    
        # go through each Drawable in the list
        for i, n in enumerate(self.list):
            # create display objects for the associated Drawables
            cell = self.createCellValue(i, n.val, n.color)
            n.display_shape = cell[0]
            n.display_val = cell[1] if len(cell) > 1 else None
            n.color = self.canvas.itemconfigure(n.display_shape, 'fill')[-1]
    
        self.window.update()

    def toTarget(         # Return the 2-D vector between the indexed item's
            self, index): # current position and its normal position in array
        return subtract_vector(
            self.cellCoords(index), 
            self.canvas.coords(self.list[index].display_shape)[:2])
    
    def shuffle(self, steps=20):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()

        nItems = len(self.list)    
        random.shuffle(self.list)  # Randomly move items internally in array

        coords0 = self.cellCoords(0) # Get the height of a cell
        canvasDims = self.widgetDimensions(self.canvas)
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
                for item in self.list[i][2:]: # Get drawable shape and val
                    if item:       # If not None, move it by velocity
                        self.canvas.move(item, *velocity[i])
                velocity[i] = add_vector(  # Change velocity to move towards
                    add_vector(            # target location
                        multiply_vector(velocity[i], 0.8), 
                        divide_vector(self.toTarget(i), stepsToGo)),
                    (random.randint(-jitter, jitter), # Add some random jitter
                     random.randint(-half, half)))
            self.wait(0.05)

        # Ensure all items get to new positions
        self.fixCells()

        # Animation stops
        self.cleanUp(callEnviron)
        
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
                dx[i] = dy * ((toX + self.CELL_SIZE * i) - fromX) / (toY - fromY)
            else:
                done[i] = True
                doneCount += 1
    
        # while all of the elements have not yet been returned to the original position
        while doneCount < len(self.list):
            for i in range(len(self.list)):
                # move the done elements up by dy and corresponding dx
                if not done[i]:
                    self.canvas.move(self.list[i].display_shape, dx[i], dy)
                    if not self.changeSize: self.canvas.move(self.list[i].display_val, dx[i], dy)
    
                    # when the cell is in the correct position, mark it as done
                    if self.canvas.coords(self.list[i].display_shape)[1] <= toY:
                        doneCount += 1
                        done[i] = True
    
            self.window.update()
            if self.wait(0.01):
                break
    
        self.fixCells()
    
    def fixCells(self):  # Move canvas display items to exact cell coords
        for i, drawItem in enumerate(self.list):
            if drawItem.display_shape:
                self.canvas.coords(
                    drawItem.display_shape,
                    *self.fillCoords(drawItem.val, self.cellCoords(i)))
            if not self.changeSize and drawItem.display_val:
                self.canvas.coords(drawItem.display_val, *self.cellCenter(i))
        if self.nItems:
            indexCoords = self.indexCoords(len(self.list), level=-1)
            for item in self.nItems:
                nCoords = len(self.canvas.coords(item))
                self.canvas.coords(item, *indexCoords[:nCoords]) 
        self.window.update()
        
    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        self.fixCells() 
        
    def makeButtons(self, maxRows=4):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        newButton = self.addOperation(
            "New", lambda: self.clickNew(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows)
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows)
        deleteButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows)
        randomFillButton = self.addOperation(
            "Random Fill", lambda: self.randomFill(), maxRows=maxRows)
        shuffleButton = self.addOperation(
            "Shuffle", lambda: self.shuffle(), maxRows=maxRows) 
        deleteRightmostButton = self.addOperation(
            "Delete Rightmost", lambda: self.removeFromEnd(), maxRows=maxRows)
        buttons = [newButton, insertButton, deleteButton,
                   randomFillButton, shuffleButton, deleteRightmostButton]
        return buttons, vcmd  # Buttons managed by play/pause/stop controls    
    
    def validArgument(self, valMax=None):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if valMax is None:
                valMax = self.valMax
            if val < valMax:
                return val
    
    # Button functions
    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage(
                "Input value must be an integer from 0 to {}".format(
                    self.valMax))
        elif self.insert(val, allowGrowth=True):
            self.setMessage("Value {} inserted".format(val))
            self.clearArgument() 
     
    def clickDelete(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99")
        else:
            result = self.delete(val)
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
        if self.new(val):
            self.clearArgument()
