import time
from tkinter import *
import random 

try:
    from drawnValue import *
    from coordinates import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .coordinates import *
    from .VisualizationApp import *

V = vector

class Heap(VisualizationApp):
    nextColor = 0
    MAX_SIZE = 31
    CELL_WIDTH = 25
    CELL_HEIGHT = 12
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    ARRAY_X0 = 80
    ARRAY_Y0 = 18

    def __init__(self, size=2, valMax=99, title="Heap", **kwargs):
        super().__init__(title=title, **kwargs)
        self.size = size
        self.title = title
        self.list = []
        self.nItems = 0
        self.valMax = valMax
        self.arrayCopyDelta = (2 * self.CELL_WIDTH, 0)
        self.siftDelta = (3 * self.CELL_WIDTH, 0)
        self.buttons = self.makeButtons()
        self.display()

    def __str__(self):
        return str(self.list)
    
    # Create index arrow to point at an array cell with an optional name label
    def createArrayIndex(self, index, name='nItems', level=1, color=None):
        if color is None: color = self.VARIABLE_COLOR
        return self.drawArrow(
            *self.arrayIndexCoords(index, level), color, self.SMALL_FONT, name)

    def arrayIndexCoords(self, index, level=1):
        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        level_spacing = abs(self.SMALL_FONT[1])
        if level > 0:
            x0 = self.ARRAY_X0 - self.CELL_WIDTH * 0.8 - level * level_spacing
            x1 = self.ARRAY_X0 - self.CELL_WIDTH * 0.3
        else:
            x0 = self.ARRAY_X0 + 1.8 * self.CELL_WIDTH - level * level_spacing
            x1 = self.ARRAY_X0 + self.CELL_WIDTH * 1.3
        y0 = y1 = cell_center[1]
        return x0, y0, x1, y1
    
    # draw the actual arrow 
    def drawArrow(
            self, x0, y0, x1, y1, color, font, name=None):
        arrow = self.canvas.create_line(
            x0, y0, x1, y1, arrow="last", fill=color)
        leftPointing = x1 < x0
        separation = 3 if leftPointing else -3
        if name:
            label = self.canvas.create_text(
                x0 + separation, y0, text=name, anchor=W if leftPointing else E,
                font=font, fill=color)

        return (arrow, label) if name else (arrow,) 

    # HEAP FUNCTIONALITY

    insertCode = '''
def insert(self, item={val}):
   if self.isFull():
      self._growHeap()
   self._arr[self._nItems] = item
   self._nItems += 1
   self._siftUp(self._nItems - 1)
'''
    
    def insert(self, val, code=insertCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        
        #If array needs to grow, add cells:
        self.highlightCode('self.isFull()', callEnviron, wait=wait)
        if self.size <= len(self.list):
            self.highlightCode('self._growHeap()', callEnviron)
            self._growHeap()

        # Create new item near top left corner
        startPosition = V(self.cellCoords(-1.4)) - V(self.siftDelta * 2)
        cellPair = self.createCellValue(startPosition, val)
        callEnviron |= set(cellPair)

        # Place it in the array
        self.highlightCode('self._arr[self._nItems] = item', callEnviron)
        toPositions = (self.cellCoords(self.nItems), 
                       self.cellCenter(self.nItems))
        self.moveItemsTo(cellPair, toPositions, sleepTime=wait / 10)
    
        # add a new drawnValue with the new value, color, and display objects
        d = drawnValue(val, *cellPair)
        if self.nItems == len(self.list):
            self.list.append(d)    #store item at the end of the list
            self.nItems = len(self.list)
        else:
            self.list[self.nItems] = d
            self.nItems += 1
        callEnviron -= set(cellPair)
        
        # Move nItems index to one past inserted item
        self.highlightCode('self._nItems += 1', callEnviron)
        coords = self.arrayIndexCoords(self.nItems)
        self.moveItemsTo(self.nItemsIndex, (coords, coords[:2]), 
                         sleepTime=wait / 10)
            
        self.highlightCode('self._siftUp(self._nItems - 1)', callEnviron)
        self.siftUp(self.nItems - 1)  # Sift up new item
                    
        # finish the animation
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    growHeapCode = '''
def _growHeap(self):
   current = self._arr
   self._arr = [None] * 2 * len(self._arr)
   for i in range(self._nItems):
      self._arr[i] = current[i]
'''
    
    def _growHeap(self, code=growHeapCode):
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code)

        self.highlightCode('current = self._arr', callEnviron)
        callEnviron.add(self.canvas.create_text(
            *self.cellCenter(-1), text='_arr',
            anchor=S, font=self.SMALL_FONT, fill=self.VARIABLE_COLOR))
        callEnviron.add(self.canvas.create_text(
            *(V(self.cellCenter(-1)) + V(self.arrayCopyDelta)), text='current',
            anchor=S, font=self.SMALL_FONT, fill=self.VARIABLE_COLOR))
        cells = self.canvas.find_withtag("arrayCell")
        cells_and_values = list(cells)
        for v in self.list: # move current array cells and values over
            cells_and_values.extend(v.items)
        self.moveItemsBy(cells_and_values, self.arrayCopyDelta,
                         sleepTime=wait / 10)
            
        # Grow the the array 
        self.highlightCode('self._arr = [None] * 2 * len(self._arr)',
                           callEnviron)
        for i in range(self.size): 
            callEnviron.add(self.createArrayCell(i)) # Temporary
            if i + self.size < self.MAX_SIZE:
                self.createArrayCell(i + self.size) # Lasting
        self.size = min(self.size * 2, self.MAX_SIZE)
            
        #copying the values back into the larger array 
        self.highlightCode('i in range(self._nItems)', callEnviron,
                           wait=wait / 5)
        for v in self.list:
            self.highlightCode('self._arr[i] = current[i]', callEnviron)
            newValue = tuple(self.copyCanvasItem(i) for i in v.items)
            callEnviron |= set(newValue)
            self.moveItemsBy(newValue, V(self.arrayCopyDelta) * -1,
                             sleepTime=wait / 10)
            self.highlightCode('i in range(self._nItems)', callEnviron,
                               wait=wait / 5)

        # Move old cells back to original positions in one step
        # These are lasting and overlap the temporary ones just created
        self.moveItemsBy(cells_and_values, V(self.arrayCopyDelta) * -1, steps=1)
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    siftUpCode = '''
def _siftUp(self, i={i}):
   if i <= 0:
      return
   item = self._arr[i]
   itemkey = self._key(item)
   while 0 < i:
      parent = self.parent(i)
      if self._key(self._arr[parent]) < itemkey:
         self._arr[i] = self._arr[parent]
         i = parent
      else:
         break
   self._arr[i] = item
'''
    
    def siftUp(self, i, code=siftUpCode):
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))

        iIndex = self.createArrayIndex(i, name='i', level=-1)
        callEnviron |= set(iIndex)
        self.highlightCode('i <= 0', callEnviron, wait=wait)
        if i <= 0:
            self.highlightCode('return', callEnviron)
            self.cleanUp(callEnviron)
            return
        
        self.highlightCode('item = self._arr[i]', callEnviron, wait=wait)
        upItem = self.list[i].copy()
        copyItem = tuple(self.copyCanvasItem(j) for j in upItem.items)
        callEnviron |= set(copyItem)
        self.moveItemsBy(copyItem, self.siftDelta, sleepTime=wait / 10)

        self.highlightCode('itemkey = self._key(item)', callEnviron, wait=wait)
        copyItemCenter = self.canvas.coords(copyItem[1])
        itemLabel = self.canvas.create_text(
            *(V(copyItemCenter) - V(0, self.CELL_HEIGHT)), text='itemkey',
            font=self.SMALL_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(itemLabel)

        parentIndex = None
        self.highlightCode('0 < i', callEnviron, wait=wait)
        while 0 < i:
            self.highlightCode('parent = self.parent(i)', callEnviron)
            parent = (i - 1) // 2
            if parentIndex is None:
                parentIndex = self.createArrayIndex(parent, name='parent')
                callEnviron |= set(parentIndex)
            else:
                parentCoords = self.arrayIndexCoords(parent)
                self.moveItemsTo(parentIndex, (parentCoords, parentCoords[:2]),
                                 sleepTime=wait / 10)

            self.highlightCode('self._key(self._arr[parent]) < itemkey',
                               callEnviron, wait=wait)
            if self.list[parent] < upItem: # if parent less than item sifting up
                self.highlightCode('self._arr[i] = self._arr[parent]',
                                   callEnviron)
                # move a copy of the parent down to node i
                copyVal = tuple(
                    self.copyCanvasItem(j) for j in self.list[parent].items)
                callEnviron |= set(copyVal)
                self.moveItemsOnCurve(
                    copyVal, (self.cellCoords(i), self.cellCenter(i)),
                    startAngle=-90 * 11 / (10 + i - parent),
                    sleepTime=wait / 10)
                for item in self.list[i].items:
                    self.canvas.delete(item)
                self.list[i].val = self.list[parent].val
                self.list[i].items = copyVal
                callEnviron -= set(copyVal)
                
                # Advance i to parent, move original item along with i Index
                self.highlightCode('i = parent', callEnviron)
                delta = self.cellCenter(parent)[1] - self.cellCenter(i)[1]
                self.moveItemsBy(iIndex + copyItem + (itemLabel,), (0, delta),
                                 sleepTime=wait / 10)
                i = parent
            else:
                self.highlightCode('break', callEnviron, wait=wait)
                break

            self.highlightCode('0 < i', callEnviron, wait=wait)
            
        # Move copied item into appropriate location
        self.highlightCode('self._arr[i] = item', callEnviron)
        self.moveItemsBy(copyItem, V(self.siftDelta) * -1,
                         sleepTime=wait / 10)
        for item in self.list[i].items:
            self.canvas.delete(item)
        self.list[i].val, self.list[i].items = upItem.val, copyItem
        callEnviron -= set(copyItem)

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    _siftDownCode = '''
def _siftDown(self, i={i}):
   firstleaf = len(self) // 2
   if i >= firstleaf:
      return
   item = self._arr[i]
   itemkey = self._key(item)
   while i < firstleaf:
      left, right = self.leftChild(i), self.rightChild(i)
      maxi = left
      if (right < len(self) and
          self._key(self._arr[left]) < self._key(self._arr[right])):
         maxi = right
      if (itemkey < self._key(self._arr[maxi])):
         self._arr[i] = self._arr[maxi]
         i = maxi
      else:
         break
   self._arr[i] = item
'''
        
    def _siftDown(self, i=0, code=_siftDownCode):
        'Sift item i down to preserve heap condition'
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))
        
        iIndex = self.createArrayIndex(i, name='i', level=-1)
        callEnviron |= set(iIndex)

        self.highlightCode('firstleaf = len(self) // 2', callEnviron, wait=wait)
        firstleaf = self.nItems // 2 # Get index of first leaf
        leafIndex = self.createArrayIndex(firstleaf, name='firstleaf')
        callEnviron |= set(leafIndex)
        
        self.highlightCode('i >= firstleaf', callEnviron, wait=wait)
        if i >= firstleaf: # If item i is at or below leaf level, nothing to do
            self.highlightCode('return', callEnviron)
            self.cleanUp(callEnviron)
            return      

        self.highlightCode('item = self._arr[i]', callEnviron, wait=wait)
        downItem = self.list[i].copy()   # Store item at cell i
        copyItem = tuple(self.copyCanvasItem(j) for j in downItem.items)
        callEnviron |= set(copyItem)
        self.moveItemsBy(copyItem, self.siftDelta, sleepTime=wait / 10)

        self.highlightCode('itemkey = self._key(item)', callEnviron, wait=wait)
        copyItemCenter = self.canvas.coords(copyItem[1])
        itemLabel = self.canvas.create_text(
            *(V(copyItemCenter) - V(0, self.CELL_HEIGHT)), text='itemkey',
            font=self.SMALL_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(itemLabel)
        
        leftIndex, rightIndex, maxIndex = None, None, None
        itemkey = downItem.val # key
        
        self.highlightCode('i < firstleaf', callEnviron, wait=wait)
        while i < firstleaf:  # While i above leaf level, find children

            self.highlightCode(
                'left, right = self.leftChild(i), self.rightChild(i)',
                callEnviron)
            left, right = i + i + 1, i + i + 2
            if leftIndex is None:
                leftIndex = self.createArrayIndex(left, 'left', level=-1)
                rightIndex = self.createArrayIndex(right, 'right', level=-1)
                callEnviron |= set(leftIndex + rightIndex)
            else:
                leftCoords = self.arrayIndexCoords(left, level=-1)
                rightCoords = self.arrayIndexCoords(right, level=-1)
                self.moveItemsTo(
                    leftIndex + rightIndex, 
                    (leftCoords, leftCoords[:2], rightCoords, rightCoords[:2]),
                    sleepTime=wait / 10)

            self.highlightCode('maxi = left', callEnviron)
            maxi = left        # Assume left child has larger key
            if maxIndex is None:
                maxIndex = self.createArrayIndex(maxi, name='maxi', level=-4)
                callEnviron |= set(maxIndex)
            else:
                maxCoords = self.arrayIndexCoords(maxi, level=-4)
                self.moveItemsTo(
                    maxIndex, (maxCoords, maxCoords[:2]), sleepTime=wait / 10)
           
            self.highlightCode('right < len(self)', callEnviron, wait=wait)
            if right < self.nItems:
                self.highlightCode(
                    'self._key(self._arr[left]) < self._key(self._arr[right])',
                    callEnviron, wait=wait)
            if (right < self.nItems and # If both children are present, and
                self.list[left].val < # left child has smaller key
                self.list[right].val): 
                self.highlightCode('maxi = right', callEnviron)
                maxi = right    # then use right child
                maxCoords = self.arrayIndexCoords(right, level=-4)
                self.moveItemsTo(
                    maxIndex, (maxCoords, maxCoords[:2]), sleepTime=wait / 10)

            self.highlightCode('itemkey < self._key(self._arr[maxi])',
                               callEnviron, wait=wait)
            if (itemkey < self.list[maxi].val): # If item i less than max,
                # move a copy of the max child up to node i
                self.highlightCode('self._arr[i] = self._arr[maxi]',
                                   callEnviron)
                copyVal = tuple(
                    self.copyCanvasItem(j) for j in self.list[maxi].items)
                callEnviron |= set(copyVal)
                self.moveItemsOnCurve(
                    copyVal, (self.cellCoords(i), self.cellCenter(i)),
                    sleepTime=wait / 10)
                for item in self.list[i].items:
                    self.canvas.delete(item)
                self.list[i].val = self.list[maxi].val
                self.list[i].items = copyVal
                callEnviron -= set(copyVal)
                
                self.highlightCode('i = maxi', callEnviron)
                # Advance i to max child, move original item along with i Index
                delta = self.cellCenter(maxi)[1] - self.cellCenter(i)[1]
                self.moveItemsBy(iIndex + copyItem + (itemLabel,), (0, delta), 
                                 sleepTime=wait / 10)
                i = maxi
                 
            else:              # If item i's key is greater than or equal
                self.highlightCode('break', callEnviron, wait=wait)
                break          # to larger child, then found position
            
            self.highlightCode('i < firstleaf', callEnviron, wait=wait)

        # Move copied item into appropriate location
        self.highlightCode('self._arr[i] = item', callEnviron, wait=wait)
        self.moveItemsBy(copyItem, V(self.siftDelta) * -1,
                         sleepTime=wait / 10)
        for item in self.list[i].items:
            self.canvas.delete(item)
        self.list[i].val, self.list[i].items = downItem.val, copyItem
        callEnviron -= set(copyItem)

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    siftDownCode = '''
def siftDown(array, j={j}, N=None, key=identity):
   if N is None:
      N = len(array)
   firstleaf = N // 2
   if j >= firstleaf:
      return
   item = array[j]
   itemkey = key(item)
   while j < firstleaf:
      left, right = j + j + 1, j + j + 2
      maxi = left
      if (right < N and
          key(array[left]) < key(array[right])):
         maxi = right
      if (itemkey < key(array[maxi])):
         array[j] = array[maxi]
         j = maxi
      else:
         break
   array[j] = item
'''
        
    def siftDown(self, j=0, code=siftDownCode):
        'Sift item j down to preserve heap condition'
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))
        
        jIndex = self.createArrayIndex(j, name='j', level=-1)
        callEnviron |= set(jIndex)

        self.highlightCode('N is None', callEnviron, wait=wait)
        self.highlightCode('N = len(array)', callEnviron, wait=wait)
        N = len(self.list)
        NIndex = self.createArrayIndex(N, name='N', level=2)
        callEnviron |= set(NIndex)

        self.highlightCode('firstleaf = N // 2', callEnviron, wait=wait)
        firstleaf = len(self.list) // 2 # Get index of first leaf
        leafIndex = self.createArrayIndex(firstleaf, name='firstleaf')
        callEnviron |= set(leafIndex)
        
        self.highlightCode('j >= firstleaf', callEnviron, wait=wait)
        if j >= firstleaf: # If item j is at or below leaf level, nothing to do
            self.highlightCode('return', callEnviron)
            self.cleanUp(callEnviron)
            return      

        self.highlightCode('item = array[j]', callEnviron, wait=wait)
        downItem = self.list[j].copy()   # Store item at cell j
        copyItem = tuple(self.copyCanvasItem(i) for i in downItem.items)
        callEnviron |= set(copyItem)
        self.moveItemsBy(copyItem, self.siftDelta, sleepTime=wait / 10)

        self.highlightCode('itemkey = key(item)', callEnviron, wait=wait)
        copyItemCenter = self.canvas.coords(copyItem[1])
        itemLabel = self.canvas.create_text(
            *(V(copyItemCenter) - V(0, self.CELL_HEIGHT)), text='itemkey',
            font=self.SMALL_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(itemLabel)
        
        leftIndex, rightIndex, maxIndex = None, None, None
        itemkey = downItem.val # key
        
        self.highlightCode('j < firstleaf', callEnviron, wait=wait)
        while j < firstleaf:  # While j above leaf level, find children

            self.highlightCode(
                'left, right = j + j + 1, j + j + 2', callEnviron)
            left, right = j + j + 1, j + j + 2
            if leftIndex is None:
                leftIndex = self.createArrayIndex(left, 'left', level=-1)
                rightIndex = self.createArrayIndex(right, 'right', level=-1)
                callEnviron |= set(leftIndex + rightIndex)
            else:
                leftCoords = self.arrayIndexCoords(left, level=-1)
                rightCoords = self.arrayIndexCoords(right, level=-1)
                self.moveItemsTo(
                    leftIndex + rightIndex, 
                    (leftCoords, leftCoords[:2], rightCoords, rightCoords[:2]),
                    sleepTime=wait / 10)

            self.highlightCode('maxi = left', callEnviron)
            maxi = left        # Assume left child has larger key
            if maxIndex is None:
                maxIndex = self.createArrayIndex(maxi, name='maxi', level=-4)
                callEnviron |= set(maxIndex)
            else:
                maxCoords = self.arrayIndexCoords(maxi, level=-4)
                self.moveItemsTo(
                    maxIndex, (maxCoords, maxCoords[:2]), sleepTime=wait / 10)
           
            self.highlightCode('right < N', callEnviron, wait=wait)
            if right < len(self.list):
                self.highlightCode('key(array[left]) < key(array[right])',
                                   callEnviron, wait=wait)
            if (right < len(self.list) and # If both children are present, and
                self.list[left].val < # left child has smaller key
                self.list[right].val): 
                self.highlightCode('maxi = right', callEnviron)
                maxi = right    # then use right child
                maxCoords = self.arrayIndexCoords(right, level=-4)
                self.moveItemsTo(
                    maxIndex, (maxCoords, maxCoords[:2]), sleepTime=wait / 10)

            self.highlightCode('itemkey < key(array[maxi])',
                               callEnviron, wait=wait)
            if (itemkey < self.list[maxi].val): # If item j less than max,
                # move a copy of the max child up to node j
                self.highlightCode('array[j] = array[maxi]',
                                   callEnviron)
                copyVal = tuple(
                    self.copyCanvasItem(i) for i in self.list[maxi].items)
                callEnviron |= set(copyVal)
                self.moveItemsOnCurve(
                    copyVal, (self.cellCoords(j), self.cellCenter(j)),
                    sleepTime=wait / 10)
                for item in self.list[j].items:
                    self.canvas.delete(item)
                self.list[j].val = self.list[maxi].val
                self.list[j].items = copyVal
                callEnviron -= set(copyVal)
                
                self.highlightCode('j = maxi', callEnviron)
                # Advance j to max child, move original item along with j Index
                delta = self.cellCenter(maxi)[1] - self.cellCenter(j)[1]
                self.moveItemsBy(jIndex + copyItem + (itemLabel,), (0, delta), 
                                 sleepTime=wait / 10)
                j = maxi
                 
            else:              # If item j's key is greater than or equal
                self.highlightCode('break', callEnviron, wait=wait)
                break          # to larger child, then found position
            
            self.highlightCode('j < firstleaf', callEnviron, wait=wait)

        # Move copied item into appropriate location
        self.highlightCode('array[j] = item', callEnviron, wait=wait)
        self.moveItemsBy(copyItem, V(self.siftDelta) * -1,
                         sleepTime=wait / 10)
        for item in self.list[j].items:
            self.canvas.delete(item)
        self.list[j].val, self.list[j].items = downItem.val, copyItem
        callEnviron -= set(copyItem)

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    heapifyCode = '''
def heapify(array, N=None, key=identity):
   if N is None:
      N = len(array)
   heapLo = N // 2
   while heapLo > 0:
      heapLo -= 1
      siftDown(array, heapLo, N, key)
'''
    
    def heapify(self, N = None, code=heapifyCode, start=True):
        'Organize an array of N items to satisfy the heap condition'
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code,
                                                 startAnimations=start)
        self.highlightCode('N is None', callEnviron, wait=wait)
        if N is None:            # If N is not supplied,
            N = len(self.list)   # then use number of items in list
            self.highlightCode('N = len(array)', callEnviron, wait=wait)
            NIndex = self.createArrayIndex(N, name='N', level=2)
            callEnviron |= set(NIndex)
            
        self.highlightCode('heapLo = N // 2', callEnviron, wait=wait)
        heapLo = N // 2          # The heap lies in the range [heapLo, N)
        heapLoIndex = self.createArrayIndex(heapLo, name='heapLo')
        callEnviron |= set(heapLoIndex)
        
        self.highlightCode('heapLo > 0', callEnviron, wait=wait)
        localVars = NIndex + heapLoIndex
        while heapLo > 0:        # Heapify until the entire array is a heap
            self.highlightCode('heapLo -= 1', callEnviron, wait=wait)
            heapLo -= 1           # Decrement heap's lower boundary
            heapLoCoords = self.arrayIndexCoords(heapLo)
            self.moveItemsTo(heapLoIndex, (heapLoCoords, heapLoCoords[:2]),
                             sleepTime=wait / 10)
            
            self.highlightCode('siftDown(array, heapLo, N, key)',
                               callEnviron)
            colors = self.fadeNonLocalItems(localVars)
            self.siftDown(heapLo) # Sift down item at heapLo
            self.restoreLocalItems(localVars) # colors TBD

            self.highlightCode('heapLo > 0', callEnviron, wait=wait)

        # Adjust nItems pointer to indicate heap condition is satisfied
        self.nItems = N
        coords = self.arrayIndexCoords(self.nItems)
        self.moveItemsTo(self.nItemsIndex, (coords, coords[:2]),
                         sleepTime=wait / 10)
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
              
    # lets user input an int argument that determines max size of the Heap
    def newArray(self):
        #gets rid of old elements in the list
        del self.list[:]
        self.size = 2
        self.display()

    peekCode = '''
def peek(self):
   return None if self.isEmpty() else self._arr[0]
'''
    
    def peek(self, code=peekCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)

        self.highlightCode('self.isEmpty()', callEnviron, wait=wait)
        
        # draw output box
        outBoxCoords = self.outputBoxCoords()
        outBoxCenter = V(V(outBoxCoords[:2]) + V(outBoxCoords[2:])) / 2 # TBD //
        outputBox = self.canvas.create_rectangle(
            *outBoxCoords, fill=self.OPERATIONS_BG)
        callEnviron.add(outputBox)

        if self.nItems > 0:
            self.highlightCode(['return', 'self._arr[0]'], callEnviron)
            # create the value to move to output box
            valueOutput = self.copyCanvasItem(self.list[0].items[1])
            callEnviron.add(valueOutput)
            self.moveItemsTo(valueOutput, outBoxCenter, sleepTime=wait / 10)
            # make the value 25% smaller
            newFont = (self.VALUE_FONT[0], self.VALUE_FONT[1] * 3 // 4)
            self.canvas.itemconfig(valueOutput, font=newFont)
            root = self.list[0].val

        else:
            self.highlightCode('return None', callEnviron)
            root = None
            
        # finish animation
        self.cleanUp(callEnviron)
        return root

    removeCode = '''
def remove(self):
   if self.isEmpty():
      raise Exception("Heap underflow")
   root = self._arr[0]
   self._nItems -= 1
   self._arr[0] = self._arr[self._nItems]
   self._siftDown(0)
   return root
'''
    
    def removeMax(self, code=removeCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)

        self.highlightCode('self.isEmpty()', callEnviron, wait=wait)
        if self.nItems <= 0:
            self.highlightCode(
                'raise Exception("Heap underflow")', callEnviron, wait=wait,
                color=self.EXCEPTION_HIGHLIGHT)
            self.cleanUp(callEnviron)
            return
            
        # Copy first element from array/root of heap
        self.highlightCode('root = self._arr[0]', callEnviron, wait=wait)
        root = self.list[0]
        outBoxCoords = self.outputBoxCoords()
        outBoxCenter = V(V(outBoxCoords[:2]) + V(outBoxCoords[2:])) / 2 # TBD //
        callEnviron.add(self.canvas.create_text(
            *(V(outBoxCenter) - V(0, outBoxCoords[3] - outBoxCoords[1])),
            text='root', font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR))
        self.moveItemsTo(
            root.items, (outBoxCoords, outBoxCenter), sleepTime=wait / 10)

        self.highlightCode('self._nItems -= 1', callEnviron)
        last = self.list[self.nItems - 1]
        self.nItems = min(self.nItems - 1, len(self.list) - 1)
        lastCoords = self.arrayIndexCoords(self.nItems)
        self.moveItemsTo(self.nItemsIndex, (lastCoords, lastCoords[:2]),
                         sleepTime=wait / 10)

        itemsToMove = last.items if self.nItems > 0 else []
        self.highlightCode('self._arr[0] = self._arr[self._nItems]',
                           callEnviron, wait=0 if itemsToMove else wait)
        if itemsToMove:
            cellCoords = self.cellCoords(0)
            cellCenter = self.cellCenter(0)
            startAngle = 90 * 50 / (50 + abs(cellCoords[1] - lastCoords[1]))
            self.moveItemsOnCurve(
                last.items, (cellCoords, cellCenter), startAngle=startAngle,
                sleepTime=wait / 10)
            self.list[0] = self.list.pop()
            callEnviron |= set(root.items)
        else:
            self.list.pop()
        
        self.highlightCode('self._siftDown(0)', callEnviron)
        self._siftDown(0)
        
        # Finish animation
        self.highlightCode('return root', callEnviron, wait=wait)
        self.cleanUp(callEnviron)
        return root.val
    
    def randomFill(self, val):
        self.size = max(self.size, val)
        
        self.list = [drawnValue(random.randrange(self.valMax + 1))
                     for i in range(val)]
        self.nItems = 1
        self.display()

    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        return V(
            self.ARRAY_X0, self.ARRAY_Y0, self.ARRAY_X0, self.ARRAY_Y0) + V(
                0, self.CELL_HEIGHT * cell_index,
                self.CELL_WIDTH - self.CELL_BORDER,
                self.CELL_HEIGHT * (cell_index + 1) - self.CELL_BORDER)

    def cellCenter(self, index):  # Center point for array cell at index
        half_cell_x = (self.CELL_WIDTH - self.CELL_BORDER) // 2
        half_cell_y = (self.CELL_HEIGHT - self.CELL_BORDER) // 2
        return V(self.cellCoords(index)) + V(half_cell_x, half_cell_y)

    def arrayCellCoords(self, index):
        cell_coords = self.cellCoords(index)
        half_border = self.CELL_BORDER // 2
        other_half = self.CELL_BORDER - half_border
        return V(cell_coords) + V(
            -half_border, -half_border, other_half, other_half)
        
    def createArrayCell(self, index):  # Create a box representing an array cell
        rect = self.canvas.create_rectangle(
            self.arrayCellCoords(index), fill=None, tags= "arrayCell",
            outline=self.CELL_BORDER_COLOR, width=self.CELL_BORDER)
        self.canvas.lower(rect)

        return rect

    def createCellValue(self, indexOrCoords, key, color=None):
        """Create new canvas items to represent a cell value.  A square
        is created filled with a particular color with an text key centered
        inside.  The position of the cell can either be an integer index in
        the Array or the bounding box coordinates of the square.  If color
        is not supplied, the next color in the palette is used.
        An event handler is set up to update the VisualizationApp argument
        with the cell's value if clicked with any button.
        Returns the tuple, (square, text), of canvas items
        """
        # Determine position and color of cell
        if isinstance(indexOrCoords, (int, float)):
            rectPos = self.cellCoords(indexOrCoords)
            valPos = self.cellCenter(indexOrCoords)
        else:
            rectPos = indexOrCoords
            valPos = divide_vector(add_vector(rectPos[:2], rectPos[2:]), 2)

        if color is None:
            # Take the next color from the palette
            color = drawnValue.palette[Heap.nextColor]
            Heap.nextColor = (Heap.nextColor + 1) % len(drawnValue.palette)
        cell_rect = self.canvas.create_rectangle(
            *rectPos, fill=color, outline='', width=0)
        cell_val = self.canvas.create_text(
            *valPos, text=str(key), font=self.SMALL_FONT, fill=self.VALUE_COLOR)
        handler = lambda e: self.setArgument(str(key))
        for item in (cell_rect, cell_val):
            self.canvas.tag_bind(item, '<Button>', handler)

        return cell_rect, cell_val

    def outputBoxCoords(self, padding=20):
        canvasDimensions = self.widgetDimensions(self.canvas)
        return (self.ARRAY_X0 + self.CELL_WIDTH + padding,
                canvasDimensions[1] - self.CELL_HEIGHT * 2 - padding,
                self.ARRAY_X0 + self.CELL_WIDTH*2 + padding,
                canvasDimensions[1] - self.CELL_HEIGHT - padding)
        
    def display(self):
        self.canvas.delete("all")

        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)

        #make a new arrow pointing to the top of the Heap
        self.nItemsIndex = self.createArrayIndex(self.nItems, color='black')

        # go through each drawnValue in the list
        for i, n in enumerate(self.list):
            # create display objects for the associated drawnValues
            n.items = self.createCellValue(i, n.val)

    def fixPositions(self):  # Move canvas display items to exact cell coords
        for i, dValue in enumerate(self.list):
            self.canvas.coords(dValue.items[0], *self.cellCoords(i))
            self.canvas.coords(dValue.items[1], *self.cellCenter(i))
            
        # Restore array cell borders in case they were moved
        for i, item in enumerate(self.canvas.find_withtag('arrayCell')):
            if i >= self.size: # Delete any extra cell borders
                self.canvas.delete(item)
            else:
                self.canvas.coords(item, *self.arrayCellCoords(i))
            
        # Restore nItems index to one past end of array
        coords = self.arrayIndexCoords(self.nItems)
        self.canvas.coords(self.nItemsIndex[0], coords)
        self.canvas.coords(self.nItemsIndex[1], coords[:2])

    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        if ((len(args) == 0 or args[0] is None) and # When cleaning up entire 
            kwargs.get('callEnviron', None) is None): # call stack,
            self.fixPositions()       # restore positions of all structures

    def makeButtons(self, maxRows=3):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd, argHelpText=['item'],
            helpText='Insert a new item in the heap')
        randomFillButton = self.addOperation(
            "Random Fill ", lambda: self.clickRandomFill(), numArguments=1,
            validationCmd=vcmd, argHelpText=['number of items'],
            helpText='Fill array with N random items')
        newHeapButton = self.addOperation(
            "New", lambda: self.clickNewArray(), maxRows=maxRows,
            helpText='Create empty heap')
        self.peekButton = self.addOperation(
            "Peek", lambda: self.clickPeek(), maxRows=maxRows,
            helpText='Peek at maximum item')
        self.removeMaxButton = self.addOperation(
            "Remove Max", lambda: self.clickRemoveMax(), maxRows=maxRows,
            helpText='Remove maximum item from heap')
        self.heapifyButton = self.addOperation(
            "Heapify", lambda: self.clickHeapify(), maxRows=maxRows,
            helpText='Organize items into heap')
        self.addAnimationButtons(maxRows=maxRows)
        self.enableButtons()
        return [self.insertButton, randomFillButton,
                newHeapButton, self.peekButton, self.removeMaxButton, 
                self.heapifyButton]

    def enableButtons(self, enable=True, **kwargs):
        super().enableButtons(enable, **kwargs)
        self.argumentChanged()
        isHeap = self.nItems >= len(self.list)
        self.widgetState(
            self.insertButton,
            NORMAL if self.widgetState(self.insertButton) == NORMAL 
            and isHeap and len(self.list) < self.MAX_SIZE else DISABLED)
      
    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val

    # Button functions
    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            if len(self.list) >= self.MAX_SIZE:
                self.setMessage("Error! Heap is already full.")
            else:
                self.insert(val, start=self.startMode())
                self.setMessage("Value {} inserted".format(val))
        self.clearArgument()
        
    def clickPeek(self):
        val = self.peek(start=self.startMode())
        if val is None:
            self.setMessage("Error! Heap is empty.")
        else:
            self.setMessage("{} is the root value".format(val))
            
    def clickNewArray(self):
        self.newArray()

    def clickRemoveMax(self):
        val = self.removeMax(start=self.startMode())
        if val is None:
            self.setMessage('Heap is empty!')
        else:
            self.setMessage("{} was removed".format(val))

    def clickRandomFill(self):
        val = self.validArgument()
        if val is None or val < 1 or self.MAX_SIZE < val:
            self.setMessage(
                "Input value must be between 1 to {}.".format(self.MAX_SIZE))
        else:
            self.randomFill(val)
            self.clearArgument()

    def clickHeapify(self):
        self.heapify(start=self.startMode())

if __name__ == '__main__':
    numArgs = [int(arg) for arg in sys.argv[1:] if arg.isdigit()]
    HEAP = Heap()
    try:
        for arg in numArgs:
            HEAP.setArgument(str(arg))
            HEAP.insertButton.invoke()
    except UserStop:
        HEAP.cleanUp()
    HEAP.runVisualization()
