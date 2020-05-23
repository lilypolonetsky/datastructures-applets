import random
import time
from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

WIDTH = 800
HEIGHT = 400

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
    def __init__(self, size=10, title="Simple Sorting", **kwargs):
        super().__init__(title=title, **kwargs)
        self.size = size
        self.title = title
        self.list = []

        self.waitVar = BooleanVar()
        self.running = False

        self.cleanup = []
        self.buttons = self.makeButtons()
        for i in range(size):
            self.insert(random.randrange(20), animate=False)
        self.display()
        
    nextColor = 0

    def __str__(self):
        return str(self.list)

    # ANIMATION METHODS
    def assignElement(self, fromIndex, toIndex):
        fromItem = self.list[fromIndex]
        toItem = self.list[toIndex]
        
        # get positions of "to" cell in array
        toPositions = (self.cellCoords(toIndex), self.cellCenter(toIndex))

        # create new display objects as copies of the "from" cell and value
        newCell = self.copyCanvasItem(fromItem.display_shape)
        newCellVal = self.copyCanvasItem(fromItem.display_val)

        # Move copies to the desired location
        self.moveItemsTo((newCell, newCellVal), toPositions, steps=CELL_SIZE,
                       sleepTime=0.01)
        
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

    def assignToTemp(self, index, varName="temp", existing=(None,)):
        """Assign indexed cell to a temporary variable named varName.
        Animate value moving to the temporary variable above the array.
        Return a drawable for the new temporary value and a text item for
        its name.  Those can be passed in the existing parameter to place
        new values in the same temporary variable.
        """
        fromDrawable = self.list[index]
        fromCell = fromDrawable.display_shape
        fromCellVal = fromDrawable.display_val
        posCell = self.canvas.coords(fromCell)
        posCellVal = self.canvas.coords(fromCellVal)

        shape = self.copyCanvasItem(fromCell)
        val = self.copyCanvasItem(fromCellVal)
        posLabel = subtract_vector(posCellVal, (0, CELL_SIZE * 9 / 5))
        if existing[1] is None:
            templabel = self.canvas.create_text(
                *posLabel, text=varName, font=VARIABLE_FONT, 
                fill=VARIABLE_COLOR)
        else:
            tempPos = self.canvas.coords(existing[0])
            templabel = existing[1]

        delta = (0 if existing[0] is None else tempPos[0] - posCell[0],
                 - CELL_SIZE * 4 // 3)
        self.moveItemsBy((shape, val), delta, sleepTime=0.01)

        return drawable(fromDrawable.val, fromDrawable.color, shape, val), templabel

    def assignFromTemp(self, index, temp, templabel):

        toCellCoords = self.cellCoords(index)
        toCellCenter = self.cellCenter(index)
        tempCellCoords = self.canvas.coords(temp.display_shape)
        deltaX = toCellCoords[0] - tempCellCoords[0]
        startAngle = 90 * 500 / (500 + abs(deltaX)) * (-1 if deltaX < 0 else 1)
                           
        self.moveItemsOnCurve(
            (temp.display_shape, temp.display_val),
            (toCellCoords, toCellCenter), sleepTime=0.04, startAngle=startAngle)
        
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
            color=VARIABLE_COLOR): # with a particular color
        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        level_spacing = VARIABLE_FONT[1] 
        x = cell_center[0]
        y0 = cell_coords[1] - CELL_SIZE * 3 // 5 - level * level_spacing
        y1 = cell_coords[1] - CELL_SIZE * 3 // 10
        arrow = self.canvas.create_line(
            x, y0, x, y1, arrow="last", fill=color)
        if name:
            label = self.canvas.create_text(
                x + 2, y0, text=name, anchor=SW,
                font=VARIABLE_FONT, fill=color)
        return (arrow, label) if name else (arrow, )

    def insert(self, val, animate=True):
        self.cleanUp()
        # If array needs to grow, add cells:
        while self.size < len(self.list) + 1:
            self.size += 1
            self.createArrayCell(len(self.list))

        # draw an index pointing to the last cell
        if animate:
            indexDisplay = self.createIndex(len(self.list))
            self.cleanup.extend(indexDisplay)

        # create new cell and cell value display objects
        toPositions = (self.cellCoords(len(self.list)), 
                       self.cellCenter(len(self.list)))

        # Animate arrival of new value from operations panel area
        if animate:
            startPosition = [
                int(self.canvas.config('width')[-1]) // 2,
                int(self.canvas.config('height')[-1])]
            cell = self.canvas.create_rectangle(
                *startPosition, *add_vector(startPosition, [CELL_SIZE] * 2),
                fill=drawable.palette[SimpleArraySort.nextColor], outline='')
            cell_val = self.canvas.create_text(
                *add_vector(startPosition, [CELL_SIZE // 2] * 2), text=val,
                font=VALUE_FONT, fill=VALUE_COLOR)
            self.moveItemsTo((cell, cell_val), toPositions, steps=CELL_SIZE,
                           sleepTime=0.01)
        else:
            cell = self.canvas.create_rectangle(
                *toPositions[0], fill=drawable.palette[SimpleArraySort.nextColor], 
                outline='')
            cell_val = self.canvas.create_text(
                *toPositions[1], text=val, font=VALUE_FONT, fill=VALUE_COLOR)

        # add a new Drawable with the new value, color, and display objects
        self.list.append(drawable(
            val, drawable.palette[SimpleArraySort.nextColor], cell, cell_val))

        # increment nextColor
        SimpleArraySort.nextColor = (
            SimpleArraySort.nextColor + 1) % len(drawable.palette)

        # update window
        self.window.update()

        # advance index for next insert
        if animate:
            self.moveItemsBy(indexDisplay, (CELL_SIZE, 0))

    def removeFromEnd(self):
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

    def display(self):
        self.canvas.delete("all")

        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)
        
        # go through each Drawable in the list
        for i, n in enumerate(self.list):
            # create display objects for the associated Elements
            cell = self.canvas.create_rectangle(
                *self.cellCoords(i), fill=n.color, outline='', width=0)
            cell_val = self.canvas.create_text(
                *self.cellCenter(i), text=n.val, font=VALUE_FONT,
                fill=VALUE_COLOR)

            # save the display objects in the Drawable object fields
            n.display_shape = cell
            n.display_val = cell_val

        self.window.update()

    def find(self, val):
        self.running = True
        self.cleanUp()

        # draw an index for variable j pointing to the first cell
        indexDisplay = self.createIndex(0, 'j')
        self.cleanup.extend(indexDisplay)

        # go through each Drawable in the list
        for i in range(len(self.list)):
            self.window.update()

            n = self.list[i]

            # if the value is found
            if n.val == val:
                # get the position of the displayed cell and val
                posVal = self.canvas.coords(n.display_val)
                
                # Highlight the found element with a circle
                self.cleanup.append(self.canvas.create_oval(
                    *add_vector(
                        posVal,
                        (CELL_BORDER, CELL_BORDER, -CELL_BORDER, -CELL_BORDER)),
                    outline=FOUND_COLOR))

                # update the display
                self.window.update()
                
                # Animation stops
                self.running = False
                return i

            # if not found, wait 1 second, and then move the index over one cell
            time.sleep(self.speed(1))
            for item in indexDisplay:
                self.canvas.move(item, CELL_SIZE, 0)

            if not self.running:
                break

        # Animation stops
        self.running = False
        return None

    def shuffle(self):
        self.running = True

        maxHeight = HEIGHT - 5
        maxWidth = WIDTH -5
        y = ARRAY_Y0
        for i in range(len(self.list)):
            newX = random.randint(0, len(self.list)-1)
            self.list[i], self.list[newX] = self.list[newX], self.list[i]
            finalX = ARRAY_X0 + (CELL_SIZE * newX)

        times = 0

        # while all of the elements have not yet been returned to the original position
        while times < len(self.list)*2 and self.running:
            for i in range(len(self.list)):
                time.sleep(self.speed(0.01))
                shuffleY = random.randint(-30, 30)
                shuffleX = random.randint(-30, 30)


                # not go off the sides
                if self.canvas.coords(self.list[i].display_shape)[0] + shuffleX <= 0 or self.canvas.coords(self.list[i].display_shape)[0] + shuffleX >= maxWidth:
                    shuffleX = -shuffleX * 2
                if self.canvas.coords(self.list[i].display_shape)[1] + shuffleY <= ARRAY_Y0 or self.canvas.coords(self.list[i].display_shape)[1] + shuffleY >= maxHeight:
                    shuffleY = -shuffleY * 2
                self.canvas.move(self.list[i].display_shape, shuffleX, shuffleY)
                self.canvas.move(self.list[i].display_val, shuffleX, shuffleY)
            times += 1
            time.sleep(self.speed(0.01))
            self.window.update()

        # Animation stops
        self.running = False
        self.stopMergeSort()

    # SORTING METHODS
    def insertionSort(self):
        self.running = True
        self.cleanUp()
        
        # make a done arrow that points to 0'th element
        x = self.canvas.coords(self.list[0].display_shape)[0] + (CELL_SIZE / 2)
        y0 = self.canvas.coords(self.list[0].display_shape)[1] + CELL_SIZE + 15
        y1 = self.canvas.coords(self.list[0].display_shape)[1] + CELL_SIZE + 40
        outerArrow = self.canvas.create_line(x+CELL_SIZE, y0, x+CELL_SIZE, y1, arrow="first", fill='red')

        # Traverse through 1 to len(arr)
        for i in range(1, len(self.list)):

            cur, text = self.assignToTemp(i, "cur")
            self.cleanup.extend([cur, text])

            # Move elements of self.list[0..i-1], that are
            # greater than key, to one position ahead
            # of their current position
            j = i - 1

            innerArrow = self.canvas.create_line(x+CELL_SIZE*i, y0, x+CELL_SIZE*i, y1, arrow="first", fill='blue')

            while j >= 0 and cur.val < self.list[j].val:
                #self.list[j + 1] = self.list[j]
                time.sleep(self.speed(0.1))
                self.assignElement(j, j+1)
                j -= 1

                self.canvas.move(innerArrow, -CELL_SIZE, 0)

                if not self.running:
                    self.canvas.delete(innerArrow)
                    break

            #self.list[j + 1] = cur
            time.sleep(self.speed(0.1))
            self.assignFromTemp(j+1, cur, text)

            self.canvas.delete(innerArrow)

            if not self.running:
                break

            # move done arrow to next element
            self.canvas.move(outerArrow, CELL_SIZE, 0)


        self.canvas.delete(outerArrow)
        self.fixGaps()

        # Animation stops
        self.running = False

    def bubbleSort(self):
        self.running = True
        self.cleanUp()
        n = len(self.list)

        # make an index arrow that points to last unsorted element
        last = n - 1
        lastIndex = self.createIndex(last, "last", level=2)
        self.cleanup.extend(lastIndex)

        # make an index arrow that points to the next cell to check
        innerIndex = self.createIndex(0, "inner", level=1)
        self.cleanup.extend(innerIndex)
        
        # While unsorted cells remain
        while last > 0:
            for inner in range(last):
                # Move inner index arrow to cell to check
                centerX0 = self.cellCenter(inner)[0]
                deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
                if deltaX != 0:
                    self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=0.02)
                    
                # Compare cell value at inner index with the next value
                if self.list[inner].val > self.list[inner+1].val:
                    self.swap(inner, inner+1)
                else:
                    time.sleep(self.speed(0.4))

                if not self.running:
                    break

            if not self.running:
                break

            # move last index one lower
            last -= 1
            self.moveItemsBy(lastIndex, (-CELL_SIZE, 0), sleepTime=0.05)

        # Animation stops
        self.running = False
        
    def selectionSort(self):
        self.running = True
        self.cleanUp()
        n = len(self.list)

        # make an index arrow for the outer loop
        outer = 0
        outerIndex = self.createIndex(outer, "outer", level=3)
        self.cleanup.extend(outerIndex)

        # make an index arrow that points to the next cell to check
        innerIndex = self.createIndex(outer+1, "inner", level=1)
        self.cleanup.extend(innerIndex)
        minIndex = None

        # All items beyond the outer index have not been sorted
        while outer < len(self.list) - 1:

            min_idx = outer
            if minIndex:
                self.moveItemsBy(
                    minIndex,
                    (self.cellCenter(outer)[0] - 
                     self.canvas.coords(minIndex[0])[0], 0), sleepTime=0.02)
            else:
                minIndex = self.createIndex(outer, "min", level=2)
                self.cleanup.extend(minIndex)
            
            # Find the minimum element in remaining
            # unsorted array
            for inner in range(outer + 1, len(self.list)):
                
                # Move inner index arrow to point at cell to check
                centerX0 = self.cellCenter(inner)[0]
                deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
                if deltaX != 0:
                    self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=0.02)

                if self.list[inner].val < self.list[min_idx].val:
                    min_idx = inner
                    self.moveItemsBy(
                        minIndex,
                        (self.canvas.coords(innerIndex[0])[0] -
                         self.canvas.coords(minIndex[0])[0], 0), sleepTime=0.02)
                else:
                    time.sleep(self.speed(0.4))

                if not self.running:
                    break

            if not self.running:
                break

            # Swap the found minimum element with the one indexed by outer
            self.swap(outer, min_idx)
            
            # move outer index one higher
            outer += 1
            self.moveItemsBy(outerIndex, (CELL_SIZE, 0), sleepTime=0.05)

        self.fixGaps()

        # Animation stops
        self.running = False
        
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
            time.sleep(self.speed(0.01))

        self.fixGaps()
        
    def fixGaps(self):        # Move canvas display items to exact cell coords
        for i, drawItem in enumerate(self.list):
            self.canvas.coords(drawItem.display_shape, *self.cellCoords(i))
            self.canvas.coords(drawItem.display_val, *self.cellCenter(i))
        self.window.update()

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
        self.pauseButton = self.addOperation(
            "Pause", lambda: self.onClick(self.pause, self.pauseButton()))
        self.stopButton = self.addOperation(
            "Stop", lambda: self.onClick(self.stop, self.pauseButton()))
        findButton = self.addOperation(
            "Find", lambda: self.clickFind(), hasArgument=True,
            validationCmd=vcmd)
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), hasArgument=True,
            validationCmd=vcmd)
        buttons = [bubbleSortButton, selectionSortButton, insertionSortButton,
                   findButton, insertButton, deleteButton]
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

    def stop(self, pauseButton): # will stop after the current shuffle is done
        self.running = False

        if self.waitVar.get():
            self.play(pauseButton)

    def pause(self, pauseButton):
        self.waitVar.set(True)

        pauseButton['text'] = "Play"
        pauseButton['command'] = lambda: self.onClick(self.play, pauseButton)

        self.canvas.wait_variable(self.waitVar)

    def play(self, pauseButton):
        self.waitVar.set(False)

        pauseButton['text'] = 'Pause'
        pauseButton['command'] = lambda: self.onClick(self.pause, pauseButton)

    def onClick(self, command, parameter = None):
        self.cleanUp()
        self.enableButtons(False)
        if parameter:
            command(self, parameter)
        else:
            command(self)
        if command not in [self.pause, self.play]:
            self.enableButtons()
            
    def enableButtons(self, enable=True):
        for btn in self.buttons:
            btn.config(state=NORMAL if enable else DISABLED)


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
