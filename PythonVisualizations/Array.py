from tkinter import *
import time
import random
from recordclass import recordclass

WIDTH = 800
HEIGHT = 600

CELL_SIZE = 50
ARRAY_X0 = 100
ARRAY_Y0 = 100

window = Tk()
frame = Frame(window)
frame.pack()

canvas = Canvas(frame, width=WIDTH, height=HEIGHT)
window.title("Array")
canvas.pack()

global cleanup
cleanup = []


def clean():
    global cleanup
    if len(cleanup) > 0:
        for o in cleanup:
            canvas.delete(o)
        window.update()


# Button functions
# Call clean() as the first line of each button function!
def clickFind():
    clean()
    entered_text = textBox.get()
    txt = ''
    result = array.find(int(entered_text))
    if result:
        txt = "Found!"
    else:
        txt = "Value not found"
    outputText.set(txt)

def close_window():
    window.destroy()
    exit()


bottomframe = Frame(window)
bottomframe.pack(side=BOTTOM)

Label(bottomframe, text="Find:", font="none 12 bold").grid(row=0, column=0, sticky=W)
textBox = Entry(bottomframe, width=20, bg="white")
textBox.grid(row=0, column=1, sticky=W)

# add a submit button
Button(bottomframe, text="Enter", width=6, command=clickFind).grid(row=0, column=2, sticky=W)
outputText = StringVar()
outputText.set('')
output = Label(bottomframe, textvariable=outputText, font="none 12 bold")
output.grid(row=0, column=3, sticky=E)

# exit button
Button(bottomframe, text="EXIT", width=4, command=close_window).grid(row=2, column=0, sticky=W)


class Array(object):
    Element = recordclass('Element', ['val', 'color', 'display_shape', 'display_val'])
    Element.__new__.__defaults__ = (None,) * len(Element._fields)

    colors = ['red', 'green', 'blue', 'orange', 'yellow', 'cyan', 'magenta',
              'dodgerblue', 'turquoise', 'grey', 'gold', 'pink']
    nextColor = 0

    def __init__(self, size=0):
        self.list = [0]*size

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

    def find(self, val):
        global cleanup
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
                posCell = canvas.coords(n.display_shape)
                posVal = canvas.coords(n.display_val)

                # cover the current display value with the updated value in green
                cell_shape = canvas.create_rectangle(posCell[0], posCell[1], posCell[2], posCell[3], fill=n[1])
                cell_val = canvas.create_text(posVal[0], posVal[1], text=str(val), font=('Helvetica', '25'), fill='green2')

                # add the green value to findDisplayObjects for cleanup later
                findDisplayObjects.append(cell_shape)
                findDisplayObjects.append(cell_val)

                # update the display
                window.update()

                cleanup += findDisplayObjects
                return True

            # if the value hasn't been found, wait 1 second, and then move the arrow over one cell
            time.sleep(1)
            canvas.move(arrow, CELL_SIZE, 0)

        cleanup += findDisplayObjects
        return False

    def remove(self, index):
        self.list.pop(3)
        self.display()

    def shuffle(self):
        global running
        running = True
        #random.shuffle(self.list)
        #self.display()
        for i in range(10):
            self.swap(random.randrange(0, len(self.list)), random.randrange(0, len(self.list)))
            if not running:
                break

    def insertElement(self, val):
        '''
        if index < len(self.list) - 1:
            xspeed = -5
            nextShape = self.list[index+1].display_shape
            while canvas.coords(nextShape) != cell_pos[0]:
                for i in range(index+1, len(self.list)):
                    canvas.move(self.list[i].display_shape, xspeed, 0)
                    canvas.move(self.list[i].display_val, xspeed, 0)
                window.update()
                time.sleep(0.01)
        '''
        pass

    def split(self):
        pass

    def merge(self, other):
        pass

    # animation methods

    def assignElement(self, fromIndex, toIndex):
        # get position of "to" cell
        posToCell = canvas.coords(self.list[toIndex].display_shape)

        # get position of "from" cell and value
        posFromCell = canvas.coords(self.list[fromIndex].display_shape)
        posFromCellVal = canvas.coords(self.list[fromIndex].display_val)

        # create new display objects that are copies of the "from" cell and value
        newCellShape = canvas.create_rectangle(posFromCell[0], posFromCell[1], posFromCell[2], posFromCell[3], fill=self.list[fromIndex][1])
        newCellVal = canvas.create_text(posFromCellVal[0], posFromCellVal[1], text=self.list[fromIndex][0], font=('Helvetica', '20'))

        # set xspeed to move in the correct direction
        xspeed = 5
        if fromIndex > toIndex:
            xspeed = -xspeed

        # move the new display objects until they are in the position of the "to" cell
        while canvas.coords(newCellShape) != posToCell:
            canvas.move(newCellShape, xspeed, 0)
            canvas.move(newCellVal, xspeed, 0)
            window.update()
            time.sleep(0.01)

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

    def assignToTemp(self, index, varName = "temp"):

        posCell = canvas.coords(self.list[index].display_shape)
        posCellVal = canvas.coords(self.list[index].display_val)
        
        yspeed = -5
        shape = canvas.create_rectangle(posCell[0], posCell[1], posCell[2], posCell[3], fill=self.list[index][1])
        val = canvas.create_text(posCellVal[0], posCellVal[1], text=str(self.list[index][0]), font=('Helvetica', '20'))

        while canvas.coords(shape)[1] != (ARRAY_Y0-CELL_SIZE-15):
            canvas.move(shape, 0, yspeed)
            canvas.move(val, 0, yspeed)
            window.update()
            time.sleep(0.01)

        text = canvas.create_text(posCell[0] + (CELL_SIZE/2), ARRAY_Y0-CELL_SIZE-30, text=varName, font=('Helvetica', '20'))
        temp = Array.Element(self.list[index][0], self.list[index][1], shape, val)
        return temp, text

    def assignFromTemp(self, index, temp, text):

        posCell = canvas.coords(self.list[index].display_shape)
        posCellVal = canvas.coords(self.list[index].display_val)

        xspeed = 5
        if canvas.coords(temp.display_shape)[0] > posCell[0]:
            xspeed = -xspeed

        while canvas.coords(temp.display_shape)[0] != posCell[0]:
            canvas.move(temp.display_shape, xspeed, 0)
            canvas.move(temp.display_val, xspeed, 0)
            canvas.move(text, xspeed, 0)
            window.update()
            time.sleep(0.01)

        time.sleep(0.1)

        yspeed = 5
        while canvas.coords(temp.display_shape)[1] != ARRAY_Y0:
            canvas.move(temp.display_shape, 0, yspeed)
            canvas.move(temp.display_val, 0, yspeed)
            window.update()
            time.sleep(0.01)

        time.sleep(0.1)
        canvas.delete(text)
        canvas.delete(self.list[index].display_shape)
        canvas.delete(self.list[index].display_val)
        self.list[index] = temp

    def swap(self, a, b):
        if a==b:
            yspeed = -5
            shapeA = self.list[a].display_shape
            while canvas.coords(shapeA)[1] != (ARRAY_Y0 - CELL_SIZE - 15):
                canvas.move(shapeA, 0, yspeed)
                canvas.move(self.list[a].display_val, 0, yspeed)
                window.update()
                time.sleep(0.01)

            time.sleep(0.1)

            while canvas.coords(shapeA)[1] != ARRAY_Y0:
                canvas.move(shapeA, 0, -yspeed)
                canvas.move(self.list[a].display_val, 0, -yspeed)
                window.update()
                time.sleep(0.01)

            return

        # save original coordinates of b cell
        posCellB = canvas.coords(self.list[b].display_shape)

        # move a and b cells up
        yspeed = -5
        shapeA = self.list[a].display_shape
        while canvas.coords(shapeA)[1] != (ARRAY_Y0 - CELL_SIZE - 15):
            canvas.move(shapeA, 0, yspeed)
            canvas.move(self.list[a].display_val, 0, yspeed)
            canvas.move(self.list[b].display_shape, 0, yspeed)
            canvas.move(self.list[b].display_val, 0, yspeed)
            window.update()
            time.sleep(0.01)

        time.sleep(0.1)

        # make a and b cells switch places
        xspeed = 5
        if b < a:
            xspeed = -xspeed

        # move the cells until the a cell is above the original position of the b cell
        while canvas.coords(shapeA)[0] != posCellB[0]:
            canvas.move(shapeA, xspeed, 0)
            canvas.move(self.list[a].display_val, xspeed, 0)
            canvas.move(self.list[b].display_shape, -xspeed, 0)
            canvas.move(self.list[b].display_val, -xspeed, 0)
            window.update()
            time.sleep(0.01)

        time.sleep(0.1)

        # move the cells back down into the list
        while canvas.coords(shapeA)[1] != ARRAY_Y0:
            canvas.move(shapeA, 0, -yspeed)
            canvas.move(self.list[a].display_val, 0, -yspeed)
            canvas.move(self.list[b].display_shape, 0, -yspeed)
            canvas.move(self.list[b].display_val, 0, -yspeed)
            window.update()
            time.sleep(0.01)

        # perform the actual swap operation in the list
        self.list[a], self.list[b] = self.list[b], self.list[a]

    # sorting methods

    def insertionSort(self):
        global running
        running = True
        # make a done arrow that points to 0'th element
        # Traverse through 1 to len(arr)
        for i in range(1, len(self.list)):

            cur, text = self.assignToTemp(i, "cur")

            # Move elements of self.list[0..i-1], that are
            # greater than key, to one position ahead
            # of their current position
            j = i - 1
            while j >= 0 and cur.val < self.list[j].val:
                #self.list[j + 1] = self.list[j]
                time.sleep(.5)
                self.assignElement(j, j+1)
                j -= 1

                if not running:
                    break

            #self.list[j + 1] = cur
            self.assignFromTemp(j+1, cur, text)
            # move done arrow to next element

    def bubbleSort(self):
        global running
        running = True
        n = len(self.list)

        # Traverse through all array elements
        for i in range(n):

            # Last i elements are already in place
            for j in range(0, n - i - 1):

                # traverse the array from 0 to n-i-1
                # Swap if the element found is greater
                # than the next element
                if self.list[j].val > self.list[j+1].val:
                    #arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    self.swap(j, j+1)

                if not running:
                    break

    def selectionSort(self):
        global running
        running = True
        for i in range(len(self.list)):

            # Find the minimum element in remaining
            # unsorted array
            min_idx = i
            for j in range(i + 1, len(self.list)):
                if self.list[min_idx].val > self.list[j].val:
                    min_idx = j

                if not running:
                    break

            # Swap the found minimum element with
            # the first element
            #A[i], A[min_idx] = A[min_idx], A[i]
            self.swap(i, min_idx)

    def isSorted(self):
        for i in range(len(self.list)):
            if self.list[i] > self.list[i+1]:
                return False
        return True

    def bogoSort(self):
        global running
        running = True
        while not self.isSorted() and running:
            time.sleep(1) # pauses in between shuffles to show that checking if its sorted
            self.shuffle()

    def stop(self): # will stop after the current shuffle is done
        global running
        running = False

def makeButtons():
    b = Button(text="Bubble Sort", width=11, command=array.bubbleSort)
    b.pack()
    b1 = Button(text="Selection Sort", width=14, command=array.selectionSort)
    b1.pack()
    b2 = Button(text="Insertion Sort", width=14, command=array.insertionSort)
    b2.pack()
    b3 = Button(text="Bogo Sort", width=9, command=array.bogoSort)
    b3.pack()
    b4 = Button(text="Shuffle", width=7, command=array.shuffle)
    b4.pack()
    b5 = Button(text="Stop", width=4, command=array.stop)
    b5.pack()

#cleanup = []
array = Array()
makeButtons()
array.display()


for i in range(10):
    array.append(i)

#array.display()

time.sleep(1)

# array.find(3)
# time.sleep(1)
#
# clean()
#
# array.append(10)
# time.sleep(1)
#
# clean()
#
# array.remove(3)
# time.sleep(1)
#
# clean()
#
# array.append(3)
# time.sleep(1)
#
# clean()
#
# array.set(3, 20)
# time.sleep(1)
#
# clean()
#
# array.assignElement(4, 2)
# time.sleep(1)
#
# clean()
#
# array.assignElement(5, 8)
# time.sleep(1)
#
# clean()
#
# array.swap(1, 9)
# time.sleep(1)
#
# clean()
#
# #array.insertionSort()
# #array.bubbleSort()
# array.selectionSort()
# time.sleep(1)


# array.shuffle()
# time.sleep(1)
#
# array.insertionSort()
# time.sleep(1)
#
# array.shuffle()
# time.sleep(1)
#
# array.bubbleSort()
# time.sleep(1)
# array.shuffle()

window.mainloop()

'''
To Do:
- make it look pretty
- disable use of buttons when a function is in progress
- add buttons for all the different functionality
'''