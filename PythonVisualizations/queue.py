# TO DO
# Add Queue functionality to the array
# - Currently is circular, need to prevent it from overriding if exisiting (check if something there, or nElems vs size)
#    - just delete from end
# - Get rid of superfluous code
# - Toggle switch between deque and queue functionality

import random
import time
from tkinter import *
from recordclass import recordclass

WIDTH = 800
HEIGHT = 400

CELL_SIZE = 50
ARRAY_X0 = 100
ARRAY_Y0 = 100

class Queue(object):
    Element = recordclass('Element', ['val', 'color', 'display_shape', 'display_val'])
    Element.__new__.__defaults__ = (None,) * len(Element._fields)

    colors = ['red', 'green', 'blue', 'orange', 'yellow', 'cyan', 'magenta',
              'dodgerblue', 'turquoise', 'grey', 'gold', 'pink']
    nextColor = 0

    def __init__(self, size=10):
        self.list = [None]*size
        self.size = size
        self.front = 1  # when Queue is empty, front 
        self.rear = 0   # should be to right of rear.
        self.nItems = 0        

    def __str__(self):
        return str(self.list)

    # ANIMATION METHODS
    def speed(self, sleepTime):
        return (sleepTime * (scaleDefault + 50)) / (scale.get() + 50)

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

    
    def insert(self, val):
        
        # Because queue is circular, first check and make sure the 
        # position is empty
        
        if self.list[self.rear] == None:
            
            # create new cell and cell value display objects
            # Start drawing new one at rear
            cell = canvas.create_rectangle(ARRAY_X0+CELL_SIZE*self.rear, ARRAY_Y0, ARRAY_X0+CELL_SIZE*(self.rear+1), ARRAY_Y0 + CELL_SIZE, fill=Queue.colors[Queue.nextColor], outline='')
            cell_val = canvas.create_text(ARRAY_X0+CELL_SIZE*self.rear + (CELL_SIZE / 2), ARRAY_Y0 + (CELL_SIZE / 2), text=val,
                                          font=('Helvetica', '20'))
    
            # add a new Element to the list with the new value, color, and display objects
            self.list[self.rear] = (Queue.Element(val, Queue.colors[Queue.nextColor], cell, cell_val))
            self.rear = (self.rear+1) % (self.size)
            self.nItems += 1
    
            # increment nextColor
            Queue.nextColor = (Queue.nextColor + 1) % len(Queue.colors)
    
            # update window
            window.update()
            
            
            
            

        
    def removeFromFront(self):
        
        # Set front value in list to None
        n = self.list[self.front]
        self.list[self.front] = None
        
        # Increment front
        self.front += 1
        
        # Decrement number of items
        self.nItems -= 1

        # delete the associated display objects
        canvas.delete(n.display_shape)
        canvas.delete(n.display_val)

        # update window
        window.update()
      

    def removeFromEnd(self):
        
        # If full, decrement 
        if len(self.list) == self.nItems:
            self.rear -=1
        
        # pop an Element from the list
        n = self.list[self.rear]
        self.list[self.rear] = None
        self.rear -= 1
        self.nItems -= 1

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
        newCellShape = canvas.create_rectangle(posFromCell[0], posFromCell[1], posFromCell[2], posFromCell[3],
                                               fill=self.list[fromIndex][1], outline='')
        newCellVal = canvas.create_text(posFromCellVal[0], posFromCellVal[1], text=self.list[fromIndex][0],
                                        font=('Helvetica', '20'))

        # set xspeed to move in the correct direction
        xspeed = 1
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

    def display(self):
        canvas.delete("all")
        xpos = ARRAY_X0
        ypos = ARRAY_Y0

        print(self.size)
        for i in range(self.size):
            canvas.create_rectangle(xpos + CELL_SIZE*i, ypos, xpos + CELL_SIZE*(i+1), ypos + CELL_SIZE, fill='white', outline='black')

        # go through each Element in the list
        for n in self.list:
            
            # Only loop through the existing elements
            if n:
                print(n)
                # create display objects for the associated Elements
                cell = canvas.create_rectangle(xpos, ypos, xpos+CELL_SIZE, ypos+CELL_SIZE, fill=n[1], outline='')
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
def clickFind():
    entered_text = textBox.get()
    txt = ''
    if entered_text:
        if int(entered_text) < 100:
            result = queue.find(int(entered_text))
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
            queue.insert(int(entered_text))
        else:
            outputText.set("Input value must be an integer from 0 to 99.")
        textBox.delete(0, END )

def clickDelete():
    entered_text = textBox.get()
    txt = ''
    if entered_text:
        if int(entered_text) < 100:
            result = queue.remove(int(entered_text))
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
    findButton = Button(operationsLeft, text="Find", width=7, command= lambda: onClick(clickFind))
    findButton.grid(row=1, column=0)
    insertButton = Button(operationsLeft, text="Insert", width=7, command= lambda: onClick(clickInsert))
    insertButton.grid(row=2, column=0)
    deleteRightmostButton = Button(operationsRight, text="Delete From End", width=16, command= lambda: onClick(queue.removeFromEnd))
    deleteRightmostButton.grid(row=1, column=0)
    deleteValueButton = Button(operationsLeft, text="Delete From Front", width=16, command= lambda: onClick(queue.removeFromFront))
    deleteValueButton.grid(row=3, column=0)
    buttons = [findButton, insertButton, deleteRightmostButton, deleteValueButton]
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
window.title("Queue")
canvas.pack()

bottomframe = Frame(window)
bottomframe.pack(side=BOTTOM)
operationsUpper = LabelFrame(bottomframe, text="Operations", padx=4, pady=4)
operationsUpper.pack(side=TOP)
operationsLeft = Frame(operationsUpper, bd=5)
operationsLeft.pack(side=LEFT)
operationsRight = Frame(operationsUpper, bd=5)
operationsRight.pack(side=RIGHT)
operationsLower = Frame(bottomframe)
operationsLower.pack(side=BOTTOM)

#Label(bottomframe, text="Find:", font="none 12 bold").grid(row=0, column=0, sticky=W)
vcmd = (window.register(validate),
        '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
textBox = Entry(operationsLeft, width=20, bg="white", validate='key', validatecommand=vcmd)
textBox.grid(row=2, column=2, padx=5, sticky=E)
scaleDefault = 100
scale = Scale(operationsLower, from_=1, to=200, orient=HORIZONTAL, sliderlength=15)
scale.grid(row=0, column=1, sticky=W)
scale.set(scaleDefault)
scaleLabel = Label(operationsLower, text="Speed:", font="none 10")
scaleLabel.grid(row=0, column=0, sticky=W)

# add a submit button
#Button(bottomframe, text="Find", width=6, command=lambda: queue.onClick(clickFind)).grid(row=0, column=2, sticky=W)
outputText = StringVar()
outputText.set('')
output = Label(operationsLower, textvariable=outputText, font="none 10 italic", fg="blue")
output.grid(row=0, column=3, sticky=(E, W))
operationsLower.grid_columnconfigure(3, minsize=160)

# exit button
Button(operationsLower, text="EXIT", width=0, command=close_window)\
    .grid(row=0, column=4, sticky=E)

cleanup = []
queue = Queue()
buttons = makeButtons()
queue.display()

for i in range(4):
    queue.insert(i)

window.mainloop()

'''
To Do:
- make it look pretty
- animate insert and delete
- delete/insert at index?
- label arrows for sorts (inner, outer, etc.)
- implement shell sort, radix sort, quick sort
'''
