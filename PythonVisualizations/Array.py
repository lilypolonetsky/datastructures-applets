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
ARRAY_X0 = 100
ARRAY_Y0 = 100
FONT_SIZE = '20'
VALUE_FONT = ('Helvetica', FONT_SIZE)
VALUE_COLOR = 'black'
FOUND_COLOR = 'brown4'

class Array(VisualizationApp):
    def __init__(self, size=10, **kwargs):
        super().__init__(**kwargs)
        self.list = []
        self.size = size
        self.buttons = self.makeButtons()
        
        for i in range(9):
            self.insert(random.randrange(90), animate=False)
        self.display()

    nextColor = 0

    def __str__(self):
        return str(self.list)

    # ARRAY FUNCTIONALITY
    def get(self, index):
        try:
            return self.list[index].val
        except:
            print("Invalid list index")
            return -1

    def set(self, index, val):
        # reset the value of the Drawable at that index to val
        self.list[index].val = val

        # get the position of the displayed value
        pos = self.canvas.coords(self.list[index].display_val)

        # delete the displayed value and replace it with the updated value
        self.canvas.delete(self.list[index].display_val)
        self.list[index].display_val = self.canvas.create_text(
            pos[0], pos[1], text=str(val), font=VALUE_FONT, fill=VALUE_COLOR)

        # update window
        self.window.update()

    def createIndex(         # Create an index arrow to point at an indexed
            self, index, name=None): # cell with an optional name label
        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        x = cell_center[0]
        y0 = cell_coords[1] - CELL_SIZE * 4 // 5
        y1 = cell_coords[1] - CELL_SIZE * 3 // 10
        arrow = self.canvas.create_line(
            x, y0, x, y1, arrow="last", fill=VARIABLE_COLOR)
        if name:
            label = self.canvas.create_text(
                x + 2, y0, text=name, anchor=SW,
                font=VARIABLE_FONT, fill=VARIABLE_COLOR)
        return (arrow, label) if name else (arrow, )
        
    def insert(self, val, animate=True):
        self.cleanUp()
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
                fill=drawable.palette[Array.nextColor], outline='')
            cell_val = self.canvas.create_text(
                *add_vector(startPosition, [CELL_SIZE // 2] * 2), text=val,
                font=VALUE_FONT, fill=VALUE_COLOR)
            self.moveItemsTo((cell, cell_val), toPositions, steps=CELL_SIZE,
                           sleepTime=0.01)
        else:
            cell = self.canvas.create_rectangle(
                *toPositions[0], fill=drawable.palette[Array.nextColor], 
                outline='')
            cell_val = self.canvas.create_text(
                *toPositions[1], text=val, font=VALUE_FONT, fill=VALUE_COLOR)

        # add a new Drawable with the new value, color, and display objects
        self.list.append(drawable(val, drawable.palette[Array.nextColor], 
                                  cell, cell_val))

        # increment nextColor
        Array.nextColor = (Array.nextColor + 1) % len(drawable.palette)

        # update window
        self.window.update()

        # advance index for next insert
        if animate:
            self.moveItemsBy(indexDisplay, (CELL_SIZE, 0))

    def removeFromEnd(self):
        self.cleanUp()
        # pop a Drawable from the list
        if len(self.list) == 0:
            self.setMessage('Array is empty!')
            return
        n = self.list.pop()

        # delete the associated display objects
        self.canvas.delete(n.display_shape)
        self.canvas.delete(n.display_val)

        # update window
        self.window.update()

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

    def cellCoords(self, cell_index): # Get bounding rectangle for array cell
        return (ARRAY_X0 + CELL_SIZE * cell_index, ARRAY_Y0, # at index
                ARRAY_X0 + CELL_SIZE * (cell_index + 1) - CELL_BORDER,
                ARRAY_Y0 + CELL_SIZE - CELL_BORDER)

    def cellCenter(self, index): # Center point for array cell at index
        half_cell = (CELL_SIZE - CELL_BORDER) // 2
        return add_vector(self.cellCoords(index), (half_cell, half_cell))

    def createArrayCell(self, index): # Create a box representing an array cell
        cell_coords = self.cellCoords(index)
        half_border = CELL_BORDER // 2
        self.canvas.create_rectangle(
            *add_vector(cell_coords, 
                        (-half_border, -half_border,
                         CELL_BORDER - half_border, CELL_BORDER - half_border)),
            fill='white', outline='black', width=CELL_BORDER)
        
    def display(self):
        self.canvas.delete("all")

        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)

        # go through each Drawable in the list
        for i, n in enumerate(self.list):
            # print(n)
            # create display objects for the associated Drawables
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
        global running
        running = True
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
                # get the position of the displayed cell 
                posVal = self.canvas.coords(n.display_shape)
                
                # Highlight the found element with a circle
                self.cleanup.append(self.canvas.create_oval(
                    *add_vector(
                        posVal,
                        (CELL_BORDER, CELL_BORDER, -CELL_BORDER, -CELL_BORDER)),
                    outline=FOUND_COLOR))

                # update the display
                self.window.update()

                return i

            # if the value hasn't been found, wait 1 second, and then move the arrow over one cell
            time.sleep(self.speed(1))
            for item in indexDisplay:
                self.canvas.move(item, CELL_SIZE, 0)

            if not running:
                break

        return None

    def remove(self, val):
        index = self.find(val)
        if index != None:
            time.sleep(1)
            self.cleanUp()

            n = self.list[index]

            # Slide value rectangle up and off screen
            items = (n.display_shape, n.display_val)
            toPositions = [self.canvas.coords(i) for i in items]
            toPositions[0][1] = - CELL_SIZE
            toPositions[0][3] = 0
            toPositions[1][1] = - (CELL_SIZE // 2)
            self.moveItemsTo(items, toPositions, sleepTime=0.02)

            # Create an index for shifting the cells
            kIndex = self.createIndex(index, 'k')
            self.cleanup.extend(kIndex)
            
            # Slide values from right to left to fill gap
            for i in range(index+1, len(self.list)):
                self.assignElement(i, i-1)
                self.moveItemsBy(kIndex, (CELL_SIZE, 0), sleepTime=0.01)

            self.removeFromEnd()
            return True
        return False

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        findButton = self.addOperation(
            "Find", lambda: self.clickFind(), hasArgument=True,
            validationCmd=vcmd)
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), hasArgument=True,
            validationCmd=vcmd)
        deleteValueButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), hasArgument=True,
            validationCmd=vcmd)
        deleteRightmostButton = self.addOperation(
            "Delete Rightmost", lambda: self.removeFromEnd())
        return [findButton, insertButton, deleteValueButton,
                deleteRightmostButton]

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
            if len(array.list) >= array.size:
                self.setMessage("Error! Array is already full.")
            else:
                array.insert(val)
                self.setMessage("Value {} inserted".format(val))
        self.clearArgument()

    def clickDelete(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            result = array.remove(val)
            if result:
                msg = "Value {} deleted!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()

if __name__ == '__main__':
    random.seed(3.14159)    # Use fixed seed for testing consistency
    array = Array()

    array.runVisualization()

'''
To Do:
- make it look pretty
- animate insert
'''
