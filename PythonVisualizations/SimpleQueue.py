from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

WIDTH = 800
HEIGHT = 400
CELL_SIZE = 50
ARRAY_X0 = 100
ARRAY_Y0 = 100

class Queue(VisualizationApp):

    colors = ['red', 'green', 'blue', 'orange', 'yellow', 'cyan', 'magenta',
              'dodgerblue', 'turquoise', 'grey', 'gold', 'pink']
    nextColor = 0

    def __init__(self, size=12, title="Queue", **kwargs):
        super().__init__(title=title, **kwargs)
        self.list = [None]*size
        self.size = size
        self.front = 1  # when Queue is empty, front 
        self.rear = 0   # should be to right of rear.
        self.nItems = 0
        self.rearArrow = (None, None)
        self.frontArrow = (None, None)
        self.buttons = self.makeButtons()
        self.display()

    def __str__(self):
        return str(self.list)
    
    # ANIMATION METHODS
    def createIndex(  # Create an index arrow to point at an indexed
            self, index=-1, name=None, high=True):  # cell with an optional name label

        coords = [ARRAY_X0 + CELL_SIZE * index, ARRAY_Y0, ARRAY_X0 + CELL_SIZE * (index + 1), ARRAY_Y0 + CELL_SIZE]

        x0 = coords[0]
        x1 = coords[0]
        y0 = coords[1] - CELL_SIZE * 2 // 2
        y1 = coords[1] - CELL_SIZE * 1 // 4
        if high:  # changes height of arrow
            y0 -= 20

        arrow = self.canvas.create_line(
            x0, y0, x1, y1, arrow="last", fill=self.VARIABLE_COLOR)
        if name:
            label = self.canvas.create_text(
                x1 + 2, y0, text=name, anchor=SW,
                font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        return (arrow, label) if name else (arrow,)

    # def speed(self, sleepTime):
    #     return (sleepTime * (scaleDefault + 50)) / (scale.get() + 50)
    
    def set(self, index, val):
        # reset the value of the Element at that index to val
        self.list[index].val = val

        # get the position of the displayed value
        pos = self.canvas.coords(self.list[index].display_val)

        # delete the displayed value and replace it with the updated value
        self.canvas.delete(self.list[index].display_val)
        self.list[index].display_val = self.canvas.create_text(pos[0], pos[1], text=str(val), font=('Helvetica', '20'))

        # update window
        self.window.update()
        
        
    # insert item at rear of queue   
    def insertRear(self, val):

        didInsert=False
        # Fix to self.rear starting at 1
        if self.nItems == 0:
            self.rear = 0
            self.front = self.rear # circular
            
            # create new cell and cell value display objects
            # Start drawing new one at rear
            cell = self.canvas.create_rectangle(ARRAY_X0+CELL_SIZE*self.rear, ARRAY_Y0, \
                                           ARRAY_X0+CELL_SIZE*(self.rear+1), ARRAY_Y0 + CELL_SIZE, \
                                           fill=Queue.colors[Queue.nextColor], outline='')
            cell_val = self.canvas.create_text(ARRAY_X0+CELL_SIZE*self.rear + (CELL_SIZE / 2), \
                                          ARRAY_Y0 + (CELL_SIZE / 2), text=val, font=('Helvetica', '20'))
            
            
            #insert the item
            self.list[self.rear] = drawable(val, Queue.colors[Queue.nextColor], cell, cell_val)
            
            self.nItems += 1
            
            # increment nextColor
            Queue.nextColor = (Queue.nextColor + 1) % len(Queue.colors)
        
            self.onOffButtons()
            
            # update window
            self.window.update()

            self.list[self.rear] = drawable(val, Queue.colors[Queue.nextColor], cell, cell_val)
            didInsert = True
        
        #if there's a space to insert into
        elif self.nItems != self.size:

            #deal with wraparound
            if self.rear == self.size-1:
                self.rear = -1
                # move rear arrow back to the beginning
                self.moveItemsBy(self.rearArrow, (CELL_SIZE * self.size * -1, 0), steps=1)
                
            #increment rear
            self.rear += 1
            
            # create new cell and cell value display objects
            # Start drawing new one at rear
            cell = self.canvas.create_rectangle(ARRAY_X0+CELL_SIZE*self.rear, ARRAY_Y0, \
                                           ARRAY_X0+CELL_SIZE*(self.rear+1), ARRAY_Y0 + CELL_SIZE, \
                                           fill=Queue.colors[Queue.nextColor], outline='')
            cell_val = self.canvas.create_text(ARRAY_X0+CELL_SIZE*self.rear + (CELL_SIZE / 2), \
                                          ARRAY_Y0 + (CELL_SIZE / 2), text=val, font=('Helvetica', '20'))
            
            
            #insert the item
            self.list[self.rear] = drawable(val, Queue.colors[Queue.nextColor], cell, cell_val)
            didInsert=True

        if didInsert:
            self.nItems += 1
            self.moveItemsBy(self.rearArrow,(CELL_SIZE,0),steps=1)

            # increment nextColor
            Queue.nextColor = (Queue.nextColor + 1) % len(Queue.colors)

            self.onOffButtons()

            # update window
            self.window.update()
            
            
    
    def insertFront(self, val):
        
        #if there's a space to insert into
        if self.nItems != self.size:
            
            #deal with wraparound
            if self.front == 0:
                self.front = self.size
            
            #decrement front
            self.front -= 1
                        
            # create new cell and cell value display objects
            # Start drawing new one at rear
            cell = self.canvas.create_rectangle(ARRAY_X0+CELL_SIZE*self.front, ARRAY_Y0, \
                                           ARRAY_X0+CELL_SIZE*(self.front+1), ARRAY_Y0 + CELL_SIZE, \
                                           fill=Queue.colors[Queue.nextColor], outline='')
            cell_val = self.canvas.create_text(ARRAY_X0+CELL_SIZE*self.front + (CELL_SIZE / 2), \
                                          ARRAY_Y0 + (CELL_SIZE / 2), text=val, font=('Helvetica', '20'))
            
            #insert the item
            self.list[self.front] = drawable(val, Queue.colors[Queue.nextColor], cell, cell_val)
            
            self.nItems += 1
            
            # increment nextColor
            Queue.nextColor = (Queue.nextColor + 1) % len(Queue.colors)
            
            self.onOffButtons()
            
            # update window
            self.window.update()


    
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
            self.moveItemsBy(self.frontArrow, (CELL_SIZE * self.size * -1, 0), steps=1)

        self.nItems -= 1
        
        # delete the associated display objects
        self.canvas.delete(n.display_shape)
        self.canvas.delete(n.display_val)
        
        self.onOffButtons()
        self.moveItemsBy(self.frontArrow, (CELL_SIZE, 0), steps=1)

        # update window
        self.window.update()
    
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
        self.canvas.delete(n.display_shape)
        self.canvas.delete(n.display_val)
        
        self.onOffButtons()
        
        # update window
        self.window.update()
    
    def display(self):
        self.canvas.delete("all")
        xpos = ARRAY_X0
        ypos = ARRAY_Y0

        for i in range(self.size):
            self.canvas.create_rectangle(xpos + CELL_SIZE*i, ypos, xpos + CELL_SIZE*(i+1), ypos + CELL_SIZE, fill='white', outline='black')

        # go through each Element in the list
        for n in self.list:
            
            # Only loop through the existing elements
            if n:

                # create display objects for the associated Elements
                cell = self.canvas.create_rectangle(xpos, ypos, xpos+CELL_SIZE, ypos+CELL_SIZE, fill=n[1], outline='')
                cell_val = self.canvas.create_text(xpos+(CELL_SIZE/2), ypos+(CELL_SIZE/2), text=n[0], font=('Helvetica', '20'))
    
                # save the display objects to the appropriate attributes of the Element object
                n.display_shape = cell
                n.display_val = cell_val
    
                # increment xpos
                xpos += CELL_SIZE

        self.rearArrow = self.createIndex(self.rear, "Rear", high=False)
        self.frontArrow = self.createIndex(self.front, "Front", high=True)
        self.window.update()

    #disable insert if queue if full, disable delete if empty
    #enable everything else without overriding queue/deque functionality
    def onOffButtons(self):
        #if it's a deque
        if self.buttons[5]['relief'] == 'sunken':
            pass
          #  enableButtons()
            
        #if it's a queue
        else:
            self.buttons[0].config(state = NORMAL)
            self.buttons[3].config(state = NORMAL)
        
        #in all cases: disable buttons as necessary
        if self.nItems == self.size:
            self.buttons[0].config(state = DISABLED)
            self.buttons[1].config(state = DISABLED)
            
        if self.nItems == 0:
            self.buttons[2].config(state = DISABLED)
            self.buttons[3].config(state = DISABLED)



    def onClick(self,command, parameter = None):
        self.cleanUp()
        #disableButtons()
        if parameter:
            command(parameter)
        else:
            command()
        #if command not in [pause, play]:
         #   enableButtons()

# Button functions

    def clickInsertRear(self):
        entered_text = self.textEntries[0].get()
        if entered_text:
            val = int(entered_text)
            if val < 100:
                self.insertRear(int(entered_text))
            else:
                self.outputText.set("Input value must be an integer from 0 to 99.")
            self.textEntries[0].delete(0, END )
        
    def clickInsertFront(self):
        entered_text = self.textBox.get()
        if entered_text:
            val = int(entered_text)
            if val < 100:
                self.insertFront(int(entered_text))
            else:
                self.outputText.set("Input value must be an integer from 0 to 99.")
            self.textBox.delete(0, END )
        
    def clickEnableQueue(self):
        #THIS IS HARDWIRED (THE ORDER OF THE BUTTONS) - FIX
        self.buttons[1].config(state = DISABLED)
        self.buttons[2].config(state = DISABLED)

        # Toggling between deque and queue
        self.buttons[4].config(relief = SUNKEN)
        self.buttons[5].config(relief = RAISED)

        self.onOffButtons()
    
    def clickEnableDeque(self):
        for button in buttons:
            button.config(state = NORMAL)

        # Toggling between deque and queue
        self.buttons[4].config(relief = RAISED)
        self.buttons[5].config(relief = SUNKEN)

        self.onOffButtons()
                
    def close_window(self):
        self.window.destroy()
        self.exit()


    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        enableQueue = self.addOperation("Queue", lambda: self.clickEnableQueue())
        # enableQueue.grid(row=0, column=1)
        enableDeque = self.addOperation("Deque", lambda: self.clickEnableDeque())
        # enableDeque.grid(row=0, column=3)
        # traverseButton = self.addOperation(
        #     "Traverse", lambda: self.traverse())
        # findButton = self.addOperation(
        #     "Find", lambda: self.clickFind(), numArguments=1,
        #     validationCmd=vcmd)
        # insertButton = self.addOperation(
        #     "Insert", lambda: self.clickInsert(), numArguments=1,
        #     validationCmd=vcmd)
        # deleteValueButton = self.addOperation(
        #     "Delete", lambda: self.clickDelete(), numArguments=1,
        #     validationCmd=vcmd)
        # deleteRightmostButton = self.addOperation(
        #     "Delete Rightmost", lambda: self.removeFromEnd())
        # return [findButton, insertButton, deleteValueButton,
        #         deleteRightmostButton, traverseButton]
        insertRearButton = self.addOperation("Insert At Rear", lambda: self.clickInsertRear(),
                                             numArguments=1, validationCmd=vcmd)
        # insertRearButton.grid(row=3, column=0)
        insertFrontButton = self.addOperation("Insert At Front", lambda: self.clickInsertFront(),
                                              numArguments=1, validationCmd=vcmd)
        # insertFrontButton.grid(row=4, column=0)
        deleteRearButton = self.addOperation("Delete From End", lambda: self.removeRear())
        # deleteRearButton.grid(row=3, column=0)
        deleteFrontButton = self.addOperation("Delete From Front", lambda: self.removeFront())
        # deleteFrontButton.grid(row=4, column=0)

        buttons = [insertRearButton, insertFrontButton, deleteRearButton, deleteFrontButton, enableQueue, enableDeque]
        return buttons

# validate text entry
def validate(action, index, value_if_allowed,
             prior_value, text, validation_type, trigger_type, widget_name):
    if text in '0123456789':
        return True
    else:
        return False

if __name__ == '__main__':
    queue = Queue()

    queue.runVisualization()