import random
import time
from tkinter import *
from recordclass import recordclass 

# Three methods used in animation
# 1) canvas.coords() - give you current location, put the object (i.e. square) inside the parameters
#     - For pop, find where the top square currently is located
#     - Then go up, and move off the screen. 
#     - For push, need to know where last elem is to know where to push the next element (100 pixels higher, for example)
# 2) canvas.move(objectMoving, deltaX, deltaY)
#     - Put this into a while loop, and have a computation to know how long to keep iterating
#     - while canvas.coords() desired location is !=, then move again incrementally using the deltaX and deltaY
# 3) window.update() - after each incremental movement to update

# POP (sketch)
# - canvas.move(object, deltaX, deltaY) until the object is off the screen
#    - deltaX == 0
#    - put in while loop to some huge number to ensure it gets off screen



# Size of the canvas
WIDTH = 150
HEIGHT = 600

CELL_SIZE = 50
ARRAY_X0 = 50 #top left corner first cell
ARRAY_Y0 = 550

# Boolean for enabling buttons
running = False

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

    def get(self, index):
        try:
            return self.list[index][0]
        except:
            print("Invalid list index")
            return -1
        
    # Allows us to make pop conditional    
    def getSize(self):   
        return len(self.list)

    def push(self, val):
        
        # Using old code for push() to try and create cells off-screen
        # to enable our animation
        cell = canvas.create_rectangle(ARRAY_X0, 0-CELL_SIZE, ARRAY_X0+CELL_SIZE, \
                                       0, fill=Stack.colors[Stack.nextColor])
        cell_val = canvas.create_text(ARRAY_X0 + (CELL_SIZE / 2), \
                                      0 - (CELL_SIZE / 2), text=val,
                                      font=('Helvetica', '20'))
        
        # Top left corner (could need to be changed to bottom right)
        desiredY = ARRAY_Y0-CELL_SIZE*len(self.list)

        # add a new Element to the list with the new value, color, and display objects
        n = Stack.Element(val, Stack.colors[Stack.nextColor], cell, cell_val)
        self.list.append(n)

        # increment nextColor
        Stack.nextColor = (Stack.nextColor + 1) % len(Stack.colors)
        
        # Move the visible shape on to stack
        # - create object off screen
        # - Get coords of desired location -- original coords
        # - move incrementally until you hit that location
        while (canvas.coords(n.display_shape)[1] < desiredY):
            canvas.move(n.display_shape, 0, 5)
            canvas.move(n.display_val, 0, 5)
            window.update()        

        # update window
        window.update()


    def pop(self):
        # pop an Element from the list
        n = self.list.pop()
        
        # Move animation
        
        # While y >=0 (i.e. the y of the top object on the screen
        # is still visible on the canvas)
        while (canvas.coords(n.display_shape)[1] + CELL_SIZE >= 0):
            canvas.move(n.display_shape, 0, -5)
            canvas.move(n.display_val, 0, -5)
            window.update()

        # delete the associated display objects
        canvas.delete(n.display_shape)
        canvas.delete(n.display_val)

        # update window
        window.update()


def onClick(command, parameter = None):
    cleanUp()
    disableButtons()
    if parameter:
        command(parameter)
    else:
        command()
        enableButtons()

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
        stack.push(int(entered_text))
        textBox.delete(0, END)

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
    pushButton = Button(sideframe, text="Push", width=20, command= lambda: onClick(clickPush))
    pushButton.grid(row=0, column=1)
    popButton = Button(sideframe, text="Pop", width=20, command= lambda: onClick(clickPop))
    popButton.grid(row=1, column=1)
    buttons = [pushButton, popButton]
    return buttons

window = Tk()
frame = Frame(window)
frame.pack(side = "left")

waitVar = BooleanVar()

canvas = Canvas(frame, width=WIDTH, height=HEIGHT)
window.title("Stack")
canvas.pack()

sideframe = Frame(window)
sideframe.pack(side="left")

textBox = Entry(sideframe, width=14, bg="white")
textBox.grid(row=4, column=1, sticky=E)
textBoxLabel = Label(sideframe, text="To Push:", font="none 12")
textBoxLabel.grid(row=4, column=1, sticky=W)

outputText = StringVar()
outputText.set('')
output = Label(sideframe, textvariable=outputText, font="none 12 bold")
output.grid(row=4, column=1, sticky=E)

# exit button
#Button(sideframe, text="EXIT", width=4, command=close_window).grid(row=6, column=1, sticky=W)

cleanup = []

stack = Stack()
buttons = makeButtons()

for i in range(10):
    stack.push(i)
    
window.mainloop()
