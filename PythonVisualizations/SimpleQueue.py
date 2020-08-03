from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

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
            size=MAX_CELLS,    # with a max number of cells
            title="Queue",
            **kwargs):
        super().__init__(title=title, **kwargs)
        self.list = [None]*size
        self.size = size
        self.nItems = 0
        self.front = 1  # when Queue is empty, front is one more than rear
        self.rear = 0
        if center is None:
            center = divide_vector(self.widgetDimensions(self.canvas), 2)
        self.X0, self.Y0 = int(center[0]), int(center[1])
        minDimension = min(self.X0, self.Y0)
        self.innerRadius = (innerRadius * minDimension if innerRadius <= 1 else
                            innerRadus)
        self.outerRadius = (outerRadius * minDimension if outerRadius <= 1 else
                            outerRadus)
        self.makeButtons()
        self.display()

    def __str__(self):
        return str(self.list)    
    # ANIMATION METHODS
    def createIndex(  # Create an arrow to point at a particuar cell
            self,     # cell with an optional name label
            index=-1,
            name=None,
            level=1): # Level controls arrow length to avoid overlapping labels
        arrow_coords = self.arrowCoords(index, level)
        arrow = self.canvas.create_line(
            *arrow_coords, arrow="last", fill=self.VARIABLE_COLOR)
        if name:
            label = self.canvas.create_text(
                arrow_coords[0], arrow_coords[1], text=name, anchor=SW,
                font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        return (arrow, label) if name else (arrow,)

    # Arrow endpoint coordinates to point at cell
    def arrowCoords(self, cellIndex, level=1):
        cell_coords = self.cellCoords(cellIndex)
        cell_center = self.cellCenter(cellIndex)
        sign = 1 if level > 0 else -1
        x0 = cell_center[0]
        y = cell_coords[1 if level > 0 else 3]
        y0 = y - sign * self.CELL_SIZE * 3 / 4 - self.VARIABLE_FONT[1] * level
        y1 = y - sign * self.CELL_SIZE * 1 // 4
        return (x0, y0, x0, y1)

    def moveIndexTo(
            self, indexItems, cellIndex, level, steps=10, sleepTime=0.02):
        '''Move an index arrow and optional label to the point at the cell
        indexed by cellIndex from its current position'''
        newArrowCoords = self.arrowCoords(cellIndex, level)
        self.moveItemsTo(indexItems, [newArrowCoords, newArrowCoords[:2]],
                         steps=steps, sleepTime=sleepTime)

    def newCellValue(self, indexOrCoords, value, color=None):
        if isinstance(indexOrCoords, int):
            indexOrCoords = self.cellCoords(indexOrCoords)
        if color is None:
            color = drawable.palette[self.nextColor]
            # increment nextColor
            self.nextColor = (self.nextColor + 1) % len(drawable.palette)
        
        center = ((indexOrCoords[0] + indexOrCoords[2]) / 2,
                  (indexOrCoords[1] + indexOrCoords[3]) / 2)
        return (self.canvas.create_rectangle(
            *indexOrCoords, fill=color, outline=''),
                self.canvas.create_text(
                    *center, text=value, font=self.VALUE_FONT,
                    fill=self.VALUE_COLOR))
            
    # insert item at rear of queue   
    def insertRear(self, val):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        # increment rear
        self.rear += 1
        # deal with wraparound
        self.rear %= self.size
        self.moveIndexTo(self.rearArrow, self.rear, self.rearLevel)

        # create new cell and cell value display objects
        # Start drawing new one at rear
        cellValue = self.newCellValue(self.rear, val)

       # insert the item
        self.list[self.rear] = drawable(val, 'color?', *cellValue)
        #increment number of items
        self.updateNItems(self.nItems + 1)

        # update window
        self.cleanUp(callEnviron)

    # remove the left element of the queue, or None if empty
    def removeFront(self):
        # if the queue is empty, exit
        if self.nItems == 0:
            self.setMessage('Queue is empty!')
            return None
        
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        #get the value at front
        n = self.list[self.front]

        # set front value to None so it will be garbage collected
        self.list[self.front] = None
        # delete the associated display objects
        self.canvas.delete(n.display_shape)
        self.canvas.delete(n.display_val)
        
        #increment front
        self.front += 1
        self.front %= self.size
        
        #move arrow
        self.moveIndexTo(self.frontArrow, self.front, self.frontLevel)

        # decrement number of items
        self.updateNItems(self.nItems - 1)

        self.cleanUp(callEnviron)

    def display(self):
        self.canvas.delete("all")

        self.nItemsDisplay = self.canvas.create_text(
            self.X0 - self.outerRadius, self.Y0 - self.outerRadius,
            text='nItems: {}'.format(self.nItems), anchor=NW,
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)

        self.rearLevel = 1
        self.rearArrow = self.createIndex(
            self.rear, "rear", level=self.rearLevel)
        self.frontLevel = 2
        self.frontArrow = self.createIndex(
            self.front, "front", level=self.frontLevel)

    def updateNItems(self, newNItems):
        self.nItems = newNItems
        self.canvas.itemconfigure(
            self.nItemsDisplay, text='nItems: {}'.format(self.nItems))

    #disable insert if queue if full, disable delete if empty
    #enable everything else without overriding queue/deque functionality
    def onOffButtons(self):

        #disable buttons as necessary
        if self.nItems == self.size:
            self.insertButton.config(state = DISABLED)
        elif self.nItems==0:
            self.deleteButton.config(state = DISABLED)


# Button functions
    def clickNew(self):
        entered_text = self.getArgument()
        if not (entered_text.isdigit() and 1 < int(entered_text) and
                int(entered_text) <= self.MAX_CELLS):
            self.setMessage('New queue must have 2 - {} cells'.format(
                self.MAX_CELLS))
            return
        self.size = int(entered_text)
        self.list = [None] * self.size
        self.front = 1
        self.rear = 0
        self.nItems = 0
        self.display()
        
    def clickInsertRear(self):
        entered_text = self.getArgument()
        if self.nItems == self.size:
            self.setMessage('Queue is full!')
            self.clearArgument()
        elif entered_text:
            val = int(entered_text)
            if val < 100:
                # if is full does not insert

                self.insertRear(int(entered_text))

            else:
                self.setMessage("Input value must be an integer from 0 to 99.")
            self.clearArgument()
                
    def close_window(self):
        self.window.destroy()
        self.exit()

    def startAnimations(self):
        self.onOffButtons()
        super().startAnimations()


    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        return (self.ARRAY_X0 + self.CELL_SIZE * cell_index, self.ARRAY_Y0,  # at index
                self.ARRAY_X0 + self.CELL_SIZE * (cell_index + 1) - self.CELL_BORDER,
                self.ARRAY_Y0 + self.CELL_SIZE - self.CELL_BORDER)

    def cellCenter(self, index):  # Center point for array cell at index
        half_cell = (self.CELL_SIZE - self.CELL_BORDER) // 2
        return add_vector(self.cellCoords(index), (half_cell, half_cell))

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.insertButton = self.addOperation(
            "New", lambda: self.clickNew(), numArguments=1, validationCmd=vcmd)

        self.insertButton = self.addOperation(
            "Insert", lambda: self.clickInsertRear(), numArguments=1,
            validationCmd=vcmd)

        self.deleteButton = self.addOperation("Delete", lambda: self.removeFront())
        self.addAnimationButtons()

    def createArrayCell(self, index):  # Create a box representing an array cell
        cell_coords = self.cellCoords(index)
        half_border = self.CELL_BORDER // 2
        rect = self.canvas.create_rectangle(
            *add_vector(cell_coords,
                        (-half_border, -half_border,
                         self.CELL_BORDER - half_border, self.CELL_BORDER - half_border)),
            fill=None, outline=self.CELL_BORDER_COLOR, width=self.CELL_BORDER)
        self.canvas.lower(rect)
        return rect

    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        self.onOffButtons()       # disable buttons as necessary

# validate text entry
def validate(action, index, value_if_allowed,
             prior_value, text, validation_type, trigger_type, widget_name):
    if text in '0123456789':
        return True
    else:
        return False

if __name__ == '__main__':
    queue = Queue()

    queue.runVisualization()
