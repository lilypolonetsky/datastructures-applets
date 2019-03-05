import random
import time
from tkinter import *
from recordclass import recordclass

WIDTH = 800
HEIGHT = 400

CELL_SIZE = 50
CELL_BORDER = 2
ARRAY_X0 = 100
ARRAY_Y0 = 100
OPERATIONS_BG = 'beige'
OPERATIONS_BORDER = 'black'
FONT_SIZE = '20'
VALUE_FONT = ('Helvetica', FONT_SIZE)
VALUE_COLOR = 'black'
FOUND_FONT = ('Helvetica', FONT_SIZE)
FOUND_COLOR = 'green2'
CONTROLS_FONT = ('none', '14')

def add_vector(v1, v2):
    return tuple(map(lambda x, y: x + y, v1, v2))

class Array(object):
    Element = recordclass('Element', ['val', 'color', 'display_shape', 'display_val'])
    Element.__new__.__defaults__ = (None,) * len(Element._fields)

    colors = ['red', 'green', 'blue', 'orange', 'yellow', 'cyan', 'magenta',
              'dodgerblue', 'turquoise', 'grey', 'gold', 'pink']
    nextColor = 0

    def __init__(self, size=10):
        self.list = []
        self.size = size

    def __str__(self):
        return str(self.list)

    # ANIMATION METHODS
    def speed(self, sleepTime):
        return (sleepTime * (scaleDefault + 50)) / (scale.get() + 50)

    # ARRAY FUNCTIONALITY
    def isSorted(self):
        for i in range(1, len(self.list)):
            if self.list[i] < self.list[i-1]:
                return False
        return True

    def get(self, index):
        try:
            return self.list[index][0]
        except:
            print("Invalid list index")
            return -1

    def set(self, index, val):
        # reset the value of the Element at that index to val
        self.list[index].val = val

        # get the position of the displayed value
        pos = canvas.coords(self.list[index].display_val)

        # delete the displayed value and replace it with the updated value
        canvas.delete(self.list[index].display_val)
        self.list[index].display_val = canvas.create_text(pos[0], pos[1], text=str(val), font=VALUE_FONT, fill=VALUE_COLOR)

        # update window
        window.update()

    def append(self, val):
        # create new cell and cell value display objects
        cell = canvas.create_rectangle(*self.cellCoords(len(self.list)), fill=Array.colors[Array.nextColor], outline='')
        cell_val = canvas.create_text(*self.cellCenter(len(self.list)), text=val, font=VALUE_FONT, fill=VALUE_COLOR)

        # add a new Element to the list with the new value, color, and display objects
        self.list.append(Array.Element(val, Array.colors[Array.nextColor], cell, cell_val))

        # increment nextColor
        Array.nextColor = (Array.nextColor + 1) % len(Array.colors)

        # update window
        window.update()

    def removeFromEnd(self):
        # pop an Element from the list
        n = self.list.pop()

        # delete the associated display objects
        canvas.delete(n.display_shape)
        canvas.delete(n.display_val)

        # update window
        window.update()

    def assignElement(self, fromIndex, toIndex):

        # get position of "to" cell
        posToCell = canvas.coords(self.list[toIndex].display_shape)

        # get position of "from" cell and value
        posFromCell = canvas.coords(self.list[fromIndex].display_shape)
        posFromCellVal = canvas.coords(self.list[fromIndex].display_val)

        # create new display objects that are copies of the "from" cell and value
        newCellShape = canvas.create_rectangle(*posFromCell, fill=self.list[fromIndex][1], outline='')
        newCellVal = canvas.create_text(*posFromCellVal, text=self.list[fromIndex][0],
                                        font=VALUE_FONT, fill=VALUE_COLOR)

        # set xspeed to move in the correct direction
        xspeed = 1
        if fromIndex > toIndex:
            xspeed = -xspeed
        distance = abs(int(posToCell[0] - posFromCell[0]))

        # move the new display objects until they are in the position of the "to" cell
        for i in range(distance):
            canvas.move(newCellShape, xspeed, 0)
            canvas.move(newCellVal, xspeed, 0)
            window.update()
            time.sleep(self.speed(0.01))

        # delete the original "to" display value and the new display shape
        canvas.delete(self.list[toIndex].display_val)
        canvas.delete(self.list[toIndex].display_shape)

        # update value and display value in "to" position in the list
        self.list[toIndex].display_val = newCellVal
        self.list[toIndex].val = self.list[fromIndex].val
        self.list[toIndex].display_shape = newCellShape
        self.list[toIndex].color = self.list[fromIndex].color

        # update the window
        window.update()

    def cellCoords(self, cell_index):          # Get bounding rectangle for colored cell at a particular index
        return (ARRAY_X0 + CELL_SIZE * cell_index, ARRAY_Y0,
                ARRAY_X0 + CELL_SIZE * (cell_index + 1) - CELL_BORDER, ARRAY_Y0 + CELL_SIZE - CELL_BORDER)

    def cellCenter(self, cell_index):          # Get center point for colored cell at a particular index
        half_cell = (CELL_SIZE - CELL_BORDER) // 2
        return add_vector(self.cellCoords(cell_index), (half_cell, half_cell))

    def display(self):
        canvas.delete("all")

        # print(self.size)
        for i in range(self.size):  # Draw grid of cells
            cell_coords = self.cellCoords(i)
            half_border = CELL_BORDER // 2
            canvas.create_rectangle(*add_vector(cell_coords, 
                                                (-half_border, -half_border,
                                                 CELL_BORDER - half_border, CELL_BORDER - half_border)),
                                    fill='white', outline='black', width=CELL_BORDER)

        # go through each Element in the list
        for i, n in enumerate(self.list):
            # print(n)
            # create display objects for the associated Elements
            cell = canvas.create_rectangle(*self.cellCoords(i), fill=n[1], outline='', width=0)
            cell_val = canvas.create_text(*self.cellCenter(i), text=n[0], font=VALUE_FONT, fill=VALUE_COLOR)

            # save the display objects to the appropriate attributes of the Element object
            n.display_shape = cell
            n.display_val = cell_val

        window.update()

    def find(self, val):
        global cleanup, running
        running = True
        findDisplayObjects = []
        #canvas.delete(findDisplayObjects)
        #self.display()

        # draw an arrow over the first cell
        cell_coords = self.cellCoords(0)
        cell_center = self.cellCenter(0)
        x = cell_center[0]
        y0 = cell_coords[1] - 40
        y1 = cell_coords[1] - 15
        arrow = canvas.create_line(x, y0, x, y1, arrow="last", fill='red')
        findDisplayObjects.append(arrow)

        # go through each Element in the list
        for i in range(len(self.list)):
            window.update()

            n = self.list[i]

            # if the value is found
            if n.val == val:
                # get the position of the displayed cell and val
                #posCell = canvas.coords(n.display_shape)
                posVal = canvas.coords(n.display_val)

                # cover the current display value with the updated value in green
                #cell_shape = canvas.create_rectangle(posCell[0], posCell[1], posCell[2], posCell[3], fill=n[1])
                cell_val = canvas.create_text(*posVal, text=str(val), font=FOUND_FONT, fill=FOUND_COLOR)

                # add the green value to findDisplayObjects for cleanup later
                #findDisplayObjects.append(cell_shape)
                findDisplayObjects.append(cell_val)

                # update the display
                window.update()

                cleanup += findDisplayObjects
                #canvas.after(1000, canvas.delete, arrow)
                #canvas.after(1000, canvas.delete, cell_val)
                return i

            # if the value hasn't been found, wait 1 second, and then move the arrow over one cell
            time.sleep(self.speed(1))
            canvas.move(arrow, CELL_SIZE, 0)

            if not running:
                break

        cleanup += findDisplayObjects
        #canvas.after(1000, canvas.delete, arrow)
        return None

    def remove(self, val):
        index = self.find(val)
        if index != None:
            time.sleep(1)
            cleanUp()

            n = self.list[index]

            # Slide value rectangle up and off screen
            while canvas.coords(n.display_shape)[3] > 0:
                canvas.move(n.display_shape, 0, -1)
                canvas.move(n.display_val, 0, -1)
                window.update()
                time.sleep(self.speed(0.01))

            #canvas.delete(n.display_shape)
            #canvas.delete(n.display_val)
            window.update()

            # Slide values from right to left to fill gap
            for i in range(index+1, len(self.list)):
                self.assignElement(i, i-1)

            self.removeFromEnd()
            return True
        return False

def stop(pauseButton): # will stop after the current shuffle is done
    global running
    running = False

    if waitVar.get():
        play(pauseButton)

def pause(pauseButton):
    global waitVar
    waitVar.set(True)

    pauseButton['text'] = "Play"
    pauseButton['command'] = lambda: onClick(play, pauseButton)

    canvas.wait_variable(waitVar)

def play(pauseButton):
    global waitVar
    waitVar.set(False)

    pauseButton['text'] = 'Pause'
    pauseButton['command'] = lambda: onClick(pause, pauseButton)

def onClick(command, parameter = None):
    cleanUp()
    disableButtons()
    if parameter:
        command(parameter)
    else:
        command()
    if command not in [pause, play]:
        enableButtons()

def cleanUp():
    global cleanup
    if len(cleanup) > 0:
        for o in cleanup:
            canvas.delete(o)
    outputText.set('')
    window.update()

# Button functions
def clickFind():
    entered_text = textBox.get()
    txt = ''
    if entered_text:
        if int(entered_text) < 100:
            result = array.find(int(entered_text))
            if result != None:
                txt = "Found!"
            else:
                txt = "Value not found"
            outputText.set(txt)
        else:
            outputText.set("Input value must be an integer from 0 to 99.")
            textBox.delete(0, END )

def clickInsert():
    entered_text = textBox.get()
    if entered_text:
        val = int(entered_text)
        if val < 100:
            array.append(int(entered_text))
        else:
            outputText.set("Input value must be an integer from 0 to 99.")
        textBox.delete(0, END )

def clickDelete():
    entered_text = textBox.get()
    txt = ''
    if entered_text:
        if int(entered_text) < 100:
            result = array.remove(int(entered_text))
            if result:
                txt = "Value deleted!"
            else:
                txt = "Value not found"
            outputText.set(txt)
        else:
            outputText.set("Input value must be an integer from 0 to 99.")
            textBox.delete(0, END )
def close_window():
    window.destroy()
    exit()

def disableButtons():
    for button in buttons:
        button.config(state = DISABLED)

def enableButtons():
    for button in buttons:
        button.config(state = NORMAL)

def makeButtons():
    findButton = Button(operations, text="Find", command= lambda: onClick(clickFind))
    findButton.grid(row=1, column=0, padx=8, sticky=(E, W))
    insertButton = Button(operations, text="Insert", command= lambda: onClick(clickInsert))
    insertButton.grid(row=2, column=0, padx=8, sticky=(E, W))
    deleteValueButton = Button(operations, text="Delete", command= lambda: onClick(clickDelete))
    deleteValueButton.grid(row=3, column=0, padx=8, sticky=(E, W))
    separator = Frame(operations, width=2, bg=OPERATIONS_BORDER)
    separator.grid(row=1, column=3, rowspan=3, sticky=(N, E, W, S))
    deleteRightmostButton = Button(operations, text="Delete Rightmost",
                                   command= lambda: onClick(array.removeFromEnd))
    deleteRightmostButton.grid(row=1, column=4, rowspan=3, padx=8)
    buttons = [findButton, insertButton, deleteValueButton, deleteRightmostButton]
    return buttons

# validate text entry
def validate(action, index, value_if_allowed,
             prior_value, text, validation_type, trigger_type, widget_name):
    if text in '0123456789':
        return True
    else:
        return False

window = Tk()
frame = Frame(window)
frame.pack()

waitVar = BooleanVar()

canvas = Canvas(frame, width=WIDTH, height=HEIGHT)
window.title("Array")
canvas.pack()

bottomframe = Frame(window)
bottomframe.pack(side=BOTTOM)
operationsUpper = LabelFrame(bottomframe, text="Operations")
operationsUpper.pack(side=TOP)
operationsBorder = Frame(operationsUpper, padx=2, pady=2, bg=OPERATIONS_BORDER)
operationsBorder.pack(side=TOP)
operations = Frame(operationsBorder, bg=OPERATIONS_BG)
operations.pack(side=LEFT)
operationsLower = Frame(bottomframe)
operationsLower.pack(side=BOTTOM)

#Label(bottomframe, text="Find:", font=CONTROLS_FONT + ('bold',)).grid(row=0, column=0, sticky=W)
vcmd = (window.register(validate),
        '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
textBox = Entry(operations, width=20, bg="white", validate='key', validatecommand=vcmd)
textBox.grid(row=2, column=2, padx=8, sticky=E)
scaleDefault = 100
scale = Scale(operationsLower, from_=1, to=200, orient=HORIZONTAL, sliderlength=15)
scale.grid(row=0, column=1, sticky=W)
scale.set(scaleDefault)
scaleLabel = Label(operationsLower, text="Speed:", font=CONTROLS_FONT)
scaleLabel.grid(row=0, column=0, sticky=W)

# add a submit button
#Button(bottomframe, text="Find", width=6, command=lambda: array.onClick(clickFind)).grid(row=0, column=2, sticky=W)
outputText = StringVar()
outputText.set('')
output = Label(operationsLower, textvariable=outputText, font=CONTROLS_FONT + ('italic',), fg="blue")
output.grid(row=0, column=3, sticky=(E, W))
operationsLower.grid_columnconfigure(3, minsize=160)

# exit button
Button(operationsLower, text="EXIT", width=0, command=close_window)\
    .grid(row=0, column=4, sticky=E)

cleanup = []
array = Array()
buttons = makeButtons()
array.display()

for i in range(9):
    array.append(i)

window.mainloop()

'''
To Do:
- make it look pretty
- animate insert
'''
