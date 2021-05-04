from tkinter import *
import re, math
try:
    from drawnValue import *
    from HashBase import *
    from HashTable_OpenAddressing import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .HashBase import *
    from .HashTable_OpenAddressing import *

# Regular expression for fraction
fraction = re.compile(r'0*\.\d+')

class HashTableOpenAddressing(HashBase):
    MIN_LOAD_FACTOR = 0.2
    MAX_LOAD_FACTOR = 1.0
    CELL_INDEX_COLOR = 'gray60'
    __Deleted = (None, None)
    
    def __init__(
            self, maxArgWidth=8, title="Hash Table - Open Addressing",
            **kwargs):
        kwargs['maxArgWidth'] = maxArgWidth
        super().__init__(title=title, **kwargs)
        self.probe = linearProbe
        self.hash = simpleHash
        self.hashAddressCharacters = ()
        self.nItemsText, self.maxLoadFactorText = None, None
        self.buttons = self.makeButtons()
        self.setupDisplay()
        self.newHashTable()

    def newHashTable(self, nCells=2, maxLoadFactor=0.5):
        self.table = [None] * max(1, nCells)
        self.nItems = 0
        self.maxLoadFactor = maxLoadFactor
        self.display()
        
    def insert(self, key, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(startAnimations=start)
        self.cleanUp(callEnviron)

    def search(self, key, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(startAnimations=start)
        self.cleanUp(callEnviron)

    _findCode = '''
def __find(self, key={key}, deletedOK={deletedOK}):
   for i in self.__probe(self.hash(key), key, self.cells()):
      if (self.__table[i] is None or
          (self.__table[i] is HashTable.__Deleted and
           deletedOK) or
          self.__table[i][0] == key):
         return i
   return None
'''
    
    def _find(self, key, deletedOK=False, code=_findCode, animate=True):
        wait = 0.1 if animate else 0
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()) if animate and code else '',
            startAnimations=animate)

        hashAddress = self.hash(key)
        if animate:
            self.highlightCode(
                'i in self.__probe(self.hash(key), key, self.cells())',
                callEnviron)
            self.hashAddressCharacters = self.animateStringHashing(
                key, hashAddress, sleepTime=wait / 10,
                callEnviron=callEnviron) if self.showHashing.get() else [
                    self.canvas.create_text(
                        *self.hashOutputCoords(), anchor=W,
                        text=' ' + str(hashAddress), font=self.VARIABLE_FONT,
                        fill=self.VARIABLE_COLOR)]

            lastI, currentI = None, None

        for i in self.probe(hashAddress, key, len(self.table)):
            if animate:
                if lastI is None:
                    lastI = self.hashAddressCoords()
                else:
                    lastI = currentI[2:] + currentI[:2]
                currentI = self.cellArrowCoords(i)
                steps = max(abs(c) for c in V(lastI[:2]) - V(currentI[2:]))
                arrow = self.canvas.create_line(
                    *lastI, *currentI, arrow=LAST, width=1, fill='darkblue',
                    smooth=True, splinesteps=steps, tags='probeline')
                callEnviron.add(arrow)
                self.highlightCode(
                    'self.__table[i] is None', callEnviron, wait=wait)
                if self.table[i] is not None:
                    self.highlightCode(
                        'self.__table[i] is HashTable.__Deleted', callEnviron,
                        wait=wait)
                    if self.table[i] is self.__Deleted:
                        self.highlightCode(
                            ('deletedOK', 2), callEnviron, wait=wait)
                    if self.table[i] is not self.__Deleted or not deletedOK:
                        self.highlightCode(
                            'self.__table[i][0] == key', callEnviron, wait=wait)
            if (self.table[i] is None or
                (self.table[i] is self.__Deleted and deletedOK) or
                self.table[i].val == key):
                if animate:
                    self.highlightCode('return i', callEnviron, wait=wait)
                    self.cleanUp(callEnviron)
                    return i

            if animate:
                self.highlightCode(
                    'i in self.__probe(self.hash(key), key, self.cells())',
                    callEnviron)
            
        if animate:
            self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        return None
    
    def display(self):
        '''Erase canvas and redisplay contents.  Call setupDisplay() before
        this to set the display parameters.'''
        canvasDimensions = self.widgetDimensions(self.canvas)
        self.canvas.delete("all")
        self.hasher = self.createHasher(
            y0=canvasDimensions[1] - self.hasherHeight,
            y1=canvasDimensions[1] - 1)
        self.updateNItems()
        self.updateMaxLoadFactor()
        self.arrayCells = [
            self.createArrayCell(j) for j in range(len(self.table))]
        for j in range(len(self.table)):
            coords = self.cellArrowCoords(j)
            self.canvas.create_text(
                *coords[2:], anchor=W, text='{:2d}'.format(j), tags='cellIndex',
                font=self.cellIndexFont, fill=self.CELL_INDEX_COLOR)
        for j, item in enumerate(self.table):
            if item:
                self.table[j] = drawnValue(
                    item.val, *self.createCellValue(
                        j, item.val,
                        color=self.canvas.itemconfigure(
                            item.items[0], 'fill')[-1] if item.items else None))
        self.window.update()

    def updateNItems(self, nItems=None):
        if nItems is None:
            nItems = self.nItems
        outputBoxCoords = self.outputBoxCoords()
        if self.nItemsText is None or self.canvas.type(self.nItemsText) != 'text':
            self.nItemsText = self.canvas.create_text(
                *(V(outputBoxCoords[:2]) + V(5, -5)), anchor=SW,
                text='', font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
        self.canvas.itemconfigure(
            self.nItemsText, text='nItems = {}'.format(nItems))
        
    def updateMaxLoadFactor(self, maxLoadFactor=None):
        if maxLoadFactor is None:
            maxLoadFactor = self.maxLoadFactor
        outputBoxCoords = self.outputBoxCoords()
        if (self.maxLoadFactorText is None or
            self.canvas.type(self.maxLoadFactorText) != 'text'):
            self.maxLoadFactorText = self.canvas.create_text(
                outputBoxCoords[2] - 5, outputBoxCoords[1] - 5, anchor=SE,
                text='', font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
        self.canvas.itemconfigure(
            self.maxLoadFactorText, text='maxLoadFactor = {}%'.format(
                int(100 * maxLoadFactor)))
            
    def animateStringHashing(
            self, text, hashed, sleepTime=0.01,
            callEnviron=None, dx=2, font=VisualizationApp.VARIABLE_FONT, 
            color=VisualizationApp.VARIABLE_COLOR):
        """Animate text flowing into left of hasher and producing
        hashed output string while hasher churns.  Move characters by dx
        on each animation step. Returns list of canvas items for output
        characters"""
        
        if not self.hasher:
            return
        h = self.hasher

        # Create individual character text items to feed into hasher
        text, hashed = str(text), str(hashed)
        inputCoords = self.hashInputCoords(nInputs=1)
        outputCoords = self.hashOutputCoords()
        charWidth = self.textWidth(font, 'W')
        characters = set([
            self.canvas.create_text(
                inputCoords[0] - ((len(text) - i) * charWidth),
                inputCoords[1], text=c, font=font, fill=color, state=DISABLED)
            for i, c in enumerate(text)])
        for c in characters:
            self.canvas.lower(c)
        if callEnviron:
            callEnviron |= characters

        output = []        # Characters of hashed output
        pad = abs(font[1])
        rightEdge = h['BBox'][2] + pad
        leftmostOutput = rightEdge

        # While there are input characters or characters yet to output or
        # characters to move out of hasher
        while (characters or len(output) < len(hashed) or
               leftmostOutput < rightEdge):
            self.moveItemsBy(    # Move all characters
                characters.union(output), (dx, 0), sleepTime=sleepTime, steps=1)
            self.incrementHasherPhase()
            deletion = False
            for char in list(characters): # For all input characters
                coords = self.canvas.coords(char)  # See if they entered the
                if coords[0] - pad >= h['BBox'][0]: # hasher bounding box and
                    deletion = True       # delete them if they did
                    if callEnviron:
                        self.dispose(callEnviron, char)
                    else:
                        self.canvas.delete(char)
                    characters.discard(char)
                    
            if output:
                leftmostOutput = self.canvas.coords(output[-1])[0]

            # When there are characters to ouput and we've either already
            # output a character or deleted an input character and there
            # is room for the next output character, create it
            if (len(output) < len(hashed) and (output or deletion) and
                leftmostOutput >= rightEdge):
                output.append(
                    self.canvas.create_text(
                        max(leftmostOutput - charWidth, outputCoords[0]),
                        outputCoords[1], text=hashed[-(len(output) + 1)], 
                        font=font, fill=color, state=DISABLED))
                self.canvas.lower(output[-1])
                if callEnviron:
                    callEnviron.add(output[-1])
        return output
 
    def hashAddressCoords(self):
        bbox = BBoxUnion(self.canvas.bbox(c) 
                         for c in self.hashAddressCharacters)
        top = ((bbox[0] + bbox[2]) // 2, bbox[1])
        return top + (V(top) + V(0, -60))
                         
    # Button functions
    def clickSearch(self):
        entered_text = self.getArgument(0)
        if not entered_text or entered_text.isspace():
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
            self.setMessage("No printable text entered")
            return
        key = int(entered_text) if entered_text.isdigit() else entered_text
        self.setMessage("{} {} in hash table".format(
            repr(key),
            "found" if self.search(key, start=self.startMode()) else
            "not found"))
        self.clearArgument()

    def clickInsert(self):
        entered_text = self.getArgument(0)
        if not entered_text or entered_text.isspace():
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
            self.setMessage("No printable text entered")
            return
        key = int(entered_text) if entered_text.isdigit() else entered_text
        self.setMessage("{} {} in hash table".format(
            repr(key),
            "inserted" if self.insert(key, start=self.startMode()) else
            "updated"))
        self.clearArgument()

    def clickDelete(self):
        entered_text = self.getArgument(0)
        if not entered_text or entered_text.isspace():
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
            self.setMessage("No printable text entered")
            return
        key = int(entered_text) if entered_text.isdigit() else entered_text
        self.setMessage("{} {} hash table".format(
            repr(key),
            "deleted from" if self.delete(key, start=self.startMode()) else
            "not found in"))
        self.clearArgument()

    def clickNew(self):
        nCells, maxLoadFactor = self.getArguments()
        msg = []
        if (nCells.isdigit() and
            1 <= int(nCells) and int(nCells) <= self.MAX_CELLS):
            nCells = int(nCells)
        else:
            msg.append('Number of cells must be between 1 and {}.'.format(
                self.MAX_CELLS))
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
            nCells = 2
            msg.append('Using {} cells'.format(nCells))
        if fraction.match(maxLoadFactor):
            maxLoadFactor = float(maxLoadFactor)
        if not isinstance(maxLoadFactor, float) or not (
                self.MIN_LOAD_FACTOR <= maxLoadFactor and
                maxLoadFactor < self.MAX_LOAD_FACTOR):
            msg.append('Max load factor must be fraction between {} and {}'
                       .format(self.MIN_LOAD_FACTOR, self.MAX_LOAD_FACTOR))
            self.setArgumentHighlight(1, self.ERROR_HIGHLIGHT)
            maxLoadFactor = 0.5
            msg.append('Using max load factor = {}'.format(maxLoadFactor))
        if msg:
            self.setMessage('\n'.join(msg))
        self.newHashTable(nCells, maxLoadFactor)

    def clickShowHashing(self):
        if not self.showHashing.get():
            self.positionHashBlocks(0)

    def clickChangeProbeHandler(self, probeFunction):
        def changeProbe():
            self.probe = probeFunction
        return changeProbe
        
    def makeButtons(self):
        vcmd = (self.window.register(
            makeFilterValidate(self.maxArgWidth)), '%P')
        self.insertButton = self.addOperation(
            "Insert", self.clickInsert, numArguments=1, validationCmd=vcmd,
            helpText='Insert a key into the hash table',
            argHelpText=['key'])
        searchButton = self.addOperation(
            "Search", self.clickSearch, numArguments=1, validationCmd=vcmd,
            helpText='Search for a key in the hash table',
            argHelpText=['key'])
        deleteButton = self.addOperation(
            "Delete", self.clickDelete, numArguments=1, validationCmd=vcmd,
            helpText='Delete a key in the hash table',
            argHelpText=['key'])
        newButton = self.addOperation(
            "New", self.clickNew, numArguments=2, validationCmd=vcmd,
            helpText='Create new hash table with\n'
            'number of keys & max load factor',
            argHelpText=['number of cells', 'max load factor'])
        self.showHashing = IntVar()
        self.showHashing.set(1)
        showHashingButton = self.addOperation(
            "Animate hashing", self.clickShowHashing, buttonType=Checkbutton,
            variable=self.showHashing, 
            helpText='Show/hide animation during hashing')
        self.probeChoice = StringVar()
        self.probeChoice.set(self.probe.__name__)
        self.probeChoiceButtons = [
            self.addOperation(
                "Use {}".format(probe.__name__),
                self.clickChangeProbeHandler(probe), buttonType=Radiobutton,
                variable=self.probeChoice, cleanUpBefore=False, 
                value=probe.__name__,
                helpText='Set probe to {}'.format(probe.__name__))
            for probe in (linearProbe, quadraticProbe, doubleHashProbe)]
        self.addAnimationButtons()

    def enableButtons(self, enable=True):
        super().enableButtons(enable)
        for btn in self.probeChoiceButtons: # Probe function can only be
            self.widgetState(               # selected while hash table has no
                btn,                        # items
                NORMAL if enable and self.nItems == 0 else DISABLED)
    
def makeFilterValidate(maxWidth, exclude=''):
    "Register this with one parameter: %P"
    return lambda value_if_allowed: (
        len(value_if_allowed) <= maxWidth and
        all(c not in exclude for c in value_if_allowed))

if __name__ == '__main__':
    hashTable = HashTableOpenAddressing()
    showHashing = hashTable.showHashing.get()
    hashTable.showHashing.set(0)
    for arg in sys.argv[1:]:
        hashTable.setArgument(arg)
        hashTable.insertButton.invoke()
        
    hashTable.showHashing.set(showHashing)
    hashTable.runVisualization()
