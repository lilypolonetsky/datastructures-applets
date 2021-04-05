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

import time, re, pdb, sys, os.path
from collections import *
from tkinter import *
from tkinter import ttk
PRESSED = 'pressed' # Oddly the ttk module does not define this like tk's ACTIVE

try:
    from PIL import Image as Img
    from PIL import ImageTk
except ModuleNotFoundError as e:
    print('Pillow module not found.  Did you try running:')
    print('pip3 install -r requirements.txt')
    raise e

try:
    from TextHighlight import *
    from Visualization import *
except ModuleNotFoundError:
    from .TextHighlight import *
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

    def __init__(  # Constructor
            self,
            maxArgWidth=3,    # Maximum length/width of text arguments
            hoverDelay=3000,  # Milliseconds to wait before showing hints
            **kwargs):
        super().__init__(**kwargs)

        self.maxArgWidth = maxArgWidth
        self.HOVER_DELAY = hoverDelay

        # Set up instance variables for managing animations and operations
        self.callStack = []    # Stack of local environments for visualziation

        self.pauseButton, self.stopButton, self.stepButton = None, None, None
        self.lastHighlights = self.callStackHighlights()
        self.modifierKeyState = 0
        self.debugRequested = False
        self.createPlayControlImages()
        self.setUpControlPanel()
 
    def setUpControlPanel(self):  # Set up control panel structure
        self.controlPanel = Frame(self.window, bg=self.DEFAULT_BG)
        self.controlPanel.pack(side=BOTTOM, expand=True, fill=X)
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
        # self.controlPanel.grid_columnconfigure(1, maxsize=200)
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
        self.outputText = StringVar()
        self.outputText.set('')
        self.message = Label(
            self.operationsLowerCenter, textvariable=self.outputText,
            font=self.CONTROLS_FONT + ('italic',), fg="blue",
            bg=self.DEFAULT_BG)
        self.message.grid(row=0, column=4, sticky=(E, W))
        self.operationsLowerCenter.grid_columnconfigure(4, minsize=200)
        self.operationsLowerCenter.grid_columnconfigure(3, minsize=10)

    def newValueCoords(self, buffer=30):
        '''Return a set of canvas coords that are below the visible canvas
        somewhere behind the control panel.  New values can be centered
        on these coordinates to make them appear as if they are coming from
        the control panel'''
        visibleCanvas = self.visibleCanvas()
        upperDims = self.widgetDimensions(self.operationsUpper)
        lowerDims = self.widgetDimensions(self.operationsLower)
        midControlPanel = max(upperDims[0], lowerDims[0]) // 2
        return visibleCanvas[0] + midControlPanel, visibleCanvas[3] + buffer

    buttonTypes = (ttk.Button, Button, Checkbutton, Radiobutton)

    def getOperations(self):
        '''Get all the currently defined operations.  Return:
        withArgument: List of operation buttons that require 1+ argument(s)
        withoutArgument: List of operation buttons that require no arguments
        nColumns: number of columns in operations grid
        nRows: number of rows in opserations grid

        Buttons are returned in the order they were added - top to bottom in
        grid.  The self.playControlsFrame is returned as a single operation
        in the withoutArgument list, if it is present.
        '''
        gridItems = gridDict(self.operations) # Operations inserted in grid
        nColumns, nRows = self.operations.grid_size()
        withArgument = [
            gridItems[0, row] for row in range(nRows)
            if isinstance(gridItems[0, row], self.buttonTypes)]
        withoutArgument = [
            gridItems[col, row]
            for row in range(nRows) for col in range(4, nColumns)
            if isinstance(gridItems[col, row], self.buttonTypes) or
            gridItems[col, row] is getattr(self, 'playControlsFrame', False)]
        return withArgument, withoutArgument, nColumns, nRows
        
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
        button['command'] = self.runOperation(callback, cleanUpBefore, button)
        button.bind('<Button>', self.recordModifierKeyState)
        button.bind('<KeyPress>', self.recordModifierKeyState)
        setattr(button, 'required_args', numArguments)

        # Placement
        withArgs, withoutArgs, nColumns, nRows = self.getOperations()
        if numArguments:
            while len(self.textEntries) < numArguments:  # Build argument entry
                textEntry = self.makeArgumentEntry(validationCmd)
                self.textEntries.append(textEntry)
                textEntry.grid(column=2, row=len(self.textEntries), padx=8)
            for help, textEntry in zip(argHelpText, self.textEntries):
                helpTexts = getattr(textEntry, 'helpTexts', set())
                helpTexts.add(help)
                setattr(textEntry, 'helpTexts', helpTexts)
            if argHelpText: # Make a label if there are hints on what to enter
                self.setHint()

            # Place button in grid of buttons
            buttonRow = len(withArgs) + 1
            button.grid(column=0, row=buttonRow, padx=8, sticky=(E, W))
            self.widgetState(button, DISABLED)
            nEntries = len(self.textEntries)
            rowSpan = max(1, (len(withArgs) + 1) // nEntries)
            
            # Spread text entries across all rows of buttons with arguments
            # with the hint about what to enter below, if any
            for i, entry in enumerate(self.textEntries):
                entryRowSpan = rowSpan if i < nEntries - 1 else max(
                    1, len(withArgs) + 1 - (nEntries - 1) * rowSpan)
                entry.grid_configure(row=rowSpan * i + 1, rowspan=entryRowSpan)
            if self.entryHint:
                self.entryHintRow = max(nEntries, len(withArgs) + 1) + (
                    0 if entryRowSpan > 2 else 1)
                self.entryHint.grid_configure(column=2, row=self.entryHintRow)

        else:
            buttonRow = len(withoutArgs) % maxRows + 1
            button.grid(column=4 + len(withoutArgs) // maxRows,
                        row=buttonRow, padx=8, sticky=(E, W))
        if ((len(withoutArgs) if numArguments else len(withArgs)) > 0
                and not self.opSeparator):  # Add separator if both kinds of
            self.opSeparator = Frame(  # buttons are present and none built
                self.operations, width=2, bg=self.OPERATIONS_BORDER)
            self.opSeparator.grid(column=3, row=1, sticky=(N, E, W, S))
        if self.opSeparator:
            self.opSeparator.grid_configure(
                rowspan=max(nRows, buttonRow, 
                            self.entryHintRow if self.entryHint else 1))
        if helpText:
            button.bind('<Enter>', self.makeArmHintHandler(button, helpText))
            button.bind('<Leave>', self.makeDisarmHandler(button))
            button.bind('<Button>', self.makeDisarmHandler(button), '+')
        self.opButtons.append(button)
        return button

    def makeArgumentEntry(self, validationCmd):
        entry = Entry(
            self.operations, width=self.maxArgWidth, bg=self.ENTRY_BG,
            validate='key', validatecommand=validationCmd, 
            font=self.CONTROLS_FONT)
        entry.bind(
            '<KeyRelease>', lambda ev: self.argumentChanged(ev.widget), '+')
        for key in ('Return', 'KP_Enter'):
            entry.bind('<KeyPress-{}>'.format(key),
                       lambda ev: self.returnPressed(ev), '+')
        entry.bind('<Enter>', self.makeArmHintHandler(entry))
        entry.bind('<Leave>', self.makeDisarmHandler(entry))
        entry.bind('<KeyRelease>', self.makeDisarmHandler(entry), '+')
        return entry

    def setHint(self, hintText=None):
        if hintText is None:    # Default hint is description of all arguments
            hintText = 'Click to enter {}'.format(
                ',\n'.join([
                    ' or '.join(hint for hint in 
                                getattr(entry, 'helpTexts', set()))
                    for entry in self.textEntries]))
        if self.entryHint is None: # Create hint if not present
            self.entryHint = Label(
                self.operations, text=hintText,
                font=self.HINT_FONT, fg=self.HINT_FG, bg=self.HINT_BG)
            self.entryHint.bind(
                '<Button>', # Clear the hint when label clicked
                clearHintHandler(self.entryHint, self.textEntries[0]))
            self.entryHint.bind(
                '<Shift-Button>', # Extend hint activation delay
                self.extendHintActivationHandler())
        else:                      # Update hint text if already present
            self.entryHint['text'] = hintText
            if hintText == '':
                self.entryHint.grid_remove()
            else:
                self.entryHint.grid()
        for entry in self.textEntries:      # Clear hint when entries get focus
            if not entry.bind('<FocusIn>'): # if handler not already set up 
                entry.bind('<FocusIn>', 
                           clearHintHandler(self.entryHint, entry))
        
    def makeArmHintHandler(self, widget, helpText=None):
        def handler(event):
            hint = ' or '.join(
                getattr(widget, 'helpTexts', set())) if helpText is None else helpText
            setattr(widget, 'timeout_ID',
                    widget.after(
                        self.HOVER_DELAY, 
                        lambda: self.setHint(hint) or
                        setattr(widget, 'timeout_ID', None)))
        return handler

    def makeDisarmHandler(self, widget):
        def Dhandler(event):
            if event.widget == widget and getattr(widget, 'timeout_ID', None):
                widget.after_cancel(getattr(widget, 'timeout_ID'))
            setattr(widget, 'timeout_ID', None)
        return Dhandler

    def makeTimer(self, widget, delay=300, attrName='timeout_ID'):
        'Make a handler that sets a timeout that clears itself after a delay'
        return lambda event: setattr(
            widget, attrName,
            widget.after(delay, lambda: setattr(widget, attrName, None)))

    def extendHintActivationHandler(self):
        def Ehandler(event):
            self.HOVER_DELAY += self.HOVER_DELAY
            msg = 'Show hints after {} seconds'.format(self.HOVER_DELAY / 1000)
            self.setHint(msg)
        return Ehandler
    
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
        if self.widgetState(button) == NORMAL:
            self.widgetState(    # Simulate button press
                button, PRESSED if isinstance(button, ttk.Button) else ACTIVE)
            self.window.update()
            time.sleep(0.05)
            self.widgetState(
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
        withArgs, withoutArgs, nColumns, nRows = self.getOperations()
        self.playControlsFrame.grid(
            column=4 + len(withoutArgs) // maxRows,
            row=len(withoutArgs) % maxRows + 1)

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
        images = dict((name, Img.open(name + '-symbol.png')) for name in names)
        ratios = dict((name, min(*(V(targetSize) / V(images[name].size))))
                      for name in names)
        self.playControlImages = dict(
            (name, ImageTk.PhotoImage(images[name].resize(
                (int(round(d)) for d in V(images[name].size) * ratios[name]))))
            for name in names)
        
    def runOperation(self, command, cleanUpBefore, button=None):
        def animatedOperation(): # If button that uses arguments is provided,
            if button and getattr(button, 'required_args', 0) > 0: # record it
                for entry in self.textEntries[:getattr( # as the last button
                        button, 'required_args')]: # pressed for all its args
                    setattr(entry, 'last_button', button)
            animationControls = [
                b for b in (self.pauseButton, self.stepButton, self.stopButton)
                if b]
            withArgs, withoutArgs, nColumns, nRows = self.getOperations()
            try:
                if cleanUpBefore:
                    self.cleanUp()
                if button and button in animationControls:
                    button.focus_set()
                command()
            except UserStop as e:
                self.cleanUp(self.callStack[0] if self.callStack else None,
                             ignoreStops=True)
            self.enableButtons()
            focus = self.window.focus_get()
            if (focus and  # If focus ended on an argument button or an
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

    def setArgument(self, val='', index=0):
        if 0 <= index and index < len(self.textEntries):
            self.textEntries[index].delete(0, END)
            if str(val):
                self.textEntries[index].insert(0, str(val))
            self.setArgumentHighlight(index)
            self.setHint('')
            self.argumentChanged()

    def setArguments(self, *values):
        for index in range(min(len(values), len(self.textEntries))):
            self.setArgument(str(values[index], index))
        self.argumentChanged()

    def setArgumentHighlight(self, index=0, color=ENTRY_BG):
        self.textEntries[index].configure(bg=color)
            
    def argumentChanged(self, widget=None):
        args = self.getArguments()
        withArgs, withoutArgs, nColumns, nRows = self.getOperations()
        for button in withArgs:
            nArgs = getattr(button, 'required_args')
            self.widgetState(
                button,
                DISABLED if not self.animationsStopped() or any(
                    arg == '' for arg in args[:nArgs]) else NORMAL)

        for i, entry in enumerate(self.textEntries):
            if widget == entry:  # For the entry widget that changed,
                self.setArgumentHighlight(i) # clean any error highlight
            
    def setMessage(self, val=''):
        self.outputText.set(val)

    def getMessage(self):
        return self.outputText.get()
        
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
            self.codeTextCharWidth = self.textWidth( 
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
            self.window.update()
            
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
        if self.codeText is None or not self.codeText.winfo_ismapped():
            return
        ct = self.codeText
        nCharsWide = ct['width']
        padX = ct['padx']
        self.vScrollWidth = max(
            self.vScrollWidth, self.codeVScroll.winfo_width())
        desired = self.codeTextWidth(padX, self.vScrollWidth, debug)
        timeout_ID = getattr(self.codeText, 'timeout_ID', None)
        skip = event is not None and timeout_ID is not None
        if False:     # Set true for debugging printout
            print('Current width is', nCharsWide, 'and desired is', desired)
            if skip and desired != nCharsWide:
                print('Skipping resize while timer {} running'.format(
                    timeout_ID))
        if not skip and desired != nCharsWide:
            ct['width'] = desired

    def highlightCode(self, fragments, callEnviron, wait=0, color=None):
        '''Highlight a code fragment for a particular call environment.
        Multiple fragments can be highlighted.  Each fragment can be
        either a string of code, or a (string, int) tuple where the int
        is 1 for the first instance of the string, 2 for the second, etc.
        '''
        codeBlock = self.getCodeHighlightBlock(callEnviron)
        if self.codeText is None or codeBlock is None: 
            return        # This should only happen when code is hidden
        if color is None:
            color = self.CODE_HIGHLIGHT
        if isinstance(fragments, (list, tuple)):
            if (len(fragments) == 2 and   # Look for (str, int) pair
                isinstance(fragments[0], str) and
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

    def yieldCallEnvironment(self, callEnviron, sleepTime=0):
        '''Remove the call environment from an iterator right before
        yielding its value.  The callEnviron must be on top of the
        call stack.  Returns a dictionary mapping item numbers to
        coordinates for canvas items that are moved off canvas'''
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
                      self.widgetDimensions(self.canvas))
        away = V(canvasDims) * 10
        for item in callEnviron:
            if isinstance(item, int) and self.canvas.type(item):
                coords = self.canvas.coords(item)
                if any(self.withinCanvas((coords[j], coords[j + 1]))
                       for j in range(0, len(coords), 2)):
                    itemCoords[item] = coords
                    self.canvas.coords(item, V(coords) +
                                       V(away * (len(coords) // 2)))
        return itemCoords

    def resumeCallEnvironment(self, callEnviron, itemCoords, sleepTime=0):
        self.callStack.append(callEnviron)
        codeBlock = self.getCodeHighlightBlock(callEnviron)
        if codeBlock:
            self.showCode(codeBlock.code, sleepTime=sleepTime,
                          addBoundary=True, allowStepping=False)
            codeBlock.markStart()
            self.highlightCode(codeBlock.currentFragments, callEnviron, wait=0)
        for item in itemCoords:
            self.canvas.coords(item, *itemCoords[item])
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
                self.window.update()
                if self.destroyed:
                    sys.exit()
                time.sleep(0.02)
                if self.destroyed:
                    sys.exit()
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
        withArgs, withoutArgs, nColumns, nRows = self.getOperations()
        args = self.getArguments()
        for btn in withArgs + withoutArgs:
            if isinstance(btn, self.buttonTypes):
                nArgs = getattr(btn, 'required_args', 0)
                self.widgetState(
                    btn, NORMAL if enable and all(args[:nArgs]) else DISABLED)
            
            elif btn is getattr(self, 'playControlsFrame', False):
                for b in (self.pauseButton, self.stepButton, self.stopButton):
                    if b:
                        self.widgetState(
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
        self.animationState = state if state is not None else (
            self.animationState if self.animationState in (Animation.RUNNING,
                                                           Animation.STEP)
            else Animation.RUNNING)
        self.enableButtons(enable=False)
        if self.pauseButton and not self.animationsStepping():
            buttonImage(self.pauseButton, self.playControlImages['pause'])
        for btn in (self.pauseButton, self.stopButton):
            if btn and enableStops:
                self.widgetState(btn, NORMAL)
        if self.stepButton and enableStops and (
                self.codeText or state == Animation.STEP):
            self.widgetState(self.stepButton, NORMAL)

    def stopAnimations(self):  # Stop animation of a call on the call stack
        # Calls from stack level 2+ only stop animation for their level
        # At lowest level, animation stops and play & stop buttons are disabled
        if len(self.callStack) <= 1:
            self.animationState = Animation.STOPPED
            self.enableButtons(enable=True)
            for btn in (self.pauseButton, self.stopButton, self.stepButton):
                if btn:
                    self.widgetState(btn, DISABLED)
            self.argumentChanged()
        # Otherwise, let animation be stopped by a lower call

# Tk widget utilities

def buttonImage(btn, image=None):
    if image is None:   # Tk stores the actual image in the image attribute
        return btn.image
    else:    
        btn['image'] = image # This triggers an update to the button appearance
        btn.image = image  # and this puts the aclual image in the attribut
        return image

def clearHintHandler(hintLabel, textEntry=None):
    'Clear the hint text and set focus to textEntry, if provided'
    return lambda event: (
        textEntry.focus_set() if event.widget == hintLabel and textEntry
        else 0) or hintLabel.config(text='') or hintLabel.grid_remove()
