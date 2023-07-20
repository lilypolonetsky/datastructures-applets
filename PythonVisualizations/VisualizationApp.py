__doc__ = """
Base class for Python visualization applications, built on top of
the basic Visualization class.
Provides common user interface tools for all modules including control panel.
The control panel has containers for
 * Functions that take an argument
 * Functions that take no argument
 * A speed control for slow to fast animation or single step increments
 * A text message area for providing messages
 * A text window for showing and highlighting code snippets
"""

import time, re, pdb, sys, os.path, threading
from collections import *
from tkinter import *
from tkinter import ttk

try:
    from TextHighlight import *
    from tkUtilities import *
    from Visualization import *
except ModuleNotFoundError:
    from .TextHighlight import *
    from .tkUtilities import *
    from .Visualization import *
    
def gridDict(frame):    # Get all widget's within a frame's grid indexed by
    slaves = frame.grid_slaves() # their grid cooordinates (col, row)
    return defaultdict(
        lambda: None,
        zip([(int(s.grid_info()['column']), int(s.grid_info()['row']))
             for s in slaves],
            slaves))

# Utilities for validating characters typed in Tk entry widgets
# These must be registered with the parent window before use
def numericValidate(action, index, value_if_allowed, prior_value, text,
                    validation_type, trigger_type, widget_name):
    return len(value_if_allowed) == 0 or value_if_allowed.isdigit()

def makeWidthValidate(maxWidth):
    "Register this with one parameter: %P"
    return lambda value_if_allowed: len(value_if_allowed) <= maxWidth
        
def makeFilterValidate(maxWidth, exclude=''):
    "Register this with one parameter: %P"
    return lambda value_if_allowed: (
        len(value_if_allowed) <= maxWidth and
        all(c not in exclude for c in value_if_allowed))

class VisualizationApp(Visualization): # Base class for visualization apps

    # Default styles for display of operational controls
    OPERATIONS_BG = 'beige'
    OPERATIONS_BORDER = 'black'
    CODE_FONT = ('Courier', -12)
    CODE_HIGHLIGHT = 'yellow'
    EXCEPTION_HIGHLIGHT = 'orange'
    CONTROLS_FONT = ('Helvetica', -12)
    CONTROLS_COLOR = 'blue'
    HINT_FONT = CONTROLS_FONT + ('italic',)
    HINT_FG = 'blue'
    HINT_BG = 'beige'
    ENTRY_BG = 'white'
    ERROR_HIGHLIGHT = 'tomato'
    CALL_STACK_BOUNDARY = 'gray60'

    # Code text box
    MIN_CODE_CHARACTER_WIDTH = 20
    MIN_CODE_CHARACTER_HEIGHT = 12
    
    # Speed control slider
    SPEED_SCALE_MIN = 10
    SPEED_SCALE_MAX = 500
    SPEED_SCALE_DEFAULT = (SPEED_SCALE_MIN + SPEED_SCALE_MAX) // 2
    DEBUG = False

    def __init__(  # Constructor
            self,
            maxArgWidth=3,    # Maximum length/width of text arguments
            hoverDelay=500,   # Milliseconds to wait before showing hints
            **kwargs):
        super().__init__(**kwargs)

        self.maxArgWidth = maxArgWidth
        self.HOVER_DELAY = hoverDelay

        # Set up instance variables for managing animations and operations
        self.callStack = []    # Stack of local environments for visualziation

        self.operationMutex = threading.Lock()
        self.pauseButton, self.stopButton, self.stepButton = None, None, None
        self.stepPause = False
        self.lastHighlights = self.callStackHighlights()
        self.modifierKeyState = 0
        self.debugRequested = False
        self.tw, self.entryHint = None, None
        self.createPlayControlImages()
        self.setUpControlPanel()
        self.window.bind('<Unmap>', self.clearHintHandler(), '+')
 
    def setUpControlPanel(self):  # Set up control panel structure
        self.controlPanel = Frame(self.window, bg=self.DEFAULT_BG)
        self.controlPanel.pack(side=BOTTOM, expand=False, fill=X)
        self.operationsUpper = LabelFrame(
            self.controlPanel, text="Operations", bg=self.DEFAULT_BG)
        self.operationsUpper.grid(row=0, column=0)
        self.opButtons = []
        self.operationsPadding = Frame(
            self.operationsUpper, padx=2, pady=2, bg=self.OPERATIONS_BORDER)
        self.operationsPadding.pack(side=TOP)
        self.operations = Frame(self.operationsPadding, bg=self.OPERATIONS_BG)
        self.opSeparator = None
        self.operations.pack(side=LEFT)
        self.operationsLower = Frame(self.controlPanel, bg=self.DEFAULT_BG)
        self.operationsLower.grid(row=1, column=0)
        self.operationsLowerCenter = Frame(
            self.operationsLower, padx=2, pady=5, bg=self.DEFAULT_BG)
        self.operationsLowerCenter.pack(side=TOP)
        self.codeFrame = Frame(self.controlPanel, bg=self.DEFAULT_BG)
        self.codeFrame.grid(row=0, column=1, rowspan=2, sticky=(N, E, S, W))
        self.codeText = None

        self.speedControl = None
        self.speedScale = Scale(
            self.operationsLowerCenter, orient=HORIZONTAL,
            from_=self.SPEED_SCALE_MIN, to=self.SPEED_SCALE_MAX,
            showvalue=False, sliderlength=20)
        self.speedScale.grid(row=0, column=1, sticky=W)
        self.speedScale.set(self.SPEED_SCALE_DEFAULT)
        self.slowLabel = Label(
            self.operationsLowerCenter, text="Animation speed:  slow",
            font=self.CONTROLS_FONT, bg=self.DEFAULT_BG)
        self.slowLabel.grid(row=0, column=0, sticky=W)
        self.fastLabel = Label(
            self.operationsLowerCenter, text="fast", font=self.CONTROLS_FONT,
            bg=self.DEFAULT_BG)
        self.fastLabel.grid(row=0, column=2, sticky=W)
        self.textEntries, self.entryHint = [], None
        self.messageText = StringVar()
        self.messageText.set('')
        self.message = Label(
            self.operationsLowerCenter, textvariable=self.messageText,
            font=self.CONTROLS_FONT + ('italic',), fg="blue",
            bg=self.DEFAULT_BG)
        self.message.grid(row=0, column=4, sticky=(E, W))
        self.operationsLowerCenter.grid_columnconfigure(4, minsize=200)
        self.operationsLowerCenter.grid_columnconfigure(3, minsize=10)

    def newValueCoords(self, buffer=30, offCanvas=False):
        '''Return a set of canvas coords that are below the canvas
        somewhere behind the control panel.  New values can be centered
        on these coordinates to make them appear as if they are coming from
        the control panel.  If the canvas is taller than the visible portion,
        the the new coordinates are placed off the canvas when offCanvas is
        true.'''
        visibleCanvas = self.visibleCanvas()
        maxY = (self.canvasBounds[3] if self.canvasBounds and offCanvas else
                visibleCanvas[3])
        upperDims = widgetDimensions(self.operationsUpper)
        lowerDims = widgetDimensions(self.operationsLower)
        midControlPanel = max(upperDims[0], lowerDims[0]) // 2
        return visibleCanvas[0] + midControlPanel, maxY + buffer

    buttonTypes = (ttk.Button, Button, Checkbutton, Radiobutton)

    def getOperations(self):
        '''Get all the currently defined operations.  Return 2 results:
        withArgument: List of operation buttons that require 1+ argument(s)
        withoutArgument: List of operation buttons that require no arguments

        Buttons are returned in the reverse order they were added -
        bottom to top in the grid.  The self.playControlsFrame is returned
        as a single operation in the withoutArgument list, if it is
        present.
        '''
        withArgument, withoutArgument = [], []
        playControls = getattr(self, 'playControlsFrame', False)
        for item in self.operations.grid_slaves():
            if (isinstance(item, self.buttonTypes) and
                getattr(item, 'required_args', 0) > 0):
                withArgument.append(item)
            elif isinstance(item, self.buttonTypes) or item is playControls:
                withoutArgument.append(item)
        return withArgument, withoutArgument

    def getOperationGridLocation(self, btn):
        'Get the row and column of an operations button'
        info = btn.grid_info()
        return int(info['row']), int(info['column'])

    withArgsColumn = 0
    argsColumn = 8
    separatorColumn = argsColumn + 1
    withoutArgsColumn = separatorColumn + 1
    
    def addOperation(  # Add a button to the operations control panel
            self,      # The button can require N arguments provided by text
            label,     # entry widgets. Button label
            callback,  # Function to call when button pressed
            numArguments=0, # Count of required user entered arguments
            validationCmd=None, # Tk validation command tuple for argument(s)
            helpText=None,  # Help text for overall operation
            argHelpText=[], # Help text for each argument
            maxRows=4,      # Operations w/o args beyond maxRows -> new columns
            buttonType=ttk.Button, # Type of button (see buttonTypes)
            cleanUpBefore=True, # Clean up all previous animations before Op
            mutex=True,     # Operation is mutually exclusive of others
            bg=None,        # Background color, default is OPERATIONS_BG
            **kwargs):      # Tk button keyword args
        if buttonType not in self.buttonTypes:
            raise ValueError('Unknown button type: {}'.format(buttonType))
        if bg is None:
            bg = self.OPERATIONS_BG
        if buttonType in (ttk.Button,):
            ttk.Style().configure('TButton', font=self.CONTROLS_FONT, 
                                  background=bg)
            button = buttonType(self.operations, text=label, **kwargs)
        else:
            button = buttonType( # Create button based on type
                self.operations, text=label, font=self.CONTROLS_FONT, bg=bg,
                **kwargs)
        button['command'] = self.runOperation(
            callback, cleanUpBefore, button, mutex)
        button.bind('<Button>', self.recordModifierKeyState)
        button.bind('<KeyPress>', self.recordModifierKeyState)
        setattr(button, 'required_args', numArguments)
        setattr(button, 'mutex', mutex)


        # Placement
        withArgs, withoutArgs = self.getOperations()
        if numArguments:
            while len(self.textEntries) < numArguments:  # Build argument entry
                textEntry = self.createArgumentEntry(validationCmd)
                self.textEntries.append(textEntry)
                textEntry.grid(
                    column=self.argsColumn, row=len(self.textEntries), padx=8)
            for help, textEntry in zip(argHelpText, self.textEntries):
                helpTexts = getattr(textEntry, 'helpTexts', set())
                helpTexts.add(help)
                setattr(textEntry, 'helpTexts', helpTexts)

            # Place button in grid of buttons
            buttonColumn = self.withArgsColumn + len(withArgs) // maxRows
            buttonRow = len(withArgs) % maxRows + 1
            button.grid(
                column=buttonColumn, row=buttonRow, padx=8, sticky=(E, W))
            withArgs.append(button)
            widgetState(button, DISABLED)
            nEntries = len(self.textEntries)
            rowSpan = max(1, (min(maxRows, len(withArgs)) - 1) // nEntries)
            
            # Spread text entries across all rows of buttons with arguments
            # with the hint about what to enter below, if any
            for i, entry in enumerate(self.textEntries):
                entryRow = rowSpan * i + 1
                entryRowSpan = rowSpan if i < nEntries - 1 else max(
                    1, 
                    min(maxRows, len(withArgs)) - 1 - (nEntries - 1) * rowSpan)
                entry.grid_configure(row=entryRow, rowspan=entryRowSpan)
            if self.entryHint:
                self.entryHintRow = max(
                    entryRow + max(1, entryRowSpan - 1),
                    min(max(len(withoutArgs), len(withArgs)), maxRows))
                self.entryHint.grid_configure(
                    column=self.argsColumn, row=self.entryHintRow)

        else:
            buttonColumn = self.withoutArgsColumn + len(withoutArgs) // maxRows
            buttonRow = len(withoutArgs) % maxRows + 1
            button.grid(
                column=buttonColumn, row=buttonRow, padx=8, sticky=(E, W))
            withoutArgs.append(button)

        self.configureOperationsSeparator(withArgs, withoutArgs)
        if helpText:
            button.bind('<Enter>', self.makeArmHintHandler(button, helpText)) #equivalent of ttp 'enter'
            button.bind('<Leave>', self.makeDisarmHandler(button)) #equivalent of ttp 'close'
            button.bind('<Button>', self.makeDisarmHandler(button), '+')
        self.opButtons.append(button)
        return button

    def configureOperationsSeparator(self, withArgs, withoutArgs):
        'Add separator if both kinds of buttons are present and none built'
        if withArgs and withoutArgs and not self.opSeparator:
            self.opSeparator = Frame(
                self.operations, width=2, bg=self.OPERATIONS_BORDER)
            self.opSeparator.grid(
                column=self.separatorColumn, row=1, sticky=(N, E, W, S))
        if self.opSeparator:
            nColumns, nRows = self.operations.grid_size()
            self.opSeparator.grid_configure(
                rowspan=max(nRows, self.entryHintRow if self.entryHint else 1))
        
    def createArgumentEntry(self, validationCmd):
        entry = Entry(
            self.operations, width=self.maxArgWidth * 5 // 4, bg=self.ENTRY_BG,
            validate='key', validatecommand=validationCmd, 
            font=self.CONTROLS_FONT)
        entry.bind('<FocusIn>', lambda event:
                   event.widget.select_range(0, END), '+')
        entry.bind(
            '<KeyRelease>', lambda ev: self.argumentChanged(ev.widget), '+')
        for key in ('Return', 'KP_Enter'):
            entry.bind('<KeyPress-{}>'.format(key),
                       lambda ev: self.returnPressed(ev), '+')
        entry.bind('<Enter>', self.makeArmHintHandler(entry))
        entry.bind('<Leave>', self.makeDisarmHandler(entry))
        entry.bind('<KeyRelease>', self.makeDisarmHandler(entry), '+')
        entry.bind('<FocusIn>', self.clearHintHandler(), '+')
        return entry

    def setHint(self, widget, hintText=None):
        
        # creates a toplevel window
        if not self.tw:
            # Make floating window in front of this app without window controls
            self.tw = Toplevel()
            self.entryHint = None
            if not sys.platform.startswith('win'):
                self.tw.transient(self.controlPanel)
            self.tw.overrideredirect(True)
        
        if hintText is None:    # Default hint is description of all arguments
            x = widget.winfo_rootx() + 10 # and goes next to textEntry widget
            y = widget.winfo_rooty() + 20
            hintText = '^ Click to enter {}'.format(
                ',\n'.join([
                    ' or '.join(hint for hint in 
                                getattr(entry, 'helpTexts', set()))
                    for entry in self.textEntries]))
        else:
            x = widget.winfo_pointerx() + 10 # Goes next to mouse pointer
            y = widget.winfo_pointery() + 5

        self.tw.geometry("+%d+%d" % (x, y))

        if self.entryHint is None: # Create hint if not present
            self.entryHint = Label(
                self.tw, text=hintText,
                font=self.HINT_FONT, fg=self.HINT_FG, bg=self.HINT_BG)
            self.entryHint.pack()
        else:                      # Update hint text if already present
            self.entryHint['text'] = hintText
            if hintText == '':
                if self.tw:
                    self.tw.destroy()
                    self.tw = None
                self.entryHint = None
            else:
                self.entryHint.pack()
        
    def makeArmHintHandler(self, widget, helpText=None):
        def handler(event):
            hint = ' or '.join(
                getattr(widget, 'helpTexts', set())) if helpText is None else helpText
            setattr(widget, 'timeout_ID',
                    widget.after(
                        self.HOVER_DELAY, 
                        lambda: self.setHint(widget, hint) or setattr(widget, 'timeout_ID', None)))
        return handler

    def makeDisarmHandler(self, widget):
        def Dhandler(event):
            if event.widget == widget and getattr(widget, 'timeout_ID', None):
                widget.after_cancel(getattr(widget, 'timeout_ID'))
            setattr(widget, 'timeout_ID', None)
            if self.tw:
                self.tw.destroy()
                self.tw, self.entryHint = None, None
        return Dhandler

    def makeTimer(self, widget, delay=300, attrName='timeout_ID'):
        'Make a handler that sets a timeout that clears itself after a delay'
        setattr(widget, attrName,
                widget.after(delay, lambda: setattr(widget, attrName, None)))
        return getattr(widget, attrName)

    def clearHintHandler(self):
        def Chandler(event):
            if self.tw:
                self.tw.destroy()
                self.tw, self.entryHint = None, None
        return Chandler
    
    def recordModifierKeyState(self, event=None):
        if event and event.type in (EventType.ButtonPress, EventType.KeyPress):
            self.modifierKeyState = event.state
            self.debugRequested = (
                event.state & (CTRL | SHIFT) == (CTRL | SHIFT) and
                os.path.exists('.debug.pyc'))
            
    def startMode(self):
        'Choose starting animation mode based on last modifier keys used'
        return (Animation.STEP if self.modifierKeyState & SHIFT
                else Animation.RUNNING)
            
    def returnPressed(self, event):  # Handle press of Return/Enter in text
        button = getattr(            # entry argument widget.
            event.widget, 'last_button', None)
        if button:                   # If last_button attribute is defined
            self.pressButton(button)

    def pressButton(self, button):  # Simulate button press, if enabled
        if widgetState(button) == NORMAL:
            widgetState(    # Simulate button press
                button, PRESSED if isinstance(button, ttk.Button) else ACTIVE)
            self.window.update()
            time.sleep(0.05)
            widgetState(
                button, 
                '!' + PRESSED if isinstance(button, ttk.Button) else NORMAL)
            button.invoke()
        
    def addAnimationButtons(self, maxRows=4, setDefaultButton=True):
        '''Add the Play/Pause, Step, and Stop buttons to control animation.
        Add the combined button in a new column to avoid going past maxRows.
        If setDefaultButton is a button, it will be made the default button
        when Enter is pressed in the first text entry box.
        If setDefaultButton is true, and only one operation taking arguments
        has been defined, that operation will be the default when Enter is
        pressed.
        '''
        self.playControlsFrame = Frame(self.operations, bg=self.OPERATIONS_BG)
        withArgs, withoutArgs = self.getOperations()
        lastRow, lastColumn = self.getOperationGridLocation(
            withoutArgs[0]) if withoutArgs else (1, self.withoutArgsColumn)
        self.playControlsFrame.grid(
            column=lastColumn + lastRow // maxRows, row=lastRow % maxRows + 1)

        self.pauseButton, self.stepButton, self.stopButton = (
            Button(self.playControlsFrame, image=self.playControlImages[name],
                   state=DISABLED)
            for name in ('pause', 'skip-next', 'stop'))
        for btn, name, func, column in zip(
                (self.pauseButton, self.stepButton, self.stopButton),
                ('pause', 'skip-next', 'stop'),
                (self.pausePlay, self.step, self.stop),
                range(3)):
            buttonImage(btn, self.playControlImages[name])
            btn['command'] = self.onClick(func)
            btn.grid(row=0, column=column, sticky=(E, W))
            btn.bind('<FocusIn>', self.buttonFocus(btn, True))
            btn.bind('<FocusOut>', self.buttonFocus(btn, False))
            btn.bind('<Button>', self.recordModifierKeyState, add='+')
            btn.bind('<KeyPress>', self.recordModifierKeyState, add='+')
        withoutArgs.append(self.playControlsFrame)
        self.configureOperationsSeparator(withArgs, withoutArgs)
        
        if setDefaultButton and self.textEntries:
            if isinstance(setDefaultButton, self.buttonTypes):
                setattr(self.textEntries[0], 'last_button', setDefaultButton)
            else:
                if len(withArgs) == 1:
                    setattr(self.textEntries[0], 'last_button', withArgs[0])

    def createPlayControlImages(self, height=None):
        if height is None:
            height = abs(self.CONTROLS_FONT[1])
        targetSize = (height, height)
        names = ('play', 'pause', 'skip-next', 'stop')
        self.playControlImages = dict(
            (name, getPhotoImage(name + '-symbol.png', targetSize))
            for name in names)
        return self.playControlImages
        
    def runOperation(self, command, cleanUpBefore, button=None, mutex=True):
        def animatedOperation(): # If button that uses arguments is provided,
            if button and getattr(button, 'required_args', 0) > 0: # record it
                for entry in self.textEntries[:getattr( # as the last button
                        button, 'required_args')]: # pressed for all its args
                    setattr(entry, 'last_button', button)
            animationControls = [
                b for b in (self.pauseButton, self.stepButton, self.stopButton)
                if b]
            withArgs, withoutArgs = self.getOperations()
            try:
                if cleanUpBefore:
                    self.cleanUp()
                if button and button in animationControls:
                    button.focus_set()
                if mutex:
                    if not self.operationMutex.acquire(blocking=False):
                        self.setMessage('Cannot run more than one operation')
                        return
                command()
            except UserStop as e:
                self.cleanUp(self.callStack[0] if self.callStack else None,
                             ignoreStops=True)
            if mutex and self.operationMutex.locked():
                self.operationMutex.release()
            self.enableButtons()
            focus = self.window.focus_get()
            if (focus and  # If focus ended on a button needing arguments or an
                (focus in withArgs or  # animation control run on something w/
                 focus in animationControls and button in withArgs) # args
                and self.textEntries): # and there are text entry boxes
                self.textEntries[0].focus_set() # switch focus to 1st entry
            elif (focus and   # If focus ended on animation control run on
                  focus in animationControls and # something without args
                  button in withoutArgs):
                button.focus_set()     # Set focust back to operation button
        return animatedOperation
                
    def getArgument(self, index=0, clear=False):
        if 0 <= index and index < len(self.textEntries):
            val = self.textEntries[index].get()
            if clear:
                self.clearArgument(index)
            return val

    def getArguments(self, clear=False):
        return [self.getArgument(i, clear=clear)
                for i in range(len(self.textEntries))]

    def clearArgument(self, index=0):
        self.setArgument('', index)

    def clearArguments(self):
        for index in range(len(self.textEntries)):
            self.setArgument('', index)

    def setArgument(self, val='', index=0):
        if 0 <= index and index < len(self.textEntries):
            self.textEntries[index].delete(0, END)
            if str(val):
                self.textEntries[index].insert(0, str(val))
            self.setArgumentHighlight(index)
            self.argumentChanged()

    def setArguments(self, *values):
        for index in range(min(len(values), len(self.textEntries))):
            self.setArgument(str(values[index]), index)
        self.argumentChanged()

    def setArgumentHighlight(self, index=0, color=ENTRY_BG):
        self.textEntries[index].configure(bg=color)
            
    def argumentChanged(self, widget=None):
        # Enable buttons if animations are stopped
        self.enableButtons(self.animationsStopped())

        for i, entry in enumerate(self.textEntries):
            if widget == entry:  # For the entry widget that changed,
                self.setArgumentHighlight(i) # clear any error highlight
            
    def setMessage(self, val=''):
        self.messageText.set(val)

    def getMessage(self):
        return self.messageText.get()
        
    vScrollWidth = 10      # Guess for width of vertical scrollbar width
    
    def showCode(self,     # Show algorithm code in a scrollable text box
                 code,     # Code to display, plus optional boundary line
                 addBoundary=False, # to separate calls on the stack
                 sleepTime=0,       # Wait time between adding lines of text
                 allowStepping=True): # Allow stepping on waits
        code = code.strip()
        if len(code) == 0:  # Empty code string?
            return          # then nothing to show
        if self.codeText is None:
            padX, padY = 10, 10
            self.codeTextCharWidth = textWidth( 
                self.CODE_FONT, '0123456789') // 10
            self.codeVScroll = Scrollbar(self.codeFrame, orient=VERTICAL)
            self.vScrollWidth = max(
                self.vScrollWidth, self.codeVScroll.winfo_width())
            width = self.codeTextWidth(padX, self.vScrollWidth)
            self.codeText = Text(
                self.codeFrame, wrap=NONE, background=self.OPERATIONS_BG,
                font=self.CODE_FONT, width=width,
                height=self.MIN_CODE_CHARACTER_HEIGHT, padx=padX, pady=padY,
                takefocus=False)
            self.codeText.grid(row=0, column=0, sticky=(N, E, S, W))
            self.codeVScroll['command'] = self.codeText.yview
            self.codeVScroll.grid(row=0, column=1, rowspan=2, sticky=(N, S))
            self.codeHScroll = Scrollbar(
                self.codeFrame, orient=HORIZONTAL, command=self.codeText.xview)
            self.codeHScroll.grid(row=1, column=0, sticky=(E, W))
            self.codeText['xscrollcommand'] = self.codeHScroll.set
            self.codeText['yscrollcommand'] = self.codeVScroll.set
            self.controlPanel.bind('<Configure>', self.resizeCodeText)
            self.codeText.tag_config('call_stack_boundary',
                                     font=self.CODE_FONT + ('overstrike',),
                                     background=self.CALL_STACK_BOUNDARY)
        
        self.codeText.configure(state=NORMAL)
        currentCode = self.codeText.get('1.0', END)
        if currentCode:     # If there's already code, jump to view top of it
            self.codeText.see('1.0')
        
        # Add a call stack boundary line if requested and other code exists
        if addBoundary and currentCode and not currentCode.isspace():
            self.codeText.insert('1.0',
                                 self.codeText.config('width')[-1] * '-' + '\n')
            self.codeText.tag_add('call_stack_boundary', '1.0', '1.end')
        
        # Add code at top of text widget (above stack boundary, if any)
        if sleepTime > 0:
            for line in reversed(code.split('\n')):
                if self.codeText:
                    self.codeText.insert('1.0', line + '\n')
                self.wait(sleepTime, allowStepping=allowStepping)
        else:
            self.codeText.insert('1.0', code + '\n')

        # The codeText widget might have been removed during the wait() above
        if self.codeText:
            self.codeText.see('1.0')
            self.codeText.configure(state=DISABLED)

            # Doing a window update here can cause multiple resize events
            self.window.update_idletasks()
            
    def removeCode(self,     # Remove algorithm code from the codeText box
                   code,     # Code to remove
                   boundary=True, # Remove optional boundary line after code
                   sleepTime=0,   # Wait time between removing lines of text
                   ignoreStops=True, # Ignore any user stops during waits
                   allowSteps=False): # Allow step mode pauses before and during
        if not self.codeText:  # The codeText window must be present
            return
        inUserStop = False
        code = code.strip()
        lines = code.split('\n')
        self.codeText.configure(state=NORMAL)
        if allowSteps:
            try:
                self.wait(0)
            except UserStop:
                inUserStop = True
        last_line = int(float(self.codeText.index(END))
                        if len(lines) > 0 else 0)
        for i in range(1, min(last_line, len(lines) + (2 if boundary else 1))):
            if self.codeText:
                self.codeText.delete('1.0', '2.0')
                if (sleepTime > 0 and not self.animationsStopped() and
                    not inUserStop):
                    try:
                        self.wait(sleepTime, allowStepping=allowSteps)
                    except UserStop:
                        inUserStop = True
        if self.codeText:
            self.codeText.configure(state=DISABLED)
        return inUserStop
        
    def codeTextWidth(      # Compute width available for code text
            self,           # This can be called before the codeText widget
            padX,           # is created. Provide padX setting for codeText
            vScrollWidth,   # and vertical scroll bar width
            debug=False):   # Set true for debugging printout

        mainWidth = self.window.winfo_width()
        upperWidth = self.operationsUpper.winfo_width()
        lowerWidth = self.operationsLower.winfo_width()
        if mainWidth < max(upperWidth, lowerWidth) or mainWidth == 1:
            mainWidth = self.targetCanvasWidth
            lowerWidth = 500
        available = (mainWidth - max(upperWidth, lowerWidth) -
                     vScrollWidth - padX * 2)
        desired = min(80, max(self.MIN_CODE_CHARACTER_WIDTH, 
                              available // self.codeTextCharWidth))
        if debug:     # Set true for debugging printout
            print('Call to codeTextWidth, codeText =', self.codeText,
                  'which {} mapped'.format(
                      'is' if self.codeText and self.codeText.winfo_ismapped()
                      else 'is not'),
                  '\nDetermining codeText width based on window width =', 
                  self.window.winfo_width(),
                  '\noperationsUpper width =',
                  self.operationsUpper.winfo_width(), 
                  'operationsLower width =', self.operationsLower.winfo_width(),
                  '\nVScroll width =', vScrollWidth,
                  'padX =', padX, 'available pixels =', available,
                  'codeText character width =', self.codeTextCharWidth,
                  '\ndesired width in characters =', desired)
        return desired
    
    def resizeCodeText(self, event=None, debug=False):
        ct = self.codeText
        resize_ID = 'resize_timeout_ID'
        if debug:
            print('Entering resizeCodeText with event =', event,
                  'self.codeText = ', ct, '{} mapped'.format(
                      'is' if ct.winfo_ismapped() else 'is not'),
                  'timeout_ID =', getattr(ct, resize_ID, None))
        if ct is None or not ct.winfo_ismapped():
            return
        nCharsWide = ct['width']
        padX = ct['padx']
        self.vScrollWidth = max(
            self.vScrollWidth, self.codeVScroll.winfo_width())
        desired = self.codeTextWidth(padX, self.vScrollWidth, debug)
        timeout_ID = getattr(ct, resize_ID, None)
        skip = event is not None and timeout_ID is not None
        if debug and False:     # Set true for debugging printout
            print('Current width is', nCharsWide, 'and desired is', desired)
            if skip and desired != nCharsWide:
                print('Skipping resize while timer {} running'.format(
                    timeout_ID))
        if not skip and desired != nCharsWide:
            self.makeTimer(ct, 5, resize_ID)
            if debug:
                print('Timer ID set to', getattr(ct, resize_ID, None))
            ct['width'] = desired
    
    def highlightCode(
            self, fragments, callEnviron, wait=0, color=None, returnValue=None):
        '''Highlight a code fragment for a particular call environment.
        Multiple fragments can be highlighted.  Each fragment can be
        either a string of code, or a (string, int) tuple where the int
        is 1 for the first instance of the string, 2 for the second, etc.
        Return's the given returnValue for use in Boolean expressions.
        If returnValue is a function, it is called at the end of this
        routine to delay the execution and get the return value.
        '''
        codeBlock = self.getCodeHighlightBlock(callEnviron)
        if self.codeText is None or codeBlock is None:
            # This should only happen when code is hidden
            return returnValue() if callable(returnValue) else returnValue
        if color is None:
            color = self.CODE_HIGHLIGHT
        if isinstance(fragments, (list, tuple)):
            if (len(fragments) == 2 and   # Look for (str, int) pair
                isinstance(fragments[0], (str, type(geomPattern))) and
                isinstance(fragments[1], int)):
                frags = [tuple(fragments)] # Look up by (str, int) tuple
            else:
                frags = [
                    tuple(frag) if isinstance(frag, (list, tuple))
                    else (frag, 1)
                    for frag in fragments]
        else:
            frags = [(fragments, 1)]
        codeBlock.currentFragments = frags # Store standardized fragments
        tags = [codeBlock[frag] for frag in frags]
        found = False       # Assume tag not found
        for tagName in self.codeText.tag_names() if self.codeText else []:
            if not tagName.startswith(codeBlock.prefix):
                continue  # Only change tags for this call environment
            highlight = tagName in tags
            self.codeText.tag_config(
                tagName, background=color if highlight else '',
                underline=1 if highlight else 0)
            if highlight:
                found = True
                for index in reversed(self.codeText.tag_ranges(tagName)):
                    self.codeText.see(index)
        if not found and len(tags) > 0:  # This shouldn't happen so log bug
            print('Unable to find highlight tag(s) {} among {}'.format(
                ', '.join(tags), ', '.join(codeBlock.cache.keys())))
        if wait > 0 or self.animationsStepping(): # Optionally weit for a time
            self.wait(wait)                       # or pause at a step
        return returnValue() if callable(returnValue) else returnValue


    # Return the CodeHighlightBlock from the set object from the call stack
    # NOTE: this could be more efficient if the objects on the call stacks
    # were dictionaries but Python doesn't allow mutable objects like a
    # CodeHighlightBlock as keys so we'd need a special key that couldn't
    # be confused with a canvas item (string or integer) to index it
    # Instead, we do a linear search and find it by its type
    def getCodeHighlightBlock(self, callEnvironment):
        return getCodeHighlightBlock(callEnvironment)
            
    def cleanUp(self,         # Remove Tk items from past animations either
                callEnviron=None,  # for a particular call or all calls
                stopAnimations=True, # stop animations, if requested
                sleepTime=0,  # wait between removing code lines from stack
                ignoreStops=False,   # ignore UserStops, if requested
                allowSteps=False):   # Allow stepping to pause clean up
        if stopAnimations:
            self.stopAnimations()
        minStack = 1 if callEnviron else 0 # Don't clean beyond minimum, keep
        while len(self.callStack) > minStack: # 1st call unless cleaning all
            top = self.callStack.pop()
            try:
                self.cleanUpCallEnviron(top, sleepTime, allowSteps=allowSteps)
            except UserStop:
                if not ignoreStops:
                    raise UserStop
            if callEnviron is not None and callEnviron == top: # Stop popping
                break         # stack if a particular call was being cleaned up
                
        if callEnviron is None:  # Clear any messages if cleaning up everything
            self.setMessage()
        if len(self.callStack) == 0: # When call stack is empty
            self.codeText = None
            while len(self.codeFrame.children) > 0: # Remove code window
                tkItem = self.codeFrame.children.popitem()
                tkItem[1].destroy()

    def cleanUpCallEnviron(    # Clean up a call on the stack
            self, callEnviron, # removing the call environement
            sleepTime=0,       # waiting sleepTime between removing code lines
            allowSteps=False): # allowing step pauses if set
        inUserStop = False
        codeBlock = None
        toDelete = []
        while len(callEnviron):
            thing = callEnviron.pop()
            if isinstance(thing, (str, int)) and self.canvas.type(thing):
                toDelete.append(thing)
            elif isinstance(thing, CodeHighlightBlock) and self.codeText:
                codeBlock = thing
        if codeBlock:
            inUserStop = self.removeCode(
                codeBlock.code, sleepTime=sleepTime, allowSteps=allowSteps
            ) or inUserStop
        for item in toDelete:
            self.canvas.delete(item)
        if inUserStop:
            raise UserStop()

    def createCallEnvironment(self, code='', sleepTime=0, startAnimations=True):
        '''Creates a call environment, a set for local variables represented by
        canvas items, plus a codeHighlightBlock that controls code highlights.
        The set is pushed on the callStack for a particular call.  The code
        for that call will be shown in the codeText window, and will be added
        line by line if sleepTime is above 0 (otherwise all at once).  The
        startAnimations value determines how the animationState is changed,
        if at all.  True means keep RUNNING or STEP mode or switch to RUNNING.
        An explicit Animation state means switch to that state.  False or None
        means don't call startAnimations.
        '''
        code = code.strip()
        callEnviron = set()
        if len(code) > 0:
            self.showCode(
                code, addBoundary=True,
                sleepTime=0 if (self.animationsStopped() and startAnimations
                                and len(self.callStack) == 0) else sleepTime)
            codeHighlightBlock = CodeHighlightBlock(code, self.codeText)
            if self.codeText:
                codeHighlightBlock.markStart()
            callEnviron.add(codeHighlightBlock)
            
        self.callStack.append(callEnviron) # Push environment on stack
        if startAnimations:
            self.startAnimations(
                state=startAnimations if isinstance(startAnimations, Animation)
                else self.animationState if startAnimations is True and
                not self.animationsStopped()
                else Animation.RUNNING)
        return callEnviron

    def yieldCallEnvironment(
            self, callEnviron: 'Call environment to remove from stack',
            exclude: 'Set/sequence of items to remain visible' ={},
            sleepTime: 'Pause between removing code lines' =0,
            moveItems: 'Hide items by moving if true, else set state' =True):
        '''Remove the call environment from an iterator right before
        yielding its value.  The callEnviron must be on top of the
        call stack.  The items in the callEnviron are either moved off the
        canvas, or set to HIDDEN state depending on the moveItems flag.
        Items in the exclude set or sequence are not hidden.
        Returns a dictionary mapping item numbers to tuples of the form
        (state, index) where state is either their coordinates or their
        current state attribute for later restoration in the stacking
        order provided by their index.'''
        if callEnviron is not self.callStack[-1]:
            raise Exception(
                'Cannot yield from call environment that is not current')
        codeBlock = self.getCodeHighlightBlock(callEnviron)
        if codeBlock:
            self.removeCode(codeBlock.code, sleepTime=sleepTime)
        self.callStack.pop()
        itemCoords = {}
        canvasDims = (V(self.canvasBounds[2:]) - self.canvasBounds[:2]
                      if self.canvasBounds else 
                      widgetDimensions(self.canvas))
        away = V(canvasDims) * 10
        itemStackingOrder = self.canvas.find_all()
        for item in callEnviron:
            if (isinstance(item, int) and self.canvas.type(item) and
                not item in exclude):
                itemIndex = itemStackingOrder.index(item)
                if moveItems:
                    coords = self.canvas.coords(item)
                    if any(self.withinCanvas((coords[j], coords[j + 1]))
                           for j in range(0, len(coords), 2)):
                        itemCoords[item] = (coords, itemIndex)
                        self.canvas.coords(item, V(coords) +
                                           V(away * (len(coords) // 2)))
                else:
                    state = self.canvas_itemConfig(item, 'state')
                    itemCoords[item] = (state, itemIndex)
                    self.canvas_itemConfig(item, state=HIDDEN)
        return itemCoords

    def resumeCallEnvironment(
            self, callEnviron: 'Call environment to push back on stack',
            itemMap: 'Dictionary mapping items to coords or state',
            sleepTime: 'Puase between restoring code lines' =0):
        self.callStack.append(callEnviron)
        codeBlock = self.getCodeHighlightBlock(callEnviron)
        if codeBlock:
            self.showCode(codeBlock.code, sleepTime=sleepTime,
                          addBoundary=True, allowStepping=False)
            codeBlock.markStart()
            self.highlightCode(codeBlock.currentFragments, callEnviron, wait=0)
        for item in sorted(itemMap.keys(), key=lambda x: itemMap[x][1]):
            if isinstance(itemMap[item][0], (list, tuple)):
                self.canvas.coords(item, *itemMap[item][0])
            else:
                self.canvas_itemConfig(item, state=itemMap[item][0])
            self.canvas.tag_raise(item)

    def callStackHighlights(self):
        '''Return list of code fragments highlighted on every level of the call
        stack'''
        codeBlocks = [self.getCodeHighlightBlock(env) for env in self.callStack]
        return [block.currentFragments if block else [] for block in codeBlocks]
    
    # ANIMATION CONTROLS
    def speed(self, sleepTime):
        return min(
            10, sleepTime * 50 * self.SPEED_SCALE_MIN / self.speedScale.get())

    def wait(self, sleepTime, allowStepping=True):
        '''Sleep for a user-adjusted period, pausing optionally for steps
        and for user requested pauses.
        Stepping pauses when the current highlighted fragments on the call
        stack don't match those encountered in the last call to wait.
        '''
        if self.debugRequested:
            kwargs = {}
            if sys.version_info[:2] >= (3, 7):
                kwargs['header'] = (
                    "Pressed shift-control key when clicking button "
                    "or pressed Shift-Control-Enter")
            self.debugRequested = False
            pdb.set_trace(**kwargs)
            
        stateOnEntry = self.animationState
        if (self.animationsStepping() and
            buttonImage(self.pauseButton) != self.playControlImages['play']):
            buttonImage(self.pauseButton, self.playControlImages['play'])
        highlights = self.callStackHighlights()
        if (allowStepping and self.animationsStepping() and
               self.lastHighlights != highlights):
            if len(highlights) > 0 and highlights[-1]:
                codeBlock = self.getCodeHighlightBlock(self.callStack[-1])
                for fragment in reversed(highlights[-1]):
                    for index in reversed(self.codeText.tag_ranges(
                            codeBlock[fragment])):
                        self.codeText.see(index)
            while self.lastHighlights != highlights and self.animationsStepping():
                self.stepPause = True
                self.window.update()
                if self.destroyed:
                    sys.exit()
                time.sleep(0.02)
                if self.destroyed:
                    sys.exit()
            self.stepPause = False
        self.lastHighlights = self.callStackHighlights()
        if sleepTime > 0:
            self.window.update()
            if self.destroyed:
                sys.exit()
            time.sleep(self.speed(sleepTime))
            if self.destroyed:
                sys.exit()
        while self.animationsPaused():
            self.window.update()
            if self.destroyed:
                sys.exit()
            time.sleep(0.02)
            if self.destroyed:
                sys.exit()
            
        if self.animationsStopped(): # If user requested to stop
            raise UserStop()      # animation while waiting then raise exception

    def onClick(self, command, *parameters):
        ''' Return a handler for user clicks on an animation button.
        The handler runs a command and enables other buttons as appropriate
        to the animation state
        '''
        def buttonClickHandler(event=None):
            if command == self.pausePlay:  # Button takes focus if it can be
                self.pauseButton.focus_set() # repeated (pause/play & step)
            elif command == self.step:
                self.stepButton.focus_set()
                
            command(*parameters)      # run the command, and re-enable buttons
            if command in [self.stop]: # when Stop is pressed
                self.enableButtons() 
        return buttonClickHandler

    def buttonFocus(self, btn, hasFocus):
        '''Return a handler for focus change on animation buttons'''
        def focusHandler(event=None):
            btn['highlightbackground'] = (
                'deep sky blue' if hasFocus else 'White')
            btn['relief'] = (
                'groove' if hasFocus else 'raised')
        return focusHandler
            
    def enableButtons(self, enable=True):
        withArgs, withoutArgs = self.getOperations()
        args = self.getArguments()
        for btn in withArgs + withoutArgs:
            if isinstance(btn, self.buttonTypes):
                nArgs = getattr(btn, 'required_args', 0)
                mutex = getattr(btn, 'mutex', False)
                widgetState(
                    btn, NORMAL if enable and all(args[:nArgs]) and not (
                        mutex and self.operationMutex.locked()) else DISABLED)
            
            elif btn is getattr(self, 'playControlsFrame', False):
                for b in (self.pauseButton, self.stepButton, self.stopButton):
                    if b:
                        widgetState(
                            b,
                            NORMAL if (
                                enable and not self.animationsStopped() and
                                (b != self.stepButton or self.codeText))
                            else DISABLED)

    def stop(self):
        self.stopAnimations()
        self.animationState = Animation.STOPPED  # Always stop on user request
        buttonImage(self.pauseButton, self.playControlImages['play'])

    def pausePlay(self):
        if self.animationState in (Animation.PAUSED, Animation.STEP):
            self.startAnimations(state=Animation.RUNNING)
            buttonImage(self.pauseButton, self.playControlImages['pause'])
        else:
            self.pauseAnimations()
            buttonImage(self.pauseButton, self.playControlImages['play'])

    def step(self):
        '''Step forward by recording current call stack highlighted fragments
        as having been seen, so that waits will pause when stack highlights
        change.
        '''
        self.lastHighlights = self.callStackHighlights()
        self.startAnimations(state=Animation.STEP)

    def startAnimations(self, enableStops=True, state=None):
        self.animationState = state if state in set(Animation) else (
            self.animationState if self.animationState in (Animation.RUNNING,
                                                           Animation.STEP)
            else Animation.RUNNING)
        self.enableButtons(enable=False)
        if self.pauseButton and not self.animationsStepping():
            buttonImage(self.pauseButton, self.playControlImages['pause'])
        for btn in (self.pauseButton, self.stopButton):
            if btn and enableStops:
                widgetState(btn, NORMAL)
        if self.stepButton and enableStops and (
                self.codeText or state == Animation.STEP):
            widgetState(self.stepButton, NORMAL)

    def stopAnimations(self):  # Stop animation of a call on the call stack
        
        # Calls from stack level 2+ only stop animation for their level
        # At lowest level, animation stops and play & stop buttons are disabled
        if len(self.callStack) <= 1:
            self.animationState = Animation.STOPPED
            self.enableButtons(enable=True)
            for btn in (self.pauseButton, self.stopButton, self.stepButton):
                if btn:
                    widgetState(btn, DISABLED)
            self.argumentChanged()
        # Otherwise, let animation be stopped by a lower call
        
    def animationsPausedOrStepPaused(self):
        return self.animationsPaused() or self.stepPause

    def runVisualization(self): #override of runVisualization that populates default hint
        if (len(self.textEntries) > 0):
            widget = self.textEntries[0]
            setattr(widget, 'timeout_ID',
                    widget.after(
                        self.HOVER_DELAY, 
                        lambda: self.setHint(widget) or setattr(widget, 'timeout_ID', None)))
        self.window.mainloop()
