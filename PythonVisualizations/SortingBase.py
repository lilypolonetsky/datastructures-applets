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
    changeSize = False 
    
    def __init__(self, size=10, **kwargs):
        super().__init__(**kwargs)
        self.size = size
        self.list = []  # Internal array of drawable cell values
        
        self.display()
        
    def __str__(self):
        return str(self.list) 
    
    # ANIMATION METHODS
    def assignElement(self, fromIndex, toIndex, callEnviron, steps=10, sleepTime=0.01):
        
        fromItem = self.list[fromIndex]
        toItem = self.list[toIndex]

        # get positions of "to" cell in array
        toPositions = (self.cellCoords(toIndex), self.cellCenter(toIndex))
            
        
        # create new display objects as copies of the "from" cell and value
        newCell = self.copyCanvasItem(fromItem.display_shape)
        if not self.changeSize: newCellVal = self.copyCanvasItem(fromItem.display_val)
        
        items = (newCell, newCellVal) if not self.changeSize else (newCell,)
        callEnviron |= set(items)

        # Move copies to the desired location
        self.moveItemsTo(items, toPositions, steps=steps,
                         sleepTime=sleepTime)

        # delete the original "to" display value and the new display shape
        self.canvas.delete(self.list[toIndex].display_val)
        self.canvas.delete(self.list[toIndex].display_shape)

        # update value and display value in "to" position in the list
        self.list[toIndex].display_val = newCellVal if not self.changeSize else None
        self.list[toIndex].val = self.list[fromIndex].val
        self.list[toIndex].display_shape = newCell
        self.list[toIndex].color = self.list[fromIndex].color
        
        callEnviron.remove(newCell)
        if not self.changeSize: callEnviron.remove(newCellVal)
        
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
    def new(self, val, maxCells=100):
        if val > maxCells:
            self.setMessage('Too many cells; must be {} or less}'.format(
                maxCells))
            return
        elif val < 1:
            self.setMessage('Too few cells; must be 1 or more')
            return
            
        self.size = val
        self.list = []
        canvasDimensions = self.widgetDimensions(self.canvas)
        self.changeSize = (self.size + 2) * self.CELL_SIZE > canvasDimensions[0]
        self.CELL_WIDTH = 20 if self.changeSize else self.CELL_SIZE
        self.display()
        
        return True

    def insert(self, val):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()
        
        # Inserting when there is no room on the canvas
        if self.window.winfo_width() <= self.ARRAY_X0 + (
            (len(self.list)+1) * self.CELL_SIZE):
            # change cell width to 20
            self.CELL_WIDTH = 20
            # if this is the first insert that will change the width 
            if not self.changeSize:
                self.changeSize = True 
                # redraw the existing cells to be narrower
                self.fixCells()
                self.redrawArrayCells()
                # delete the cell values 
                self.canvas.delete("cellVal")
            
        # If array needs to grow, add cells:
        while self.size < len(self.list) + 1:
            self.size += 1
            self.createArrayCell(len(self.list))

        # create new cell and cell value display objects
        toPositions = (self.fillCoords(val, self.cellCoords(len(self.list))),
                       self.cellCenter(len(self.list)))

        # Animate arrival of new value from operations panel area
        canvasDimensions = self.widgetDimensions(self.canvas)
        startPosition = add_vector(
            [canvasDimensions[0] // 2 - self.CELL_WIDTH, canvasDimensions[1]] * 2,
            (0, 0) + (self.CELL_WIDTH - self.CELL_BORDER, 2.5*self.CELL_SIZE - self.CELL_BORDER))
        
        cellPair = self.createCellValue(startPosition, val)
        callEnviron |= set(cellPair)
        # if it is the smaller size cell
        if self.changeSize:
            # remove the generated cell value 
            self.canvas.delete(cellPair[1])
            callEnviron.remove(cellPair[1])
            self.moveItemsTo((cellPair[0],), toPositions, steps=self.CELL_SIZE, sleepTime=0.01)
        else:
            self.moveItemsTo(cellPair, toPositions, steps=self.CELL_SIZE, sleepTime=0.01)

        # add a new Drawable with the new value, color, and display objects
        self.list.append(drawable(
            val, self.canvas.itemconfigure(cellPair[0], 'fill'), *cellPair))
        callEnviron ^= set(cellPair) # Remove new cell from temp call environment

        # advance index for next insert
        self.moveItemsBy(self.nItems, (self.CELL_WIDTH, 0), sleepTime=0.01)

        self.cleanUp(callEnviron)     
       
    def randomFill(self):
        callEnviron = self.createCallEnvironment()        

        self.list=[drawable(random.randrange(90)) for i in range(self.size)]
        
        self.display()         
        self.cleanUp(callEnviron)      
        
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
    
        cell_rect = self.canvas.create_rectangle(
            *newCoords, fill=color, outline='', width=0)
        cell_val = self.canvas.create_text(
            *valPos, text=str(key), font=self.VALUE_FONT, fill=self.VALUE_COLOR, tags="cellVal")
        handler = lambda e: self.setArgument(str(key))
        for item in (cell_rect, cell_val):
            self.canvas.tag_bind(item, '<Button>', handler)

        return cell_rect, cell_val
    
    # get the whole box coords and return how much will get filled 
    def fillCoords(self, val, rectPos): 
        x1, y1, x2, y2 = rectPos 
        midY = (y1 + y2) // 2
        # proportion of what is filled
        prop = val / 99
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
            n.display_shape, n.display_val = self.createCellValue(
                i, n.val, n.color)
            if self.changeSize:
                self.canvas.delete(n.display_val)
            n.color = self.canvas.itemconfigure(n.display_shape, 'fill')[-1]
    
        self.window.update()
        
    def shuffle(self):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()
    
        y = self.ARRAY_Y0
        for i in range(len(self.list)):
            newI = random.randint(0, len(self.list) - 1)
            self.list[i], self.list[newI] = self.list[newI], self.list[i]
    
        times = 0
    
        # Scramble positions
        canvasDimensions = self.widgetDimensions(self.canvas)
        DX = self.CELL_SIZE * 3 / 5
        DY = DX
        while times < len(self.list) * 2:
            down = max(0, 5 - times) * self.CELL_SIZE // 5
            for i in range(len(self.list)):
                if self.wait(0.01):
                    break
                bBox = self.canvas.coords(self.list[i].display_shape)
                shuffleY = random.randint(
                    max(down - DY, -bBox[1]),
                    min(down + DY, canvasDimensions[1] - bBox[3]))
                shuffleX = random.randint(
                    max(-DX, -bBox[0]), min(DX, canvasDimensions[0] - bBox[2]))
                items = (self.list[i].display_shape, self.list[i].display_val) if not self.changeSize else (self.list[i].display_shape,)
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
        
    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        shuffleButton = self.addOperation(
            "Shuffle", lambda: self.shuffle()) 
        deleteRightmostButton = self.addOperation(
            "Delete Rightmost", lambda: self.removeFromEnd())
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd)
        buttons = [shuffleButton, deleteRightmostButton, insertButton]
        return buttons, vcmd  # Buttons managed by play/pause/stop controls    
    
    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val
    
    # Button functions
    def clickInsert(self):
        # if the animation is not stopped (it is running or paused):
        if self.animationState != self.STOPPED:
            # error message appears and insert will not take place
            self.setMessage("Unable to insert at the moment")  
        else:
            val = self.validArgument()
            if val is None:
                self.setMessage("Input value must be an integer from 0 to 99")
            else:
                self.insert(val)
                self.setMessage("Value {} inserted".format(val))
            
        self.clearArgument() 
     

