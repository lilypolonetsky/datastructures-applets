from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *



class Queue(VisualizationApp):
    WIDTH = 800
    HEIGHT = 400
    CELL_SIZE = 50
    ARRAY_X0 = 100
    ARRAY_Y0 = 100
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
        self.insertButton = None
        self.deleteButton=None
        self.display()

    def __str__(self):
        return str(self.list)
    
    # ANIMATION METHODS
    def createIndex(  # Create an index arrow to point at an indexed
            self, index=-1, name=None, high=True):  # cell with an optional name label

        coords = [self.ARRAY_X0 + self.CELL_SIZE * index, self.ARRAY_Y0, self.ARRAY_X0 + self.CELL_SIZE * (index + 1), self.ARRAY_Y0 + self.CELL_SIZE]

        x0 = coords[0]+self.CELL_SIZE//2
        x1 = x0
        y0 = coords[1] - self.CELL_SIZE * 2 // 2
        y1 = coords[1] - self.CELL_SIZE * 1 // 4
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
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        #if is full does not insert
        if self.nItems==self.size:
            self.setMessage('Queue is full!')
            return None

        #if there's a space to insert into
        color = drawable.palette[self.nextColor]
        # increment nextColor
        self.nextColor = (self.nextColor + 1) % len(drawable.palette)
        # deal with wraparound
        if self.rear == self.size - 1:  # deal with wraparound
            self.rear = -1
            self.moveItemsBy(self.rearArrow, (self.CELL_SIZE * self.size * -1, 0))
        #move arrow
        self.moveItemsBy(self.rearArrow, (self.CELL_SIZE, 0))
        # increment rear
        self.rear += 1

        # create new cell and cell value display objects
        # Start drawing new one at rear
        cell = self.canvas.create_rectangle(self.ARRAY_X0+self.CELL_SIZE*self.rear, self.ARRAY_Y0, \
                                       self.ARRAY_X0+self.CELL_SIZE*(self.rear+1), self.ARRAY_Y0 + self.CELL_SIZE, \
                                       fill=color, outline='')
        cell_val = self.canvas.create_text(self.ARRAY_X0+self.CELL_SIZE*self.rear + (self.CELL_SIZE / 2), \
                                      self.ARRAY_Y0 + (self.CELL_SIZE / 2), text=val, font=('Helvetica', '20'))

       # insert the item
        self.list[self.rear] = drawable(val, color, cell, cell_val)
        #increment number of items
        self.nItems += 1

        self.onOffButtons()
        # update window
        self.window.update()
        self.cleanUp(callEnviron)
        self.stopAnimations()

    # remove the left element of the queue, or None if empty
    def removeFront(self):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        #if the queue is empty, exit
        if self.nItems == 0:
            self.setMessage('Queue is empty!')
            return None

        #get the value at front, and then set it to None so it will be garbage collected
        n = self.list[self.front]
        self.list[self.front] = None
        
        #increment front
        self.front += 1
        # delete the associated display objects
        self.canvas.delete(n.display_shape)
        self.canvas.delete(n.display_val)
        #deal with wraparound
        if self.front == self.size:
            self.front = 0
            self.moveItemsBy(self.frontArrow, (self.CELL_SIZE * self.size * -1, 0))
        #move arrow
        self.moveItemsBy(self.frontArrow, (self.CELL_SIZE, 0))
        #decrement number of arrows
        self.nItems -= 1

        # update window
        self.onOffButtons()
        self.cleanUp(callEnviron)
        self.stopAnimations()
        self.window.update()

    
    def display(self):

        self.canvas.delete("all")

        self.makeButtons()
        self.onOffButtons()
        xpos = self.ARRAY_X0
        ypos = self.ARRAY_Y0

        for i in range(self.size):
            self.canvas.create_rectangle(xpos + self.CELL_SIZE*i, ypos, xpos + self.CELL_SIZE*(i+1), ypos + self.CELL_SIZE, fill='white', outline='black')

        # go through each Element in the list
        for n in self.list:
            
            # Only loop through the existing elements
            if n:

                # create display objects for the associated Elements
                cell = self.canvas.create_rectangle(xpos, ypos, xpos+self.CELL_SIZE, ypos+self.CELL_SIZE, fill=n[1], outline='')
                cell_val = self.canvas.create_text(xpos+(self.CELL_SIZE/2), ypos+(self.CELL_SIZE/2), text=n[0], font=('Helvetica', '20'))
    
                # save the display objects to the appropriate attributes of the Element object
                n.display_shape = cell
                n.display_val = cell_val
    
                # increment xpos
                xpos += self.CELL_SIZE

        self.rearArrow = self.createIndex(self.rear, "Rear", high=False)
        self.frontArrow = self.createIndex(self.front, "Front", high=True)
        self.window.update()

    #disable insert if queue if full, disable delete if empty
    #enable everything else without overriding queue/deque functionality
    def onOffButtons(self):

        #disable buttons as necessary
        if self.nItems == self.size:
            self.insertButton.config(state = DISABLED)
        elif self.nItems==0:
            self.deleteButton.config(state = DISABLED)


# Button functions

    def clickInsertRear(self):
        entered_text = self.getArgument()
        if entered_text:
            val = int(entered_text)
            if val < 100:
                self.insertRear(int(entered_text))

            else:
                self.setMessage("Input value must be an integer from 0 to 99.")
            self.clearArgument()
                
    def close_window(self):
        self.window.destroy()
        self.exit()

    def startAnimations(self):
        self.onOffButtons()
        super().startAnimations()

    def stopAnimations(self):
        super().stopAnimations()
        self.onOffButtons()
        self.argumentChanged()

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.insertButton = self.addOperation("Insert", lambda: self.clickInsertRear(),
                                             numArguments=1, validationCmd=vcmd)

        self.deleteButton = self.addOperation("Delete", lambda: self.removeFront())


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