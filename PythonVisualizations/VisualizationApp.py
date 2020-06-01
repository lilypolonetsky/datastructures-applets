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

import time, math, operator, re
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
CODE_FONT = ('Courier', 12)
CODE_HIGHLIGHT = 'yellow'
CONTROLS_FONT = ('none', 14)

# Speed control slider
SPEED_SCALE_MIN = 10
SPEED_SCALE_MAX = 500
SPEED_SCALE_DEFAULT = (SPEED_SCALE_MIN + SPEED_SCALE_MAX) // 2

# Animation states
STOPPED = 0
RUNNING = 1
PAUSED = 2

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

geom_delims = re.compile(r'[\sXx+-]')

class VisualizationApp(object): # Base class for Python visualizations
    def __init__(            # Constructor
            self, 
            window=None,     # Run visualization within given window
            title=None,
            canvasWidth=800, # Canvas size
            canvasHeight=400,
            maxArgWidth=3,   # Maximum length/width of text arguments
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
        self.maxArgWidth = maxArgWidth

        # Set up instance variables for managing animations and operations
        self.cleanup = set()    # Tk items to remove before next operation
        self.animationState = STOPPED
        
    def setUpControlPanel(self):  # Set up control panel structure
        self.controlPanel = Frame(self.window)
        self.controlPanel.pack(side=BOTTOM, fill=X)
        self.operationsUpper = LabelFrame(self.controlPanel, text="Operations")
        self.operationsUpper.grid(row=0, column=0)
        self.operationsBorder = Frame(
            self.operationsUpper, padx=2, pady=2, bg=OPERATIONS_BORDER)
        self.operationsBorder.pack(side=TOP)
        self.operations = Frame(self.operationsBorder, bg=OPERATIONS_BG)
        self.opSeparator = None
        self.operations.pack(side=LEFT)
        self.operationsLower = Frame(self.controlPanel)
        self.operationsLower.grid(row=1, column=0)
        self.operationsLowerCenter = Frame(self.operationsLower, padx=2, pady=5)
        self.operationsLowerCenter.pack(side=TOP)
        self.codeFrame = Frame(self.controlPanel)
        self.codeFrame.grid(row=0, column=1, rowspan=2, sticky=(N, E, S, W))
        # self.controlPanel.grid_columnconfigure(1, maxsize=200)
        self.codeText = None
        
        self.speedControl = None
        self.speedScale = Scale(
            self.operationsLowerCenter, orient=HORIZONTAL,
            from_=SPEED_SCALE_MIN, to=SPEED_SCALE_MAX, 
            showvalue=False, sliderlength=20)
        self.speedScale.grid(row=0, column=1, sticky=W)
        self.speedScale.set(SPEED_SCALE_DEFAULT)
        self.slowLabel = Label(
            self.operationsLowerCenter, text="Animation speed:  slow", 
            font=CONTROLS_FONT)
        self.slowLabel.grid(row=0, column=0, sticky=W)
        self.fastLabel = Label(
            self.operationsLowerCenter, text="fast", font=CONTROLS_FONT)
        self.fastLabel.grid(row=0, column=2, sticky=W)
        self.pauseButton = None
        self.textEntries = []
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
            numArguments=0,  # Count of required user entered arguments
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
        button = Button(self.operations, text=label, command=callback,
                        bg=OPERATIONS_BG)
        setattr(button, 'required_args', numArguments)
        if numArguments:
            while len(self.textEntries) < numArguments: # Build argument entry
                textEntry = Entry( # widgets if not already present
                    self.operations, width=self.maxArgWidth, bg='white',
                    validate='key', validatecommand=validationCmd)
                textEntry.grid(column=2, row=len(self.textEntries) + 1,
                                    padx=8, sticky=E)
                textEntry.bind(
                    '<KeyRelease>', lambda ev: self.argumentChanged(), '+')
                self.textEntries.append(textEntry)
            buttonRow = len(withArgument) + 1
            button.grid(column=0, row=buttonRow, padx = 8, sticky=(E, W))
            button.config(state=DISABLED)
            rowSpan = len(withArgument) + 1 // len(self.textEntries) 
            for textEntry in self.textEntries: # Spread text entries across
                textEntry.grid_configure(  # all rows of buttons with arguments
                    rowspan=rowSpan if textEntry != self.textEntries[-1] else
                    len(withArgument)+1 - (len(self.textEntries) - 1) * rowSpan)
        else:
            buttonRow = len(withoutArgument) % maxRows + 1
            button.grid(column=4 + len(withoutArgument) // maxRows,
                        row=buttonRow, padx = 8, sticky=(E, W))
        if ((len(withoutArgument) if numArguments else len(withArgument)) > 0
            and not self.opSeparator): # If both kinds of buttons are present
            self.opSeparator = Frame( # but not a separator line, create one
                self.operations, width=2, bg=OPERATIONS_BORDER)
            self.opSeparator.grid(column=3, row=1, sticky=(N, E, W, S))
        if self.opSeparator:
            self.opSeparator.grid_configure(rowspan=max(nRows, buttonRow))
        return button

    def addAnimationButtons(self):
        self.pauseButton = self.addOperation(
            "Pause", lambda: self.onClick(self.pause, self.pauseButton))
        self.pauseButton['state'] = DISABLED
        self.stopButton = self.addOperation(
            "Stop", lambda: self.onClick(self.stop, self.pauseButton))
        self.stopButton['state'] = DISABLED
        
    def argumentChanged(self):
        args = self.getArguments()
        gridItems = gridDict(self.operations) # All operations 
        nColumns, nRows = self.operations.grid_size()
        for button in [gridItems[0, row] for row in range(nRows)
                       if isinstance(gridItems[0, row], Button)]:
            nArgs = getattr(button, 'required_args')
            button['state'] = (
                DISABLED if any(arg == '' for arg in args[:nArgs]) else NORMAL)
        
    def getArguments(self, clear=False):
        return [self.getArgument(i, clear=clear)
                for i in range(len(self.textEntries))]
    
    def getArgument(self, index=0, clear=False):
        if 0 <= index and index < len(self.textEntries):
            val = self.textEntries[index].get()
            if clear:
                self.clearArgument(index)
            return val

    def clearArgument(self, index=0):
        if 0 <= index and index < len(self.textEntries):
            self.textEntries[index].delete(0, END)
            self.argumentChanged()

    def setArgument(self, val='', index=0):
        if 0 <= index and index < len(self.textEntries):
            self.textEntries[index].delete(0, END)
            self.textEntries[index].insert(0, str(val))
            self.argumentChanged()

    def setMessage(self, val=''):
        self.outputText.set(val)

    def showCode(self, code): # Show algorithm code in a scrollable text box
        if self.codeText is None:
            self.codeText = Text(
                self.codeFrame, wrap=NONE, background=OPERATIONS_BG, 
                font=CODE_FONT, width=40, height=12, padx=10, pady=10,
                takefocus=False)
            self.codeText.grid(row=0, column=0, sticky=(N, E, S, W))
            self.codeVScroll = Scrollbar(
                self.codeFrame, orient=VERTICAL, command=self.codeText.yview)
            self.codeVScroll.grid(row=0, column=1, rowspan=2, sticky=(N, S))
            self.codeHScroll = Scrollbar(
                self.codeFrame, orient=HORIZONTAL, command=self.codeText.xview)
            self.codeHScroll.grid(row=1, column=0, sticky=(E, W))
            self.codeText['xscrollcommand'] = self.codeHScroll.set
            self.codeText['yscrollcommand'] = self.codeVScroll.set
        else:
            self.codeText.configure(state=NORMAL)
            self.codeText.delete("1.0", END)
        self.codeText.insert("1.0", code)
        self.codeText.configure(state=DISABLED)

    def createCodeTags(self, snippets):
        self.codeText.tag_delete(*self.codeText.tag_names())
        for tagName in snippets:
            self.codeText.tag_add(tagName, *snippets[tagName])

    def highlightCodeTags(self, tags):
        if not isinstance(tags, (list, tuple)):
            tags = [tags]
        for tagName in self.codeText.tag_names():
            highlight = tagName in tags
            self.codeText.tag_config(
                tagName, 
                background=CODE_HIGHLIGHT if highlight else OPERATIONS_BG,
                underline=1 if highlight else 0)
            if highlight:
                ranges = self.codeText.tag_ranges(tagName)
                if len(ranges) > 0:
                    self.codeText.see(ranges[0])
            
    def cleanUp(self):     # Remove Tk items from past operations
        while len(self.cleanup):
            thing = self.cleanup.pop()
            if isinstance(thing, (str, int)):  # Canvas item IDs
                self.canvas.delete(thing)
        self.setMessage()  # Clear any messages
        while len(self.codeFrame.children) > 0: # Remove any code being shown
            tkItem = self.codeFrame.children.popitem()
            tkItem[1].destroy()
        self.codeText = None

    # Tk widget methods
    def widgetDimensions(self, widget): # Get widget's (width, height)
        geom = geom_delims.split(widget.winfo_geometry())
        if geom[0] == '1' and geom[1] == '1': # If not yet managed, use config
            geom = (widget.config('width')[-1], widget.config('height')[-1])
        return int(geom[0]), int(geom[1])
        
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
        newItem = creator(*self.canvas.coords(canvasitem),
                       **self.canvas_itemconfigure(canvasitem))
        for eventType in self.canvas.tag_bind(canvasitem): # Copy event handlers
            self.canvas.tag_bind(newItem, eventType,
                                 self.canvas.tag_bind(canvasitem, eventType))
        return newItem

    def moveItemsOffCanvas(  # Animate the removal of canvas items by sliding
            self, items,     # them off one of the canvas edges
            edge=N,          # One of the 4 tkinter edges: N, E, S, or W
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        if not isinstance(items, (list, tuple)):
            items = tuple(items)
        curPositions = [self.canvas.coords(i) for i in items]
        bboxes = [self.canvas.bbox(i) for i in items]
        bbox = bboxes[0]     # Get bounding box of all items
        for bb in bboxes[1:]:
            bbox = [min(bbox[0], bb[0]), min(bbox[1], bb[1]),
                    max(bbox[2], bb[2]), max(bbox[3], bb[3])]
        canvasDimensions = self.widgetDimensions(self.canvas)
        # Compute delta vector that moves them on a line away from the
        # center of the canvas
        delta = ((bbox[0] + bbox[2] - canvasDimensions[0]) / 2 ,
                 0 - bbox[3])
        if edge == S:
            delta = (delta[0], canvasDimensions[1] - bbox[1])
        elif edge in (W, E):
            delta = (0 - bbox[2],
                     (bbox[1] + bbox[3] - canvasDimensions[1]) / 2)
            if edge == E:
                delta = (canvasDimensions[0] - bbox[0], delta[1])
        # Ensure no more that 45 degree angle to departure boundary
        if abs(delta[0]) > abs(delta[1]) and edge not in (E, W):
            delta = (delta[1] * (-1 if delta[0] < 0 else 1), delta[1])
        elif abs(delta[0]) < abs(delta[1]) and edge not in (N, S):
            delta = (delta[0], delta[0] * (-1 if delta[1] < 0 else 1))
        self.moveItemsBy(items, delta, steps=steps, sleepTime=sleepTime)
    
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
            if sleepTime > 0:
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
        return sleepTime * 50 * SPEED_SCALE_MIN / self.speedScale.get()

    def wait(self, sleepTime):    # Sleep for a user-adjusted period and return
        if self.animationState == STOPPED: # a flag indicating if the user
            return True           # has stopped the animation
        if sleepTime > 0:
            time.sleep(self.speed(sleepTime))
        return self.animationState == STOPPED

    def onClick(self, command, *parameters):
        self.enableButtons(False)
        command(*parameters)
        if command not in [self.pause, self.play]:
            self.enableButtons()
        
    def stop(self, pauseButton):
        self.stopAnimations()
        pauseButton['text'] = "Play"
        pauseButton['command'] = lambda: self.onClick(self.play, pauseButton)

    def pause(self, pauseButton):
        self.pauseAnimations()
        pauseButton['text'] = "Play"
        pauseButton['command'] = lambda: self.onClick(self.play, pauseButton)
        while self.animationState == PAUSED:
            time.sleep(0.05)
            self.window.update()

    def play(self, pauseButton):
        self.startAnimations()
        
    def startAnimations(self):
        self.animationState = RUNNING
        self.pauseButton['text'] = 'Pause'
        self.pauseButton['command'] = lambda: self.onClick(
            self.pause, self.pauseButton)
        self.pauseButton['state'] = NORMAL
        self.stopButton['state'] = NORMAL

    def stopAnimations(self):
        self.animationState = STOPPED
        self.pauseButton['state'] = DISABLED
        self.stopButton['state'] = DISABLED

    def pauseAnimations(self):
        self.animationState = PAUSED

    def runVisualization(self):
        self.window.mainloop()
