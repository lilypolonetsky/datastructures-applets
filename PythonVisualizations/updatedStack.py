import random
import time
from tkinter import *
from recordclass import recordclass 

#How to read Tkinter of radix sort
#How to implement Tkinter of radix sort
#How to change coordinate assignment
#How to update textbox after push
#Push vs Append - work on this
#Animations tutorial

# TO DO LIST
# - change animations
#      - Add flying in and flying out
#      - flip to vertical
#      - make it pretty
# Make the textbox that accepts the number to pop reset after each pop (see line 249)
# Do we need the "append" method? How is it different from pop?

WIDTH = 800
HEIGHT = 400

CELL_SIZE = 50
ARRAY_X0 = 350 #top left corner first cell
ARRAY_Y0 = 350

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
    # horizontal because we're creating a vertical stack
    
    def speed(self, sleepTime):
        return (sleepTime * (scaleDefault + 50)) / (scale.get() + 50)
    
#    shapeX = canvas.coords(self.list[0].display_shape)[0]
#        valX = canvas.coords(self.list[0].display_val)[0]
#        canvas.config(width=1200, height=600)
#
#        for i in range(0, len(self.list)):
#            cur = self.list[i]
#            canvas.move(cur.display_shape, -(canvas.coords(cur.display_shape)[0] - shapeX), CELL_SIZE*i - 30)
#            canvas.move(cur.display_val, -(canvas.coords(cur.display_val)[0] - valX), CELL_SIZE*i - 30)

# must change assignElement to match what we copied from radixSort (vertical)
        
  

# CHANGE FOR VERTICAL - but not reassigning -- may need something different
    def moveUp(self, dy, toX, toY, curDisplayShape, curDisplayVal):
        global running

        if not running:
            return
        
        # WANT TO CHANGE THIS TO A DY?
        # given a toX, toY, and dy, calculate the dx required to get
        # from the current position to the new position
        fromX = canvas.coords(curDisplayShape)[0]
        fromY = canvas.coords(curDisplayShape)[1]
        if toY < fromY:
            dx = dy * (toX - fromX) / (toY - fromY)
            
        # SWITCH THIS TO A Y
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
    def isSorted(self):   #do we need this?
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
        
    def getSize(self):   #I added this method so that I could make the pop conditional
        return len(self.list)

# Important: SHOW HOW TO CREATE NEW BLOCKS!
    def push(self, val):
        # create new cell and cell value display objects
        cell = canvas.create_rectangle(ARRAY_X0+CELL_SIZE*len(self.list), \
                                       ARRAY_Y0, ARRAY_X0+CELL_SIZE*(len(self.list)+1), \
                                       ARRAY_Y0 + CELL_SIZE, fill=Stack.colors[Stack.nextColor])
        cell_val = canvas.create_text(ARRAY_X0+CELL_SIZE*len(self.list) + (CELL_SIZE / 2), \
                                      ARRAY_Y0 + (CELL_SIZE / 2), text=val,
                                      font=('Helvetica', '20'))

        # add a new Element to the list with the new value, color, and display objects
        self.list.append(Stack.Element(val, Stack.colors[Stack.nextColor], cell, cell_val))

        # increment nextColor
        Stack.nextColor = (Stack.nextColor + 1) % len(Stack.colors)
        
        #the append method has extra lines inserted here - does push need them?
        #Do we need append at all, or does push do whatever we need?

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
     
     # THIS NEEDS TO BE IRONED OUT   
    def append(self):
        # create new cell and cell value display objects
        cell = canvas.create_rectangle(ARRAY_X0+CELL_SIZE*len(self.list), \
                                       ARRAY_Y0, ARRAY_X0+CELL_SIZE*(len(self.list)+1), \
                                       ARRAY_Y0 + CELL_SIZE, fill=Stack.colors[Stack.nextColor])
        cell_val = canvas.create_text(ARRAY_X0+CELL_SIZE*len(self.list) + (CELL_SIZE / 2), \
                                      ARRAY_Y0 + (CELL_SIZE / 2), text=val,
                                      font=('Helvetica', '20'))

        # add a new Element to the list with the new value, color, and display objects
        self.list.append(Stack.Element(val, Stack.colors[Stack.nextColor], cell, cell_val))

        # increment nextColor
        Stack.nextColor = (Stack.nextColor + 1) % len(Stack.colors)
        
        # push an Element on the list
        n = self.list.push()        
        
        # ADD the associated display objects
        canvas.delete(n.display_shape)
        canvas.delete(n.display_val)        
        
        window.update()

# Will be close, but not exactly, 
# modify to display vertically. 
        #CHANGE THIS AND PUSH TO BE VERTICAL
    def display(self):
        canvas.delete("all")
        xpos = ARRAY_X0
        ypos = ARRAY_Y0

        # go through each Element in the list
        for n in self.list:
            print(n)
            # create display objects for the associated Elements
            # switched to subtraction in an attempt to make it vertical
            cell = canvas.create_rectangle(xpos, ypos, xpos-CELL_SIZE, ypos-CELL_SIZE, fill=n[1])
            cell_val = canvas.create_text(xpos+(CELL_SIZE/2), ypos+(CELL_SIZE/2), text=n[0], font=('Helvetica', '20'))

            # save the display objects to the appropriate attributes of the Element object
            n.display_shape = cell
            n.display_val = cell_val

            #DECREMENT Y INSTEAD
            ypos -= CELL_SIZE

        window.update()


def onClick(command, parameter = None):
    cleanUp()
    disableButtons()
    if parameter:
        command(parameter)
    else:
        enableButtons()   #I added this line because the Tkinter window wasn't working properly.
                          #I'm not sure if it belongs somewhere else, but it seems to work now.
        command()

def cleanUp():
    global cleanup
    if len(cleanup) > 0:
        for o in cleanup:
            canvas.delete(o)
    outputText.set('')
    window.update()

# Button functions
def clickPush():
    entered_text = textBox.get()
    if entered_text:
        stack.push(int(entered_text)) # will need to define our push
        textBox.setvar('') #this line isn't working - it should reset the textbox

        
def clickPop():
    stack.pop()
    #Check if the stack is empty
    if stack.getSize() == 0:
        disablePop()
        

def close_window():
    window.destroy()
    exit()

def disableButtons():
    for button in buttons:
        button.config(state = DISABLED)
        
def disablePop():
    buttons[1].config(state = DISABLED)

def enableButtons():
    for button in buttons:
        button.config(state = NORMAL)

def makeButtons():
    pushButton = Button(bottomframe, text="Push", width=20, command= lambda: onClick(clickPush))
    pushButton.grid(row=3, column=0)
    popButton = Button(bottomframe, text="Pop", width=20, command= lambda: onClick(clickPop))
    popButton.grid(row=3, column=1)
    buttons = [pushButton, popButton]
    return buttons

window = Tk()
frame = Frame(window)
frame.pack()

waitVar = BooleanVar()

canvas = Canvas(frame, width=WIDTH, height=HEIGHT)
window.title("Stack")
canvas.pack()

bottomframe = Frame(window)
bottomframe.pack(side=BOTTOM)

textBox = Entry(bottomframe, width=20, bg="white")
textBox.grid(row=4, column=1, sticky=W)
textBoxLabel = Label(bottomframe, text="To Push:", font="none 10")
textBoxLabel.grid(row=4, column=0, sticky=E)
scaleDefault = 100
scale = Scale(bottomframe, from_=1, to=200, orient=HORIZONTAL, sliderlength=15)
scale.grid(row=5, column=1, sticky=W)
scale.set(scaleDefault)
scaleLabel = Label(bottomframe, text="Speed:", font="none 10")
scaleLabel.grid(row=5, column=0, sticky=E)

outputText = StringVar()
outputText.set('')
output = Label(bottomframe, textvariable=outputText, font="none 12 bold")
output.grid(row=4, column=1, sticky=E)

# exit button
Button(bottomframe, text="EXIT", width=4, command=close_window).grid(row=6, column=3, sticky=W)

cleanup = []

# change to stack = Stack()
stack = Stack()
buttons = makeButtons()
stack.display()

for i in range(10):
    stack.push(i)
    
window.mainloop()

# 90 degrees about origin is (y,-x), and then make y into -y to not fall off the screen

#    def swap(self, a, b, aCellObjects = [], bCellObjects = []):
#        y0 = canvas.coords(self.list[a].display_shape)[1]
#        if a == b:
#            yspeed = -5
#            shapeA = self.list[a].display_shape
#            while canvas.coords(shapeA)[1] != (y0 - CELL_SIZE - 15):
#                canvas.move(shapeA, 0, yspeed)
#                canvas.move(self.list[a].display_val, 0, yspeed)
#                window.update()
#                time.sleep(self.speed(0.01))
#
#            time.sleep(self.speed(0.1))

#canvas.coords returns a tuple - x and y of location of the object