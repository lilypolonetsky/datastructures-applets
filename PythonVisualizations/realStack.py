import random
import time
from tkinter import *
from recordclass import recordclass 

# Size of the canvas
WIDTH = 150
HEIGHT = 600

CELL_SIZE = 50
ARRAY_X0 = 50 #top left corner first cell
ARRAY_Y0 = 550

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
        
    # Allows us to make pop conditional    
    def getSize(self):   
        return len(self.list)

    def push(self, val):
        # create new cell and cell value display objects
        cell = canvas.create_rectangle(ARRAY_X0, ARRAY_Y0-CELL_SIZE*len(self.list), \
                                       ARRAY_X0+CELL_SIZE, \
                                       ARRAY_Y0 - CELL_SIZE*(len(self.list)-1), fill=Stack.colors[Stack.nextColor])
        cell_val = canvas.create_text(ARRAY_X0 + (CELL_SIZE / 2), \
                                      ARRAY_Y0-CELL_SIZE*(len(self.list)-1) - (CELL_SIZE / 2), text=val,
                                      font=('Helvetica', '20'))

        # add a new Element to the list with the new value, color, and display objects
        self.list.append(Stack.Element(val, Stack.colors[Stack.nextColor], cell, cell_val))

        # increment nextColor
        Stack.nextColor = (Stack.nextColor + 1) % len(Stack.colors)

        # update window
        window.update()


    def pop(self):
        # pop an Element from the list
        n = self.list.pop()

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
        enableButtons()
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
sideframe.pack(side="right")

textBox = Entry(sideframe, width=20, bg="white")
textBox.grid(row=4, column=1, sticky=W)
textBoxLabel = Label(sideframe, text="To Push:", font="none 10")
textBoxLabel.grid(row=4, column=0, sticky=E)

outputText = StringVar()
outputText.set('')
output = Label(sideframe, textvariable=outputText, font="none 12 bold")
output.grid(row=4, column=1, sticky=E)

# exit button
Button(sideframe, text="EXIT", width=4, command=close_window).grid(row=6, column=1, sticky=W)

cleanup = []

stack = Stack()
buttons = makeButtons()

for i in range(10):
    stack.push(i)
    
window.mainloop()
