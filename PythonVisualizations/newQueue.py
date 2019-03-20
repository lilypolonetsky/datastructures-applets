# TO DO
# - Make sure our code aligns with his code
#    - Implement insertFront() and add button
#    - Fix issues with insertion and deletion (because front = 1 crossing issues)
# - Get rid of superfluous code
# - Toggle switch between deque and queue functionality
# - Disable delete buttons when empty
# - Discuss animation preferences, making the code prettier
# - Remove sleep, get, set, and assignElement methods? (All seem unused)

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
        
        
    # insert item at rear of queue   
    def insertRear(self, val):
        
        #if there's a space to insert into
        if self.nItems != self.size:
        
            # create new cell and cell value display objects
            # Start drawing new one at rear
            cell = canvas.create_rectangle(ARRAY_X0+CELL_SIZE*self.rear, ARRAY_Y0, \
                                           ARRAY_X0+CELL_SIZE*(self.rear+1), ARRAY_Y0 + CELL_SIZE, \
                                           fill=Queue.colors[Queue.nextColor], outline='')
            cell_val = canvas.create_text(ARRAY_X0+CELL_SIZE*self.rear + (CELL_SIZE / 2), \
                                          ARRAY_Y0 + (CELL_SIZE / 2), text=val, font=('Helvetica', '20'))
            
            #deal with wraparound
            if self.rear == self.size-1:
                self.rear = -1
                
            #increment rear and insert the item
            self.rear += 1
            self.list[self.rear] = (Queue.Element(val, Queue.colors[Queue.nextColor], cell, cell_val))
            
            self.nItems += 1
            
            # increment nextColor
            Queue.nextColor = (Queue.nextColor + 1) % len(Queue.colors)
        
            # update window
            window.update()
            
            
    
    def insertFront(self, val):
        
        #if there's a space to insert into
        if self.nItems != self.size:
            
            # create new cell and cell value display objects
            # Start drawing new one at rear
            cell = canvas.create_rectangle(ARRAY_X0+CELL_SIZE*self.rear, ARRAY_Y0, \
                                           ARRAY_X0+CELL_SIZE*(self.rear+1), ARRAY_Y0 + CELL_SIZE, \
                                           fill=Queue.colors[Queue.nextColor], outline='')
            cell_val = canvas.create_text(ARRAY_X0+CELL_SIZE*self.rear + (CELL_SIZE / 2), \
                                          ARRAY_Y0 + (CELL_SIZE / 2), text=val, font=('Helvetica', '20'))
            
            #deal with wraparound
            if self.front == 0:
                self.front = self.size
            
            #decrement front and insert the item
            self.front -= 1
            self.list[self.front] = (Queue.Element(val, Queue.colors[Queue.nextColor], cell, cell_val))
            
            self.nItems += 1
            
            # increment nextColor
            Queue.nextColor = (Queue.nextColor + 1) % len(Queue.colors)
        
            # update window
            window.update()


    
    # remove the left element of the queue, or None if empty
    def removeFront(self):
        
        #if the queue is empty, exit
        if self.size == 0:
            return None

        #get the value at front, and then set it to None so it will be garbage collected
        n = self.list[self.front]
        self.list[self.front] = None
        
        #increment front
        self.front += 1
        
        #deal with wraparound
        if self.front == self.size:
            self.front = 0
            
        self.nItems -= 1
        
        # delete the associated display objects
        canvas.delete(n.display_shape)
        canvas.delete(n.display_val)
        
        # update window
        window.update()
    
    def removeRear(self):
        
        #if the queue is empty, exit
        if self.size == 0:
            return None
        
        #get the value at rear, and then set it to None so it will be garbage collected
        n = self.list[self.rear]
        self.list[self.rear] = None
        
        #decrement rear
        self.rear -= 1
        
        #deal with wraparound
        if self.rear == -1:
            self.rear = self.size-1
            
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
#    
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

def clickInsertRear():
    entered_text = textBox.get()
    if entered_text:
        val = int(entered_text)
        if val < 100:
            queue.insertRear(int(entered_text))
        else:
            outputText.set("Input value must be an integer from 0 to 99.")
        textBox.delete(0, END )
        
def clickInsertFront():
    entered_text = textBox.get()
    if entered_text:
        val = int(entered_text)
        if val < 100:
            queue.insertFront(int(entered_text))
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
    insertRearButton = Button(operationsLeft, text="Insert At Rear", width=16, command= lambda: onClick(clickInsertRear))
    insertRearButton.grid(row=2, column=0)
    insertFrontButton = Button(operationsLeft, text="Insert At Front", width=16, command= lambda: onClick(clickInsertFront))
    insertFrontButton.grid(row=1, column=0)
    deleteRightmostButton = Button(operationsRight, text="Delete From End", width=16, command= lambda: onClick(queue.removeRear))
    deleteRightmostButton.grid(row=1, column=0)
    deleteValueButton = Button(operationsLeft, text="Delete From Front", width=16, command= lambda: onClick(queue.removeFront))
    deleteValueButton.grid(row=3, column=0)
    buttons = [insertRearButton, insertFrontButton, deleteRightmostButton, deleteValueButton]
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
    queue.insertRear(i)

window.mainloop()    
