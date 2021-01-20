__doc__ = """
Base class for Python visualizations.
Provides common tools for all modules including control panel
and drawing canvas.
The control panel has containers for
 * Functions that take an argument
 * Functions that take no argument
 * A speed control for slow to fast animation or single step increments
 * A text message area for providing messages
 * A text window for showing and highlighting code snippets
"""

import time, math, operator, re, sys
from collections import *
from tkinter import *
from tkinter import ttk
import tkinter.font as tkfont

try:
    from coordinates import *
    from TextHighlight import *
except ModuleNotFoundError:
    from .coordinates import *
    from .TextHighlight import *
    
# Utilities for vector math; used for canvas item coordinates
V = vector
def add_vector(v1, v2):
    return V(v1) + V(v2)

def subtract_vector(v1, v2):
    return V(v1) - V(v2)
    return tuple(map(operator.sub, v1, v2))

def divide_vector(v1, v2):   # v2 can be scalar
    if not isinstance(v2, (list, tuple)):
        v2 = [v2] * len(v1)  # Copy scalar value for vector dimension
    return V(v1) / V(v2)

def multiply_vector(v1, v2): # v2 can be scalar
    if not isinstance(v2, (list, tuple)):
        v2 = [v2] * len(v1)  # Copy scalar value for vector dimension
    return V(v1) * V(v2)

def rotate_vector(v1, angle=0): # Rotate vector by angle degrees
    return V(v1).rotate(angle)

def vector_length2(vect):    # Get the vector's length squared
    return V(vect).len2()

def vector_length(vect):     # Get the vector's length
    return V(vect).vlen()

def BBoxesOverlap(bbox1, bbox2): # Determine if bounding boxes overlap
    return (rangesOverlap(bbox1[0], bbox1[2], bbox2[0], bbox2[2]) and 
            rangesOverlap(bbox1[1], bbox1[3], bbox2[1], bbox2[3]))

def rangesOverlap(           # Determine if a range overlaps another
        lo1, hi1, lo2, hi2,  # Allow zero overlap, if requested
        zeroOK=True):
    return ((hi1 > lo2 or (zeroOK and hi1 == lo2)) and
            (lo1 < hi2 or (zeroOK and lo1 == hi2)))
    
def gridDict(frame):
    slaves = frame.grid_slaves()
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

geom_delims = re.compile(r'[\sXx+-]')

class VisualizationApp(object):  # Base class for Python visualizations

    # Default styles for display of values and operational controls
    DEFAULT_BG = 'white'
    FONT_SIZE = -20
    VALUE_FONT = ('Helvetica', FONT_SIZE)
    VALUE_COLOR = 'black'
    VARIABLE_FONT = ('Courier', FONT_SIZE * 8 // 10)
    VARIABLE_COLOR = 'brown3'
    NONLOCAL_VARIABLE_COLOR = 'bisque'
    FOUND_FONT = ('Helvetica', FONT_SIZE)
    FOUND_COLOR = 'green2'
    OPERATIONS_BG = 'beige'
    OPERATIONS_BORDER = 'black'
    CODE_FONT = ('Courier', -12)
    SMALL_FONT = ('Helvetica', -9)
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

    # Animation states
    STOPPED = 0
    RUNNING = 1
    PAUSED = 2
    STEP = 3

    def __init__(  # Constructor
            self,
            window=None,      # Run visualization within given window
            title=None,
            canvasWidth=800,  # Canvas size
            canvasHeight=400,
            maxArgWidth=3,    # Maximum length/width of text arguments
            hoverDelay=1000,  # Milliseconds to wait before showing hints
    ):
        self.title = title
        # Set up Tk windows for canvas and operational controls
        if window:
            self.window = window
        else:
            self.window = Tk()
            if title:
                self.window.title(title)
        self.targetCanvasWidth = canvasWidth
        self.targetCanvasHeight = canvasHeight
        self.canvas = Canvas(
            self.window, width=canvasWidth, height=canvasHeight,
            bg=self.DEFAULT_BG)
        self.canvas.pack(expand=True, fill=BOTH)
        self.maxArgWidth = maxArgWidth

        self.HOVER_DELAY = hoverDelay
        self.setUpControlPanel()

        # Set up instance variables for managing animations and operations
        self.callStack = []    # Stack of local environments for visualziation
        self.animationState = self.STOPPED
        self.pauseButton, self.stopButton, self.stepButton = None, None, None
        self.lastCodeBlock, self.lastCodeBlockFragments = None, None
 
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

    buttonTypes = (ttk.Button, Button, Checkbutton, Radiobutton)
    
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
        gridItems = gridDict(self.operations) # Operations inserted in grid
        nColumns, nRows = self.operations.grid_size()
        withArgument = [
            gridItems[0, row] for row in range(nRows)
            if isinstance(gridItems[0, row], self.buttonTypes)]
        withoutArgument = [
            gridItems[col, row]
            for row in range(nRows) for col in range(4, nColumns)
            if isinstance(gridItems[col, row], self.buttonTypes)]
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
            callback, cleanUpBefore, button if numArguments > 0 else None)
        setattr(button, 'required_args', numArguments)
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
            buttonRow = len(withArgument) + 1
            button.grid(column=0, row=buttonRow, padx=8, sticky=(E, W))
            self.widgetState(button, DISABLED)
            nEntries = len(self.textEntries)
            rowSpan = max(1, (len(withArgument) + 1) // nEntries)
            
            # Spread text entries across all rows of buttons with arguments
            # with the hint about what to enter below, if any
            for i, entry in enumerate(self.textEntries):
                entryRowSpan = rowSpan if i < nEntries - 1 else max(
                    1, len(withArgument) + 1 - (nEntries - 1) * rowSpan)
                entry.grid_configure(row=rowSpan * i + 1, rowspan=entryRowSpan)
            if self.entryHint:
                self.entryHintRow = max(nEntries, len(withArgument) + 1) + (
                    0 if entryRowSpan > 2 else 1)
                self.entryHint.grid_configure(column=2, row=self.entryHintRow)

        else:
            buttonRow = len(withoutArgument) % maxRows + 1
            button.grid(column=4 + len(withoutArgument) // maxRows,
                        row=buttonRow, padx=8, sticky=(E, W))
        if ((len(withoutArgument) if numArguments else len(withArgument)) > 0
                and not self.opSeparator):  # If both kinds of buttons are present
            self.opSeparator = Frame(  # but not a separator line, create one
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
    
    def returnPressed(self, event):  # Handle press of Return/Enter in text
        button = getattr(            # entry argument widget.
            event.widget, 'last_button', None)
        if button:                   # If last_button attribute is defined
            if self.widgetState(button) == NORMAL:
                self.widgetState(    # Re-do button press
                    button, 
                    'pressed' if isinstance(button, ttk.Button) else ACTIVE)
                self.window.update()
                time.sleep(0.05)
                self.widgetState(
                    button, 
                    '!pressed' if isinstance(button, ttk.Button) else NORMAL)
                button.invoke()
                
    def addAnimationButtons(self, maxRows=4, setDefaultButton=True):
        self.pauseButton = self.addOperation(
            "Pause", lambda: self.onClick(self.pause, self.pauseButton),
            cleanUpBefore=False, maxRows=maxRows,
            helpText='Pause or resume playing animation')
        self.widgetState(self.pauseButton, DISABLED)
        self.stepButton = self.addOperation(
            "Step", lambda: self.onClick(self.step, self.pauseButton),
            cleanUpBefore=False, maxRows=maxRows,
            helpText='Play one step')
        self.widgetState(self.stepButton, DISABLED)
        self.stopButton = self.addOperation(
            "Stop", lambda: self.onClick(self.stop, self.pauseButton),
            cleanUpBefore=False, maxRows=maxRows,
            helpText='Stop animation')
        self.widgetState(self.stopButton, DISABLED)
        if setDefaultButton and self.textEntries:
            if isinstance(setDefaultButton, self.buttonTypes):
                setattr(self.textEntries[0], 'last_button', setDefaultButton)
            else:
                gridItems = gridDict(self.operations)
                nColumns, nRows = self.operations.grid_size()
                withArgument = [
                    gridItems[0, row] for row in range(nRows)
                    if isinstance(gridItems[0, row], self.buttonTypes)]
                if len(withArgument) == 1:
                    setattr(self.textEntries[0], 'last_button', withArgument[0])
        
    def runOperation(self, command, cleanUpBefore, button=None):
        def animatedOperation(): # If button that uses arguments is provided,
            if button and hasattr(button, 'required_args'): # record it as the
                for entry in self.textEntries[:getattr( # last button pressed
                        button, 'required_args')]: # for all its required args
                    setattr(entry, 'last_button', button)
            try:
                if cleanUpBefore:
                    self.cleanUp()
                command()
            except UserStop as e:
                self.cleanUp(self.callStack[0] if self.callStack else None)
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
        gridItems = gridDict(self.operations)  # All operations
        nColumns, nRows = self.operations.grid_size()
        for button in [gridItems[0, row] for row in range(nRows)
                       if isinstance(gridItems[0, row], self.buttonTypes)]:
            nArgs = getattr(button, 'required_args')
            self.widgetState(
                button,
                DISABLED if self.animationState != self.STOPPED or any(
                    arg == '' for arg in args[:nArgs]) else NORMAL)

        for i, entry in enumerate(self.textEntries):
            if widget == entry:  # For the entry widget that changed,
                self.setArgumentHighlight(i) # clean any error highlight
            
    def setMessage(self, val=''):
        self.outputText.set(val)
        
    vScrollWidth = 10      # Guess for width of vertical scrollbar width
    
    def showCode(self,     # Show algorithm code in a scrollable text box
                 code,     # Code to display, plus optional boundary line
                 addBoundary=False, # to separate calls on the stack
                 prefix='',      # Prefix to apply to snippet labels
                 snippets={},    # Dict of snippet label -> text indices
                 sleepTime=0):   # Wait time between adding lines of text
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
        
        # Add a call stack boundary line if requested and other code exists
        currentCode = self.codeText.get('1.0', END)
        if addBoundary and currentCode and not currentCode.isspace():
            self.codeText.insert('1.0',
                                 self.codeText.config('width')[-1] * '-' + '\n')
            self.codeText.tag_add('call_stack_boundary', '1.0', '1.end')
        
        # Add code at top of text widget (above stack boundary, if any)
        if sleepTime > 0:
            for line in reversed(code.split('\n')):
                if self.codeText:
                    self.codeText.insert('1.0', line + '\n')
                self.wait(sleepTime)
        else:
            self.codeText.insert('1.0', code + '\n')
        if self.codeText:
            self.codeText.see('1.0')
            
        # Doing a window update here can cause multiple resize events
        self.window.update()
        
        # Tag the snippets with unique tag name
        if self.codeText:
            for tagName in snippets:
                self.codeText.tag_add(prefix + tagName, *snippets[tagName])
            self.codeText.configure(state=DISABLED)

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
                print('Skipping resize whiler timer {} running'.format(
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
        if codeBlock is None:  # This should only happen when code is hidden
            return
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
                ranges = self.codeText.tag_ranges(tagName)
                if len(ranges) > 0:
                    self.codeText.see(ranges[0])
        if not found and len(tags) > 0:  # This shouldn't happen so log bug
            print('Unable to find highlight tag(s) {} among {}'.format(
                ', '.join(tags), ', '.join(codeBlock.cache.keys())))
        if wait > 0:              # Optionally weit for highlight to show
            self.wait(wait)

    # Return the CodeHighlightBlock from the set object from the call stack
    # NOTE: this could be more efficient if the objects on the call stacks
    # were dictionaries but Python doesn't allow mutable objects like a
    # CodeHighlightBlock as keys so we'd need a special key that couldn't
    # be confused with a canvas item (string or integer) to index it
    # Instead, we do a linear search and find it by its type
    def getCodeHighlightBlock(self, callEnvironment):
        for item in callEnvironment:
            if isinstance(item, CodeHighlightBlock):
                return item
            
    def cleanUp(self,         # Remove Tk items from past animations either
                callEnviron=None,  # for a particular call or all calls
                stopAnimations=True, # stop animations if requested and
                sleepTime=0): # wait between removing code lines from stack
        if stopAnimations:
            self.stopAnimations()
        minStack = 1 if callEnviron else 0 # Don't clean beyond minimum, keep
        while len(self.callStack) > minStack: # 1st call unless cleaning all
            top = self.callStack.pop()
            self.cleanUpCallEnviron(top, sleepTime)
            if callEnviron is not None and callEnviron == top: # Stop popping
                break         # stack if a particular call was being cleaned up
                
        if callEnviron is None:  # Clear any messages if cleaning up everything
            self.setMessage()
        if len(self.callStack) == 0: # When call stack is empty
            while len(self.codeFrame.children) > 0: # Remove code window
                tkItem = self.codeFrame.children.popitem()
                tkItem[1].destroy()
            self.codeText = None

    def cleanUpCallEnviron(    # Clean up a call on the stack
            self, callEnviron, # removing the call environement
            sleepTime=0):      # waiting sleepTime between removing code lines
        inUserStop = False
        while len(callEnviron):
            thing = callEnviron.pop()
            if isinstance(thing, (str, int)) and self.canvas.type(thing):
                self.canvas.delete(thing)
            elif isinstance(thing, CodeHighlightBlock) and self.codeText:
                self.codeText.configure(state=NORMAL)
                self.wait(0)
                last_line = int(
                    float(self.codeText.index(END))
                    ) if len(thing.lines) > 0 else 0
                for i in range(1, min(last_line, len(thing.lines) + 2)):
                    if self.codeText:
                        self.codeText.delete('1.0', '2.0')
                        if sleepTime > 0 and not self.animationsStopped():
                            try:
                                self.wait(sleepTime)
                            except UserStop:
                                inUserStop = True
                if self.codeText:
                    self.codeText.configure(state=DISABLED)
        if inUserStop:
            raise UserStop()

    def createCallEnvironment( # Create a call environment on the call stack
            self,              # for animating a particular call
            code='',           # code for this call, if any
            sleepTime=0):      # Wait time between inserting lines of code
        # The call environment is a set for local variables represented by
        # canvas items plus a codeHighlightBlock that controls code highlights
        code = code.strip()
        callEnviron = set()
        if len(code) > 0:
            self.showCode(code, addBoundary=True, sleepTime=sleepTime)
            codeHighlightBlock = CodeHighlightBlock(code, self.codeText)
            if self.codeText:
                codeHighlightBlock.markStart()
            callEnviron.add(codeHighlightBlock)
            
        self.callStack.append(callEnviron) # Push environment on stack
        return callEnviron
        
    # General Tk widget methods
    def widgetDimensions(self, widget):  # Get widget's (width, height)
        geom = geom_delims.split(widget.winfo_geometry())
        if geom[0] == '1' and geom[1] == '1':  # If not yet managed, use config
            geom = (widget.config('width')[-1], widget.config('height')[-1])
        return int(geom[0]), int(geom[1])

    def widgetState(self, widget, state=None): # Get or set widget state
        if isinstance(widget, (ttk.Button,)):
            if state is None:
                stateFlags = widget.state()
                return DISABLED if DISABLED in stateFlags else NORMAL
            else:
                widget.state(('!disabled', '!pressed') if state == NORMAL 
                             else (state, ))
        else:
            if state is None:
                return widget['state']
            else:
                widget['state'] = state
            
    sizePattern = re.compile(r'-?\d+')

    def textWidth(self, font, text=' '):
        return self.tkFontFromSpec(font).measure(text)
        
    def textHeight(self, font, text=' '):
        lines = text.split('\n')
        nLines = len(lines) if lines and len(lines[-1]) > 0 else len(lines) - 1
        return self.tkFontFromSpec(font).metrics()['linespace'] * nLines

    def tkFontFromSpec(self, spec):
        family = spec[0]
        size = spec[1] if (len(spec) > 1 and 
                           (isinstance(spec[1], int) or
                            (isinstance(spec[1], str) and 
                             self.sizePattern.match(spec[1])))) else 0
        return tkfont.Font(
            family=family, size=size,
            weight=self.lookFor(('bold', 'light'), spec, 'normal'),
            slant=self.lookFor(('italic', 'oblique'), spec, 'roman'),
            underline=1 if self.lookFor(('underline',), spec, 0) else 0,
            overstrike=1 if self.lookFor(('overstrike',), spec, 0) else 0)
        
    def lookFor(self, keys, spec, default):  # Find keyword in font spec
        strings = [x.lower() for x in spec if isinstance(x, str)]
        for key in keys:
            if key.lower() in strings:
                return key
        return default

    # CANVAS ITEM METHODS
    def canvas_itemconfigure(  # Get a dictionary with the canvas item's
            self, canvasitem): # configuration
        config = self.canvas.itemconfigure(canvasitem)
        for key in config:     # Replace tuple values with the last item
            if isinstance(config[key], tuple):  # in tuple
                config[key] = config[key][-1]
        return config

    def copyCanvasItem(      # Make a copy of an item in the canvas
            self, canvasitem):
        creator = getattr(self.canvas,  # Get canvas creation function for type
                          'create_{}'.format(self.canvas.type(canvasitem)))
        newItem = creator(*self.canvas.coords(canvasitem),
                          **self.canvas_itemconfigure(canvasitem))
        for eventType in self.canvas.tag_bind(canvasitem): # Copy event handlers
            self.canvas.tag_bind(newItem, eventType,
                                 self.canvas.tag_bind(canvasitem, eventType))
        return newItem

    def fadeNonLocalItems(self, items, color=NONLOCAL_VARIABLE_COLOR):
        'Set fill color of non-local variable canvas items to a faded color'
        self.setItemsFillColor(items, color)
        
    def restoreLocalItems(self, items, color=VARIABLE_COLOR):
        'Restore fill color of local variable canvas items to normal'
        self.setItemsFillColor(items, color)

    def setItemsFillColor(self, items, color):
        for item in items:
            self.canvas.itemconfigure(item, fill=color)

    #####################################################################
    #                                                                   #
    #                       Animation Methods                           #
    #                                                                   #
    #####################################################################
    # These methods animate canvas items moving in increments with an
    # adjustable speed.  The items are moved together as a group.
    # They take differing paths to get to their destinations.  The
    # items parameter for each method can be either a single item ID
    # or tag, or a list|tuple|set of IDs or tags. The steps parameter
    # specifies how many incremental steps should be taken in
    # completing the movement and must be 1 or more.  The sleepTime
    # specifies how long to wait between incremental steps.  A
    # sleepTime of 0 will produce the fastest steps, but you may not
    # see the intermediate positions of the items.  Each moveItems____
    # method calls a generator called moveItems____Sequence that
    # iterates over the steps yielding the step from 0 up to steps-1
    # and the total number of steps (some methods my change the number
    # of steps) This enables combining animation sequences by using
    # the *Sequence generator to go through the steps and performing
    # other animation actions for each step.  Each moveItems____
    # method calls self.wait(0) at the beginning to wait if step mode
    # has been engaged

    def moveItemsOffCanvas(  # Animate the removal of canvas items by sliding
            self, items,     # them off one of the canvas edges
            edge=N,          # One of the 4 tkinter edges: N, E, S, or W
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        self.wait(0)
        for step, _ in self.moveItemsOffCanvasSequence(items, edge, steps):
            self.wait(sleepTime)

    def moveItemsOffCanvasSequence(  # Iterator for moveItemsOffCanvas
            self, items, edge=N, steps=10):
        if not isinstance(items, (list, tuple, set)):
            items = (items,)
        curPositions = [self.canvas.coords(i) for i in items if i is not None]
        bboxes = [self.canvas.bbox(i) for i in items if i is not None]
        bbox = bboxes[0]  # Get bounding box of all items
        for bb in bboxes[1:]:
            bbox = [min(bbox[0], bb[0]), min(bbox[1], bb[1]),
                    max(bbox[2], bb[2]), max(bbox[3], bb[3])]
        canvasDimensions = self.widgetDimensions(self.canvas)
        # Compute delta vector that moves them on a line away from the
        # center of the canvas
        delta = ((bbox[0] + bbox[2] - canvasDimensions[0]) / 2,
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
            delta = (abs(delta[1]) * (-1 if delta[0] < 0 else 1), delta[1])
        elif abs(delta[0]) < abs(delta[1]) and edge not in (N, S):
            delta = (delta[0], abs(delta[0]) * (-1 if delta[1] < 0 else 1))
        for step, _ in self.moveItemsBySequence(items, delta, steps):
            yield (step, _)

    def moveItemsBy(         # Animate canvas items moving from their current
            self, items,     # location in a direction indicated by a single
            delta,           # delta vector. items can be 1 item or a list/tuple
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        self.wait(0)
        for step, _ in self.moveItemsBySequence(items, delta, steps):
            self.wait(sleepTime)

    def moveItemsBySequence( # Iterator for moveItemsBy
            self, items, delta, steps=10):
        if not isinstance(items, (list, tuple, set)):
            items = (items,)
        if not isinstance(delta, (list, tuple)) or len(delta) != 2:
            raise ValueError('Delta must be a 2-dimensional vector')
        if vector_length2(delta) < 0.001: # If delta is tiny
            return           # then no movement is needed
        steps = max(1, steps) # Must use at least 1 step

        # move the items in steps along vector
        moveBy = divide_vector(delta, steps)
        for step in range(steps):
            for item in items:
                if item is not None:
                    self.canvas.move(item, *moveBy)
            yield (step, steps) # Yield step in sequence

    def moveItemsTo(         # Animate canvas items moving rigidly 
            self, items,     # to destination locations along line(s)
            toPositions,     # items can be a single item or list of items
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        self.wait(0)
        for step, _ in self.moveItemsToSequence(items, toPositions, steps):
            self.wait(sleepTime)

    def moveItemsToSequence( # Iterator for moveItemsTo
            self, items,     # to destination locations along line(s)
            toPositions,     # items can be a single item or list of items
            steps=10):
        if not isinstance(items, (list, tuple, set)):
            items = (items,)
        if not isinstance(toPositions, (list, tuple)):
            raise ValueError('toPositions must be a list or tuple of positions')
        if not isinstance(toPositions[0], (list, tuple)):
            toPositions = (toPositions,)
        steps = max(1, steps) # Must use at least 1 step
        moveBy = [divide_vector(subtract_vector(toPos, fromPos), steps)
                  for toPos, fromPos in zip(
                          toPositions,
                          [self.canvas.coords(item)[:2] for item in items])]

        # move the items until they reach the toPositions
        for step in range(steps):
            for i, item in enumerate(items):
                if len(moveBy[i]) == 2:
                    self.canvas.move(item, *moveBy[i])
                # else:  # This shouldn't happen, but is a good point to debug
                #     pdb.set_trace()
            yield (step, steps) # Yield step in sequence
            
        # Force position of new objects to their exact destinations
        for pos, item in zip(toPositions, items):
            self.canvas.coords(item, *pos)

    # The moveItemsLinearly method uses all the coordinates of canvas
    # items in calculating the movement vectors.  Don't pass the
    # 'items' arguments with canvas tags attached to multiple items.
    # If you do, it will only move one of them and the number of
    # coordinates for it the toPositions argument could be a mismatch.
    # Pass item IDs to ensure a 1-to-1 mapping.
    def moveItemsLinearly(   # Animate canvas items moving each of their 
            self, items,     # coordinates linearly to new destinations
            toPositions,     # Items can be single or multiple, but not tags
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        self.wait(0)
        for step, _ in self.moveItemsLinearlySequence(
                items, toPositions, steps):
            self.wait(sleepTime)

    def moveItemsLinearlySequence( # Iterator for moveItemsLinearly
            self, items, toPositions, steps=10):
        if not isinstance(items, (list, tuple, set)):
            items = (items,)
        if not isinstance(toPositions, (list, tuple)):
            raise ValueError('toPositions must be a list or tuple of positions')
        if not isinstance(toPositions[0], (list, tuple)):
            toPositions = (toPositions,)
        if len(items) != len(toPositions):
            raise ValueError('Number of items must match length of toPositions')
        steps = max(1, steps) # Must use at least 1 step
        moveBy = [divide_vector(subtract_vector(toPos, fromPos), steps)
                  for toPos, fromPos in zip(
                          toPositions,
                          [self.canvas.coords(item) for item in items])]

        # move the items until they reach the toPositions
        for step in range(steps):
            for i, item in enumerate(items):
                if len(moveBy[i]) >= 2:
                    self.canvas.coords(
                        item, *add_vector(self.canvas.coords(item), moveBy[i]))
            yield (step, steps) # Yield step in sequence
            
        # Force position of new objects to their exact destinations
        for pos, item in zip(toPositions, items):
            self.canvas.coords(item, *pos)
             
    def moveItemsOnCurve(    # Animate canvas items moving from their current
            self, items,     # location to destinations along a curve
            toPositions,     # items can be a single item or list of items
            startAngle=90,   # Starting angle away from destination
            steps=10,        # Number of intermediate steps to reach destination
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        self.wait(0)
        for step, _ in self.moveItemsOnCurveSequence(
                items, toPositions, startAngle, steps):
            self.wait(sleepTime)
            
    def moveItemsOnCurveSequence( # Iterator for moveItemsOnCurve
            self, items, toPositions, startAngle=90, steps=10):
        if not isinstance(items, (list, tuple, set)):
            items = tuple(items)
        if not isinstance(toPositions, (list, tuple)):
            raise ValueError('toPositions must be a list or tuple of positions')
        if not isinstance(toPositions[0], (list, tuple)):
            toPositions = tuple(toPositions)
        steps = max(1, steps) # Must use at least 1 step

        # move the items until they reach the toPositions
        for step in range(steps):  # Go through all steps of the annimation
            toGo = steps - 1 - step  # remaining steps to go
            ang = startAngle * toGo / steps  # angle decreases on each step
            scale = 1 + abs(ang) / 180  # scale is larger for higher angles
            for i, item in enumerate(items):
                coords = self.canvas.coords(item)[:2]
                if len(coords) == 2:
                    moveBy = rotate_vector(
                        divide_vector(subtract_vector(toPositions[i], coords),
                                      (toGo + 1) / scale),
                        ang)
                    self.canvas.move(item, *moveBy)
            yield (step, steps) # Yield step in sequence
            
        # Force position of new objects to their exact destinations
        for pos, item in zip(toPositions, items):
            self.canvas.coords(item, *pos)

    # ANIMATION CONTROLS
    def speed(self, sleepTime):
        return min(
            10, sleepTime * 50 * self.SPEED_SCALE_MIN / self.speedScale.get())

    def wait(self, sleepTime):    # Sleep for a user-adjusted period
        codeBlock = (self.getCodeHighlightBlock(self.callStack[-1])
                     if self.callStack else None)
        while self.animationState == self.STEP and (
                self.lastCodeBlock is not codeBlock or
                self.lastCodeBlockFragments != codeBlock.currentFragments):
            self.pauseButton['text'] = "Play"
            self.pauseButton['command'] = self.runOperation(
                lambda: self.onClick(self.play, self.pauseButton), False)
            self.window.update()
            time.sleep(0.02)
        self.lastCodeBlock = codeBlock
        self.lastCodeBlockFragments = (
            self.lastCodeBlock.currentFragments if self.lastCodeBlock else None)
        if sleepTime > 0:
            self.window.update()
            time.sleep(self.speed(sleepTime))
        if self.animationState == self.STOPPED: # If user requested to stop
            raise UserStop()      # animation while waiting then raise exception

    def onClick(self, command, *parameters): # When user clicks an operations
        self.enableButtons(False) # button, disable all buttons,
        command(*parameters)      # run the command, and re-enable the buttons
        if command not in [self.pause, self.play]: # if it was something
            self.enableButtons()  # other than pause or play command
            
    def enableButtons(self, enable=True):
        gridItems = gridDict(self.operations)  # All Tk items in operations 
        nColumns, nRows = self.operations.grid_size() # by grid cell
        for col in range(nColumns):
            for btn in [gridItems[col, row] for row in range(nRows)]:
                # Only change button types, not text entry or other widgets
                # Pause/Stop buttons can only be enabled here
                if isinstance(btn, self.buttonTypes) and (
                        enable or btn not in (self.stopButton, 
                                              self.pauseButton)):
                    self.widgetState(btn, NORMAL if enable else DISABLED)

    def stop(self, pauseButton):
        self.stopAnimations()
        self.animationState = self.STOPPED  # Always stop on user request
        pauseButton['text'] = "Play"
        pauseButton['command'] = self.runOperation(
            lambda: self.onClick(self.play, pauseButton), False)

    def pause(self, pauseButton):
        self.pauseAnimations()
        pauseButton['text'] = "Play"
        pauseButton['command'] = self.runOperation(
            lambda: self.onClick(self.play, pauseButton), False)
        while self.animationState == self.PAUSED:
            self.wait(0.02)

    def play(self, pauseButton):
        self.startAnimations(state=self.RUNNING)

    def step(self, pauseButton):
        codeBlock = (self.getCodeHighlightBlock(self.callStack[-1])
                     if self.callStack else None)
        self.lastCodeBlock = codeBlock
        self.lastCodeBlockFragments = (
            self.lastCodeBlock.currentFragments if self.lastCodeBlock else None)
        self.startAnimations(state=self.STEP)

    def startAnimations(self, enableStops=True, state=None):
        self.animationState = state if state is not None else (
            self.animationState if self.animationState in (self.RUNNING,
                                                           self.STEP)
            else self.RUNNING)
        self.enableButtons(enable=False)
        if self.pauseButton:
            self.pauseButton['text'] = 'Pause'
            self.pauseButton['command'] = self.runOperation(
                lambda: self.onClick(self.pause, self.pauseButton), False)
        for btn in (self.pauseButton, self.stopButton, self.stepButton):
            if btn and enableStops:
                self.widgetState(btn, NORMAL)

    def stopAnimations(self):  # Stop animation of a call on the call stack
        # Calls from stack level 2+ only stop animation for their level
        # At lowest level, animation stops and play & stop buttons are disabled
        if len(self.callStack) <= 1:
            self.animationState = self.STOPPED
            self.enableButtons(enable=True)
            for btn in (self.pauseButton, self.stopButton, self.stepButton):
                if btn:
                    self.widgetState(btn, DISABLED)
            self.argumentChanged()
        # Otherwise, let animation be stopped by a lower call

    def pauseAnimations(self):
        self.animationState = self.PAUSED

    def animationsStopped(self):
        return self.animationState == self.STOPPED

    def animationsRunning(self):
        return self.animationState != self.STOPPED
    
    def runVisualization(self):
        self.window.mainloop()

class UserStop(Exception):   # Exception thrown when user stops animation
    pass

# Tk widget utilities

def clearHintHandler(hintLabel, textEntry=None):
    'Clear the hint text and set focus to textEntry, if provided'
    return lambda event: (
        textEntry.focus_set() if event.widget == hintLabel and textEntry
        else 0) or hintLabel.config(text='') or hintLabel.grid_remove()
