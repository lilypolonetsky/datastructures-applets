from tkinter import *
import re, math
try:
    from drawnValue import *
    from tkUtilities import *
    from HashBase import *
    from OutputBox import *
    from HashTable_OpenAddressing import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .tkUtilities import *
    from .HashBase import *
    from .OutputBox import *
    from .HashTable_OpenAddressing import *

# Regular expression for fraction
fraction = re.compile(r'0*\.\d+')

class HashTableOpenAddressing(HashBase):
    MIN_LOAD_FACTOR = 0.2
    MAX_LOAD_FACTOR = 1.0
    CELL_INDEX_COLOR = 'gray60'
    __Deleted = (None, 'Deletion marker')
    deletedFillColor = 'lemon chiffon'
    deletedFontModifiers = ('italic', 'overstrike', 'underline')
    deletedStipple = 'gray50'
    
    def __init__(
            self, maxArgWidth=8, title="Hash Table - Open Addressing",
            **kwargs):
        kwargs['maxArgWidth'] = maxArgWidth
        super().__init__(title=title, **kwargs)
        self.maxFillAmount = 99
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

    def loadFactor(self):
        return self.nItems / len(self.table)
        
    insertCode = '''
def insert(self, key={key}, value):
   i = self.__find(key, deletedOK=True)
   if i is None:
      raise Exception('Hash table probe sequence failed on insert')
   if (self.__table[i] is None or
       self.__table[i] is HashTable.__Deleted):
      self.__table[i] = (key, value)
      self.__nItems += 1
      if self.loadFactor() > self.__maxLoadFactor:
         self.__growTable()
      return True
                         
   if self.__table[i][0] == key:
      self.__table[i] = (key, value)
      return False
'''
    
    def insert(
            self, key, keyAndDataItems=None, inputText=None,
            code=insertCode, start=True):
        '''Insert a user provided key or the key-data item from the old table
        during growTable.  Animate operation if code is provided,
        starting in the specified animation mode.  The inputText can
        be a text item that is moved into the input of the hasher.  It
        will be deleted and replaced by the hashed address for hashing
        animation.
        '''
        wait = 0.1 if code else 0
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()) if code else '',
            startAnimations=code and start)
        
        if code:
            self.highlightCode('i = self.__find(key, deletedOK=True)',
                               callEnviron)
        i = self._find(key, deletedOK=True, code=self._findCode if code else '',
                       inputText=inputText)
        if i is not None and code:
            iArrow = self.createArrayIndex(i, 'i')
            callEnviron |= set(iArrow)

        if code:
            self.highlightCode('i is None', callEnviron, wait=wait)
        if i is None:
            if code:
                self.highlightCode(
                    "raise Exception('Hash table probe sequence failed on insert')",
                    callEnviron, wait=wait, color=self.EXCEPTION_HIGHLIGHT)
            self.setMessage('Probe sequence failed')
            self.cleanUp(callEnviron)
            return
        
        if code:
            self.highlightCode('self.__table[i] is None', callEnviron, wait=wait)
            if self.table[i] is not None:
                self.highlightCode(
                    'self.__table[i] is HashTable.__Deleted', callEnviron,
                    wait=wait)
                
        newItems = keyAndDataItems or self.createCellValue(
            self.newItemCoords() if code else self.cellCoords(i), key)
        if self.table[i] is None or self.table[i].val is self.__Deleted:
            if code:
                callEnviron |= set(newItems)
                self.highlightCode('self.__table[i] = (key, value)', callEnviron)
                self.moveItemsTo(
                    newItems, (self.cellCoords(i), self.cellCenter(i)),
                    sleepTime=wait / 10)
            else:
                self.canvas.coords(newItems[0], self.cellCoords(i))
                self.canvas.coords(newItems[1], self.cellCenter(i))
            if self.table[i]:
                self.dispose(callEnviron, *self.table[i].items)
            self.table[i] = drawnValue(key, *newItems)
            callEnviron -= set(newItems)

            if code:
                self.highlightCode('self.__nItems += 1', callEnviron, wait=wait)
            self.nItems += 1
            self.updateNItems()

            if code:
                self.highlightCode('self.loadFactor() > self.__maxLoadFactor',
                                   callEnviron, wait=wait)
                if self.loadFactor() > self.maxLoadFactor:
                    self.highlightCode('self.__growTable()', callEnviron)
                    colors = self.canvas.fadeItems(iArrow)

            if self.loadFactor() > self.maxLoadFactor:
                self.__growTable(code=self._growTableCode if code else '')
                if code:
                    self.canvas.restoreItems(iArrow, colors)

            if code:
                self.highlightCode('return True', callEnviron)
            self.cleanUp(callEnviron)
            return True
                    
        if code:
            self.highlightCode('self.__table[i][0] == key', callEnviron, 
                               wait=wait)
        if self.table[i].val == key:
            if code:
                self.highlightCode(('self.__table[i] = (key, value)', 2),
                                   callEnviron)
                self.moveItemsTo(
                    newItems, (self.cellCoords(i), self.cellCenter(i)),
                    sleepTime=wait / 10)
            self.dispose(callEnviron, *self.table[i].items)
            self.table[i] = drawnValue(key, *newItems)
            callEnviron -= set(newItems)
            
            if code:
                self.highlightCode('return False', callEnviron)
        self.cleanUp(callEnviron)
        return False

    _growTableCode = '''
def __growTable(self):
   oldTable = self.__table
   size = len(oldTable) * 2 + 1
   while not is_prime(size):
      size += 2
   self.__table = [None] * size
   self.__nItems = 0
   for i in range(len(oldTable)):
      if (oldTable[i] and
          oldTable[i] is not HashTable.__Deleted):
         self.insert(*oldTable[i])
 '''
    
    def __growTable(self, code=_growTableCode):
        wait = 0.1 if code else 0
        callEnviron = self.createCallEnvironment(code=code)
        
        oldTable = self.table
        oldTableColor = 'blue2'
        tagsToMove = ('arrayBox', 'cellShape', 'cellVal', 'sizeLabel')
        if code:
            self.highlightCode('oldTable = self.__table', callEnviron)
            oldTableCells = self.arrayCells
            cell0 = self.canvas.coords(oldTableCells[0])
            arrow0 = self.cellArrowCoords(0)
            delta = (cell0[2] - arrow0[0] - 16, 0)
            for col in range(math.ceil(len(oldTable) / self.cellsPerColumn)):
                callEnviron.add(self.canvas.create_text(
                    *(V(V(BBoxCenter(self.canvas.coords(
                        oldTableCells[col * self.cellsPerColumn]))) +
                        V(delta)) - V(0, self.cellHeight)), text='oldTable',
                    font=self.cellIndexFont, fill=oldTableColor))
            self.moveItemsBy(tagsToMove, delta, sleepTime=wait / 10)
            self.canvas.itemconfigure('arrayBox', outline=oldTableColor)

        size = min(len(oldTable) * 2 + 1, self.MAX_CELLS)
        if code:
            self.highlightCode('size = len(oldTable) * 2 + 1', callEnviron,
                               wait=wait)
            sizeText = self.canvas.create_text(
                *(V(self.canvas.coords(self.nItemsText)) - 
                  V(0, self.VARIABLE_FONT[1])), anchor=SW,
                text='size = {}'.format(size), font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
            callEnviron.add(sizeText)
            if len(oldTable) * 2 + 1 > size:
                self.setMessage('Reached maximum number of cells {}'.format(
                    self.MAX_CELLS))
                self.wait(5 * wait)
                
            self.highlightCode('not is_prime(size)', callEnviron, wait=wait)

        while not is_prime(size) and size < self.MAX_CELLS:
            size += 2
            if code:
                self.highlightCode('size += 2', callEnviron, wait=wait)
                self.canvas.itemconfigure(sizeText, text='size = {}'.format(size))
                self.highlightCode('not is_prime(size)', callEnviron, wait=wait)

        if size == self.MAX_CELLS and len(oldTable) == self.MAX_CELLS:
            if code:
                self.moveItemsBy(tagsToMove, V(delta) * -1, sleepTime=0)
                self.canvas.itemconfigure('arrayBox', outline='black')
            self.cleanUp(callEnviron)
            return
            
        if code:
            self.highlightCode('self.__table = [None] * size', callEnviron,
                               wait=wait)
        callEnviron |= set(
            self.arrayCells + list(flat(*(
                self.canvas.find_withtag(tag) 
                for tag in ('sizeLabel', 'cellShape', 'cellVal')))))
        self.table = [None] * size
        self.arrayCells = [
            self.createArrayCell(j) for j in range(len(self.table))]
        self.arrayLabels += [
            self.createArrayIndexLabel(j) for j in range(len(oldTable), size)]
        self.createArraySizeLabel()
        self.nItems = 0
        if code:
            self.highlightCode('self.__nItems = 0', callEnviron, wait=wait)
        self.updateNItems()

        if code:
            self.highlightCode('i in range(len(oldTable))', callEnviron)
            iArrow = None
        for i in range(len(oldTable)):
            if code:
                if iArrow is None:
                    iArrow = self.createArrayIndex(
                        self.canvas.coords(oldTableCells[i]), 'i')
                    callEnviron |= set(iArrow)
                else:
                    self.moveItemsTo(
                        iArrow, self.arrayIndexCoords(
                            self.canvas.coords(oldTableCells[i])),
                        sleepTime=wait / 10)
                self.highlightCode('oldTable[i]', callEnviron, wait=wait)
                if oldTable[i]:
                    self.highlightCode('oldTable[i] is not HashTable.__Deleted',
                                       callEnviron, wait=wait)
            if oldTable[i]:
                if oldTable[i].val is self.__Deleted:
                    self.dispose(callEnviron, *oldTable[i].items)
                else:
                    keyCopy = None
                    if code:
                        self.highlightCode('self.insert(*oldTable[i])',
                                           callEnviron)
                        if self.showHashing.get():
                            keyCopy = self.canvas.copyItem(oldTable[i].items[1])
                            callEnviron.add(keyCopy)
                        colors = self.canvas.fadeItems(iArrow)
                    self.insert(
                        oldTable[i].val, keyAndDataItems=oldTable[i].items,
                        inputText=keyCopy, code=self.insertCode if code else '')
                    callEnviron -= set(oldTable[i].items)
                    if code:
                        self.canvas.restoreItems(iArrow, colors)
                    
            if code:
                self.highlightCode('i in range(len(oldTable))', callEnviron)
                    
        self.cleanUp(callEnviron)

    def randomFill(
            self, nItems, animate=None, alphabet=
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_+&:'):
        if animate is None: animate = self.showHashing.get()
        callEnviron = self.createCallEnvironment()
        count = 0
        for j in range(nItems):
            key = ''.join(random.choices(alphabet, k=self.maxArgWidth))
            if self.insert(key, code=self.insertCode if animate else ''):
                count += 1
        self.cleanUp(callEnviron)
        return count
        
    searchCode = '''
def search(self, key={key}):
   i = self.__find(key)
   return (None if (i is None) or
           self.__table[i] is None or
           self.__table[i][0] != key
           else self.__table[i][1])
'''
    
    def search(self, key, inputText=None, code=searchCode, start=True):
        wait = 0.1 if code else 0
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()) if code else '',
            startAnimations=code and start)

        cellSize = BBoxSize(self.cellCoords(0))
        visible = self.visibleCanvas()
        x0, y0, x1, y1 = self.outputBoxCoords()
        pad = 5
        outputBox = OutputBox(
            self, bbox=(x0, visible[3] - cellSize[1] - pad * 3,
                        x0 + cellSize[0] + pad * 2, visible[3] - pad),
            outputFont=self.outputFont)
        callEnviron |= set(outputBox.items())
        
        if code:
            self.highlightCode('i = self.__find(key)', callEnviron)
        i = self._find(
            key, code=self._findCode if code else '', inputText=inputText)
        if i is not None and code:
            iArrow = self.createArrayIndex(i, 'i')
            callEnviron |= set(iArrow)

        found = (i is not None and self.table[i] is not None and
                 self.table[i].val == key)
        if code:
            self.highlightCode('(i is None)', callEnviron, wait=wait)
            if i is not None:
                self.highlightCode('self.__table[i] is None', callEnviron,
                                   wait=wait)
                if self.table[i] is not None:
                    self.highlightCode('self.__table[i][0] != key', callEnviron,
                                       wait=wait)
                    
            self.highlightCode(('return', 'None') if not found else 
                               ('return', 'self.__table[i][1]'), 
                               callEnviron)

            if found:
                items = [self.canvas.copyItem(item)
                         for item in self.table[i].items]
                callEnviron |= set(items)
                outputBox.setToText(items, sleepTime=wait / 10, color=True)
                callEnviron -= set(items)
            
        self.cleanUp(callEnviron)
        return self.table[i] if found else None

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
    
    def _find(self, key, deletedOK=False, code=_findCode, inputText=None):
        wait = 0.1 if code else 0
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()) if code else '',
            startAnimations=True if code else False)

        hashAddress = self.hash(key)
        if code:
            self.highlightCode('self.hash(key)', callEnviron)
        self.hashAddressCharacters = self.animateStringHashing(
            key, hashAddress, textItem=inputText, sleepTime=wait / 10,
            callEnviron=callEnviron) if self.showHashing.get() else [
                self.canvas.create_text(
                    *self.hashOutputCoords(), anchor=W,
                    text=' ' + str(hashAddress), font=self.VARIABLE_FONT,
                    fill=self.VARIABLE_COLOR)]
        callEnviron |= set(self.hashAddressCharacters)

        lastI, currentI = None, None
        if code:
            self.highlightCode(
                'i in self.__probe(self.hash(key), key, self.cells())',
                callEnviron)

        for i in self.probe(hashAddress, key, len(self.table)):
            if code:
                if lastI is None:
                    lastI = self.hashAddressCoords()
                else:
                    lastI = currentI[2:] + currentI[:2]
                currentI = self.cellArrowCoords(i)
                steps = int(max(abs(c) for c in V(lastI[:2]) - V(currentI[2:])))
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
                    if self.table[i].val is self.__Deleted:
                        self.highlightCode(
                            ('deletedOK', 2), callEnviron, wait=wait)
                    if self.table[i].val is not self.__Deleted or not deletedOK:
                        self.highlightCode(
                            'self.__table[i][0] == key', callEnviron, wait=wait)
            if (self.table[i] is None or
                (self.table[i].val is self.__Deleted and deletedOK) or
                self.table[i].val == key):
                if code:
                    self.highlightCode('return i', callEnviron, wait=wait)
                self.cleanUp(callEnviron)
                return i

            if code:
                self.highlightCode(
                    'i in self.__probe(self.hash(key), key, self.cells())',
                    callEnviron)
            
        if code:
            self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        return None
    
    deleteCode = '''
def delete(self, key={key}, ignoreMissing={ignoreMissing}):
   i = self.__find(key)
   if (i is None or
       self.__table[i] is None or
       self.__table[i][0] != key):
      if ignoreMissing:
         return
      raise Exception(
         'Cannot delete key {brackets} not found in hash table'.format(key))
   self.__table[i] = HashTable.__Deleted
   self.__nItems -= 1
'''

    hashDeleteException = re.compile(r'raise Exception.*\n.*format\(key\)\)')
    
    def delete(self, key, ignoreMissing=False, code=deleteCode, start=True):
        wait = 0.1
        brackets = '{}'
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()) if code else '',
            startAnimations=code and start)
        
        self.highlightCode('i = self.__find(key)', callEnviron)
        i = self._find(key)
        if i is not None:
            iArrow = self.createArrayIndex(i, 'i')
            callEnviron |= set(iArrow)

        self.highlightCode('i is None', callEnviron, wait=wait)
        if i is not None:
            self.highlightCode('self.__table[i] is None', callEnviron,
                               wait=wait)
            if self.table[i] is not None:
                self.highlightCode('self.__table[i][0] != key', callEnviron,
                                   wait=wait)
        if i is None or self.table[i] is None or self.table[i].val != key:
            self.highlightCode(('ignoreMissing', 2), callEnviron, wait=wait)
            if ignoreMissing:
                self.highlightCode('return', callEnviron)
                self.cleanUp(callEnviron)
                return False
            
            self.highlightCode(
                self.hashDeleteException, callEnviron, wait=wait,
                color=self.EXCEPTION_HIGHLIGHT)
            self.cleanUp(callEnviron)
            return
        
        self.highlightCode('self.__table[i] = HashTable.__Deleted',
                           callEnviron, wait=wait)
        self.markCellDeleted(self.table[i])
        
        self.highlightCode('self.__nItems -= 1', callEnviron, wait=wait)
        self.nItems -= 1
        self.updateNItems()

        self.highlightCode((), callEnviron)
        self.cleanUp(callEnviron)
        return True

    def markCellDeleted(self, dValue):
        self.canvas.itemconfigure(
            dValue.items[0], fill=self.deletedFillColor,
            stipple=self.deletedStipple)
        self.canvas.itemconfigure(
            dValue.items[1], text='DELETED\t', fill=self.CELL_INDEX_COLOR,
            font=self.VALUE_FONT + self.deletedFontModifiers)
        dValue.val = self.__Deleted

    traverseExampleCode = '''
first = True
for key, data in hashTable.traverse():
   print(key if first else ', ' + key, end='')
   first = False
'''
    def traverseExample(
            self, code=traverseExampleCode, start=True, indexLabel='key'):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)
        
        outputBox = OutputBox(
            self, bbox=self.outputBoxCoords(), 
            separators=r'[\s,.;]+', outputFont=self.outputFont)
        callEnviron |= set(outputBox.items())
        
        self.highlightCode('first = True', callEnviron, wait=wait)
        first = True
        firstLabel = self.canvas.create_text(
            outputBox.bbox[0] - textWidth(self.VARIABLE_FONT, 'first = False '),
            int(outputBox.bbox[1] + outputBox.bbox[3]) // 2, anchor=W,
            text='first = True', font=self.VARIABLE_FONT,
            fill=self.VARIABLE_COLOR)
        callEnviron.add(firstLabel)
        
        self.highlightCode(
            'key, data in hashTable.traverse()', callEnviron, wait=wait)
        arrayIndex = None
        localVars = ()
        colors = self.canvas.fadeItems(localVars)
        for i, item in self.traverse():
            self.canvas.restoreItems(localVars, colors)
            if arrayIndex is None:
                arrayIndex = self.createArrayIndex(i, indexLabel)
                callEnviron |= set(arrayIndex)
                localVars += arrayIndex
            else:
                self.moveItemsTo(
                    arrayIndex, self.arrayIndexCoords(i), sleepTime=wait / 10)

            self.highlightCode(('first', 2), callEnviron, wait=wait)
            self.highlightCode(
                ('print(',
                 ('key', 2) if first else "', ' + key",
                 ", end='')"), callEnviron, wait=wait)

            copy = self.canvas.copyItem(item.items[1])
            callEnviron.add(copy)
            outputBox.appendText(copy, separator=', ', sleepTime=wait / 10)
            callEnviron.discard(copy)

            self.highlightCode('first = False', callEnviron, wait=wait)
            first = False
            self.canvas_itemConfig(firstLabel, text='first = False')
            
            self.highlightCode(
                'key, data in hashTable.traverse()', callEnviron, wait=wait)
            colors = self.canvas.fadeItems(localVars)
        
        self.highlightCode((), callEnviron)
        self.cleanUp(callEnviron)

    traverseCode = '''
def traverse(self):
   for i in range(len(self.__table)):
      if (self.__table[i] and
          self.__table[i] is not HashTable.__Deleted):
         yield self.__table[i]
'''

    def traverse(self, code=traverseCode):
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code, sleepTime=wait / 10)

        self.highlightCode('i in range(len(self.__table)', callEnviron,
                           wait=wait)
        iArrayIndex = None
        for i in range(len(self.table)):
            if iArrayIndex is None:
                iArrayIndex = self.createArrayIndex(i, 'i')
                callEnviron |= set(iArrayIndex)
            else:
                self.moveItemsTo(iArrayIndex, self.arrayIndexCoords(i),
                                 sleepTime=wait / 10)

            self.highlightCode('self.__table[i]', callEnviron, wait=wait)
            if self.table[i]:
                self.highlightCode('self.__table[i] is not HashTable.__Deleted',
                                   callEnviron, wait=wait)
            if self.table[i] and self.table[i].val is not self.__Deleted:
                self.highlightCode('yield self.__table[i]', callEnviron)
                itemCoords = self.yieldCallEnvironment(
                    callEnviron, sleepTime=wait / 10)
                yield i, self.table[i]
                self.resumeCallEnvironment(
                    callEnviron, itemCoords, sleepTime=wait / 10)
            self.highlightCode('i in range(len(self.__table)', callEnviron,
                               wait=wait)
        
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)
        
    def display(self):
        '''Erase canvas and redisplay contents.  Call setupDisplay() before
        this to set the display parameters.'''
        canvasDimensions = widgetDimensions(self.canvas)
        self.canvas.delete("all")
        self.createHasher(
            y0=canvasDimensions[1] - self.hasherHeight,
            y1=canvasDimensions[1] - 1)
        self.updateNItems()
        self.updateMaxLoadFactor()
        self.arrayCells = [
            self.createArrayCell(j) for j in range(len(self.table))]
        self.arrayLabels = [
            self.createArrayIndexLabel(j) for j in range(len(self.table))]
        self.createArraySizeLabel()
        for j, item in enumerate(self.table):
            if item:
                self.table[j] = drawnValue(
                    item.val,
                    *self.createCellValue(
                        j, 'DELETED\t' if item.val is self.__Deleted else
                        item.val,
                        color=self.canvas.itemconfigure(
                            item.items[0], 'fill')[-1] if item.items
                        and self.canvas.type(item.items[0]) == 'rectangle'
                        else None))
                if item.val is self.__Deleted:
                    self.markCellDeleted(self.table[j])
                    
        self.window.update()
            
    def animateStringHashing(
            self, text, hashed, textItem=None, sleepTime=0.01,
            callEnviron=None, dx=2, font=VisualizationApp.VARIABLE_FONT, 
            color=VisualizationApp.VARIABLE_COLOR):
        """Animate text flowing into left of hasher and producing
        hashed output string while hasher churns.  Move characters by dx
        on each animation step. Returns list of canvas items for output
        characters. If textItem is provided, it is a text item that is
        moved into the input of the hasher."""
        
        if not self.hasher:
            return
        h = self.hasher

        if textItem and self.canvas.type(textItem) == 'text':
            self.canvas.changeAnchor(E, textItem)
            bbox = self.canvas.bbox(textItem)
            self.moveItemsTo(
                textItem, self.hashInputCoords(nInputs=1),
                sleepTime=sleepTime, endFont=self.VARIABLE_FONT,
                startFont=self.canvas.getItemFont(textItem))
            self.canvas.itemconfigure(textItem, fill=color)
            
        # Create individual character text items to feed into hasher
        text, hashed = str(text), str(hashed)
        inputCoords = self.hashInputCoords(nInputs=1)
        outputCoords = self.hashOutputCoords()
        charWidth = textWidth(font, 'W')
        characters = set([
            self.canvas.create_text(
                inputCoords[0] - ((len(text) - i) * charWidth),
                inputCoords[1], anchor=E, text=c, font=font, fill=color,
                state=DISABLED)
            for i, c in enumerate(text)])
        if textItem:
            self.dispose(callEnviron, textItem)
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
        bbox = BBoxUnion(*(self.canvas.bbox(c) 
                           for c in self.hashAddressCharacters))
        top = ((bbox[0] + bbox[2]) // 2, bbox[1])
        return top + (V(top) + V(0, -50))
                         
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
        result = self.insert(key, start=self.startMode())
        self.setMessage("{} in hash table".format(
            'Unable to insert {}'.format(repr(key)) if result is None else
            '{} {}'.format(repr(key), 'inserted' if result else 'updated')))
        self.clearArgument()

    def clickDelete(self):
        entered_text = self.getArgument(0)
        if not entered_text or entered_text.isspace():
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
            self.setMessage("No printable text entered")
            return
        key = int(entered_text) if entered_text.isdigit() else entered_text
        result = self.delete(key, start=self.startMode())
        self.setMessage("{} {} hash table".format(
            repr(key),
            "unexpectedly missing from" if result is None else
            "deleted from" if result else "not found in"))
        self.clearArgument()

    def clickRandomFill(self):
        nItems = self.getArgument(0)
        if not (nItems and nItems.isdigit()):
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
            self.setMessage("Number of items not entered")
            return
        elif int(nItems) > self.maxFillAmount:
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
            self.setMessage('Number of items cannot exceed {}'.format(
                self.maxFillAmount))
            return
        result = self.randomFill(int(nItems))
        self.setMessage('Inserted {} random item{}'.format(
            result, '' if result == 1 else 's'))
        self.clearArgument()
        
    def clickNew(self, defaultMaxLoadFactor=0.5,
                 loadFactorRange=(MIN_LOAD_FACTOR, MAX_LOAD_FACTOR),
                 loadFactorPattern=fraction):
        nCells, loadFactor = self.getArguments()
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
        if loadFactorPattern.match(loadFactor):
            loadFactor = float(loadFactor)
        if not isinstance(loadFactor, float) or not (
                loadFactorRange[0] <= loadFactor and
                loadFactor < loadFactorRange[1]):
            msg.append('Max load factor must be a fraction\nbetween {} and {}'
                       .format(*loadFactorRange))
            self.setArgumentHighlight(1, self.ERROR_HIGHLIGHT)
            loadFactor = defaultMaxLoadFactor
            msg.append('Using max load factor = {}'.format(loadFactor))
        self.newHashTable(nCells, loadFactor)
        if msg:
            self.setMessage('\n'.join(msg))
        else:
            self.clearArguments()

    def clickTraverse(self):
        self.traverseExample(start=self.startMode())

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
            'number of cells & max load factor',
            argHelpText=['number of cells', 'max load factor'])
        randomFillButton = self.addOperation(
            "Random Fill", self.clickRandomFill, numArguments=1,
            validationCmd=vcmd, helpText='Fill with N random items',
            argHelpText=['number of items'])
        self.showHashing = IntVar()
        self.showHashing.set(1)
        showHashingButton = self.addOperation(
            "Animate Hashing", self.clickShowHashing, buttonType=Checkbutton,
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
        traverseButton = self.addOperation(
            "Traverse", self.clickTraverse, 
            helpText='Traverse items in hash table')
        self.addAnimationButtons()

    def enableButtons(self, enable=True):
        super().enableButtons(enable)
        for btn in self.probeChoiceButtons: # Probe function can only be
            widgetState(                    # selected while hash table has no
                btn,                        # items
                NORMAL if enable and self.nItems == 0 else DISABLED)

if __name__ == '__main__':
    probes = (linearProbe, quadraticProbe, doubleHashProbe)
    nonneg, negative, options, otherArgs = categorizeArguments(sys.argv[1:])
    if '-r' not in options:  # Use fixed seed for testing consistency unless
        random.seed(3.14159) # random option specified
    hashTable = HashTableOpenAddressing()
    hashTable.showHashing.set(not '-A' in options or '-a' in options)

    for probe in probes:
        if ('-' + probe.__name__[0]) in options:
            hashTable.probe = probe
            hashTable.probeChoice.set(hashTable.probe.__name__)
    for arg in negative:
        hashTable.randomFill(int(arg[1:]))
    for key in nonneg + otherArgs:
        if hashTable.showHashing.get():
            hashTable.setArgument(key)
            hashTable.insertButton.invoke()
        else:
            hashTable.insert(int(key) if key.isdigit() else key, code='')
        
    hashTable.runVisualization()
