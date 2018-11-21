import random
import time
from tkinter import *
from recordclass import recordclass 

# creating entirely new visualization
# Rewrite??

WIDTH = 800
HEIGHT = 400

CELL_SIZE = 50 # comment
ARRAY_X0 = 100
ARRAY_Y0 = 100

class Stack(object):
    Element = recordclass('Element', ['val', 'color', 'display_shape', 'display_val'])
    Element.__new__.__defaults__ = (None,) * len(Element._fields)

    colors = ['red', 'green', 'blue', 'orange', 'yellow', 'cyan', 'magenta',
              'dodgerblue', 'turquoise', 'grey', 'gold', 'pink']
    nextColor = 0

    def __init__(self, size=0):
        self.list = [0]*size

    def __str__(self):
        return str(self.list)

    # ANIMATION METHODS
    # Will need to change motion to be vertical not
    # horizontal because we're 
    
    def speed(self, sleepTime):
        return (sleepTime * (scaleDefault + 50)) / (scale.get() + 50)

    def assignElement(self, fromIndex, toIndex):

        # get position of "to" cell
        posToCell = canvas.coords(self.list[toIndex].display_shape)

        # get position of "from" cell and value
        posFromCell = canvas.coords(self.list[fromIndex].display_shape)
        posFromCellVal = canvas.coords(self.list[fromIndex].display_val)

        # create new display objects that are copies of the "from" cell and value
        newCellShape = canvas.create_rectangle(posFromCell[0], posFromCell[1], posFromCell[2], posFromCell[3],
                                               fill=self.list[fromIndex][1])
        newCellVal = canvas.create_text(posFromCellVal[0], posFromCellVal[1], text=self.list[fromIndex][0],
                                        font=('Helvetica', '20'))

        # set xspeed to move in the correct direction
        xspeed = 5
        if fromIndex > toIndex:
            xspeed = -xspeed

        # move the new display objects until they are in the position of the "to" cell
        while (fromIndex < toIndex and canvas.coords(newCellShape) < posToCell) or \
                (fromIndex > toIndex and canvas.coords(newCellShape) > posToCell):
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

# CHANGE FOR VERTICAL - but not reassigning -- may need something different
    def moveUp(self, dy, toX, toY, curDisplayShape, curDisplayVal):
        global running

        if not running:
            return

        # given a toX, toY, and dy, calculate the dx required to get
        # from the current position to the new position
        fromX = canvas.coords(curDisplayShape)[0]
        fromY = canvas.coords(curDisplayShape)[1]
        if toY < fromY:
            dx = dy * (toX - fromX) / (toY - fromY)

        # while the cell has not yet reached the new y position,
        # move it up using dx and dy
        while canvas.coords(curDisplayShape)[1] > toY:
            canvas.move(curDisplayShape, dx, dy)
            canvas.move(curDisplayVal, dx, dy)
            window.update()
            time.sleep(self.speed(0.01))

# ASK: Is this where we'd want to put our stack functionality?
# If so, do animations go here also, or are they called?

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
        self.list[index].display_val = canvas.create_text(pos[0], pos[1], text=str(val), font=('Helvetica', '20'))

        # update window
        window.update()

# Important: SHOW HOW TO CREATE NEW BLOCKS!
    def append(self, val):
        # create new cell and cell value display objects
        cell = canvas.create_rectangle(ARRAY_X0+CELL_SIZE*len(self.list), ARRAY_Y0, ARRAY_X0+CELL_SIZE*(len(self.list)+1), ARRAY_Y0 + CELL_SIZE, fill=Stack.colors[Stack.nextColor])
        cell_val = canvas.create_text(ARRAY_X0+CELL_SIZE*len(self.list) + (CELL_SIZE / 2), ARRAY_Y0 + (CELL_SIZE / 2), text=val,
                                      font=('Helvetica', '20'))

        # add a new Element to the list with the new value, color, and display objects
        self.list.append(Stack.Element(val, Stack.colors[Stack.nextColor], cell, cell_val))

        # increment nextColor
        Stack.nextColor = (Stack.nextColor + 1) % len(Stack.colors)

        # update window
        window.update()

# Animate differently
    def pop(self):
        # pop an Element from the list
        n = self.list.pop()

        # delete the associated display objects
        canvas.delete(n.display_shape)
        canvas.delete(n.display_val)

        # update window
        window.update()
        
    def push(self):
        # Fill in our push code here. 
        window.update()

# Will be close, but not exactly, 
# modify to display vertically. 
    def display(self):
        canvas.delete("all")
        xpos = ARRAY_X0
        ypos = ARRAY_Y0

        # go through each Element in the list
        for n in self.list:
            print(n)
            # create display objects for the associated Elements
            cell = canvas.create_rectangle(xpos, ypos, xpos+CELL_SIZE, ypos+CELL_SIZE, fill=n[1])
            cell_val = canvas.create_text(xpos+(CELL_SIZE/2), ypos+(CELL_SIZE/2), text=n[0], font=('Helvetica', '20'))

            # save the display objects to the appropriate attributes of the Element object
            n.display_shape = cell
            n.display_val = cell_val

            # increment xpos
            xpos += CELL_SIZE

        window.update()

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
def clickInsert():
    entered_text = textBox.get()
    if entered_text:
        array.append(int(entered_text))
        textBox.setvar('')

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
    # REPLACE WITH A PUSH AND A POP BUTTON, 
    # DON'T NEED ALL THESE SORTS
    bubbleSortButton = Button(bottomframe, text="Bubble Sort", width=11, command= lambda: onClick(array.bubbleSort))
    bubbleSortButton.grid(row=0, column=0)
    selectionSortButton = Button(bottomframe, text="Selection Sort", width=14, command= lambda: onClick(array.selectionSort))
    selectionSortButton.grid(row=0, column=1)
    insertionSortButton = Button(bottomframe, text="Insertion Sort", width=14, command= lambda: onClick(array.insertionSort))
    insertionSortButton.grid(row=0, column=2)
    bogoSortButton = Button(bottomframe, text="Bogo Sort", width=9, command= lambda: onClick(array.bogoSort))
    bogoSortButton.grid(row=0, column=3)
    mergeSortButton = Button(bottomframe, text="Merge Sort", width=9, command= lambda: onClick(array.mergeSort))
    mergeSortButton.grid(row=1, column=0)
    quickSortButton = Button(bottomframe, text="Quick Sort", width=9, command= lambda: onClick(array.quickSort))
    quickSortButton.grid(row=1, column=1)
    radixSortButton = Button(bottomframe, text="Radix Sort", width=9, command= lambda: onClick(array.radixSort))
    radixSortButton.grid(row=1, column=2)
    shuffleButton = Button(bottomframe, text="Shuffle", width=7, command= lambda: onClick(array.shuffle))
    shuffleButton.grid(row=1, column=3)
    pauseButton = Button(bottomframe, text="Pause", width=8, command = lambda: onClick(pause, pauseButton))
    pauseButton.grid(row=2, column=0)
    stopButton = Button(bottomframe, text="Stop", width=7, command = lambda: onClick(stop, pauseButton))
    stopButton.grid(row=1, column=4)
    findButton = Button(bottomframe, text="Find", width=7, command= lambda: onClick(clickFind))
    findButton.grid(row=2, column=1)
    insertButton = Button(bottomframe, text="Insert", width=7, command= lambda: onClick(clickInsert))
    insertButton.grid(row=2, column=2)
    deleteButton = Button(bottomframe, text="Delete", width=7, command= lambda: onClick(array.removeFromEnd))
    deleteButton.grid(row=2, column=3)
    buttons = [bubbleSortButton, selectionSortButton, insertionSortButton, bogoSortButton, mergeSortButton,
               quickSortButton, radixSortButton, shuffleButton, findButton, insertButton, deleteButton]
    return buttons

window = Tk()
frame = Frame(window)
frame.pack()

waitVar = BooleanVar()

canvas = Canvas(frame, width=WIDTH, height=HEIGHT)
window.title("Array")
canvas.pack()

bottomframe = Frame(window)
bottomframe.pack(side=BOTTOM)

#Label(bottomframe, text="Find:", font="none 12 bold").grid(row=0, column=0, sticky=W)
textBox = Entry(bottomframe, width=20, bg="white")
textBox.grid(row=4, column=0, sticky=W)
scaleDefault = 100
scale = Scale(bottomframe, from_=1, to=200, orient=HORIZONTAL, sliderlength=15)
scale.grid(row=5, column=1, sticky=W)
scale.set(scaleDefault)
scaleLabel = Label(bottomframe, text="Speed:", font="none 10")
scaleLabel.grid(row=5, column=0, sticky=E)

# add a submit button
#Button(bottomframe, text="Find", width=6, command=lambda: array.onClick(clickFind)).grid(row=0, column=2, sticky=W)
outputText = StringVar()
outputText.set('')
output = Label(bottomframe, textvariable=outputText, font="none 12 bold")
output.grid(row=4, column=1, sticky=E)

# exit button
Button(bottomframe, text="EXIT", width=4, command=close_window).grid(row=6, column=3, sticky=W)

cleanup = []

# change to stack = Stack()
array = Stack()
buttons = makeButtons()
array.display()


for i in range(10):
    array.append(i)

window.mainloop()

'''
To Do:
- make it look pretty
- animate insert and delete
- delete/insert at index?
- label arrows for sorts (inner, outer, etc.)
- implement shell sort, radix sort, quick sort
'''
