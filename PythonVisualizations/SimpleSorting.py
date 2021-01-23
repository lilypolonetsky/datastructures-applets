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
    def insertionSort(self):
        self.startAnimations()
        callEnviron = self.createCallEnvironment(self.insertionSortCode)
        n = len(self.list)

        # make an index arrow for the outer loop
        outer = 1
        outerIndex = self.createIndex(outer, "outer", level=2)
        callEnviron |= set(outerIndex)

        # make an index arrow that points to the next cell to check
        innerIndex = self.createIndex(outer, "inner", level=1)
        callEnviron |= set(innerIndex)
        tempVal, label = None, None

        # All items beyond the outer index have not been sorted
        while outer < len(self.list):
            self.highlightCode('outer in range(1, self.__nItems)', callEnviron)

            # Store item at outer index in temporary mark variable
            temp = self.list[outer].val
            self.highlightCode('temp = self.__a[outer]', callEnviron)
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
            self.highlightCode('inner = outer', callEnviron)
            centerX0 = self.cellCenter(inner)[0]
            deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
            if deltaX != 0:
                self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=0.02)

            # Loop down until we find an item less than or equal to the mark
            while inner > 0 and temp < self.list[inner - 1].val:
                self.highlightCode('inner > 0 and temp < self.__a[inner-1]',
                                   callEnviron, wait=0.05)

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
                    self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=0.02) 

            # Delay to show discovery of insertion point for mark
            self.wait(0.1)

            # Copy marked temporary value to insertion point
            self.highlightCode('self.__a[inner] = temp', callEnviron)
            self.assignFromTemp(inner, tempVal, None)

            # Take it out of the cleanup set since it should persist
            callEnviron -= set(tempVal.items)

            # Advance outer loop
            outer += 1
            self.highlightCode('outer in range(1, self.__nItems)', callEnviron)
            self.moveItemsBy(outerIndex, (self.CELL_WIDTH, 0), sleepTime=0.02)
                 
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

    def bubbleSort(self):
        self.startAnimations()
        callEnviron = self.createCallEnvironment(self.bubbleSortCode)
        n = len(self.list)

        # make an index arrow that points to last unsorted element
        self.highlightCode('last in range(self.__nItems-1, 0, -1)', callEnviron)
        last = n - 1
        lastIndex = self.createIndex(last, "last", level=2)
        callEnviron |= set(lastIndex)

        # make an index arrow that points to the next cell to check
        innerIndex = self.createIndex(0, "inner", level=1)
        callEnviron |= set(innerIndex)
        
        # While unsorted cells remain
        while last > 0:
            for inner in range(last):
                # Move inner index arrow to cell to check
                self.highlightCode('inner in range(last)', callEnviron)
                centerX0 = self.cellCenter(inner)[0]
                deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
                if deltaX != 0:
                    self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=0.02)

                # Compare cell value at inner index with the next value
                self.highlightCode('self.__a[inner] > self.__a[inner+1]',
                                   callEnviron, wait=0.2)
                if self.list[inner].val > self.list[inner+1].val:
                    self.highlightCode('self.swap(inner, inner+1)', callEnviron)
                    self.swap(inner, inner+1)

            self.wait(0.01)

            # move last index one lower
            last -= 1
            self.highlightCode('last in range(self.__nItems-1, 0, -1)', 
                               callEnviron)
            self.moveItemsBy(lastIndex, (-self.CELL_WIDTH, 0), sleepTime=0.05)

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

    def selectionSort(self):
        self.startAnimations()
        callEnviron = self.createCallEnvironment(self.selectionSortCode)
        n = len(self.list)      

        # make an index arrow for the outer loop
        outer = 0
        outerIndex = self.createIndex(outer, "outer", level=3)
        callEnviron |= set(outerIndex)
        self.highlightCode('outer in range(self.__nItems-1)', callEnviron)

        # make an index arrow that points to the next cell to check
        innerIndex = self.createIndex(outer+1, "inner", level=1)
        callEnviron |= set(innerIndex)
        minIndex = None

        # All items beyond the outer index have not been sorted
        while outer < len(self.list) - 1:

            min_idx = outer
            self.highlightCode('min = outer', callEnviron)
            if minIndex:
                self.moveItemsBy(
                    minIndex,
                    (self.cellCenter(outer)[0] -
                     self.canvas.coords(minIndex[0])[0], 0), sleepTime=0.02)
            else:
                minIndex = self.createIndex(outer, "min", level=2)
                self.wait(0.1)
                callEnviron |= set(minIndex)
            
            # Find the minimum element in remaining
            # unsorted array
            for inner in range(outer + 1, len(self.list)):

                # Move inner index arrow to point at cell to check
                self.highlightCode('inner in range(outer+1, self.__nItems)',
                                   callEnviron)
                centerX0 = self.cellCenter(inner)[0]
                deltaX = centerX0 - self.canvas.coords(innerIndex[0])[0]
                if deltaX != 0:
                    self.moveItemsBy(innerIndex, (deltaX, 0), sleepTime=0.02)

                self.highlightCode('self.__a[inner] < self.__a[min]',
                                   callEnviron, wait=0.2)
                if self.list[inner].val < self.list[min_idx].val:
                    min_idx = inner
                    self.highlightCode('min = inner', callEnviron)
                    self.moveItemsBy(
                        minIndex,
                        (self.canvas.coords(innerIndex[0])[0] -
                         self.canvas.coords(minIndex[0])[0], 0), sleepTime=0.02)

            self.wait(0.01)

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
            "Delete Rightmost", lambda: self.deleteLast(), maxRows=maxRows,
            helpText='Delete last array item')
        shuffleButton = self.addOperation(
            "Shuffle", lambda: self.shuffle(), maxRows=maxRows,
            helpText='Shuffle position of all items')
        bubbleSortButton = self.addOperation(
            "Bubble Sort", lambda: self.bubbleSort(), maxRows=maxRows,
            helpText='Sort array using bubble sort')
        selectionSortButton = self.addOperation(
            "Selection Sort", lambda: self.selectionSort(), maxRows=maxRows,
            helpText='Sort array using selelction sort')
        insertionSortButton = self.addOperation(
            "Insertion Sort", lambda: self.insertionSort(), maxRows=maxRows,
            helpText='Sort array using insertion sort')
        buttons = [btn for btn in self.opButtons]
        self.addAnimationButtons(maxRows=maxRows)
        return buttons  # Buttons managed by play/pause/stop controls

if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    numArgs = [int(arg) for arg in sys.argv[1:] if arg.isdigit()]
    array = SimpleArraySort(values=numArgs if len(numArgs) > 0 else None)
    array.runVisualization()
