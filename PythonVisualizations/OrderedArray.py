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

class OrderedArray(SortingBase):

    def __init__(self, title="Ordered Array", values=None, **kwargs):
        super().__init__(title=title, **kwargs)

        # Fill in initial array values with random but ordered integers
        # The display items representing these array cells are created later
        if values is None:
            for i in sorted([random.randrange(self.valMax) 
                             for i in range(self.size-1)]):
                self.list.append(drawnValue(i))
        else:
            self.list = [drawnValue(val) for val in sorted(values)]
       
        self.display()
        
        self.buttons = self.makeButtons()

    # ARRAY FUNCTIONALITY

    insertCode = '''
def insert(self, item={val}):
   if self.__nItems >= len(self.__a):
      raise Exception("Array overflow")

   index = self.find(item)
   for j in range(self.__nItems, index, -1):
      self.__a[j] = self.__a[j-1]
         
   self.__a[index] = item
   self.__nItems += 1
'''

    def insert(self, val, code=insertCode, start=True):
        canvasDims = widgetDimensions(self.canvas)
        
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        wait = 0.1

        self.highlightCode('self.__nItems >= len(self.__a)', 
                           callEnviron, wait=wait)
        if len(self.list) >= self.size:
            self.highlightCode(
                'raise Exception("Array overflow")', callEnviron, wait=wait * 2,
                color=self.EXCEPTION_HIGHLIGHT)
            self.cleanUp(callEnviron)
            return

        self.highlightCode('index = self.find(item)', callEnviron)
        index = self.find(val)
        indexIndex = self.createIndex(index, 'index', level=2)
        callEnviron |= set(indexIndex)
        
        self.highlightCode('j in range(self.__nItems, index, -1)', callEnviron,
                           wait=wait)
        #  Move bigger items right
        indexJ = None
        for j in range(len(self.list), index, -1):
            if indexJ is None:
                indexJ = self.createIndex(j, 'j')
                callEnviron |= set(indexJ)

            self.highlightCode('self.__a[j] = self.__a[j-1]', callEnviron)
            self.assignElement(j - 1, j, callEnviron, sleepTime=wait / 10)
            
            self.highlightCode('j in range(self.__nItems, index, -1)', 
                               callEnviron)
            self.moveItemsBy(indexJ, (-self.CELL_WIDTH, 0), 
                             sleepTime=wait / 10)
            
            self.highlightCode('j in range(self.__nItems, index, -1)',
                               callEnviron, wait=wait)
        
        cell = self.createCellValue(self.newValueCoords(), val)
        callEnviron |= set(cell)

        self.highlightCode('self.__a[index] = item', callEnviron, wait=wait)
        
        # Move the new cell into the array
        toPositions = (self.fillCoords(val, self.cellCoords(index)),)
        if len(cell) > 1:
            toPositions += (self.cellCenter(index),)
        self.moveItemsTo(cell, toPositions, sleepTime=wait / 10)

        if index < len(self.list):
            for item in self.list[index].items: # Delete replaced items
                if item is not None:
                    self.canvas.delete(item)
            self.list[index] = drawnValue(val, *cell)
        else:
            self.list.append(drawnValue(val, *cell))
        callEnviron ^= set(cell)  # New item is no longer temporary
        
        # Move nItems pointer
        self.highlightCode('self.__nItems += 1', callEnviron)
        self.moveItemsBy(self.nItems, (self.CELL_WIDTH, 0), sleepTime=wait / 10)

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        return True

    findCode = '''
def find(self, item={val}):
   lo = 0
   hi = self.__nItems-1
   
   while lo <= hi:
      mid = (lo + hi) // 2
      if self.__a[mid] == item:
         return mid
      elif self.__a[mid] < item:
         lo = mid + 1
      else: 
         hi = mid - 1
         
   return lo
'''
    
    def find(self, val, code=findCode):
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))
        wait = 0.1

        self.highlightCode('lo = 0', callEnviron)
        lo = 0
        loIndex = self.createIndex(lo, 'lo', level=1)
        callEnviron |= set(loIndex)
        self.wait(wait)

        self.highlightCode('hi = self.__nItems-1', callEnviron)
        hi = len(self.list) - 1
        hiIndex = self.createIndex(hi, 'hi', level=3)
        callEnviron |= set(hiIndex)
        self.wait(wait)

        midIndex = None
        self.highlightCode('lo <= hi', callEnviron, wait=wait)

        self.highlightCode('lo <= hi', callEnviron, wait=wait)
        while lo <= hi:
            self.highlightCode('mid = (lo + hi) // 2', callEnviron)
            mid = (lo + hi) // 2
            if midIndex:
                midCoords = self.indexCoords(mid, level=2)
                self.moveItemsTo(midIndex, (midCoords, midCoords[:2]),
                                 sleepTime=wait / 10)
            else:
                midIndex = self.createIndex(mid, 'mid', level=2)
                callEnviron |= set(midIndex)
                self.wait(wait)
                
            self.highlightCode('self.__a[mid] == item', callEnviron, wait=wait)
            if self.list[mid].val == val:
                callEnviron.add(self.createFoundCircle(mid))
                self.highlightCode('return mid', callEnviron, wait=wait)
                self.cleanUp(callEnviron)
                return mid

            self.highlightCode('self.__a[mid] < item', callEnviron, wait=wait)
            if self.list[mid].val < val:
                self.highlightCode('lo = mid + 1', callEnviron)
                lo = mid + 1
                loCoords = self.indexCoords(lo, level=1)
                self.moveItemsTo(loIndex, (loCoords, loCoords[:2]),
                                 sleepTime=wait / 10)
            else:
                self.highlightCode('hi = mid - 1', callEnviron)
                hi = mid - 1
                hiCoords = self.indexCoords(hi, level=3)
                self.moveItemsTo(hiIndex, (hiCoords, hiCoords[:2]),
                                 sleepTime=wait / 10)
            self.highlightCode('lo <= hi', callEnviron, wait=wait)
                
        self.highlightCode('return lo', callEnviron)
        self.cleanUp(callEnviron)
        return lo

    searchCode = """
def search(self, item={item}):
   index = self.find(item)
   if index < self.__nItems and self.__a[index] == item:
      return self.__a[index]
"""

    def search(self, item, code=searchCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        wait = 0.1
        
        self.highlightCode('self.find(item)', callEnviron, wait=wait)
        index = self.find(item)
        callEnviron |= set(self.createIndex(index, 'index'))

        result = None
        self.highlightCode('index < self.__nItems', callEnviron, wait=wait)
        if index < len(self.list):
            self.highlightCode('self.__a[index] == item', callEnviron, wait=wait)
            if self.list[index].val == item:
                callEnviron.add(self.createFoundCircle(index))
                self.highlightCode('return self.__a[index]', callEnviron, wait=wait)
                result = self.list[index].val
            else:
                self.highlightCode([], callEnviron)
        else:
            self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        return result

    def randomFill(self):
        callEnviron = self.createCallEnvironment()
        
        # Clear the list so new values can be entered
        self.list = [drawnValue(i) for i in
                     sorted([random.randrange(self.valMax) 
                             for i in range(self.size)])]

        self.display()            
        self.cleanUp(callEnviron)

    deleteCode = '''
def delete(self, item):
   j = self.find(item)
   if j < self.__nItems and self.__a[j] == item:
      self.__nItems -= 1
      for k in range(j, self.__nItems):
         self.__a[k] = self.__a[k+1]
      return True

   return False
'''
    
    def delete(self, val, code=deleteCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        wait = 0.1

        self.highlightCode('self.find(item)', callEnviron, wait=wait)
        j = self.find(val)
        found = j < len(self.list) and self.list[j].val == val
        if found:
            foundCircle = self.createFoundCircle(j)
            callEnviron.add(foundCircle)

        jIndex = self.createIndex(j, 'j')
        callEnviron |= set(jIndex)
        self.highlightCode('j < self.__nItems', callEnviron, wait=wait)

        if j < len(self.list):
            self.highlightCode('self.__a[j] == item', callEnviron, wait=wait)
            if self.list[j].val == val:
                self.wait(wait)  # Pause to show circle
                
                self.highlightCode('self.__nItems -= 1', callEnviron)
                self.moveItemsBy(self.nItems,
                                 (-self.CELL_WIDTH, 0), sleepTime=wait / 10)

                # Slide value rectangle up and off screen
                self.moveItemsOffCanvas(
                    self.list[j].items + (foundCircle,), N, sleepTime=wait / 5)

                #  Move bigger items left
                self.highlightCode('k in range(j, self.__nItems)', callEnviron)
                k = j
                kIndex = self.createIndex(k, 'k', level=2)
                callEnviron |= set(kIndex)
                while k < len(self.list) - 1:

                    self.highlightCode('self.__a[k] = self.__a[k+1]',
                                       callEnviron)
                    self.assignElement(k + 1, k, callEnviron, sleepTime=wait / 10)

                    self.highlightCode('k in range(j, self.__nItems)', 
                                       callEnviron, wait=wait)
                    self.moveItemsBy(kIndex, (self.CELL_WIDTH, 0), 
                                     sleepTime=wait / 10)
                    k += 1
                    
                self.wait(wait) # Pause for final loop comparison
                
                # remove the last item in the list
                n = self.list.pop()
                
                self.highlightCode('return True', callEnviron, wait=wait)
                # delete the associated display objects 
                for item in n.items:
                    if item is not None:
                        self.canvas.delete(item)
                
        if not found:
            self.highlightCode('return False', callEnviron, wait=wait * 2)
        self.cleanUp(callEnviron)
        return found
            
    # Button functions
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
        traverseButton = self.addOperation(
            "Traverse", 
            lambda: self.traverse(start=self.startMode()), maxRows=maxRows,
            helpText='Traverse all array cells once')
        randomFillButton = self.addOperation(
            "Random Fill", lambda: self.randomFill(), maxRows=maxRows,
            helpText='Fill all array cells with random keys')
        deleteRightmostButton = self.addOperation(
            "Delete Rightmost", 
            lambda: self.deleteLast(start=self.startMode()), maxRows=maxRows,
            helpText='Delete last array item')
        self.addAnimationButtons(maxRows=maxRows)
        buttons = [insertButton, searchButton, deleteButton, newButton, 
                   traverseButton, randomFillButton, deleteRightmostButton]
        return buttons  # Buttons managed by play/pause/stop controls
        
    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            result = self.insert(val, start=self.startMode())
            self.setMessage("Value {} inserted".format(val) if result else
                            "Array overflow")
        self.clearArgument()

if __name__ == '__main__':
    nonneg, negative, options, otherArgs = categorizeArguments(sys.argv[1:])
    if '-r' not in options:  # Use fixed seed for testing consistency unless
        random.seed(3.14159) # random option specified

    array = OrderedArray(values=[int(arg) for arg in nonneg] if nonneg else None)
    array.runVisualization()
