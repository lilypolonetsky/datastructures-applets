import random
import time
from tkinter import *
# ASK Giving an error, no recordclass module
from recordclass import recordclass 

# clarify generally - are we adding buttons to her's, 
# or creating an entirely new visualization

WIDTH = 800
HEIGHT = 400

CELL_SIZE = 50
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

# ASK: What is this doing?
    def assignToTemp(self, index, varName="temp"):

        y0 = canvas.coords(self.list[index].display_shape)[1]

        posCell = canvas.coords(self.list[index].display_shape)
        posCellVal = canvas.coords(self.list[index].display_val)

        yspeed = -5
        shape = canvas.create_rectangle(posCell[0], posCell[1], posCell[2], posCell[3], fill=self.list[index][1])
        val = canvas.create_text(posCellVal[0], posCellVal[1], text=str(self.list[index][0]),
                                 font=('Helvetica', '20'))

        while canvas.coords(shape)[1] > (y0 - CELL_SIZE - 15):
            canvas.move(shape, 0, yspeed)
            canvas.move(val, 0, yspeed)
            window.update()
            time.sleep(self.speed(0.01))

        text = canvas.create_text(posCell[0] + (CELL_SIZE / 2), y0 - CELL_SIZE - 30, text=varName,
                                  font=('Helvetica', '20'))
        temp = Array.Element(self.list[index][0], self.list[index][1], shape, val)

        window.update()
        return temp, text

# ASK - follows from above method (probably?)
    def assignFromTemp(self, index, temp, text):

        y0 = canvas.coords(self.list[index].display_shape)[1]

        posCell = canvas.coords(self.list[index].display_shape)
        posCellVal = canvas.coords(self.list[index].display_val)

        xspeed = 5
        moveRight = True
        if canvas.coords(temp.display_shape)[0] > posCell[0]:
            xspeed = -xspeed
            moveRight = False

        while (moveRight and canvas.coords(temp.display_shape)[0] < posCell[0]) or \
                (not moveRight and canvas.coords(temp.display_shape)[0] > posCell[0]):
            canvas.move(temp.display_shape, xspeed, 0)
            canvas.move(temp.display_val, xspeed, 0)
            canvas.move(text, xspeed, 0)
            window.update()
            time.sleep(self.speed(0.01))

        time.sleep(0.1)

        yspeed = 5
        while canvas.coords(temp.display_shape)[1] < y0:
            canvas.move(temp.display_shape, 0, yspeed)
            canvas.move(temp.display_val, 0, yspeed)
            window.update()
            time.sleep(self.speed(0.01))

        time.sleep(self.speed(0.1))
        canvas.delete(text)
        canvas.delete(self.list[index].display_shape)
        canvas.delete(self.list[index].display_val)
        self.list[index] = temp

# ASK: Is this already a type of sort?
#      We're not going to need this, right?
    def swap(self, a, b, aCellObjects = [], bCellObjects = []):
        y0 = canvas.coords(self.list[a].display_shape)[1]
        if a == b:
            yspeed = -5
            shapeA = self.list[a].display_shape
            while canvas.coords(shapeA)[1] != (y0 - CELL_SIZE - 15):
                canvas.move(shapeA, 0, yspeed)
                canvas.move(self.list[a].display_val, 0, yspeed)
                for o in (aCellObjects + bCellObjects):
                    canvas.move(o, 0, yspeed)
                window.update()
                time.sleep(self.speed(0.01))

            time.sleep(self.speed(0.1))

            while canvas.coords(shapeA)[1] != y0:
                canvas.move(shapeA, 0, -yspeed)
                canvas.move(self.list[a].display_val, 0, -yspeed)
                for o in (aCellObjects + bCellObjects):
                    canvas.move(o, 0, -yspeed)
                window.update()
                time.sleep(self.speed(0.01))

            return

        # save original coordinates of b cell
        posCellB = canvas.coords(self.list[b].display_shape)

        # move a and b cells up
        yspeed = -5
        shapeA = self.list[a].display_shape
        while canvas.coords(shapeA)[1] != (y0 - CELL_SIZE - 15):
            canvas.move(shapeA, 0, yspeed)
            canvas.move(self.list[a].display_val, 0, yspeed)
            canvas.move(self.list[b].display_shape, 0, yspeed)
            canvas.move(self.list[b].display_val, 0, yspeed)
            for o in (aCellObjects + bCellObjects):
                canvas.move(o, 0, yspeed)
            window.update()
            time.sleep(self.speed(0.01))

        time.sleep(self.speed(0.1))

        # make a and b cells switch places
        xspeed = 5
        if b < a:
            xspeed = -xspeed

        # move the cells until the a cell is above the original position of the b cell
        while (a < b and canvas.coords(shapeA)[0] < posCellB[0]) or \
                (a > b and canvas.coords(shapeA)[0] > posCellB[0]):
            canvas.move(shapeA, xspeed, 0)
            canvas.move(self.list[a].display_val, xspeed, 0)
            for o in aCellObjects:
                canvas.move(o, xspeed, 0)

            canvas.move(self.list[b].display_shape, -xspeed, 0)
            canvas.move(self.list[b].display_val, -xspeed, 0)
            for o in bCellObjects:
                canvas.move(o, -xspeed, 0)

            window.update()
            time.sleep(self.speed(0.01))

        time.sleep(self.speed(0.1))

        # move the cells back down into the list
        while canvas.coords(shapeA)[1] != y0:
            canvas.move(shapeA, 0, -yspeed)
            canvas.move(self.list[a].display_val, 0, -yspeed)
            canvas.move(self.list[b].display_shape, 0, -yspeed)
            canvas.move(self.list[b].display_val, 0, -yspeed)
            for o in (aCellObjects + bCellObjects):
                canvas.move(o, 0, -yspeed)
            window.update()
            time.sleep(self.speed(0.01))

        # perform the actual swap operation in the list
        self.list[a], self.list[b] = self.list[b], self.list[a]

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

# ASK: What is it? Do we need this if we're not swapping?
    def placeHolderArray(self):
        for cur in self.list:
            posCell = canvas.coords(cur.display_shape)
            posCellVal = canvas.coords(cur.display_val)

            # create new display objects that are copies of the cell
            canvas.create_rectangle(posCell[0], posCell[1], posCell[2], posCell[3],
                                               fill=cur[1])
            canvas.create_text(posCellVal[0], posCellVal[1], text=cur[0],
                                        font=('Helvetica', '20'))

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

    def append(self, val):
        # create new cell and cell value display objects
        cell = canvas.create_rectangle(ARRAY_X0+CELL_SIZE*len(self.list), ARRAY_Y0, ARRAY_X0+CELL_SIZE*(len(self.list)+1), ARRAY_Y0 + CELL_SIZE, fill=Array.colors[Array.nextColor])
        cell_val = canvas.create_text(ARRAY_X0+CELL_SIZE*len(self.list) + (CELL_SIZE / 2), ARRAY_Y0 + (CELL_SIZE / 2), text=val,
                                      font=('Helvetica', '20'))

        # add a new Element to the list with the new value, color, and display objects
        self.list.append(Array.Element(val, Array.colors[Array.nextColor], cell, cell_val))

        # increment nextColor
        Array.nextColor = (Array.nextColor + 1) % len(Array.colors)

        # update window
        window.update()

# ASK: Is this exactly the same as our pop? Do we have a built-in push?
#      do we want to animate it differently?

    def removeFromEnd(self):
        # pop an Element from the list
        n = self.list.pop()

        # delete the associated display objects
        canvas.delete(n.display_shape)
        canvas.delete(n.display_val)

        # update window
        window.update()

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

# ASK: Clarify functionality?

    def find(self, val):
        global cleanup, running
        running = True
        findDisplayObjects = []
        #canvas.delete(findDisplayObjects)
        self.display()

        # draw an arrow over the first cell
        x = ARRAY_X0 + (CELL_SIZE/2)
        y0 = ARRAY_Y0 - 40
        y1 = ARRAY_Y0 - 15
        arrow = canvas.create_line(x, y0, x, y1, arrow="last", fill='red')
        findDisplayObjects.append(arrow)

        # go through each Element in the list
        for n in self.list:
            window.update()

            # if the value is found
            if n.val == val:
                # get the position of the displayed cell and val
                #posCell = canvas.coords(n.display_shape)
                posVal = canvas.coords(n.display_val)

                # cover the current display value with the updated value in green
                #cell_shape = canvas.create_rectangle(posCell[0], posCell[1], posCell[2], posCell[3], fill=n[1])
                cell_val = canvas.create_text(posVal[0], posVal[1], text=str(val), font=('Helvetica', '25'), fill='green2')

                # add the green value to findDisplayObjects for cleanup later
                #findDisplayObjects.append(cell_shape)
                findDisplayObjects.append(cell_val)

                # update the display
                window.update()

                cleanup += findDisplayObjects
                #canvas.after(1000, canvas.delete, arrow)
                #canvas.after(1000, canvas.delete, cell_val)
                return True

            # if the value hasn't been found, wait 1 second, and then move the arrow over one cell
            time.sleep(self.speed(1))
            canvas.move(arrow, CELL_SIZE, 0)

            if not running:
                break

        cleanup += findDisplayObjects
        #canvas.after(1000, canvas.delete, arrow)
        return False

    def remove(self, index):
        n = self.list.pop(3)
        canvas.delete(n.display_shape)
        canvas.delete(n.display_val)
        window.update()

# ASK: Is this relevant to us?
    def shuffle(self):
        global running
        running = True

        maxHeight = HEIGHT - 5
        maxWidth = WIDTH -5
        y = ARRAY_Y0
        for i in range(len(self.list)):
            newX = random.randint(0, len(self.list)-1)
            self.list[i], self.list[newX] = self.list[newX], self.list[i]
            finalX = ARRAY_X0 + (CELL_SIZE * newX)

        times = 0

        # while all of the elements have not yet been returned to the original position
        while times < len(self.list)*2 and running:
            for i in range(len(self.list)):
                time.sleep(self.speed(0.01))
                shuffleY = random.randint(-30, 30)
                shuffleX = random.randint(-30, 30)


                # not go off the sides
                if canvas.coords(self.list[i].display_shape)[0] + shuffleX <= 0 or canvas.coords(self.list[i].display_shape)[0] + shuffleX >= maxWidth:
                    shuffleX = -shuffleX * 2
                if canvas.coords(self.list[i].display_shape)[1] + shuffleY <= ARRAY_Y0 or canvas.coords(self.list[i].display_shape)[1] + shuffleY >= maxHeight:
                    shuffleY = -shuffleY * 2
                canvas.move(self.list[i].display_shape, shuffleX, shuffleY)
                canvas.move(self.list[i].display_val, shuffleX, shuffleY)
            times += 1
            time.sleep(self.speed(0.01))
            window.update()

        self.stopMergeSort()

# COMMENTED OUT ILANA'S SORTS THAT WERE HERE

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
        result = array.find(int(entered_text))
        if result:
            txt = "Found!"
        else:
            txt = "Value not found"
        outputText.set(txt)

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
array = Array()
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
