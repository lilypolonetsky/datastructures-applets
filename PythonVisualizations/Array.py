from tkinter import *
import time
import random
from collections import namedtuple

WIDTH = 800
HEIGHT = 600

CELL_SIZE = 50
ARRAY_X0 = 50
ARRAY_Y0 = 50

window = Tk()
frame = Frame(window)
frame.pack()

canvas = Canvas(frame, width=WIDTH, height=HEIGHT)
window.title("Array")
canvas.pack()

# Button functions
def clickFind():
    entered_text=textBox.get()
    txt = ''
    if array.find(int(entered_text)):
        txt = "Found!"
    else:
        txt = "Value not found"
    outputText.set(txt)

def close_window():
    window.destroy()
    exit()


bottomframe = Frame(window)
bottomframe.pack( side = BOTTOM )

Label (bottomframe, text="Find:", font="none 12 bold").grid(row=0, column=0, sticky=W)
textBox = Entry(bottomframe, width=20, bg="white")
textBox.grid(row=0, column=1, sticky=W)

# add a submit button
Button(bottomframe, text="Enter", width=6, command=clickFind).grid(row=0, column=2, sticky=W)
outputText = StringVar()
outputText.set('')
output = Label (bottomframe, textvariable=outputText, font="none 12 bold")
output.grid(row=0, column=3, sticky=E)

# exit button
Button(bottomframe, text="EXIT", width=4, command=close_window).grid(row=2, column=0, sticky=W)

Element = namedtuple('Element', ['val', 'color', 'display_shape', 'display_val'])
Element.__new__.__defaults__ = (None,) * len(Element._fields)

class Array(object):
    colors = ['red', 'green', 'blue', 'orange', 'yellow', 'cyan', 'magenta',
              'dodgerblue', 'turquoise', 'grey', 'gold', 'pink']
    nextColor = 0

    def __init__(self):
        self.list = []
        #self.arrow = None
        #self.foundBox = None
        self.drawnObjects = []

    def get(self, index):
        try:
            return self.list[index][0]
        except:
            print("Invalid list index")
            return -1

    def set(self, index, val):
        self.list[index] = (val, Array.colors[Array.nextColor])
        Array.nextColor = (Array.nextColor + 1)%len(Array.colors)

    def append(self, val):
        self.list.append((val, Array.colors[Array.nextColor]))
        Array.nextColor = (Array.nextColor + 1) % len(Array.colors)
        self.display()

    def removeFromEnd(self):
        self.list.pop()
        self.display()

    def clear(self):
        for o in self.drawnObjects:
            canvas.delete(o)

    def display(self):
        self.clear()
        xpos = ARRAY_X0
        ypos = ARRAY_Y0
        for n in self.list:
            print(n)
            cell = canvas.create_rectangle(xpos, ypos, xpos+CELL_SIZE, ypos+CELL_SIZE, fill=n[1])
            cell_val = canvas.create_text(xpos+(CELL_SIZE/2), ypos+(CELL_SIZE/2), text=n[0], font=('Helvetica', '20'))
            self.drawnObjects.append(cell)
            self.drawnObjects.append(cell_val)
            xpos += 50
        window.update()

    def find(self, val):
        self.clear()
        self.display()
        # Maybe, instead of having the foundBox, change color of value to green2?
        x = ARRAY_X0 + (CELL_SIZE/2)
        y0 = ARRAY_Y0 - 40
        y1 = ARRAY_Y0 - 15
        arrow = canvas.create_line(x, y0, x, y1, arrow="last", fill='red')
        self.drawnObjects.append(arrow)
        for n in self.list:
            window.update()
            if n[0] == val:
                pos = canvas.coords(arrow)
                #foundBox = canvas.create_rectangle(pos[0]-(x-CELL_SIZE), ARRAY_Y0, pos[2]+(x-CELL_SIZE), ARRAY_Y0+CELL_SIZE, fill='', outline="green2", width="5")
                #self.drawnObjects.append(foundBox)
                cell_val = canvas.create_text(pos[0]-(x-CELL_SIZE) + (CELL_SIZE / 2), ARRAY_Y0 + (CELL_SIZE / 2), text=n[0],
                                              font=('Helvetica', '25'), fill='green2')
                self.drawnObjects.append(cell_val)
                return True

            time.sleep(1)
            canvas.move(arrow, CELL_SIZE, 0)

        return False

    def remove(self, index):
        self.list.pop(3)
        self.display()

    def shuffle(self):
        pass

    def split(self):
        pass

    def merge(self, other):
        pass

    def removeElement(self, index):
        pass

    def insertElement(self, val):
        pass

    def swap(self, a, b):
        pass


class Ball:
    def __init__(self, color, size):
        self.shape = canvas.create_oval(10, 10, size, size, fill=color)
        self.xspeed = random.randrange(-10,10)
        self.yspeed = random.randrange(-10,10)

    def move(self):
        canvas.move(self.shape, self.xspeed, self.yspeed)
        pos = canvas.coords(self.shape)
        if pos[3] >= HEIGHT or pos[1] <= 0:
            self.yspeed = -self.yspeed
        if pos[0] <= 0 or pos[2] >= WIDTH:
            self.xspeed = -self.xspeed



array = Array()
for i in range(10):
    array.append(i)

array.display()

time.sleep(1)

#array.find(6)
#time.sleep(1)
array.append(10)
time.sleep(1)
array.remove(3)
array.append(3)

window.mainloop()

'''
To Do:
- make it look pretty
- disable use of buttons when a function is in progress
- add buttons for all the different functionality
'''