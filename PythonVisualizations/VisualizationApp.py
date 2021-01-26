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

import time, re, sys
from collections import *
from tkinter import *
from tkinter import ttk

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
            hoverDelay=1000,  # Milliseconds to wait before showing hints
            **kwargs
    ):
        super().__init__(**kwargs)

        self.maxArgWidth = maxArgWidth
        self.HOVER_DELAY = hoverDelay

        # Set up instance variables for managing animations and operations
        self.callStack = []    # Stack of local environments for visualziation

        self.pauseButton, self.stopButton, self.stepButton = None, None, None
        self.lastCodeBlock, self.lastCodeBlockFragments = None, None
        
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
                self.cleanUp(self.callStack[0] if self.callStack else None,
                             ignoreStops=True)
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
                stopAnimations=True, # stop animations, if requested
                sleepTime=0,  # wait between removing code lines from stack
                ignoreStops=False): # ignore UserStops, if requested
        if stopAnimations:
            self.stopAnimations()
        minStack = 1 if callEnviron else 0 # Don't clean beyond minimum, keep
        while len(self.callStack) > minStack: # 1st call unless cleaning all
            top = self.callStack.pop()
            try:
                self.cleanUpCallEnviron(
                    top, sleepTime, allowSteps=len(self.callStack) > 0)
            except UserStop:
                if not ignoreStops:
                    raise UserStop
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
            sleepTime=0,       # waiting sleepTime between removing code lines
            allowSteps=True):  # allowing step pauses if set
        inUserStop = False
        while len(callEnviron):
            thing = callEnviron.pop()
            if isinstance(thing, (str, int)) and self.canvas.type(thing):
                self.canvas.delete(thing)
            elif isinstance(thing, CodeHighlightBlock) and self.codeText:
                self.codeText.configure(state=NORMAL)
                if allowSteps:
                    try:
                        self.wait(0)
                    except UserStop:
                        inUserStop = True
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

    # ANIMATION CONTROLS
    def speed(self, sleepTime):
        return min(
            10, sleepTime * 50 * self.SPEED_SCALE_MIN / self.speedScale.get())

    def wait(self, sleepTime):    # Sleep for a user-adjusted period
        codeBlock = (self.getCodeHighlightBlock(self.callStack[-1])
                     if self.callStack else None)
        while self.animationState == self.STEP and (
                self.lastCodeBlock is not codeBlock or
                codeBlock and
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
                        enable or btn not in (self.stopButton, self.stepButton,
                                              self.pauseButton)):
                    self.widgetState(
                        btn, 
                        NORMAL if enable and (btn != self.stepButton or
                                              self.codeText) 
                        else DISABLED)

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
        for btn in (self.pauseButton, self.stopButton):
            if btn and enableStops:
                self.widgetState(btn, NORMAL)
        if self.stepButton and (self.codeText or state == self.STEP):
            self.widgetState(self.stepButton, NORMAL)

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

# Tk widget utilities

def clearHintHandler(hintLabel, textEntry=None):
    'Clear the hint text and set focus to textEntry, if provided'
    return lambda event: (
        textEntry.focus_set() if event.widget == hintLabel and textEntry
        else 0) or hintLabel.config(text='') or hintLabel.grid_remove()
