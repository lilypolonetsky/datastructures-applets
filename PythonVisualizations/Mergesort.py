import random
from tkinter import *
try:
    from coordinates import *
    from drawnValue import *
    from VisualizationApp import *
    from SortingBase import *    
except ModuleNotFoundError:
    from coordinates import *
    from .drawnValue import *
    from .VisualizationApp import *
    from .SortingBase import *    
      
V = vector

class Mergesort(SortingBase):

    CELL_GAP = 6
    LEVEL_SEPARATION = 25

    def __init__(self, title="Mergesort", values=None, **kwargs):
        super().__init__(title=title, **kwargs)
        self.ARRAY_Y0 = 50
        self.CELL_HEIGHT = 90
        self.LABEL_GAP = abs(self.VARIABLE_FONT[1])

        if values is None:
            for i in range(self.size):
                self.list.append(drawnValue(random.randrange(self.valMax)))
        else:
            self.list = [drawnValue(val) for val in values]
        self.display(showNItems=False)
        
        self.buttons = self.makeButtons()
    
    # SORTING METHODS 

    initMergesortCode = '''
def __init__(self, unordered, key=identity):
   self.__arr = unordered
   self.__key = key
   n = len(unordered)
   self.__work = Array(n)
   for i in range(n):
      self.__work.insert(None)
   self.mergesort(0, n)
'''
        
    def mergesortInit(self, code=initMergesortCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        wait = 0.1
        self.highlightCode('self.__arr = unordered', callEnviron, wait=wait)
        self.highlightCode('self.__key = key', callEnviron, wait=wait)
        self.highlightCode('n = len(unordered)', callEnviron, wait=wait)
        self.highlightCode('self.__work = Array(n)', callEnviron, wait=wait)
        if len(getattr(self, 'arrayCells', [])) > 0:
            cell0coords = self.canvas.coords(self.arrayCells[0])
        else:
            cell0Coords = [0] * 4
        canvasDims = widgetDimensions(self.canvas)
        delta = (0, canvasDims[1] - self.CELL_BORDER * 2 - cell0coords[3])
        callEnviron.add(self.canvas.create_text(
            cell0coords[0] - self.CELL_GAP,
            (cell0coords[1] + cell0coords[3]) // 2 + delta[1],
            text='__work', font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR,
            anchor=E))
        tags = ["workArray"]
        self.workCells, self.workArray = [], []
        self.highlightCode('i in range(n)', callEnviron, wait=wait / 2)
        for i in range(self.size):
            self.highlightCode(
                'self.__work.insert(None)', callEnviron, wait=wait / 50)
            rect = self.createArrayCell(i, tags=tags)
            self.canvas.move(rect, *delta)
            self.workCells.append(rect)
            self.workArray.append(None)
            callEnviron.add(rect)
            self.highlightCode('i in range(n)', callEnviron, wait=wait / 20)

        self.loIndex, self.hiIndex = None, None
        if len(self.arrayCells) == self.size:  # Create an invisible array cell
            self.arrayCells.append(self.createArrayCell( # at the right end
                len(self.arrayCells),          # to use for hi index
                tags=["hidden", "arrayBox"], width=0, color=self.DEFAULT_BG))
        self.highlightCode('self.mergesort(0, n)', callEnviron)
        self.mergesort(0, len(self.list))
        self.fixCells()
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    mergesortCode = '''
def mergesort(self, lo={lo}, hi={hi}):
   if lo + 1 >= hi:
      return
   mid = (lo + hi) // 2
   self.mergesort(lo, mid)
   self.mergesort(mid, hi)
   self.merge(lo, mid, hi)
'''
    
    def mergesort(self, lo, hi, level=0, code=mergesortCode):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=wait / 10)
        for idx, val in (('loIndex', lo), ('hiIndex', hi)):
            arrayCell = self.arrayCells[val]
            if getattr(self, idx, None) is None:
                setattr(self, idx, self.createCellIndex(
                    arrayCell, idx[:2], level=2))
                callEnviron.add(getattr(self, idx))
            else:
                self.moveIndex(getattr(self, idx), arrayCell)
            
        self.highlightCode('lo + 1 >= hi', callEnviron, wait=wait)
        if lo + 1 >= hi:
            self.highlightCode('return', callEnviron, wait=wait)
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return
        
        self.highlightCode('mid = (lo + hi) // 2', callEnviron)
        mid = (lo + hi) // 2
        midLabel = self.createCellIndex(self.list[mid].items[0], 'mid', level=1)
        callEnviron.add(midLabel)
        local = [midLabel]
        self.wait(wait)

        self.highlightCode('self.mergesort(lo, mid)', callEnviron, wait=wait)
        delta = (-self.CELL_GAP, self.LEVEL_SEPARATION)
        self.moveItemsBy(
            flat(*([self.arrayCells[j]] + [item for item in self.list[j].items]
                   for j in range(lo, mid))),
            delta, sleepTime=wait / 10)
        colors = self.canvas.fadeItems(local)
        self.mergesort(lo, mid, level=level + 1)
        self.canvas.restoreItems(local, colors)
        self.moveItemsBy(
            flat(*([self.arrayCells[j]] + [item for item in self.list[j].items]
                   for j in range(lo, mid))),
            V(delta) * -1, sleepTime=wait / 10)
        self.moveIndex(self.loIndex, self.arrayCells[lo])
        self.moveIndex(self.hiIndex, self.arrayCells[hi])

        self.highlightCode('self.mergesort(mid, hi)', callEnviron, wait=wait)
        delta = (self.CELL_GAP, self.LEVEL_SEPARATION)
        self.moveItemsBy(
            flat(*([self.arrayCells[j]] + [item for item in self.list[j].items]
                   for j in range(mid, hi))),
            delta, sleepTime=wait / 10)
        colors = self.canvas.fadeItems(local)
        self.mergesort(mid, hi, level=level + 1)
        self.canvas.restoreItems(local, colors)
        self.moveItemsBy(
            flat(*([self.arrayCells[j]] + [item for item in self.list[j].items]
                   for j in range(mid, hi))),
            V(delta) * -1, sleepTime=wait / 10)
        self.moveIndex(self.loIndex, self.arrayCells[lo])
        self.moveIndex(self.hiIndex, self.arrayCells[hi])
            
        self.highlightCode('self.merge(lo, mid, hi)', callEnviron)
        self.merge(lo, mid, hi)
        
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)

    mergeCode = '''
def merge(self, lo={lo}, mid={mid}, hi={hi}):
   n = 0
   idxLo = lo
   idxHi = mid
   while (idxLo < mid and idxHi < hi):
      itemLo = self.__arr.get(idxLo)
      itemHi = self.__arr.get(idxHi)
      if (self.__key(itemLo) <= self.__key(itemHi)):
         self.__work.set(n, itemLo)
         idxLo += 1
      else:
         self.__work.set(n, itemHi)
         idxHi += 1
      n += 1

   while idxLo < mid:
      self.__work.set(n, self.__arr.get(idxLo))
      idxLo += 1
      n += 1

   while n > 0:
      n -= 1
      self.__arr.set(lo + n, self.__work.get(n))
'''
    
    def merge(self, lo, mid, hi, code=mergeCode):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=wait / 10)

        self.highlightCode('n = 0', callEnviron, wait=wait)
        n = 0
        nIndex = self.createCellIndex(self.workCells[n], 'n', level=1)
        callEnviron.add(nIndex)

        self.highlightCode('idxLo = lo', callEnviron, wait=wait)
        idxLo = lo
        idxLoIndex = self.createCellIndex(
            self.arrayCells[idxLo], 'idxLo', level=-1)
        callEnviron.add(idxLoIndex)

        self.highlightCode('idxHi = mid', callEnviron, wait=wait)
        idxHi = mid
        idxHiIndex = self.createCellIndex(
            self.arrayCells[idxHi], 'idxHi', level=-2)
        callEnviron.add(idxHiIndex)

        idxDelta = (self.CELL_WIDTH, 0)

        self.highlightCode('idxLo < mid', callEnviron, wait=wait)
        if idxLo < mid:
            self.highlightCode('idxHi < hi', callEnviron, wait=wait)
        while idxLo < mid and idxHi < hi:
            self.highlightCode(
                'itemLo = self.__arr.get(idxLo)', callEnviron, wait=wait)
            self.highlightCode(
                'itemHi = self.__arr.get(idxHi)', callEnviron, wait=wait)
            self.highlightCode(
                'self.__key(itemLo) <= self.__key(itemHi)', callEnviron,
                wait=wait)
            if self.list[idxLo].val <= self.list[idxHi].val:
                self.highlightCode('self.__work.set(n, itemLo)', callEnviron)
                copiedVal = self.setArrayValue(
                    self.workArray, self.workCells, n, 
                    self.list, self.arrayCells, idxLo, callEnviron)
                self.workArray[n] = copiedVal
                
                self.highlightCode('idxLo += 1', callEnviron)
                idxLo += 1
                self.moveItemsBy(idxLoIndex, idxDelta, sleepTime=wait / 10)
                
            else:
                self.highlightCode('self.__work.set(n, itemHi)', callEnviron)
                copiedVal = self.setArrayValue(
                    self.workArray, self.workCells, n, 
                    self.list, self.arrayCells, idxHi, callEnviron)
                self.workArray[n] = copiedVal
                
                self.highlightCode('idxHi += 1', callEnviron)
                idxHi += 1
                self.moveItemsBy(idxHiIndex, idxDelta, sleepTime=wait / 10)
            
            self.highlightCode('n += 1', callEnviron)
            n += 1
            self.moveItemsBy(nIndex, idxDelta, sleepTime=wait / 10)

            self.highlightCode('idxLo < mid', callEnviron, wait=wait)
            if idxLo < mid:
                self.highlightCode('idxHi < hi', callEnviron, wait=wait)

        self.highlightCode(('idxLo < mid', 2), callEnviron, wait=wait)
        while idxLo < mid:
            self.highlightCode(
                'self.__work.set(n, self.__arr.get(idxLo))', callEnviron)
            copiedVal = self.setArrayValue(
                self.workArray, self.workCells, n, 
                self.list, self.arrayCells, idxLo, callEnviron)
            self.workArray[n] = copiedVal

            self.highlightCode(('idxLo += 1', 2), callEnviron)
            idxLo += 1
            self.moveItemsBy(idxLoIndex, idxDelta, sleepTime=wait / 10)
            
            self.highlightCode(('n += 1', 2), callEnviron)
            n += 1
            self.moveItemsBy(nIndex, idxDelta, sleepTime=wait / 10)
            self.highlightCode(('idxLo < mid', 2), callEnviron, wait=wait)

        idxDelta = V(idxDelta) * -1
        self.highlightCode('n > 0', callEnviron, wait=wait)
        while n > 0:
            self.highlightCode('n -= 1', callEnviron)
            n -= 1
            self.moveItemsBy(nIndex, idxDelta, sleepTime=wait / 10)
            
            self.highlightCode(
                'self.__arr.set(lo + n, self.__work.get(n))', callEnviron)
            copiedVal = self.setArrayValue(
                self.list, self.arrayCells, lo + n,
                self.workArray, self.workCells, n, callEnviron)
            for item in self.list[lo + n].items:
                self.canvas.delete(item)
            self.list[lo + n] = copiedVal
            callEnviron -= set(copiedVal.items)

            self.highlightCode('n > 0', callEnviron, wait=wait)
            
        self.cleanUp(callEnviron)

    def moveIndex(self, index, rectID): # Move an index to be above a rectangle
        self.canvas.coords(
            index,
            (self.cellIndexCoords(rectID, 1)[0], self.canvas.coords(index)[1]))
        
    def setArrayValue(
            self, toArray, toCells, toIndex, fromArray, fromCells, fromIndex,
            callEnviron):
        if not isinstance(fromArray[fromIndex], drawnValue):
            raise Exception('Cannot get drawn value to copy')
        copiedVal = drawnValue(
            fromArray[fromIndex].val,
            *(self.canvas.copyItem(i) for i in fromArray[fromIndex].items))
        if callEnviron:
            callEnviron |= set(copiedVal.items)
        delta = V(self.canvas.coords(toCells[toIndex])) - V(
            self.canvas.coords(fromCells[fromIndex]))
        self.moveItemsBy(copiedVal.items, delta[:2], sleepTime=0.01)
        return copiedVal
        
    def cellIndexCoords(self, rectID, level):
        rectCoords = self.canvas.coords(rectID)
        return (
            (rectCoords[0] + rectCoords[2]) // 2,
            rectCoords[1 if level >= 0 else 3] - 
            (level + (-0.4 if level >=0 else 0.5)) * self.LABEL_GAP)
        
    def createCellIndex(self, rectID, name, level=1, color=None):
        if not color: color = self.VARIABLE_COLOR
        textCoords = self.cellIndexCoords(rectID, level)
        return self.canvas.create_text(
            *textCoords, text=name, fill=color, font=self.VARIABLE_FONT)
        
    def fixCells(self):
        super().fixCells()
        for i, cell in enumerate(self.arrayCells):
            self.canvas.coords(cell, self.arrayCellCoords(i))
                
    def makeButtons(self, maxRows=4):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows,
            argHelpText=['item key'], helpText='Insert item in array')
        searchButton = self.addOperation(
            "Search", lambda: self.clickSearch(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows,
            argHelpText=['item key'], helpText='Search for item in array')
        deleteButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows,
            argHelpText=['item key'], helpText='Delete array item')
        newButton = self.addOperation(
            "New", lambda: self.clickNew(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows, 
            argHelpText=['number of cells'],
            helpText='Create new empty array')
        randomFillButton = self.addOperation(
            "Random Fill", lambda: self.randomFill(), maxRows=maxRows,
            helpText='Fill empty array cells with random keys')
        increasingFillButton = self.addOperation(
            "Increasing Fill", lambda: self.linearFill(), maxRows=maxRows,
            helpText='Fill empty array cells with increasing keys')
        decreasingFillButton = self.addOperation(
            "Decreasing Fill", lambda: self.linearFill(False), maxRows=maxRows,
            helpText='Fill empty array cells with decreasing keys')
        deleteRightmostButton = self.addOperation(
            "Delete Rightmost", 
            lambda: self.deleteLast(start=self.startMode()), maxRows=maxRows,
            helpText='Delete last array item')
        shuffleButton = self.addOperation(
            "Shuffle", lambda: self.shuffle(), maxRows=maxRows,
            helpText='Shuffle position of all items')
        mergesortButton = self.addOperation(
            "Mergesort", 
            lambda: self.mergesortInit(start=self.startMode()), maxRows=maxRows,
            helpText='Sort items using mergesort')
        buttons = [btn for btn in self.opButtons]
        self.addAnimationButtons(maxRows=maxRows)
        return buttons  # Buttons managed by play/pause/stop controls

    def new(self, val, start=None):
        canvasDims = widgetDimensions(self.canvas)
        maxCells = min(
            self.maxCells, 
            (canvasDims[0] - self.ARRAY_X0) // self.CELL_MIN_WIDTH - 1)
        if val > maxCells:
            self.setMessage('Too many cells; must be {} or less'.format(
                maxCells))
            return
        elif val < 1:
            self.setMessage('Too few cells; must be 1 or more')
            return

        self.canvas.delete('all')
        
        self.size = val
        self.list = []
        self.CELL_WIDTH = self.computeCellWidth()
        self.showValues = self.canShowValues()

        self.display(showNItems=False)
        return True
        
if __name__ == '__main__':
    nonneg, negative, options, otherArgs = categorizeArguments(sys.argv[1:])
    if '-r' not in options:  # Use fixed seed for testing consistency unless
        random.seed(3.14159) # random option specified

    array = Mergesort(values=[int(arg) for arg in nonneg] if nonneg else None)
    array.runVisualization()
