from tkinter import *
import time
import random
from recordclass import recordclass

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
                # get the position of the displayed value
                pos = canvas.coords(n.display_val)

                # cover the current display value with the updated value in green
                cell_val = canvas.create_text(pos[0], pos[1], text=str(val), font=('Helvetica', '22'), fill='green2')

                # add the green value to findDisplayObjects for cleanup later
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


#cleanup = []
array = Array()
array.display()

for i in range(10):
    array.append(i)

#array.display()

time.sleep(1)

array.find(3)
time.sleep(1)

clean()

array.append(10)
time.sleep(1)

clean()

array.remove(3)
time.sleep(1)

clean()

array.append(3)
time.sleep(1)

clean()

array.set(3, 20)
time.sleep(1)

window.mainloop()

'''
To Do:
- make it look pretty
- disable use of buttons when a function is in progress
- add buttons for all the different functionality
'''