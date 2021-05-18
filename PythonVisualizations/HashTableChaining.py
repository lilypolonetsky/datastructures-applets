from tkinter import *
import re, math
try:
    from drawnValue import *
    from HashTableOpenAddressing import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .HashTableOpenAddressing import *

# Regular expression for max load factor
maxLoadFactorPattern = re.compile(r'[01](\.\d*)?')

class HashTableChaining(HashTableOpenAddressing):
    MIN_LOAD_FACTOR = 0.5
    MAX_LOAD_FACTOR = 2.0
    CELL_INDEX_COLOR = 'gray60'
    
    def __init__(self, title="Hash Table - Open Chaining", **kwargs):
        self.initialRect = (
            0, 0, kwargs.get('canvasWidth', self.DEFAULT_CANVAS_WIDTH),
            kwargs.get('canvasHeight', self.DEFAULT_CANVAS_HEIGHT))
        super().__init__(title=title, canvasBounds=self.initialRect, **kwargs)

    def newHashTable(self, nCells=2, maxLoadFactor=1.0):
        self.table = [None] * max(1, nCells)
        self.nItems = 0
        self.maxLoadFactor = maxLoadFactor
        self.display()
        
    insertCode = '''
def insert(self, key={key}, value):
   i = self.hash(key)
   flag = self.insert(self.__table[i], key, value)
   if flag:
      self.__nItems += 1
      if self.loadFactor() > self.__maxLoadFactor:
         self.__growTable()
   return flag
'''
    
    def insert(self, key, nodeItems=None, inputText=None,
               code=insertCode, start=True):
        '''Insert a user provided key or the link node items from the old table
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

        hashAddress = self.hash(key)
        i = hashAddress % len(self.table)
        localVars = ()
        if code:
            self.highlightCode('i = self.hash(key)', callEnviron)
        self.hashAddressCharacters = self.animateStringHashing(
            key, hashAddress, textItem=inputText, sleepTime=wait / 10,
            callEnviron=callEnviron) if code and self.showHashing.get() else [
                self.canvas.create_text(
                    *self.hashOutputCoords(), anchor=W,
                    text=' ' + str(hashAddress), font=self.VARIABLE_FONT,
                    fill=self.VARIABLE_COLOR)]
        callEnviron |= set(self.hashAddressCharacters)
        localVars += tuple(self.hashAddressCharacters)

        if code:
            iArrow = self.createArrayIndex(i, 'i')
            callEnviron |= set(iArrow)
            localVars += iArrow
            self.highlightCode(
                'flag = self.insert(self.__table[i], key, value)', callEnviron)

        flag = self.insertIntoList(i, key, nodeItems, callEnviron, wait)
        
        if code:
            outputBoxCoords = self.outputBoxCoords()
            gap = 4
            flagText = self.canvas.create_text(
                *(V(self.canvas.coords(self.nItemsText)) - 
                  V(0, self.VARIABLE_FONT[1])), anchor=SW,
                text='flag = {}'.format(flag), font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
            callEnviron.add(flagText)
            localVars += (flagText,)
            self.highlightCode(('flag', 2), callEnviron, wait=wait)

        if flag:
            if code:
                self.highlightCode('self.__nItems += 1', callEnviron, wait=wait)
            self.nItems += 1
            self.updateNItems()

            if code:
                self.highlightCode('self.loadFactor() > self.__maxLoadFactor',
                                   callEnviron, wait=wait)
                if self.loadFactor() > self.maxLoadFactor:
                    self.highlightCode('self.__growTable()', callEnviron)
                    colors = self.fadeNonLocalItems(localVars)

            if self.loadFactor() > self.maxLoadFactor:
                self.__growTable(code=self._growTableCode if code else '')
                if code:
                    self.restoreLocalItems(localVars, colors)

        if code:
            self.highlightCode('return flag', callEnviron)
        self.cleanUp(callEnviron)
        return flag

    def insertIntoList(self, cell, key, nodeItems, callEnviron, wait):
        linkedList = self.table[cell].val if self.table[cell] else []
        listIndex = 0
        while listIndex < len(linkedList):
            if linkedList[listIndex].val == key:
                break
            listIndex += 1
        updateExisting = listIndex < len(linkedList)
        linkCoords = ([self.canvas.coords(item) 
                       for item in linkedList[listIndex].items]
                      if updateExisting else 
                      self.findSpaceForLink(cell, key=key))
        newItems = nodeItems or self.createLinkItems(
            self.newItemCoords()[:2] if wait else linkCoords, key)
        callEnviron |= set(newItems)
        if wait:
            linkIndex = self.createLinkIndex(cell)
            callEnviron |= set(linkIndex)
            for j in range(listIndex):
                self.moveItemsTo(linkIndex, self.linkIndexCoords(linkedList[j]),
                                 sleepTime=wait / 10)
                self.wait(wait / 2)
            self.moveItemsTo(linkIndex, self.linkIndexCoords(linkCoords),
                             sleepTime=wait / 10)
            if updateExisting:
                self.canvas.tag_lower(
                    newItems[0], linkedList[listIndex].items[1])
                self.moveItemsTo(newItems[0], linkCoords[0],
                                 sleepTime=wait / 10)
            else:
                self.moveItemsLinearly(
                    newItems, linkCoords, sleepTime=wait / 10)
        else:
            if not updateExisting:
                for item, coords in zip(newItems, linkCoords):
                    self.canvas.coords(item, coords)
                self.expandCanvasFor(*newItems)
                
        if updateExisting:
            self.copyItemAttributes(newItems[0], linkedList[listIndex].items[0],
                                    'fill')
            self.dispose(callEnviron, *newitems)
        else:
            linkedList.append(drawnValue(key, *newItems))
            if self.table[cell] is None:
                self.table[cell] = drawnValue(
                    linkedList, *self.createInitialLink(cell, linkedList[0]))
            else:
                self.table[cell].val = linkedList
                self.linkNodes(linkedList[-2], linkedList[-1])
            callEnviron -= set(newItems)
        if wait:
            self.dispose(callEnviron, *linkIndex)
        return not updateExisting

    def findSpaceForLink(self, cell, key=' '):
        cellCoords = self.cellCenter(cell)
        linkCoords = self.newLinkCoords(key=key)
        rowGap = self.linkHeight * 5 // 2
        widthNeeded = linkCoords[2][2] - linkCoords[2][0]
        pad = self.linkHeight
        bboxes = [self.canvas.bbox(n.items[2])
                  for d in self.table if d for n in d.val]
        y0 = self.array_y0 + self.cellHeight
        used = []
        for bbox in bboxes:
            level = (bbox[1] + 5 - y0) // rowGap
            while level >= len(used):
                used.append([])
            used[level].append((bbox[0], bbox[2]))
        level = 1 if self.table[cell] is None else (
            (self.canvas.bbox(self.table[cell].val[-1].items[2])[1] + 1 - y0) //
            rowGap) + 1
        bounds = ()
        x = cellCoords[0]
        while level < len(used) and used[level]:
            used[level].sort()
            blocks = used[level]
            j = 0
            while j < len(blocks) and blocks[j][0] < x:
                j += 1
            # blocks[j - 1][0] < x <= blocks[j][0]
            if j >= len(blocks) and blocks[j - 1][1] < x:
                bounds = (blocks[j - 1][1], math.inf)
                break
            if j > 0:
                if (x <= blocks[j - 1][1] or
                    blocks[j][0] - blocks[j - 1][1] < widthNeeded + 2 * pad):
                    level += 1
                else:
                    bounds = (blocks[j - 1][1], blocks[j][0])
                    break
            else:
                bounds = (-math.inf, blocks[j][0])
                break

        offset = self.linkHeight // 2
        y = y0 + level * rowGap
        x -= offset
        if bounds:
            x = max(bounds[0] + pad, min(bounds[1] - pad - widthNeeded, x))
        return self.linkCoords((x, y), key=key)
    
    _growTableCode = '''
def __growTable(self):
   oldTable = self.__table
   size = len(oldTable) * 2 + 1
   while not is_prime(size):
      size += 2
   self.__table = [None] * size
   self.__nItems = 0
   for i in range(len(oldTable)):
      if oldTable[i]:
         for item in oldTable[i].traverse():
             self.insert(*item)
 '''
    
    def __growTable(self, code=_growTableCode):
        wait = 0.1 if code else 0
        callEnviron = self.createCallEnvironment(code=code)
        
        localVars = set()
        oldTable = self.table
        oldTableColor = 'blue2'
        tagsToMove = ('arrayBox', 'cell', 'link', 'sizeLabel')
        if code:
            self.highlightCode('oldTable = self.__table', callEnviron)
            oldTableCells = self.arrayCells
            cell0 = self.canvas.coords(oldTableCells[0])
            delta = (self.cellWidth * 2 * (len(self.table) + 2),
                     2 * self.cellHeight)
            callEnviron.add(self.canvas.create_text(
                cell0[0] - self.cellWidth // 2 + delta[0],
                (cell0[1] + cell0[3]) // 2 + delta[1], anchor=E,
                text='oldTable', font=self.cellIndexFont, fill=oldTableColor))
            self.moveItemsBy(tagsToMove, delta, sleepTime=wait / 10)
            self.canvas_itemConfig('arrayBox', outline=oldTableColor)
            for tag in ('linkArrow', 'cellArrow'):
                self.canvas_itemConfig(tag, fill=oldTableColor)

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
            localVars.add(sizeText)
            if len(oldTable) * 2 + 1 > size:
                self.setMessage('Reached maximum number of cells {}'.format(
                    self.MAX_CELLS))
                self.wait(5 * wait)
                
            self.highlightCode('not is_prime(size)', callEnviron, wait=wait)

        while not is_prime(size) and size < self.MAX_CELLS:
            size += 2
            if code:
                self.highlightCode('size += 2', callEnviron, wait=wait)
                self.canvas_itemConfig(sizeText, text='size = {}'.format(size))
                self.highlightCode('not is_prime(size)', callEnviron, wait=wait)

        if size == self.MAX_CELLS and len(oldTable) == self.MAX_CELLS:
            if code:
                self.moveItemsBy(tagsToMove, V(delta) * -1, sleepTime=0)
                self.canvas_itemConfig('arrayBox', outline='black')
            self.cleanUp(callEnviron)
            return
            
        if code:
            self.highlightCode('self.__table = [None] * size', callEnviron,
                               wait=wait)
        callEnviron |= set(
            self.arrayCells + list(flat(*(
                self.canvas.find_withtag(tag) for tag in ('sizeLabel', 'link')))))
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
            iArrow, itemArrow = None, None
        for i in range(len(oldTable)):
            if code:
                if iArrow is None:
                    iArrow = self.createArrayIndex(
                        self.canvas.coords(oldTableCells[i]), 'i')
                    callEnviron |= set(iArrow)
                    localVars |= set(iArrow)
                else:
                    self.moveItemsTo(
                        iArrow, self.arrayIndexCoords(
                            self.canvas.coords(oldTableCells[i])),
                        sleepTime=wait / 10)
                self.highlightCode('oldTable[i]', callEnviron, wait=wait)

            if oldTable[i] and oldTable[i].val:
                keyCopy = None
                if code:
                    self.highlightCode('item in oldTable[i].traverse()',
                                       callEnviron, wait=wait)
                linkedList = oldTable[i].val
                self.dispose(callEnviron, *oldTable[i].items)
                for linkIndex in range(len(linkedList)):
                    if code:
                        if itemArrow is None:
                            itemArrow = self.createLinkIndex(
                                linkedList[linkIndex], 'item')
                            callEnviron |= set(itemArrow)
                            localVars |= set(itemArrow)
                        else:
                            self.moveItemsTo(itemArrow, self.linkIndexCoords(
                                linkedList[linkIndex]), sleepTime=wait / 10)
                            
                        self.highlightCode('self.insert(*item)',
                                           callEnviron)
                        if self.showHashing.get():
                            keyCopy = self.copyCanvasItem(
                                linkedList[linkIndex].items[1])
                            callEnviron.add(keyCopy)
                        colors = self.fadeNonLocalItems(localVars)
                    self.insert(
                        linkedList[linkIndex].val, 
                        nodeItems=linkedList[linkIndex].items,
                        inputText=keyCopy, code=self.insertCode if code else '')
                    callEnviron -= set(linkedList[linkIndex].items)
                    if code:
                        self.restoreLocalItems(localVars, colors)
                        self.highlightCode('item in oldTable[i].traverse()',
                                           callEnviron, wait=wait)
                if code:
                    self.dispose(callEnviron, *itemArrow)
                    localVars -= set(itemArrow)
                    itemArrow = None
            if code:
                self.highlightCode('i in range(len(oldTable))', callEnviron)
                    
        self.cleanUp(callEnviron)
        
    searchCode = '''
def search(self, key={key}):
   i = self.hash(key)
   return (None if self.__table[i] is None else
           self.__table[i].search(key))
'''
    
    def search(self, key, inputText=None, code=searchCode, start=True):
        wait = 0.1 if code else 0
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()) if code else '',
            startAnimations=code and start)

        pad = 5
        outBox = self.outputBoxCoords(nLines=2, pad=pad)
        outBox = (outBox[0], outBox[1], 
                  outBox[0] + self.linkWidth + 2 * pad, outBox[3])
        outBoxCenter = BBoxCenter(outBox)
        outputBox = self.createOutputBox(coords=outBox)
        callEnviron.add(outputBox)
        
        hashAddress = self.hash(key)
        i = hashAddress % len(self.table)
        if code:
            self.highlightCode('i = self.hash(key)', callEnviron)
        self.hashAddressCharacters = self.animateStringHashing(
            key, hashAddress, textItem=inputText, sleepTime=wait / 10,
            callEnviron=callEnviron) if code and self.showHashing.get() else [
                self.canvas.create_text(
                    *self.hashOutputCoords(), anchor=W,
                    text=' ' + str(hashAddress), font=self.VARIABLE_FONT,
                    fill=self.VARIABLE_COLOR)]
        callEnviron |= set(self.hashAddressCharacters)

        if code:
            iArrow = self.createArrayIndex(i, 'i')
            callEnviron |= set(iArrow)
            self.highlightCode('self.__table[i] is None', callEnviron)

        if self.table[i] is None or len(self.table[i].val) == 0:
            if code:
                self.highlightCode(('return', 'None'), callEnviron)
            self.cleanUp(callEnviron)
            return None
        
        if code:
            self.highlightCode('self.__table[i].search(key)', callEnviron)
            
        linkedList = self.table[i].val
        itemArrow = None
        linkIndex = 0
        while linkIndex < len(linkedList):
            if code:
                if itemArrow is None:
                    itemArrow = self.createLinkIndex(linkedList[linkIndex])
                    callEnviron |= set(itemArrow)
                else:
                    self.moveItemsTo(itemArrow, self.linkIndexCoords(
                        linkedList[linkIndex]), sleepTime=wait / 10)
            if linkedList[linkIndex].val == key:
                break
            linkIndex += 1

        found = linkIndex < len(linkedList)
        if found:
            items = [self.copyCanvasItem(item)
                     for item in linkedList[linkIndex].items[0:2]]
            callEnviron |= set(items)
            self.canvas.tag_lower(items[0])
            upperLeft = V(outBox) + V(pad, pad)
            self.moveItemsTo(
                items,
                    (upperLeft + (V(upperLeft) + V(cellSize)), outBoxCenter),
                    sleepTime=wait / 10, startFont=self.getItemFont(items[1]),
                    endFont=self.outputFont)
            self.copyItemAttributes(items[0], outputBox, 'fill')
            self.dispose(callEnviron, items[0])
            
        self.cleanUp(callEnviron)
        return self.table[i] if found else None
    
    deleteCode = '''
def delete(self, key={key}, ignoreMissing={ignoreMissing}):
   if (i is None or
       self.__table[i] is None or
       self.__table[i][0] != key):
      if ignoreMissing:
         return
      raise Exception(
         'Hash table does not contain key {brackets} so cannot delete'
         .format(key))
   self.__table[i] = HashTable.__Deleted
   self.__nItems -= 1
'''

    hashDeleteException = re.compile(r'raise Exception.*\n.*\n.*key\)\)')
    
    def delete(self, key, ignoreMissing=False, code=deleteCode, start=True):
        wait = 0.1
        brackets = '{}'
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()) if code else '',
            startAnimations=code and start)
        
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
        
        self.highlightCode('self.__nItems -= 1', callEnviron, wait=wait)
        self.nItems -= 1
        self.updateNItems()

        self.highlightCode((), callEnviron)
        self.cleanUp(callEnviron)
        return True

    traverseExampleCode = '''
for item in hashTable.traverse():
   print(item)
'''
    def traverseExample(self, code=traverseExampleCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)
        
        outputBox = self.createOutputBox(coords=self.outputBoxCoords())
        callEnviron.add(outputBox)
        
        self.highlightCode(
            'item in hashTable.traverse()', callEnviron, wait=wait)
        arrayIndex = None
        localVars = ()
        colors = self.fadeNonLocalItems(localVars)
        for i, item in self.traverse():
            self.restoreLocalItems(localVars, colors)
            if arrayIndex is None:
                arrayIndex = self.createArrayIndex(i, 'item')
                callEnviron |= set(arrayIndex)
                localVars += arrayIndex
            else:
                self.moveItemsTo(
                    arrayIndex, self.arrayIndexCoords(i), sleepTime=wait / 10)

            self.highlightCode('print(item)', callEnviron, wait=wait)
            self.appendTextToOutputBox(
                item.items[1], callEnviron, sleepTime=wait / 10)

            colors = self.fadeNonLocalItems(localVars)
            self.highlightCode(
                'item in hashTable.traverse()', callEnviron, wait=wait)
        
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
            if self.table[i] and self.table[i] is not self.__Deleted:
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
        
    def cellCoords(self, index):
        x0 = self.array_x0 + index * self.cellWidth
        y0 = self.array_y0
        return (x0, y0, 
                x0 + self.cellWidth - self.CELL_BORDER,
                y0 + self.cellHeight - self.CELL_BORDER)
    
    def arrayIndexCoords(self, indexOrCoords, level=1):
        'Coordinates of an index arrow and anchor of its text label'
        cell_coords = (
            self.cellCoords(indexOrCoords) if isinstance(indexOrCoords, int)
            else indexOrCoords)
        tip = ((cell_coords[0] + cell_coords[2]) // 2, 
               cell_coords[1] + self.cellIndexFont[1] * 3 // 2)
        base = V(tip) + V(0, level * self.VARIABLE_FONT[1])
        return (base + tip, base)

    def linkIndexCoords(self, linkOrCoords, level=1, orientation=-150):
        corner = (tuple(self.canvas.coords(linkOrCoords.items[2])[:2])
                  if isinstance(linkOrCoords, drawnValue) else
                  self.arrayCellCoords(linkOrCoords)[:2]
                  if isinstance(linkOrCoords, int) else
                  linkOrCoords[2][:2] if len(linkOrCoords) == 5 else
                  linkOrCoords)
        base = V(V(abs(self.VARIABLE_FONT[1]) * level, 0).rotate(
            orientation)) + V(corner)
        return base + corner, base
    
    def linkCoords(self, corner, nextLink=None, key=''):
        '''Coordinates for all the canvas items in a linked list Link:
        colored rectangle, text key, box outline, dot, arrow to next link
        When the next link is None, the arrow will have zero length.
        The nextLink can be a corner coordinate or a drawnValue for a link.
        '''
        vCorner = V(corner)
        rectAt = (vCorner + V(self.linkHeight, 0))
        width = (self.textWidth(self.VALUE_FONT, str(key) + '  ') 
                 if key else self.linkWidth)
        rectAt += V(rectAt) + V(width, self.linkHeight)
        keyAt = BBoxCenter(rectAt)
        boxAt =  (vCorner - V(1, 1)) + rectAt[2:]
        dot = (vCorner + V(self.linkHeight, self.linkHeight) // 2) * 2
        arrow = dot if nextLink is None else (
            dot[:2] + 
            (dot[0], nextLink[1] if isnstance(nextLink, (tuple, list)) else
             self.canvas.coords(nextLink.items[0])[1]))
        if nextLink is not None:
            dotRadius = (self.linkDotRadius, ) * 2
            dot = (V(dot[:2]) - V(dotRadius)) + (V(dot[:2]) + V(dotRadius))
        return rectAt, keyAt, boxAt, dot, arrow

    def newLinkCoords(self, key=''):
        delta = self.newValueCoords()
        return tuple(V(coords) + V(delta * (len(coords) // len(delta)))
                     for coords in self.linkCoords((0, 0), key=key))

    def createLinkItems(self, cornerOrCoords, key, nextLink=None, color=None):
        '''Create all the canvas items in a linked list Link containing a key:
        colored rectangle, text key, box outline, dot, arrow to next link
        The upper left corner can be provided or a tuple of coordinates for
        each of the 5 items.
        When the next link is None, the arrow will have zero length.
        The nextLink can be a corner coordinate or a drawnValue for a link.
        '''
        coords = (self.linkCoords(cornerOrCoords, nextLink=nextLink, key=key)
                  if len(cornerOrCoords) == 2 else cornerOrCoords)
        if color is None:
            color = drawnValue.palette[self.nextColor]
            self.nextColor = (self.nextColor + 1) % len(drawnValue.palette)
        box = self.canvas.create_rectangle(
            *coords[2], fill=None, outline=self.linkBoxColor, width=1,
            tags=('link', 'linkBox'))
        rect = self.canvas.create_rectangle(
            *coords[0], fill=color, outline='', width=0,
            tags=('link', 'linkShape'))
        textKey = self.canvas.create_text(
            *coords[1], text=str(key), fill=self.VALUE_COLOR,
            font=self.VALUE_FONT, tags=('link', 'linkVal'))
        dot = self.canvas.create_oval(
            *coords[3], fill=self.linkDotColor, outline='', width=0,
            tags=('link', 'linkDot'))
        arrow = self.canvas.create_line(
            *coords[4], fill=self.linkArrowColor, width=self.linkArrowWidth,
            arrow=LAST, tags=('link', 'linkArrow'))
        return rect, textKey, box, dot, arrow

    def createInitialLink(self, cell, firstNodeOrCoords=None):
        center = V(self.cellCenter(cell))
        radius = V((self.cellDotRadius if firstNodeOrCoords else 0, ) * 2)
        dot = self.canvas.create_oval(
            *((center - radius) + (center + radius)), fill=self.cellDotColor,
            outline='', width=0, tags=('cell', 'cellDot'))
        if firstNodeOrCoords is None:
            tip = center
        elif isinstance(firstNodeOrCoords, drawnValue):
            boxCoords = self.canvas.coords(firstNodeOrCoords.items[2])
            tip = (max(boxCoords[0], min(boxCoords[2], center[0])), boxCoords[1])
        else:
            tip = firstNodeOrCoords
        arrow = self.canvas.create_line(
            *center, *tip, fill=self.linkArrowColor, width=self.linkArrowWidth,
            arrow=LAST, tags=('cell', 'cellArrow'))
        return dot, arrow
    
    def createLinkIndex(
            self, link, label='', level=1, orientation=-150, color='black',
            width=1, anchor=SW, font=None):
        if font is None: font = self.VARIABLE_FONT
        coords = self.linkIndexCoords(
            link, level=level, orientation=orientation)
        arrow = self.canvas.create_line(
            *coords[0], arrow=LAST, width=width, fill=color)
        label = self.canvas.create_text(
            *coords[1], text=label or '', fill=color, anchor=anchor, font=font)
        return arrow, label
        
    def createArrayIndexLabel(self, index, tags='cellIndex'):
        coords = self.arrayCellCoords(index)
        return self.canvas.create_text(
            (coords[0] + coords[2]) // 2, coords[1] - 1, anchor=S,
            text=str(index), tags=tags,
            font=self.cellIndexFont, fill=self.CELL_INDEX_COLOR)

    def createArraySizeLabel(self, tags='sizeLabel'):
        coords = self.cellCenter(len(self.table))
        return self.canvas.create_text(
            *coords, text='{} cells'.format(len(self.table)), anchor=W,
            tags=tags, font=self.VALUE_FONT, fill=self.VARIABLE_COLOR)
        
    def setupDisplay(self, hasherHeight=70):
        'Define dimensions and coordinates for display items'
        self.hasherHeight = hasherHeight
        # self.cellWidth = self.targetCanvasWidth // (self.MAX_CELLS + 10)
        self.cellWidth = 14
        self.cellHeight = self.cellWidth
        self.array_x0 = self.cellWidth * 4
        self.array_y0 = 45 # self.cellHeight * 4
        self.cellDotRadius = (self.cellWidth - 4) // 2
        self.cellDotColor = 'red'

        self.outputFont = (self.VALUE_FONT[0], - 12)
        self.VALUE_FONT = (self.VALUE_FONT[0], - 10)
        self.cellIndexFont = (self.VARIABLE_FONT[0], - 10)

        self.linkHeight = 12
        self.linkWidth = self.textWidth(self.VALUE_FONT,
                                        'W' * (self.maxArgWidth + 2))
        self.linkDotRadius = 4
        self.linkDotColor = 'red'
        self.linkArrowColor = 'black'
        self.linkArrowWidth = 1
        self.linkBoxColor = 'black'
        
    def display(self):
        '''Erase canvas and redisplay contents.  Call setupDisplay() before
        this to set the display parameters.'''
        saveCoords = dict(
            (item, self.canvas.coords(item)) for item in
            flat(*(d.items + flat(*(n.items for n in d.val))
                   for d in self.table if d)))
        saveColors = dict(
            (item, self.canvas_itemConfig(item, 'fill')) for item in
            flat(*(n.items for d in self.table if d for n in d.val)))
        self.canvas.delete("all")
        self.setCanvasBounds(self.initialRect, expandOnly=False)
        self.createHasher(
            y0=self.targetCanvasHeight - self.hasherHeight,
            y1=self.targetCanvasHeight - 1)
        self.updateNItems()
        self.updateMaxLoadFactor()
        self.arrayCells = [
            self.createArrayCell(j) for j in range(len(self.table))]
        self.arrayLabels = [
            self.createArrayIndexLabel(j) for j in range(len(self.table))]
        self.createArraySizeLabel()
        for j, item in enumerate(self.table):
            if item:
                for l, link in enumerate(item.val):
                    item.val[l] = drawnValue(
                        link.val, *self.createLinkItems(
                            [saveCoords[i] for i in link.items], link.val,
                            nextLink=saveCoords[item.val[l + 1].items[2]]
                            if l < len(item.val) - 1 else None,
                            color=saveColors[link.items[0]]))
                    self.expandCanvasFor(*item.val[l].items)
                self.table[j] = drawnValue(
                    item.val,
                    *self.createInitialLink(
                        j, item.val[0] if len(item.val) > 0 else None))
                self.expandCanvasFor(*self.table[j].items)
                    
        self.window.update()

    def linkNodes(self, fromNode, toNode=None):
        dotItem, arrowItem = fromNode.items[-2:]
        dotCenter = BBoxCenter(self.canvas.coords(dotItem))
        radius = V((self.linkDotRadius if toNode else 0,) * 2)
        self.canvas.coords(dotItem,
                           (V(dotCenter) - radius) + (V(dotCenter) + radius))
        toBox = self.canvas.coords((toNode or fromNode).items[2]) 
        self.canvas.coords(
            arrowItem,
            dotCenter + (dotCenter if toNode is None else
                         (max(toBox[0], min(toBox[2], dotCenter[0])), toBox[1])))
        self.canvas_itemConfig(arrowItem, fill=self.linkArrowColor)
        self.expandCanvasFor(dotItem, arrowItem)
        
    def updateNItems(self, nItems=None, gap=4):
        if nItems is None:
            nItems = self.nItems
        outputBoxCoords = self.outputBoxCoords()
        if self.nItemsText is None or self.canvas.type(self.nItemsText) != 'text':
            self.nItemsText = self.canvas.create_text(
                *(V(outputBoxCoords[:2]) + V(gap, - gap)), anchor=SW,
                text='', font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        self.canvas_itemConfig(self.nItemsText,
                               text='nItems = {}'.format(nItems))
        
    def updateMaxLoadFactor(self, maxLoadFactor=None, gap=4):
        if maxLoadFactor is None:
            maxLoadFactor = self.maxLoadFactor
        outputBoxCoords = self.outputBoxCoords()
        if (self.maxLoadFactorText is None or
            self.canvas.type(self.maxLoadFactorText) != 'text'):
            self.maxLoadFactorText = self.canvas.create_text(
                outputBoxCoords[2] - gap, outputBoxCoords[1] - gap, anchor=SE,
                text='', font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
        self.canvas_itemConfig(
            self.maxLoadFactorText, text='maxLoadFactor = {}%'.format(
                int(100 * maxLoadFactor)))
            
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
            self.changeAnchor(E, textItem)
            bbox = self.canvas.bbox(textItem)
            self.moveItemsTo(
                textItem, self.hashInputCoords(nInputs=1),
                sleepTime=sleepTime, startFont=self.getItemFont(textItem),
                endFont=self.VARIABLE_FONT)
            self.canvas_itemConfig(textItem, fill=color)
            
        # Create individual character text items to feed into hasher
        text, hashed = str(text), str(hashed)
        inputCoords = self.hashInputCoords(nInputs=1)
        outputCoords = self.hashOutputCoords()
        charWidth = self.textWidth(font, 'W')
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
                self.canvas.lower(output[-1], h['Blocks'][0])
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
        result = self.randomFill(int(nItems))
        self.setMessage('Inserted {} random item{}'.format(
            result, '' if result == 1 else 's'))
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
            maxLoadFactor = 1.0
            msg.append('Using max load factor = {}'.format(maxLoadFactor))
        if msg:
            self.setMessage('\n'.join(msg))
        self.newHashTable(nCells, maxLoadFactor)

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
            "Random fill", self.clickRandomFill, numArguments=1,
            validationCmd=vcmd, helpText='Fill with N random items',
            argHelpText=['number of items'])
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
        traverseButton = self.addOperation(
            "Traverse", self.clickTraverse, 
            helpText='Traverse items in hash table')
        self.addAnimationButtons()

    def enableButtons(self, enable=True):
        super().enableButtons(enable)
        for btn in self.probeChoiceButtons: # Probe function can only be
            self.widgetState(               # selected while hash table has no
                btn,                        # items
                NORMAL if enable and self.nItems == 0 else DISABLED)

if __name__ == '__main__':
    hashTable = HashTableChaining()
    animate = '-a' in sys.argv[1:]
    showHashing = hashTable.showHashing.get()
    hashTable.showHashing.set(1 if animate else 0)
    for arg in sys.argv[1:]:
        if not(arg[0] == '-' and len(arg) == 2 and arg[1:].isalpha()):
            if animate:
                hashTable.setArgument(arg)
                hashTable.insertButton.invoke()
            else:
                hashTable.insert(int(arg) if arg.isdigit() else arg, code='')
        
    hashTable.showHashing.set(showHashing)
    if not animate:
        hashTable.stopAnimations()
    hashTable.runVisualization()
