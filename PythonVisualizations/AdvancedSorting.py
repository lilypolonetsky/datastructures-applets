import random
from tkinter import *
try:
    from drawnValue import *
    from VisualizationApp import *
    from SortingBase import *    
except ModuleNotFoundError:
    from .drawnValue import *
    from .VisualizationApp import *
    from .SortingBase import *    
      

class AdvancedArraySort(SortingBase):
    PIVOT_LINE_COLOR = 'VioletRed3'
    PIVOT_LINE_WIDTH = 2
    PIVOT_LINE_PAD = 0

    def __init__(self, title="Advanced Sorting", **kwargs):
        super().__init__(title=title, **kwargs)
        self.ARRAY_Y0 = 60
        
        for i in range(self.size):
            self.list.append(drawnValue(random.randrange(self.valMax)))
        self.display()
        
        self.buttons = self.makeButtons()
        
    def fillCoords(self, val, rectPos, valMin=0, valMax=None):
        if valMax is None:
            valMax = self.valMax
        x1, y1, x2, y2 = rectPos 
        minY = (y1 * 8 + y2 * 2) // 10
        # proportion of what is filled
        prop = (val - valMin) / (valMax - valMin)
        y2 = round(minY + prop * (y2 - minY))
        
        return (x1, y1, x2, y2)
        
    def fixGaps(self, toX=SortingBase.ARRAY_X0, toY=SortingBase.ARRAY_Y0):
        done = [False] * len(self.list)
        doneCount = 0
        while doneCount < len(self.list):
            for i in range(len(self.list)):
                # move the done elements up by dy and corresponding dx
                if not done[i]:
                    dx=0
                    dy=0
                    coords = self.canvas.coords(self.list[i].items[0])
                    curX, curY = coords[:2]

                    # calculate dx based on if the cell is to the right or to
                    # the left of its desired position
                    if curX < toX + self.CELL_SIZE*i:
                        dx = 0.5 if curX % 1 == 0 else toX + self.CELL_SIZE*i - curX
                    elif curX > toX + self.CELL_SIZE*i:
                        dx = -0.5 if curX % 1 == 0 else toX + self.CELL_SIZE*i - curX
                    # do the same for dy
                    if curY < toY:
                        dy = 0.5 if curY % 1 == 0 else toY - curY
                    elif curY > toY:
                        dy = -0.5 if curY % 1 == 0 else toY - curY
                    # if dx or dy are not zero, the cell isn't in position and still needs to be moved
                    if dx or dy:
                        self.moveItemsBy(self.list[i].items, (dx, dy))

                    # when the cell is in the correct position, mark it as done
                    else:
                        doneCount += 1
                        done[i] = True
            self.wait(0.01)
    
    # SORTING METHODS 

    rightmostCode = '''
def rightmost(self, lo={lo}, hi={hi}, key=identity):
   return self.get(hi)
'''
    def rightmost(self, lo, hi, code=rightmostCode):
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))
        self.startAnimations()
        self.highlightCode('return self.get(hi)', callEnviron, wait=0.1)
        self.cleanUp(callEnviron)
        return self.list[hi].val
    
    medianOfThreeCode = '''
def medianOfThree(self, lo={lo}, hi={hi}, key=identity):
   mid = (lo + hi) // 2
   if key(self.get(lo)) > key(self.get(mid)):
      self.swap(lo, mid)
   if key(self.get(lo)) > key(self.get(hi)):
      self.swap(lo, hi)
   if key(self.get(hi)) > key(self.get(mid)):
      self.swap(hi, mid)
   return self.get(hi)
'''
    
    def medianOfThree(self, lo, hi, code=medianOfThreeCode):
        wait = 0.1
        codeWait = 0.01
        self.startAnimations()
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=codeWait)

        loIndex = self.createIndex(lo, 'lo')
        hiIndex = self.createIndex(hi, 'hi')
        callEnviron |= set(loIndex + hiIndex)
        
        self.highlightCode('mid = (lo + hi) // 2', callEnviron, wait=wait)
        mid = (lo + hi) // 2
        midIndex = self.createIndex(mid, 'mid', level=2)
        callEnviron |= set(midIndex)

        self.highlightCode('key(self.get(lo)) > key(self.get(mid))',
                           callEnviron, wait=wait)
        if self.list[lo].val > self.list[mid].val:
            self.highlightCode('self.swap(lo, mid)', callEnviron)
            self.swap(lo, mid)

        self.highlightCode('key(self.get(lo)) > key(self.get(hi))',
                           callEnviron, wait=wait)
        if self.list[lo].val > self.list[hi].val:
            self.highlightCode('self.swap(lo, hi)', callEnviron)
            self.swap(lo, hi)

        self.highlightCode('key(self.get(hi)) > key(self.get(mid))',
                           callEnviron, wait=wait)
        if self.list[hi].val > self.list[mid].val:
            self.highlightCode('self.swap(hi, mid)', callEnviron)
            self.swap(hi, mid)

        self.highlightCode('return self.get(hi)', callEnviron, wait=wait)
        self.cleanUp(callEnviron, sleepTime=codeWait)
        return self.list[hi].val

    __partCode = '''
def __part(self, pivot={pivot}, lo={lo}, hi={hi}, key=identity):
   while lo <= hi:
      while (key(self.get(lo)) < pivot):
         lo += 1
      while (pivot < key(self.get(hi))):
         hi -= 1
      if lo >= hi:
         return lo
      self.swap(lo, hi)
      lo, hi = lo + 1, hi - 1
   return lo
'''
    def partition(self, pivot, lo, hi, code=__partCode):
        wait = 0.1
        codeWait = 0.01
        self.startAnimations()
        if not self.useMedianOf3.get():
            code = code.replace('pivot <', 'lo < hi and pivot <')
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=codeWait)
        
        loIndex = self.createIndex(lo, 'lo')
        hiIndex = self.createIndex(hi, 'hi', level=2)
        callEnviron |= set(loIndex + hiIndex)
        leftDelta = (-self.CELL_WIDTH, 0)
        rightDelta = (self.CELL_WIDTH, 0)
        
        self.highlightCode('lo <= hi', callEnviron, wait=wait)
        while lo <= hi:
            self.highlightCode('key(self.get(lo)) < pivot', callEnviron,
                               wait=wait)
            while self.list[lo].val < pivot:
                self.highlightCode('lo += 1', callEnviron)
                lo += 1
                self.moveItemsBy(loIndex, rightDelta, sleepTime=wait / 10)
                
                self.highlightCode('key(self.get(lo)) < pivot', callEnviron,
                                   wait=wait)

            if not self.useMedianOf3.get():
                self.highlightCode('lo < hi', callEnviron, wait=wait)
            if lo < hi or self.useMedianOf3.get():
                self.highlightCode('pivot < key(self.get(hi))', callEnviron,
                                   wait=wait)
            while lo < hi and pivot < self.list[hi].val:
                self.highlightCode('hi -= 1', callEnviron)
                hi -= 1
                self.moveItemsBy(hiIndex, leftDelta, sleepTime=wait / 10)
                
                if not self.useMedianOf3.get():
                    self.highlightCode('lo < hi', callEnviron, wait=wait)
                if lo < hi or self.useMedianOf3.get():
                    self.highlightCode('pivot < key(self.get(hi))', callEnviron,
                                       wait=wait)
                
            self.highlightCode('lo >= hi', callEnviron, wait=wait)
            if lo >= hi:
                self.highlightCode('return lo', callEnviron, wait=wait)
                self.cleanUp(callEnviron, sleepTime=codeWait)
                return lo
                
            self.highlightCode('self.swap(lo, hi)', callEnviron)
            self.swap(lo, hi)

            self.highlightCode('lo, hi = lo + 1, hi - 1', callEnviron)
            lo, hi = lo + 1, hi - 1
            loCoords, hiCoords = self.indexCoords(lo), self.indexCoords(hi, 2)
            self.moveItemsTo(
                loIndex + hiIndex, 
                (loCoords, loCoords[:2], hiCoords, hiCoords[:2]),
                sleepTime=wait / 10)
            
            self.highlightCode('lo <= hi', callEnviron, wait=wait)
        
        self.highlightCode('return lo', callEnviron, wait=wait)
        self.cleanUp(callEnviron, sleepTime=codeWait)
        return lo

    quicksortCode = '''
def quicksort(self, lo={lo}, hi={hi}, short=3, key=identity):
   if hi is None:
      hi = len(self) - 1
   short = max(3, short)
   if hi - lo + 1 <= short:
      return self.insertionSort(lo, hi, key)
   pivotItem = self.medianOfThree(lo, hi, key)
   hipart = self.__part(key(pivotItem), lo + 1, hi - 1, key)
   self.swap(hipart, hi)
   self.quicksort(lo, hipart - 1, short, key)
   self.quicksort(hipart + 1, hi, short, key)
'''
    
    def quicksort(
            self, lo=0, hi=None, short=3, code=quicksortCode,
            bottomCallEnviron=None):
            
        # Start animation
        wait = 0.1
        codeWait = 0.01
        self.startAnimations()
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=codeWait)
        if bottomCallEnviron is None:
            bottomCallEnviron = callEnviron
            callEnviron |= set(self.createShowPartitionsControl())
        
        loIndex = self.createIndex(lo, 'lo')
        callEnviron |= set(loIndex)

        self.highlightCode('hi is None', callEnviron, wait=wait)
        if hi is None:
            self.highlightCode('hi = len(self) - 1', callEnviron, wait=wait)
            hi = len(self.list) - 1
            
        hiIndex = self.createIndex(hi, 'hi', level=2)
        callEnviron |= set(hiIndex)

        self.highlightCode('short = max(3, short)', callEnviron, wait=wait)
        short = max(3, short)

        self.highlightCode('hi - lo + 1 <= short', callEnviron, wait=wait)
        if hi - lo + 1 <= short:
            self.highlightCode('return self.insertionSort(lo, hi, key)',
                               callEnviron, wait=wait)
            self.fadeNonLocalItems(loIndex + hiIndex)
            self.insertionSort(lo, hi)
            self.restoreLocalItems(loIndex + hiIndex)
            self.cleanUp(callEnviron, sleepTime=codeWait)
            return
        
        self.highlightCode('pivotItem = self.{}(lo, hi, key)'.format(
            'medianOfThree' if  self.useMedianOf3.get() else 'rightmost'),
                           callEnviron)
        self.fadeNonLocalItems(loIndex + hiIndex)
        pivotItem = (self.medianOfThree(lo, hi) if self.useMedianOf3.get() else
                     self.rightmost(lo, hi))
        self.restoreLocalItems(loIndex + hiIndex)

        pivotPartition = self.createPivotPartition(lo, hi, pivotItem, hi)
        callEnviron |= set(pivotPartition)
        # bottomCallEnviron.add(pivotPartition[-1])
                
        self.highlightCode(
            'hipart = self.__part(key(pivotItem), {}, hi - 1, key)'.format(
                'lo + 1' if self.useMedianOf3.get() else 'lo'),
            callEnviron)
        self.fadeNonLocalItems(loIndex + hiIndex)
        hipart = self.partition(
            pivotItem, lo + (1 if self.useMedianOf3.get() else 0), hi - 1)
        self.restoreLocalItems(loIndex + hiIndex)
        hipartIndex = self.createIndex(hipart, 'hipart', level=2)
        callEnviron |= set(hipartIndex)
        
        self.highlightCode('self.swap(hipart, hi)', callEnviron)
        self.swap(hipart, hi)
        pivotMark = self.createPivotMark(hipart, pivotItem)
        bottomCallEnviron |= set(pivotMark)

        for item in pivotPartition:
            self.canvas.delete(item)
            callEnviron.discard(item)
        pivotPartition = ()

        self.highlightCode('self.quicksort(lo, hipart - 1, short, key)',
                           callEnviron)
        self.fadeNonLocalItems(loIndex + hiIndex + hipartIndex)
        self.quicksort(lo, hipart - 1, short, code, 
                       bottomCallEnviron=bottomCallEnviron)
        self.restoreLocalItems(loIndex + hiIndex + hipartIndex)
        self.canvas.tag_raise('pivotPartition')

        self.highlightCode('self.quicksort(hipart + 1, hi, short, key)',
                           callEnviron)
        self.fadeNonLocalItems(loIndex + hiIndex + hipartIndex)
        self.quicksort(hipart + 1, hi, short, code, 
                       bottomCallEnviron=bottomCallEnviron)
        self.restoreLocalItems(loIndex + hiIndex + hipartIndex)
        self.canvas.tag_raise('pivotPartition')
        
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=codeWait)

    def createPivotPartition(
            self, lo, hi, pivot, pivotIndex,
            font=VisualizationApp.VARIABLE_FONT, 
            labelColor=VisualizationApp.VARIABLE_COLOR, 
            tags=['pivotPartition']):
        pivotCoords, loCoords, hiCoords = (
            self.canvas.coords(self.list[idx].items[0]) for idx in
            (pivotIndex, lo, hi))
        
        pad = self.PIVOT_LINE_PAD

        labels = ['pivot', str(pivot), '[{}, {}]'.format(lo, hi)]
        widths = [self.textWidth(font, label) for label in labels]
        height = abs(font[1])
        maxWidth = max(*widths)
        lbls = tuple(self.canvas.create_text(
            self.ARRAY_X0 - maxWidth // 2 - 1,
            pivotCoords[3] + (i - 1) * height,
            text=labels[i], font=font, fill=labelColor)
                  for i in range(len(labels)))
        line = self.canvas.create_line(
            loCoords[0] - pad, pivotCoords[3], 
            hiCoords[2] + pad, pivotCoords[3], tags=tags, dash=(5, 5),
            fill=self.PIVOT_LINE_COLOR, width=self.PIVOT_LINE_WIDTH)
        if not self.showPartitions:
            for item in lbls + (line,):
                self.canvas.coords(
                    item, multiply_vector(self.canvas.coords(item), -1))
        return lbls + (line,)

    def pivotMarkCoords(self, pivotIndex):
        cellCoords = self.cellCoords(pivotIndex)
        centerX = (cellCoords[0] + cellCoords[2]) // 2
        top = cellCoords[3] + 10
        dX, dY = 5, 15
        return (centerX, top, centerX - dX, top + dY, centerX + dX, top + dY)
        
    def createPivotMark(
            self, pivotIndex, pivotValue, 
            color=VisualizationApp.VARIABLE_COLOR, tags=['pivotPartition']):
        mark = self.canvas.create_polygon(
            *self.pivotMarkCoords(pivotIndex), tags=tags, fill=color, width=0)
        items = (mark,)
        if not self.showPartitions:
            for item in items:
                self.canvas.coords(
                    item, multiply_vector(self.canvas.coords(item), -1))
        return items

    def showPartitionsControlCoords(self):
        gap = 10
        size = 16
        canvasDims = self.widgetDimensions(self.canvas)
        return (gap, canvasDims[1] - gap - size, 
                gap + size, canvasDims[1] - gap)
    
    def createShowPartitionsControl(self):
        coords = self.showPartitionsControlCoords()
        box = self.canvas.create_rectangle(
            *coords, fill=self.DEFAULT_BG, outline=self.CONTROLS_COLOR, width=2)
        center = divide_vector(add_vector(coords[:2], coords[2:]), 2)
        self.showPartitionsCheck = self.canvas.create_text(
            *(center if self.showPartitions else multiply_vector(center, -1)),
            text='✓', fill=self.CONTROLS_COLOR, font=self.CONTROLS_FONT)
        label = self.canvas.create_text(
            *add_vector(center, (coords[2] - coords[0], 0)), anchor=W,
            text='Show pivot partitions', fill=self.CONTROLS_COLOR, 
            font=self.CONTROLS_FONT)
        items = (box, self.showPartitionsCheck, label)
        for item in items:
            self.canvas.tag_bind(item, '<Button>', self.toggleShowPartitons)
        return items

    def toggleShowPartitons(self, event=None):
        self.showPartitions = not self.showPartitions
        sign = 1 if self.showPartitions else -1
        for item in self.canvas.find_withtag('pivotPartition') + (
                self.showPartitionsCheck,):
            self.canvas.coords(
                item, *(sign * abs(c) for c in self.canvas.coords(item)))
        
    def insertionSort(self, lo, hi):
        'Sort a short range of cells using insertion sort (no code)'
        wait = 0.1
        self.startAnimations()
        callEnviron = self.createCallEnvironment()
        n = len(self.list)

        # make an index arrow for the outer loop
        outer = lo + 1
        outerIndex = self.createIndex(outer, "outer", level=2)
        callEnviron |= set(outerIndex)

        # make an index arrow that points to the next cell to check
        innerIndex = self.createIndex(outer, "inner", level=1)
        callEnviron |= set(innerIndex)
        tempVal, label = None, None

        # All items beyond the outer index have not been sorted
        while outer <= hi:

            # Store item at outer index in temporary mark variable
            temp = self.list[outer].val

            if tempVal:
                tempVal, _ = self.assignToTemp(
                    outer, callEnviron, varName="temp", existing=label)
            else:
                tempVal, label = self.assignToTemp(
                    outer, callEnviron, varName="temp")
                callEnviron.add(label)

            # Inner loop starts at marked temporary item
            inner = outer

            # Move inner index arrow to point at cell to check
            centerX0 = self.cellCenter(inner)[0]
            deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
            if deltaX != 0:
                self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=wait / 10)

            # Loop down until we find an item less than or equal to the mark
            while inner > lo and temp < self.list[inner - 1].val:

                # Shift cells right that are greater than mark
                self.assignElement(inner - 1, inner, callEnviron)

                # Move inner index arrow to point at next cell to check
                inner -= 1
                centerX0 = self.cellCenter(inner)[0]
                deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
                if deltaX != 0:
                    self.moveItemsBy(
                        innerIndex, (deltaX, 0), sleepTime=wait / 10) 

            # Delay to show discovery of insertion point for mark
            self.wait(wait)

            # Copy marked temporary value to insertion point
            self.assignFromTemp(inner, tempVal, None)

            # Take it out of the cleanup set since it should persist
            callEnviron -= set(tempVal.items)

            # Advance outer loop
            outer += 1
            self.moveItemsBy(outerIndex, (self.CELL_WIDTH, 0), 
                             sleepTime=wait / 10)

        # Animation stops
        self.cleanUp(callEnviron)

    shellSortCode = """
def shellSort(self):
    h = 1
    while h * 3 < len(self):
        h = 3 * h + 1
    nShifts = 0
    while h > 0:
        for outer in range(h, len(self)):
            temp = self.get(outer)
            inner = outer
            while inner >= h and temp < self.get(inner-h):
                self.set(inner, self.get(inner-h))
                inner -= h
                nShifts += 1
            if inner < outer:
                self.set(inner, temp)
                nShifts += 1
        h = (h - 1) // 3
    return nShifts
    """

    def shellSort(self, code=shellSortCode):
        wait = 0.1
        moveWait = wait / 10
        descend = (0, 16) * 2
        callEnviron = self.createCallEnvironment(code=code)
        self.startAnimations()

        # calculate h
        h = 1
        hLabel = None
        hLabel = self.adjustHLabel(h, 0, None)
        callEnviron |= set(hLabel)
        self.highlightCode('h = 1', callEnviron, wait=wait)
        
        self.highlightCode('h * 3 < len(self)', callEnviron, wait=wait)
        while h * 3 < len(self.list):
            self.highlightCode('h = 3 * h + 1', callEnviron)
            h = 3 * h + 1
            self.adjustHLabel(h, 0, hLabel)
            
            self.highlightCode('h * 3 < len(self)', callEnviron, wait=wait)
            
        nShifts = 0
        nShiftsPos = (10, self.ARRAY_Y0 // 3)
        nShiftsValue = "nShifts: {}"
        nShiftsLabel = self.canvas.create_text(
            *nShiftsPos, anchor=W, text=nShiftsValue.format(nShifts),
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(nShiftsLabel)
        self.highlightCode('nShifts = 0', callEnviron, wait=wait)

        tempLabel, outerArrow, innerArrow = None, None, None
        toRestore = []
        self.highlightCode('h > 0', callEnviron, wait=wait)
        while h > 0:
            if outerArrow is None:
                outerArrow = self.createIndex(h, name="outer", level=-2)
                callEnviron |= set(outerArrow)
            
            self.highlightCode('outer in range(h, len(self))', callEnviron,
                               wait=wait)
            for outer in range(h, len(self.list)):
                # move outer index
                arrowPos = self.indexCoords(outer, level=-2)
                outerCoords = self.canvas.coords(outerArrow[0])
                if outerCoords != arrowPos:
                    self.moveItemsTo(outerArrow, (arrowPos, arrowPos[:2]), 
                                     sleepTime=moveWait)
                    self.adjustHLabel(h, outer - h, hLabel)

                # Move cells being worked down
                toMove = [j for j in range(outer if h > 1 else -1, -1, -h)]
                itemsToMove = list(flat(*[
                    self.list[j].items + (self.arrayCells[j],) for j in toMove]))
                toMoveCoords = [add_vector(self.canvas.coords(i), descend)
                                for i in itemsToMove]
                itemsToRestore = list(flat(*[
                    self.list[j].items + (self.arrayCells[j],) for j in toRestore]))
                toRestoreCoords = list(flat(*[
                    [self.fillCoords(self.list[j].val, self.cellCoords(j))] +
                    ([self.cellCenter(j)] if len(self.list[j].items) > 1 
                     else []) +
                    [self.arrayCellCoords(j)] for j in toRestore]))
                if len(itemsToMove + itemsToRestore) > 0:
                    self.moveItemsTo(
                        itemsToMove + itemsToRestore, 
                        toMoveCoords + toRestoreCoords, sleepTime=moveWait)
                toRestore = toMove
                
                # assign outer to temp
                self.highlightCode('temp = self.get(outer)', callEnviron)
                temp = self.list[outer]
                tempVal, tempLabel = self.assignToTemp(
                    outer, callEnviron, varName="temp", existing=tempLabel)
                callEnviron |= set(tempVal.items + (tempLabel,))

                # create the inner index
                inner = outer
                if innerArrow is None:
                    innerArrow = self.createIndex(inner, name="inner", level=-1)
                    callEnviron |= set(innerArrow)
                    self.highlightCode('inner = outer', callEnviron, wait=wait)
                else:
                    arrowPos = self.indexCoords(inner, level=-1)
                    self.moveItemsTo(innerArrow, (arrowPos, arrowPos[:2]),
                                     sleepTime=moveWait)

                self.highlightCode('inner >= h', callEnviron, wait=wait)
                if inner >= h:
                    self.highlightCode('temp < self.get(inner-h)', callEnviron,
                                       wait=wait)
                    
                while inner >= h and tempVal.val < self.list[inner-h].val:
                    self.highlightCode('self.set(inner, self.get(inner-h))',
                                       callEnviron)
                    self.assignElement(
                        inner-h, inner, callEnviron, sleepTime=moveWait,
                        startAngle=90 * 11 / (10 + abs(inner-h)))

                    # move the inner index
                    self.highlightCode('inner -= h', callEnviron)
                    inner -= h
                    arrowPos = self.indexCoords(inner, level=-1)
                    self.moveItemsTo(innerArrow, (arrowPos, arrowPos[:2]),
                                     sleepTime=moveWait)

                    nShifts += 1
                    self.canvas.itemconfigure(
                        nShiftsLabel, text=nShiftsValue.format(nShifts))
                    self.highlightCode('nShifts += 1', callEnviron, wait=wait)
                    
                    self.highlightCode('inner >= h', callEnviron, wait=wait)
                    if inner >= h:
                        self.highlightCode('temp < self.get(inner-h)',
                                           callEnviron, wait=wait)

                self.highlightCode('inner < outer', callEnviron, wait=wait)
                if inner < outer:
                    self.highlightCode('self.set(inner, temp)', callEnviron)
                    self.assignFromTemp(inner, tempVal, tempLabel, delete=False,
                                        sleepTime=moveWait)
                    
                    # Take temp out of the cleanup set since it should persist
                    callEnviron -= set(tempVal.items)

                    nShifts += 1
                    self.canvas.itemconfigure(
                        nShiftsLabel, text=nShiftsValue.format(nShifts))
                    self.highlightCode('nShifts += 1', callEnviron, wait=wait)
                    
                    self.highlightCode('outer in range(h, len(self))',
                                       callEnviron)
                else:
                    for item in tempVal.items:
                        self.canvas.delete(item)
                    
            # change h
            self.highlightCode('h = (h - 1) // 3', callEnviron)
            h = (h - 1) // 3
            self.adjustHLabel(h, 0, hLabel)
            
            self.highlightCode('h > 0', callEnviron, wait=wait)
        
        self.highlightCode('return nShifts', callEnviron, wait=wait)
        self.cleanUp(callEnviron)
        return nShifts

    def adjustHLabel(
            self, h, leftCell, hLabel, steps=10, sleepTime=0.01, font=None,
            color=None):
        'Adjust or make the h span label'
        if font is None:
            font = self.VARIABLE_FONT
        leftCenter = self.cellCenter(leftCell)[0]
        spanCoords = self.hSpanCoords(h, leftCenter)
        spanCenter = ((spanCoords[0] + spanCoords[-2]) // 2, spanCoords[5])
        textPattern = "h: {}"
        hText = textPattern.format(h)
        textWidth = self.textWidth(font, hText)
        boxCoords = (spanCenter[0] - textWidth / 2 - 1, spanCoords[1],
                     spanCenter[0] + textWidth / 2 + 1, spanCoords[3])
        if hLabel:  # Adjust existing hLabel: (span, box, text)
            currentCoords = self.canvas.coords(hLabel[0])
            currentText = self.canvas.itemconfigure(hLabel[2], 'text')[-1]
            startH = int(currentText[3:]) if currentText != hText else h
            if currentCoords != spanCoords or currentText != hText:
                for step in range(steps):
                    sCoords = divide_vector(
                        add_vector(multiply_vector(currentCoords,
                                                   steps - 1 - step),
                                   multiply_vector(spanCoords, step + 1)),
                        steps)
                    sCenter = ((sCoords[0] + sCoords[-2]) // 2, sCoords[5])
                    if startH != h:
                        text = 'h: {:3.1f}'.format(
                            (startH * (steps - 1 - step) + h * (step + 1)) /
                            steps)
                        textWidth = self.textWidth(font, text)
                    bCoords = (sCenter[0] - textWidth / 2 - 1, sCoords[1],
                               sCenter[0] + textWidth / 2 + 1, sCoords[3])
                    for i, coords in zip(hLabel, (sCoords, bCoords, sCenter)):
                        self.canvas.coords(i, *coords)
                    if startH != h:
                        self.canvas.itemconfigure(hLabel[2], text=text)
                    self.wait(sleepTime)
                    
                for i, coords in zip(hLabel, 
                                     (spanCoords, boxCoords, spanCenter)):
                    self.canvas.coords(i, *coords)
                self.canvas.itemconfigure(hLabel[2], text=hText)
                        
        else: # Create new hLabel
            if color is None:
                color = self.VARIABLE_COLOR
            span = self.canvas.create_line(*spanCoords, fill=color)
            box = self.canvas.create_rectangle(*boxCoords,
                fill=self.DEFAULT_BG, width=0, outline='')
            text = self.canvas.create_text(
                *spanCenter, text=hText, font=font, fill=color)
            hLabel = (span, box, text)
        return hLabel   # Return created or adjusted canvas items
                
    def hSpanCoords(self, h, leftCenter):
        width = h * self.CELL_WIDTH
        height = 18
        _, y0, x, y = self.indexCoords(0, level=1)
        x0, x1 = leftCenter, leftCenter + width
        return (x0, y0 - height // 2, x0, y0 + height // 2,
                x0, y0, x1, y0,
                x1, y0 - height // 2, x1, y0 + height // 2)
    
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
            "Delete Rightmost", lambda: self.deleteLast(), maxRows=maxRows,
            helpText='Delete last array item')
        shuffleButton = self.addOperation(
            "Shuffle", lambda: self.shuffle(), maxRows=maxRows,
            helpText='Shuffle position of all items')
        shellSortButton = self.addOperation(
            "Shellsort", lambda: self.shellSort(), maxRows=maxRows,
            helpText='Sort items using shellsort algorithm')
        quicksortButton = self.addOperation(
            "Quicksort", lambda: self.clickQuicksort(), maxRows=maxRows,
            helpText='Sort items using quicksort algorithm')
        self.useMedianOf3 = IntVar()
        self.useMedianOf3.set(1)
        useMedianOf3Button = self.addOperation(
            "Use median of 3", self.clickUseMedianOf3, buttonType=Checkbutton,
            variable=self.useMedianOf3, maxRows=maxRows,
            helpText='Use median of 3 to select\npivot in quicksort algorithm')
        buttons = [btn for btn in self.opButtons]
        self.addAnimationButtons(maxRows=maxRows)
        return buttons  # Buttons managed by play/pause/stop controls

    def clickQuicksort(self):
        self.partitions = []
        self.showPartitions = True
        self.quicksort(code=self.quicksortCode if self.useMedianOf3.get() else
                       self.quicksortCode.replace('medianOfThree', 'rightmost')
                       .replace('lo + 1,', 'lo,'))

    def clickUseMedianOf3(self):
        pass
        
if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    array = AdvancedArraySort()

    array.runVisualization()
