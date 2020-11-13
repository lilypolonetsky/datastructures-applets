import random
from tkinter import *

try:
    from drawable import *
    from VisualizationApp import *
    from SortingBase import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *
    from .SortingBase import *

class OrderedArray(SortingBase):

    def __init__(self, title="Ordered Array", **kwargs):
        super().__init__(title=title, **kwargs)

        # Fill in initial array values with random but ordered integers
        # The display items representing these array cells are created later
        for i in sorted([random.randrange(self.valMax) 
                         for i in range(self.size-1)]):
            self.list.append(drawable(i))
        
        self.display()

        self.buttons = self.makeButtons()

    # ARRAY FUNCTIONALITY

    insertCode = '''
def insert(self, item={val}):
   if self.__nItems >= len(self.__a):
      raise Exception("Array overflow")

   j = self.__nItems
   while 0 < j and self.__a[j - 1] > item:
      self.__a[j] = self.__a[j-1]
      j -= 1

   self.__a[j] = item
   self.__nItems += 1
'''

    def insert(self, val, code=insertCode):
        canvasDims = self.widgetDimensions(self.canvas)
        
        self.startAnimations()
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))

        self.highlightCode('self.__nItems >= len(self.__a)', 
                           callEnviron, wait=0.1)
        if len(self.list) >= self.size:
            self.highlightCode(
                'raise Exception("Array overflow")', callEnviron, wait=0.2,
                color=self.EXCEPTION_HIGHLIGHT)
            self.cleanUp(callEnviron)
            return

        self.highlightCode('j = self.__nItems', callEnviron, wait=0.1)
        j = len(self.list)
        indexJ = self.createIndex(j, 'j')
        callEnviron |= set(indexJ)

        startPosition = self.tempCoords(j - 1)
        cell = self.createCellValue(startPosition, val)
        if cell[1] is None:
            cell = cell[:1]
        itemLabel = self.canvas.create_text(
            *self.tempLabelCoords(j - 1, self.VARIABLE_FONT), text='item', 
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        newItem = cell + (itemLabel,)
        callEnviron |= set(newItem)
        
        self.list.append(drawable(None))
        self.highlightCode('0 < j and self.__a[j - 1] > item', callEnviron)
        
        #  Move bigger items right
        while 0 < j and self.list[j-1].val > val:
            self.wait(0.1) # Pause to compare values

            self.highlightCode('self.__a[j] = self.__a[j-1]', callEnviron)
            self.assignElement(j - 1, j, callEnviron, sleepTime=0.01)
            
            self.highlightCode('j -= 1', callEnviron)
            j -= 1
            self.moveItemsBy(indexJ + newItem, (-self.CELL_WIDTH, 0), 
                             sleepTime=0.01)
            
        self.wait(0.1) # Pause for last loop comparison
        
        self.highlightCode('self.__a[j] = item', callEnviron, wait=0.1)
        
        # Move the new cell into the array
        toPositions = (self.fillCoords(val, self.cellCoords(j)),)
        if len(cell) > 1:
            toPositions += (self.cellCenter(j),)
        self.moveItemsTo(cell, toPositions, sleepTime=0.01)

        self.canvas.delete(self.list[j].display_shape) # Delete items covered
        if self.list[j].display_val:   # by the new item
            self.canvas.delete(self.list[j].display_val)
        self.list[j] = drawable(
            val, self.canvas.itemconfigure(cell[0], 'fill')[-1], *cell)
        callEnviron ^= set(cell)  # New item is no longer temporary
        
        # Move nItems pointer
        self.highlightCode('self.__nItems += 1', callEnviron)
        self.moveItemsBy(self.nItems, (self.CELL_WIDTH, 0))
        self.wait(0.1)        

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron) 

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
        self.startAnimations()

        self.highlightCode('lo = 0', callEnviron)
        lo = 0
        loIndex = self.createIndex(lo, 'lo', level=1)
        callEnviron |= set(loIndex)
        self.wait(0.1)

        self.highlightCode('hi = self.__nItems-1', callEnviron)
        hi = len(self.list) - 1
        hiIndex = self.createIndex(hi, 'hi', level=3)
        callEnviron |= set(hiIndex)
        self.wait(0.1)

        midIndex = None

        while lo <= hi:
            self.highlightCode('lo <= hi', callEnviron, wait=0.1)

            self.highlightCode('mid = (lo + hi) // 2', callEnviron)
            mid = (lo + hi) // 2
            if midIndex:
                midCoords = self.indexCoords(mid, level=2)
                self.moveItemsTo(midIndex, (midCoords, midCoords[:2]),
                                 sleepTime=0.01)
            else:
                midIndex = self.createIndex(mid, 'mid', level=2)
                callEnviron |= set(midIndex)
                self.wait(0.1)
                
            self.highlightCode('self.__a[mid] == item', callEnviron, wait=0.1)
            if self.list[mid].val == val:
                callEnviron.add(self.createFoundCircle(mid))
                self.highlightCode('return mid', callEnviron, wait=0.1)
                self.cleanUp(callEnviron)
                return mid

            self.highlightCode('self.__a[mid] < item', callEnviron, wait=0.1)
            if self.list[mid].val < val:
                self.highlightCode('lo = mid + 1', callEnviron)
                lo = mid + 1
                loCoords = self.indexCoords(lo, level=1)
                self.moveItemsTo(loIndex, (loCoords, loCoords[:2]),
                                 sleepTime=0.01)
            else:
                self.highlightCode('hi = mid - 1', callEnviron)
                hi = mid - 1
                hiCoords = self.indexCoords(hi, level=3)
                self.moveItemsTo(hiIndex, (hiCoords, hiCoords[:2]),
                                 sleepTime=0.01)
                
        self.wait(0.1)        # Pause for final loop comparison
        self.highlightCode('return lo', callEnviron)
        self.cleanUp(callEnviron)
        return lo

    searchCode = """
def search(self, item={item}):
   index = self.find(item)
   if index < self.__nItems and self.__a[index] == item:
      return self.__a[index]
"""

    def search(self, item, code=searchCode):
        self.startAnimations()
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))
        self.highlightCode('self.find(item)', callEnviron, wait=0.1)
        nIndex = self.find(item)
        if nIndex < len(self.list) and self.list[nIndex].val == item:
            callEnviron.add(self.createFoundCircle(nIndex))

        result = None
        self.highlightCode('index < self.__nItems', callEnviron, wait=0.1)
        if nIndex < len(self.list):
            self.highlightCode('self.__a[index] == item', callEnviron, wait=0.1)
            if self.list[nIndex].val == item:
                self.highlightCode('return self.__a[index]', callEnviron,
                                   wait=0.1)
                result = self.list[nIndex].val
            else:
                self.highlightCode([], callEnviron)
        else:
            self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        return result

    def randomFill(self):
        callEnviron = self.createCallEnvironment()
        
        # Clear the list so new values can be entered
        self.list = [drawable(i) for i in
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
    
    def delete(self, val, code=deleteCode):
        self.startAnimations()
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))

        self.highlightCode('self.find(item)', callEnviron, wait=0.1)
        j = self.find(val)
        found = j < len(self.list) and self.list[j].val == val
        if found:
            foundCircle = self.createFoundCircle(j)
            callEnviron.add(foundCircle)

        jIndex = self.createIndex(j, 'j')
        callEnviron |= set(jIndex)
        self.highlightCode('j < self.__nItems', callEnviron, wait=0.1)

        if j < len(self.list):
            self.highlightCode('self.__a[j] == item', callEnviron, wait=0.1)
            if self.list[j].val == val:
                self.wait(0.2)  # Pause to show circle
                
                self.highlightCode('self.__nItems -= 1', callEnviron)
                self.moveItemsBy(self.nItems,
                                 (-self.CELL_SIZE, 0), sleepTime=0.01)

                # Slide value rectangle up and off screen
                items = (self.list[j].display_shape, foundCircle)
                if self.list[j].display_val:
                    items += (self.list[j].display_val,)
                self.moveItemsOffCanvas(items, N, sleepTime=0.02)

                #  Move bigger items left
                self.highlightCode('k in range(j, self.__nItems)', callEnviron)
                k = j
                kIndex = self.createIndex(k, 'k', level=2)
                callEnviron |= set(kIndex)
                while k < len(self.list) - 1:

                    self.highlightCode('self.__a[k] = self.__a[k+1]',
                                       callEnviron)
                    self.assignElement(k + 1, k, callEnviron, sleepTime=0.01)

                    self.highlightCode('k in range(j, self.__nItems)', 
                                       callEnviron, wait=0.1)
                    self.moveItemsBy(kIndex, (self.CELL_WIDTH, 0), 
                                     sleepTime=0.01)
                    k += 1
                    
                self.wait(0.1) # Pause for final loop comparison
                
                # remove the last item in the list
                n = self.list.pop()
                # delete the associated display objects
                self.canvas.delete(n.display_shape)
                if n.display_val:
                    self.canvas.delete(n.display_val)
                    
                self.highlightCode('return True', callEnviron, wait=0.)
                
        if not found:
            self.highlightCode('return False', callEnviron, wait=0.2)
        self.cleanUp(callEnviron)
        return found
            
    # Button functions
    def makeButtons(self, maxRows=3):
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
            "Traverse", lambda: self.traverse(), maxRows=maxRows,
            helpText='Traverse all array cells once')
        randomFillButton = self.addOperation(
            "Random Fill", lambda: self.randomFill(), maxRows=maxRows,
            helpText='Fill all array cells with random keys')
        deleteRightmostButton = self.addOperation(
            "Delete Rightmost", lambda: self.deleteLast(), maxRows=maxRows,
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
            result = self.insert(val)
            self.setMessage("Value {} inserted".format(val) if result else
                            "Array overflow")
        self.clearArgument()

if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    array = OrderedArray()

    array.runVisualization()

