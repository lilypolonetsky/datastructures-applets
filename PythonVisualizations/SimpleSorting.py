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

class SimpleArraySort(SortingBase):
    
    def __init__(self, title="Simple Sorting", values=None, **kwargs):
        kwargs['title'] = title
        super().__init__(**kwargs)

        if values is None:
            for i in range(self.size):
                self.list.append(drawnValue(random.randrange(self.valMax)))
        else:
            self.list = [drawnValue(val) for val in values]
        self.display()

        self.buttons = self.makeButtons()

    insertionSortCode = """
def insertionSort(self):
   for outer in range(1, self.__nItems):
      temp = self.__a[outer]
      inner = outer
      while inner > 0 and temp < self.__a[inner-1]:
         self.__a[inner] = self.__a[inner-1]
         inner -= 1
      self.__a[inner] = temp
"""

    # SORTING METHODS
    def insertionSort(self, code=insertionSortCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)
        n = len(self.list)

        # make an index arrow for the outer loop
        outer = 1
        outerIndex = self.createIndex(outer, "outer", level=2)
        callEnviron |= set(outerIndex)
        innerIndex, tempVal, label = None, None, None

        # All items beyond the outer index have not been sorted
        self.highlightCode('outer in range(1, self.__nItems)', callEnviron)
        while outer < len(self.list):

            # Store item at outer index in temporary mark variable
            self.highlightCode('temp = self.__a[outer]', callEnviron)
            temp = self.list[outer].val
            if tempVal:
                tempVal, _ = self.assignToTemp(
                    outer, callEnviron, varName="temp", existing=label,
                    tempCoords=self.tempLabelCoords(outer - 1))
            else:
                tempVal, label = self.assignToTemp(
                    outer, callEnviron, varName="temp",
                    tempCoords=self.tempLabelCoords(outer - 1))
                callEnviron.add(label)

            # Inner loop starts at marked temporary item
            self.highlightCode('inner = outer', callEnviron)
            inner = outer

            # make an index arrow that points to the next cell to check
            if innerIndex is None:
                innerIndex = self.createIndex(outer, "inner", level=1)
                callEnviron |= set(innerIndex)

            # Move inner index arrow to point at cell to check
            centerX0 = self.cellCenter(inner)[0]
            deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
            if deltaX != 0:
                self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=wait/5)

            # Loop down until we find an item less than or equal to the mark
            self.highlightCode('inner > 0', callEnviron, wait=wait)
            if inner > 0:
                self.highlightCode('temp < self.__a[inner-1]',
                                   callEnviron, wait=wait)
            while inner > 0 and temp < self.list[inner - 1].val:
                # Shift cells right that are greater than mark
                self.highlightCode('self.__a[inner] = self.__a[inner-1]',
                                   callEnviron)
                self.assignElement(inner - 1, inner, callEnviron)

                # Move inner index arrow to point at next cell to check
                inner -= 1
                self.highlightCode('inner -= 1', callEnviron)
                centerX0 = self.cellCenter(inner)[0]
                deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
                if deltaX != 0:
                    self.moveItemsBy(innerIndex + tempVal.items + (label,),
                                     (deltaX, 0), sleepTime=wait/5)
                    
                self.highlightCode('inner > 0', callEnviron, wait=wait)
                if inner > 0:
                    self.highlightCode('temp < self.__a[inner-1]',
                                       callEnviron, wait=wait)

            # Copy marked temporary value to insertion point
            self.highlightCode('self.__a[inner] = temp', callEnviron)
            self.assignFromTemp(inner, tempVal, None)

            # Take it out of the cleanup set since it should persist
            callEnviron -= set(tempVal.items)

            # Advance outer loop
            outer += 1
            self.highlightCode('outer in range(1, self.__nItems)', callEnviron)
            self.moveItemsBy(outerIndex, (self.CELL_WIDTH, 0), sleepTime=wait/5)
                 
        self.highlightCode([], callEnviron)
        self.fixCells()     

        # Animation stops
        self.cleanUp(callEnviron)

    bubbleSortCode = """
def bubbleSort(self):
   for last in range(self.__nItems-1, 0, -1):
      for inner in range(last):
         if self.__a[inner] > self.__a[inner+1]:
            self.swap(inner, inner+1)
"""

    def bubbleSort(self, code=bubbleSortCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)
        n = len(self.list)

        # make an index arrow that points to last unsorted element
        self.highlightCode('last in range(self.__nItems-1, 0, -1)', callEnviron)
        last = n - 1
        lastIndex = self.createIndex(last, "last", level=2)
        callEnviron |= set(lastIndex)

        # make an index arrow that points to the next cell to check
        innerIndex = None
        
        # While unsorted cells remain
        while last > 0:
            
            self.highlightCode('inner in range(last)', callEnviron)
            for inner in range(last):
                if innerIndex is None:
                    innerIndex = self.createIndex(inner, "inner", level=1)
                    callEnviron |= set(innerIndex)
                else:
                    centerX0 = self.cellCenter(inner)[0]
                    deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
                    if deltaX != 0:
                        self.moveItemsBy(
                            innerIndex, (deltaX, 0), sleepTime=wait/5)
                    
                # Compare cell value at inner index with the next value
                self.highlightCode('self.__a[inner] > self.__a[inner+1]',
                                   callEnviron, wait=wait)
                if self.list[inner].val > self.list[inner+1].val:
                    self.highlightCode('self.swap(inner, inner+1)', callEnviron)
                    self.swap(inner, inner+1)
                    
                # Move inner index arrow to cell to check
                self.highlightCode('inner in range(last)', callEnviron)
                centerX0 = self.cellCenter(inner + 1)[0]
                deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
                self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=wait/5)


            # move last index one lower
            last -= 1
            self.highlightCode('last in range(self.__nItems-1, 0, -1)', 
                               callEnviron)
            self.moveItemsBy(lastIndex, (-self.CELL_WIDTH, 0), sleepTime=wait/5)

        # Animation stops
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    selectionSortCode = """
def selectionSort(self):
   for outer in range(self.__nItems-1):
      min = outer
      for inner in range(outer+1, self.__nItems):
         if self.__a[inner] < self.__a[min]:
            min = inner
      self.swap(outer, min)
"""

    def selectionSort(self, code=selectionSortCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)
        n = len(self.list)      

        # make an index arrow for the outer loop
        self.highlightCode('outer in range(self.__nItems-1)', callEnviron)
        outer = 0
        outerIndex = self.createIndex(outer, "outer", level=3)
        callEnviron |= set(outerIndex)

        innerIndex, minIndex = None, None

        # All items beyond the outer index have not been sorted
        while outer < len(self.list) - 1:

            self.highlightCode('min = outer', callEnviron)
            min_idx = outer
            if minIndex is None:
                minIndex = self.createIndex(outer, "min", level=2)
                callEnviron |= set(minIndex)
            else:
                self.moveItemsBy(
                    minIndex,
                    (self.cellCenter(outer)[0] -
                     self.canvas.coords(minIndex[0])[0], 0), sleepTime=wait/5)
            
            # Find the minimum element in remaining unsorted array
            self.highlightCode('inner in range(outer+1, self.__nItems)',
                               callEnviron)
            for inner in range(outer + 1, len(self.list)):

                # Move inner index arrow to point at cell to check
                if innerIndex is None:
                    innerIndex= self.createIndex(inner, "inner", level=1)
                    callEnviron |= set(innerIndex)
                else:
                    centerX0 = self.cellCenter(inner)[0]
                    deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
                    if deltaX != 0:
                        self.moveItemsBy(
                            innerIndex, (deltaX, 0), sleepTime=wait/5)

                self.highlightCode('self.__a[inner] < self.__a[min]',
                                   callEnviron, wait=wait)
                if self.list[inner].val < self.list[min_idx].val:
                    self.highlightCode('min = inner', callEnviron)
                    min_idx = inner
                    self.moveItemsBy(
                        minIndex,
                        (self.canvas.coords(innerIndex[0])[0] -
                         self.canvas.coords(minIndex[0])[0], 0), 
                        sleepTime=wait/5)

                self.highlightCode('inner in range(outer+1, self.__nItems)',
                                   callEnviron)
                centerX0 = self.cellCenter(inner + 1)[0]
                deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
                self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=wait/5)

            # Swap the found minimum element with the one indexed by outer
            self.highlightCode('self.swap(outer, min)', callEnviron)
            self.swap(outer, min_idx)

            # move outer index one higher
            outer += 1
            self.highlightCode('outer in range(self.__nItems-1)', callEnviron)
            self.moveItemsBy(outerIndex, (self.CELL_WIDTH, 0), sleepTime=0.05)

        self.fixCells()

        # Animation stops
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

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
        bubbleSortButton = self.addOperation(
            "Bubble Sort", 
            lambda: self.bubbleSort(start=self.startMode()), maxRows=maxRows,
            helpText='Sort array using bubble sort')
        selectionSortButton = self.addOperation(
            "Selection Sort",
            lambda: self.selectionSort(start=self.startMode()), maxRows=maxRows,
            helpText='Sort array using selelction sort')
        insertionSortButton = self.addOperation(
            "Insertion Sort", 
            lambda: self.insertionSort(start=self.startMode()), maxRows=maxRows,
            helpText='Sort array using insertion sort')
        buttons = [btn for btn in self.opButtons]
        self.addAnimationButtons(maxRows=maxRows)
        return buttons  # Buttons managed by play/pause/stop controls

if __name__ == '__main__':
    nonneg, negative, options, otherArgs = categorizeArguments(sys.argv[1:])
    if '-r' not in options:  # Use fixed seed for testing consistency unless
        random.seed(3.14159) # random option specified
    array = SimpleArraySort(values=[int(a) for a in nonneg] if nonneg else None)
    array.runVisualization()
