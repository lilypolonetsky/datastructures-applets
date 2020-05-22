__doc__ = """
Base class for Python visualizations.
Provides common tools for all modules including control panel
and drawing canvas.
The control panel has containers for
 * Functions that take an argument
 * Functions that take no argument
 * A speed control for slow to fast animation or single step increments
 * A text message area for providing messages
"""

import time, math, operator
from collections import *
from tkinter import *

# Default styles for display of values and operational controls
FONT_SIZE = 20
VALUE_FONT = ('Helvetica', FONT_SIZE)
VALUE_COLOR = 'black'
VARIABLE_FONT = ('Courier', FONT_SIZE * 8 // 10)
VARIABLE_COLOR = 'brown3'
FOUND_FONT = ('Helvetica', FONT_SIZE)
FOUND_COLOR = 'green2'
OPERATIONS_BG = 'beige'
OPERATIONS_BORDER = 'black'
CONTROLS_FONT = ('none', 14)

scaleDefault = 100

# Utilities for vector math; used for canvas item coordinates
def add_vector(v1, v2):
    return tuple(map(operator.add, v1, v2))

def subtract_vector(v1, v2):
    return tuple(map(operator.sub, v1, v2))

def divide_vector(v1, v2):  # v2 can be scalar
    if not isinstance(v2, (list, tuple)):
        v2 = [v2] * len(v1) # Copy scalar value for vector dimension
    return tuple(map(operator.truediv, v1, v2))

def multiply_vector(v1, v2):  # v2 can be scalar
    if not isinstance(v2, (list, tuple)):
        v2 = [v2] * len(v1) # Copy scalar value for vector dimension
    return tuple(map(operator.mul, v1, v2))

def rotate_vector(v1, angle=0): # Rotate vector by angle degrees
    s, c = math.sin(math.radians(angle)), math.cos(math.radians(angle))
    return (sum(multiply_vector(v1, (c, s))), sum(multiply_vector(v1, (-s, c))))

def gridDict(frame):
    slaves = frame.grid_slaves()
    return defaultdict(
        lambda: None,
        zip([(int(s.grid_info()['column']), int(s.grid_info()['row']))
             for s in slaves],
            slaves))

# Utilities for validating characters typed in Tk entry widgets
# These must be registered with the parent window before use
def numericValidate(action, index, value_if_allowed,
             prior_value, text, validation_type, trigger_type, widget_name):
    return len(value_if_allowed) == 0 or value_if_allowed.isdigit()

class VisualizationApp(object): # Base class for Python visualizations
    def __init__(            # Constructor
            self, 
            window=None,     # Run visualization within given window
            title=None,
            canvasWidth=800, # Canvas size
            canvasHeight=400,
            ):
        # Set up Tk windows for canvas and operational controls
        if window:
            self.window = window
        else:
            self.window = Tk()
            if title:
                self.window.title(title)
        self.canvas = Canvas(
            self.window, width=canvasWidth, height=canvasHeight)            
        self.canvas.pack(expand=True, fill=BOTH)
        self.setUpControlPanel()

        # Set up instance variables for managing animations and operations
        self.cleanup = []    # Tk items to remove before next operation
        
    def setUpControlPanel(self):  # Set up control panel structure
        self.controlPanel = Frame(self.window)
        self.controlPanel.pack(side=BOTTOM, fill=X)
        self.operationsUpper = LabelFrame(self.controlPanel, text="Operations")
        self.operationsUpper.pack(side=TOP)
        self.operationsBorder = Frame(
            self.operationsUpper, padx=2, pady=2, bg=OPERATIONS_BORDER)
        self.operationsBorder.pack(side=TOP)
        self.operations = Frame(self.operationsBorder, bg=OPERATIONS_BG)
        self.opSeparator = None
        self.operations.pack(side=LEFT)
        self.operationsLower = Frame(self.controlPanel)
        self.operationsLower.pack(side=TOP, fill=X)
        self.operationsLowerCenter = Frame(self.operationsLower, padx=2, pady=5)
        self.operationsLowerCenter.pack(side=TOP)
        
        self.speedControl = None
        self.speedScale = Scale(
            self.operationsLowerCenter, from_=1, to=200, orient=HORIZONTAL,
            showvalue=False, sliderlength=20)
        self.speedScale.grid(row=0, column=1, sticky=W)
        self.speedScale.set(scaleDefault)
        self.slowLabel = Label(
            self.operationsLowerCenter, text="Animation speed:  slow", 
            font=CONTROLS_FONT)
        self.slowLabel.grid(row=0, column=0, sticky=W)
        self.fastLabel = Label(
            self.operationsLowerCenter, text="fast", font=CONTROLS_FONT)
        self.fastLabel.grid(row=0, column=2, sticky=W)
        self.waitVar = BooleanVar()
        self.pauseButton = None
        self.outputText = StringVar()
        self.outputText.set('')
        self.message = Label(
            self.operationsLowerCenter, textvariable=self.outputText,
            font=CONTROLS_FONT + ('italic',), fg="blue")
        self.message.grid(row=0, column=4, sticky=(E, W))
        self.operationsLowerCenter.grid_columnconfigure(4, minsize=200)
        self.operationsLowerCenter.grid_columnconfigure(3, minsize=10)

    def addOperation(        # Add a button to the operations control panel
            self,            # The button can be depedent on an argument
            label,           # provided in the text entry widget. Button label
            callback,        # Function to call when button pressed
            hasArgument=False, # Flag indicating whether argument required
            validationCmd=None, # Tk validation command tuple for argument
            helpText=None,   # Help text for argument (erased on first keypress)
            maxRows=4,       # Operations w/o args beyond maxRows -> new columns
            **kwargs):       # Tk button keywoard args
        gridItems = gridDict(self.operations) # Operations inserted in grid
        nColumns, nRows = self.operations.grid_size()
        withArgument = [
            gridItems[0, row] for row in range(nRows)
            if isinstance(gridItems[0, row], Button)]
        withoutArgument = [
            gridItems[col, row]
            for row in range(nRows) for col in range(4, nColumns)
            if isinstance(gridItems[col, row], Button)]
        button = Button(self.operations, text=label, command=callback)
        if hasArgument:
            if len(withArgument) == 0: # For first command with argument,
                self.textEntry = Entry( # create entry box for argument
                    self.operations, width=20, bg='white', validate='key',
                    validatecommand=validationCmd)
                self.textEntry.grid(column=2, row=1, padx=8, sticky=E)
                self.textEntry.bind(
                    '<KeyRelease>', lambda ev: self.argumentChanged(), '+')
            buttonRow = len(withArgument) + 1
            button.grid(column=0, row=buttonRow, padx = 8, sticky=(E, W))
            button.config(state=DISABLED)
            self.textEntry.grid_configure(rowspan=len(withArgument) + 1)
        else:
            buttonRow = len(withoutArgument) % maxRows + 1
            button.grid(column=4 + len(withoutArgument) // maxRows,
                        row=buttonRow, padx = 8, sticky=(E, W))
        if ((len(withoutArgument) if hasArgument else len(withArgument)) > 0 and
            not self.opSeparator): # If both kinds of buttons are present
            self.opSeparator = Frame( # but not a separator line, create one
                self.operations, width=2, bg=OPERATIONS_BORDER)
            self.opSeparator.grid(column=3, row=1, sticky=(N, E, W, S))
        if self.opSeparator:
            self.opSeparator.grid_configure(rowspan=max(nRows, buttonRow))
        return button

    def argumentChanged(self):
        arg = self.getArgument()
        gridItems = gridDict(self.operations) # All operations 
        nColumns, nRows = self.operations.grid_size()
        for button in [gridItems[0, row] for row in range(nRows)
                       if isinstance(gridItems[0, row], Button)]:
            button.config(state = DISABLED if arg == '' else NORMAL)
        
    def getArgument(self, clear=False):
        if hasattr(self, 'textEntry'):
            return self.textEntry.get()

    def clearArgument(self):
        if hasattr(self, 'textEntry'):
            self.textEntry.delete(0, END)
            self.argumentChanged()

    def setArgument(self, val=''):
        if hasattr(self, 'textEntry'):
            self.textEntry.delete(0, END)
            self.textEntry.insert(0, str(val))
            self.argumentChanged()

    def setMessage(self, val=''):
        self.outputText.set(val)

    def cleanUp(self):     # Remove Tk items from past operations
        while len(self.cleanup):
            thing = self.cleanup.pop()
            if isinstance(thing, (str, int)):
                self.canvas.delete(thing)
        self.setMessage()  # Clear any messages
        
    # CANVAS ITEM METHODS
    def canvas_itemconfigure( # Get a dictionary with the canvas item's
            self, canvasitem): # configuration
        config = self.canvas.itemconfigure(canvasitem)
        for key in config:   # Replace tuple values with the last item
            if isinstance(config[key], tuple): # in tuple
                config[key] = config[key][-1]
        return config

    def copyCanvasItem(      # Make a copy of an item in the canvas
            self, canvasitem):
        creator = getattr(self.canvas, # Get canvas creation function for type
                          'create_{}'.format(self.canvas.type(canvasitem)))
        return creator(*self.canvas.coords(canvasitem),
                       **self.canvas_itemconfigure(canvasitem))

    def moveItemsBy(         # Animate canvas items moving from their current
            self, items,     # location along a line indicated by a delta vector
            delta,           # Can be a single item or list/tuple of items
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        if not isinstance(items, (list, tuple)):
            items = tuple(items)
        if not isinstance(delta, (list, tuple)) or len(delta) != 2:
            raise ValueError('Delta must be a 2-dimensional vector')

        # move the items in steps along vector
        moveBy = divide_vector(delta, steps)
        for step in range(steps):
            for item in items:
                self.canvas.move(item, *moveBy)
            self.window.update()
            time.sleep(self.speed(sleepTime))

    def moveItemsTo(         # Animate canvas items moving from their current
            self, items,     # location to destination locations along a line
            toPositions,     # Can be a single item or list of items
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        if not isinstance(items, (list, tuple)):
            items = tuple(items)
        if not isinstance(toPositions, (list, tuple)):
            raise ValueError('toPositions must be a list or tuple of positions')
        if not isinstance(toPositions[0], (list, tuple)):
            toPositions = tuple(toPositions)
        moveBy = [divide_vector(subtract_vector(toPos, fromPos), steps)
                  for toPos, fromPos in zip(
                          toPositions,
                          map(lambda c: self.canvas.coords(c)[:2], items))]

        # move the items until they reach the toPositions
        for step in range(steps):
            for i, item in enumerate(items):
                self.canvas.move(item, *moveBy[i])
            self.window.update()
            time.sleep(self.speed(sleepTime))
            
        # Force position of new objects to their exact destinations
        for pos, item in zip(toPositions, items):
            self.canvas.coords(item, *pos)

    def moveItemsOnCurve(    # Animate canvas items moving from their current
            self, items,     # location to destinations along a curve
            toPositions,     # Can be a single item or list of items
            startAngle=90,   # Starting angle away from destination 
            steps=10,        # Number of intermediate steps to reach destination
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        if not isinstance(items, (list, tuple)):
            items = tuple(items)
        if not isinstance(toPositions, (list, tuple)):
            raise ValueError('toPositions must be a list or tuple of positions')
        if not isinstance(toPositions[0], (list, tuple)):
            toPositions = tuple(toPositions)

        # move the items until they reach the toPositions
        for step in range(steps): # Go through all steps of the annimation
            toGo = steps - 1 - step # remaining steps to go
            ang = startAngle * toGo / steps # angle decreases on each step
            scale = 1 + abs(ang) / 180 # scale is larger for higher angles
            for i, item in enumerate(items):
                coords = self.canvas.coords(item)[:2]
                moveBy = rotate_vector(
                    divide_vector(subtract_vector(toPositions[i], coords),
                                  (toGo + 1) / scale),
                    ang)
                self.canvas.move(item, *moveBy)
            self.window.update()
            time.sleep(self.speed(sleepTime))
            
        # Force position of new objects to their exact destinations
        for pos, item in zip(toPositions, items):
            self.canvas.coords(item, *pos)
        
    # ANIMATION METHODS
    def speed(self, sleepTime):
        return (sleepTime * (scaleDefault + 50)) / (self.speedScale.get() + 50)

    def stop(pauseButton):
        self.running = False

        if self.waitVar.get():
            play(self.pauseButton)

    def pause(pauseButton):
        self.waitVar.set(True)

        pauseButton['text'] = "Play"
        pauseButton['command'] = lambda: onClick(play, pauseButton)

        self.canvas.wait_variable(waitVar)

    def play(pauseButton):
        self.waitVar.set(False)

        pauseButton['text'] = 'Pause'
        pauseButton['command'] = lambda: onClick(pause, pauseButton)

    def runVisualization(self):
        self.window.mainloop()
