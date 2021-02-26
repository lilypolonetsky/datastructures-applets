from tkinter import *
import random, math

try:
    from drawnValue import *
    from coordinates import *
    from BinaryTreeBase import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .coordinates import *
    from .BinaryTreeBase import *

V = vector

class Heap(BinaryTreeBase):
    nextColor = 0
    MAX_SIZE = 31
    CELL_WIDTH = 25
    CELL_HEIGHT = 12
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    ARRAY_X0 = 80
    ARRAY_Y0 = 18

    def __init__(self, heapSize=2, valMax=99, title="Heap", **kwargs):
        self.maxLevel = int(math.ceil(math.log(self.MAX_SIZE, 2)))
        self.arrayCopyDelta = (2 * self.CELL_WIDTH, 0)
        self.siftDelta = (3 * self.CELL_WIDTH, 0)
        canvasDims = (800, 400)
        padY = 30
        self.outputFont = (self.VALUE_FONT[0], self.VALUE_FONT[1] * 9 // 10)
        outputBoxHeight = abs(self.outputFont[1]) * 2 + 6
        RECT = (self.ARRAY_X0 + self.siftDelta[0] + self.CELL_WIDTH, padY,
                canvasDims[0] - self.siftDelta[0],
                canvasDims[1] - outputBoxHeight)
        super().__init__(
            title=title, VAL_MAX=valMax, MAX_LEVEL=self.maxLevel, RECT=RECT,
            **kwargs)
        self.heapSize = heapSize
        self.list = []
        self.nItems = 0
        self.valMax = valMax
        self.buttons = self.makeButtons()
        self.display()

    def __str__(self):
        return str([cell.val for cell in self.list])
    
    # Create index arrow to point at an array cell with an optional name label
    def createArrayIndex(self, index, name='nItems', level=1, color=None):
        if color is None: color = self.VARIABLE_COLOR
        arrowCoords, labelCoords = self.arrayIndexCoords(index, level)
        return self.drawArrow(
            arrowCoords, labelCoords, color, self.SMALL_FONT, name)

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
        leftPointing = level < 0
        separation = 3 if leftPointing else -3
        return (x0, y0, x1, y1), (x0 + separation, y0)
    
    # draw the actual arrow 
    def drawArrow(self, arrowCoords, labelCoords, color, font, name=None):
        arrow = self.canvas.create_line(*arrowCoords, arrow="last", fill=color)
        leftPointing = arrowCoords[0] > arrowCoords[2]
        if name:
            label = self.canvas.create_text(
                *labelCoords, text=name, anchor=W if leftPointing else E,
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
        if self.heapSize <= len(self.list):
            self.highlightCode('self._growHeap()', callEnviron)
            self._growHeap()

        # Create new item near top left corner
        startPosition = V(self.cellCoords(-1.4)) - V(self.siftDelta * 2)
        cellPair = self.createCellValue(startPosition, val)
        callEnviron |= set(cellPair)
        nodeKey = self.copyCanvasItem(cellPair[1])
        callEnviron.add(nodeKey)

        # Place it in the array
        self.highlightCode('self._arr[self._nItems] = item', callEnviron)
        toPositions = (self.cellCoords(self.nItems), 
                       self.cellCenter(self.nItems),
                       self.nodeCenter(self.nItems))
        self.moveItemsTo(cellPair + (nodeKey,), toPositions, 
                         sleepTime=wait / 10)
    
        # Fill in the array cell and tree node
        d = drawnValue(val, *cellPair)
        node = self.createNode(
            val, parent=self.getNode((self.nItems - 1) // 2),
            direction=Child.LEFT if self.nItems % 2 == 1 else Child.RIGHT,
            color=self.canvas.itemconfigure(cellPair[0], 'fill')[-1])
        if self.nItems == len(self.list):
            self.list.append(d)    #store item at the end of the list
            self.nItems = len(self.list)
        else:
            self.list[self.nItems] = d
            self.nItems += 1
        callEnviron -= set(cellPair)
        
        # Move nItems index to one past inserted item
        self.highlightCode('self._nItems += 1', callEnviron)
        self.moveItemsTo(self.nItemsIndex, self.arrayIndexCoords(self.nItems), 
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
        for i in range(self.heapSize): 
            callEnviron.add(self.createArrayCell(i)) # Temporary
            if i + self.heapSize < self.MAX_SIZE:
                self.createArrayCell(i + self.heapSize) # Lasting
        self.heapSize = min(self.heapSize * 2, self.MAX_SIZE)
            
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
        iNodeIndex = self.createArrow(
            i, label='i', orientation=-30, color=self.VARIABLE_COLOR)
        callEnviron |= set(iIndex + iNodeIndex)
        self.highlightCode('i <= 0', callEnviron, wait=wait)
        if i <= 0:
            self.highlightCode('return', callEnviron)
            self.cleanUp(callEnviron)
            return
        
        self.highlightCode('item = self._arr[i]', callEnviron, wait=wait)
        upItem = self.list[i].copy()
        copyItem = tuple(self.copyCanvasItem(j) for j in upItem.items)
        node = self.getNode(i)
        nodeCopy = tuple(self.copyCanvasItem(j) 
                         for j in node.drawnValue.items[1:])
        callEnviron |= set(copyItem + nodeCopy)
        self.moveItemsBy(
            copyItem + nodeCopy, self.siftDelta, sleepTime=wait / 10)

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
                pNodeIndex = self.createArrow(
                    parent, label='parent', level=2, color=self.VARIABLE_COLOR)
                callEnviron |= set(parentIndex + pNodeIndex)
            else:
                self.moveItemsTo(
                    parentIndex + pNodeIndex, 
                    self.arrayIndexCoords(parent) + self.indexCoords(parent, 2),
                    sleepTime=wait / 10)

            self.highlightCode('self._key(self._arr[parent]) < itemkey',
                               callEnviron, wait=wait)
            if self.list[parent] < upItem: # if parent less than item sifting up
                self.highlightCode('self._arr[i] = self._arr[parent]',
                                   callEnviron)
                # move a copy of the parent down to node i
                copyVal = tuple(
                    self.copyCanvasItem(j) for j in self.list[parent].items)
                parentNode = self.getNode(parent)
                parentNodeCopy = tuple(
                    self.copyCanvasItem(j) 
                    for j in parentNode.drawnValue.items[1:])
                callEnviron |= set(copyVal + parentNodeCopy)
                self.moveItemsOnCurve(
                    copyVal + parentNodeCopy,
                    (self.cellCoords(i), self.cellCenter(i), 
                     *self.nodeItemCoords(i)[1:]),
                    startAngle=-90 * 11 / (10 + i - parent),
                    sleepTime=wait / 10)
                for item in self.list[i].items:
                    self.canvas.delete(item)
                self.list[i].val = self.list[parent].val
                self.list[i].items = copyVal
                callEnviron -= set(copyVal)
                for item in node.drawnValue.items[1:]:
                    self.canvas.delete(item)
                node.drawnValue = drawnValue(
                    parentNode.getKey(), node.drawnValue.items[0], 
                    *parentNodeCopy)
                callEnviron -= set(parentNodeCopy)
                
                # Advance i to parent, move original item along with i Index
                self.highlightCode('i = parent', callEnviron)
                delta = (0, self.cellCenter(parent)[1] - self.cellCenter(i)[1])
                toMove = iIndex + copyItem + (itemLabel,)
                toPositions = tuple(V(self.canvas.coords(t)) + V(delta * 2)
                                    for t in toMove)
                delta = V(parentNode.center) - V(node.center)
                toMove += iNodeIndex + nodeCopy
                toPositions += tuple(V(self.canvas.coords(t)) + V(delta * 2)
                                     for t in (iNodeIndex + nodeCopy))
                self.moveItemsTo(toMove, toPositions, sleepTime=wait / 10)
                i = parent
                node = self.getNode(i)
            else:
                self.highlightCode('break', callEnviron, wait=wait)
                break

            self.highlightCode('0 < i', callEnviron, wait=wait)
            
        # Move copied item into appropriate location
        self.highlightCode('self._arr[i] = item', callEnviron)
        self.moveItemsBy(copyItem + nodeCopy, V(self.siftDelta) * -1,
                         sleepTime=wait / 10)
        for item in self.list[i].items:
            self.canvas.delete(item)
        self.list[i].val, self.list[i].items = upItem.val, copyItem
        callEnviron -= set(copyItem)
        for item in node.drawnValue.items[1:]:
            self.canvas.delete(item)
        node.drawnValue = drawnValue(
            upItem.val, node.drawnValue.items[0], *nodeCopy)
        callEnviron -= set(nodeCopy)

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
        iNodeIndex = self.createArrow(
            i, label='i', orientation=-30, color=self.VARIABLE_COLOR)
        callEnviron |= set(iIndex + iNodeIndex)
        iNode = self.getNode(i)

        self.highlightCode('firstleaf = len(self) // 2', callEnviron, wait=wait)
        firstleaf = self.nItems // 2 # Get index of first leaf
        leafIndex = self.createArrayIndex(firstleaf, name='firstleaf')
        leafNodeIndex = self.createArrow(
            firstleaf, label='firstleaf', orientation=-135,
            color=self.VARIABLE_COLOR)
        callEnviron |= set(leafIndex + leafNodeIndex)
        
        self.highlightCode('i >= firstleaf', callEnviron, wait=wait)
        if i >= firstleaf: # If item i is at or below leaf level, nothing to do
            self.highlightCode('return', callEnviron)
            self.cleanUp(callEnviron)
            return

        self.highlightCode('item = self._arr[i]', callEnviron, wait=wait)
        downItem = self.list[i].copy()   # Store item at cell i
        itemCopy = tuple(self.copyCanvasItem(j) for j in downItem.items)
        nodeCopy = tuple(
            self.copyCanvasItem(j) for j in iNode.drawnValue.items[1:])
        callEnviron |= set(itemCopy + nodeCopy)
        self.moveItemsBy(
            itemCopy + nodeCopy, self.siftDelta, sleepTime=wait / 10)

        self.highlightCode('itemkey = self._key(item)', callEnviron, wait=wait)
        copyItemCenter = self.canvas.coords(itemCopy[1])
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
                leftNodeIndex = self.createArrow(
                    left, label='left', color=self.VARIABLE_COLOR)
                rightIndex = self.createArrayIndex(right, 'right', level=-1)
                rightNodeIndex = self.createArrow(
                    right, label='right', color=self.VARIABLE_COLOR)
                callEnviron |= set(leftIndex + leftNodeIndex +
                                   rightIndex + rightNodeIndex)
            else:
                self.moveItemsTo(
                    leftIndex + leftNodeIndex + rightIndex + rightNodeIndex, 
                    self.arrayIndexCoords(left, level=-1) +
                    self.indexCoords(left, 1) +
                    self.arrayIndexCoords(right, level=-1) +
                    self.indexCoords(right, 1),
                    sleepTime=wait / 10)

            self.highlightCode('maxi = left', callEnviron)
            maxi = left        # Assume left child has larger key
            if maxIndex is None:
                maxIndex = self.createArrayIndex(maxi, name='maxi', level=-4)
                maxNodeIndex = self.createArrow(
                    maxi, label='maxi', level=2, color=self.VARIABLE_COLOR)
                callEnviron |= set(maxIndex + maxNodeIndex)
            else:
                self.moveItemsTo(
                    maxIndex + maxNodeIndex, 
                    self.arrayIndexCoords(maxi, level=-4) + 
                    self.indexCoords(maxi, 2), sleepTime=wait / 10)
           
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
                self.moveItemsTo(
                    maxIndex + maxNodeIndex, 
                    self.arrayIndexCoords(maxi, level=-4) + 
                    self.indexCoords(maxi, 2), sleepTime=wait / 10)

            self.highlightCode('itemkey < self._key(self._arr[maxi])',
                               callEnviron, wait=wait)
            if (itemkey < self.list[maxi].val): # If item i less than max,
                # move a copy of the max child up to node i
                self.highlightCode('self._arr[i] = self._arr[maxi]',
                                   callEnviron)
                maxNode = self.getNode(maxi)
                copyVal = tuple(
                    self.copyCanvasItem(j) 
                    for j in self.list[maxi].items + 
                    maxNode.drawnValue.items[1:])
                callEnviron |= set(copyVal)
                self.moveItemsOnCurve(
                    copyVal, 
                    (self.cellCoords(i), self.cellCenter(i),
                     *self.nodeItemCoords(i)[1:]),
                    sleepTime=wait / 10)
                for item in self.list[i].items:
                    self.canvas.delete(item)
                self.list[i].val = self.list[maxi].val
                self.list[i].items = copyVal[:2]
                iNode.drawnValue.val = self.list[maxi].val
                iNode.drawnValue.items = (
                    iNode.drawnValue.items[0],) + copyVal[2:]
                callEnviron -= set(copyVal)
                
                self.highlightCode('i = maxi', callEnviron)
                # Advance i to max child, move original item along with i Index
                delta = (0, self.cellCenter(maxi)[1] - self.cellCenter(i)[1])
                toMove = iIndex + itemCopy + (itemLabel,)
                toPositions = tuple(V(self.canvas.coords(t)) + V(delta * 2)
                                    for t in toMove)
                delta = V(maxNode.center) - V(iNode.center)
                toMove += iNodeIndex + nodeCopy
                toPositions += tuple(V(self.canvas.coords(t)) + V(delta * 2)
                                     for t in (iNodeIndex + nodeCopy))
                self.moveItemsTo(toMove, toPositions, sleepTime=wait / 10)
                i = maxi
                iNode = self.getNode(i)
                 
            else:              # If item i's key is greater than or equal
                self.highlightCode('break', callEnviron, wait=wait)
                break          # to larger child, then found position
            
            self.highlightCode('i < firstleaf', callEnviron, wait=wait)

        # Move copied item into appropriate location
        self.highlightCode('self._arr[i] = item', callEnviron, wait=wait)
        self.moveItemsBy(itemCopy + nodeCopy, V(self.siftDelta) * -1,
                         sleepTime=wait / 10)
        for item in self.list[i].items:
            self.canvas.delete(item)
        self.list[i].val, self.list[i].items = downItem.val, itemCopy
        iNode.drawnValue.val = downItem.val
        iNode.drawnValue.items = (iNode.drawnValue.items[0],) + nodeCopy
        callEnviron -= set(itemCopy + nodeCopy)

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    siftDownCode = '''
def siftDown(array, j={j}, N={N}, key=identity):
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
        
    def siftDown(self, j=0, N=None, code=siftDownCode):
        'Sift item j down to preserve heap condition as part of heapify'
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))
        
        jIndex = self.createArrayIndex(j, name='j', level=-1)
        jNodeIndex = self.createArrow(
            j, label='j', orientation=-30, color=self.VARIABLE_COLOR)
        callEnviron |= set(jIndex + jNodeIndex)
        jNode = self.getNode(j)
        if jNode is None:
            jNode = self.createTreeNode(j)
        self.restoreChildLinks(j, jNode)

        if N is not None:
            NIndex = self.createArrayIndex(N, name='N', level=2)
            callEnviron |= set(NIndex)
        self.highlightCode('N is None', callEnviron, wait=wait)
        if N is None:
            self.highlightCode('N = len(array)', callEnviron, wait=wait)
            N = len(self.list)
            NIndex = self.createArrayIndex(N, name='N', level=2)
            callEnviron |= set(NIndex)

        self.highlightCode('firstleaf = N // 2', callEnviron, wait=wait)
        firstleaf = N // 2
        leafIndex = self.createArrayIndex(firstleaf, name='firstleaf')
        leafNodeIndex = self.createArrow(
            firstleaf, label='firstleaf', orientation=-135,
            color=self.VARIABLE_COLOR)
        callEnviron |= set(leafIndex + leafNodeIndex)
        
        self.highlightCode('j >= firstleaf', callEnviron, wait=wait)
        if j >= firstleaf: # If item j is at or below leaf level, nothing to do
            self.highlightCode('return', callEnviron)
            self.cleanUp(callEnviron)
            return      

        self.highlightCode('item = array[j]', callEnviron, wait=wait)
        downItem = self.list[j].copy()   # Store item at cell j
        itemCopy = tuple(self.copyCanvasItem(i) for i in downItem.items)
        nodeCopy = tuple(
            self.copyCanvasItem(i) for i in jNode.drawnValue.items[1:])
        callEnviron |= set(itemCopy + nodeCopy)
        self.moveItemsBy(
            itemCopy + nodeCopy, self.siftDelta, sleepTime=wait / 10)

        self.highlightCode('itemkey = key(item)', callEnviron, wait=wait)
        copyItemCenter = self.canvas.coords(itemCopy[1])
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
                leftNodeIndex = self.createArrow(
                    left, label='left', color=self.VARIABLE_COLOR)
                rightIndex = self.createArrayIndex(right, 'right', level=-1)
                rightNodeIndex = self.createArrow(
                    right, label='right', color=self.VARIABLE_COLOR)
                callEnviron |= set(leftIndex + leftNodeIndex +
                                   rightIndex + rightNodeIndex)
            else:
                self.moveItemsTo(
                    leftIndex + leftNodeIndex + rightIndex + rightNodeIndex, 
                    self.arrayIndexCoords(left, level=-1) +
                    self.indexCoords(left, 1) +
                    self.arrayIndexCoords(right, level=-1) +
                    self.indexCoords(right, 1),
                    sleepTime=wait / 10)

            self.highlightCode('maxi = left', callEnviron)
            maxi = left        # Assume left child has larger key
            if maxIndex is None:
                maxIndex = self.createArrayIndex(maxi, name='maxi', level=-4)
                maxNodeIndex = self.createArrow(
                    maxi, label='maxi', level=2, color=self.VARIABLE_COLOR)
                callEnviron |= set(maxIndex + maxNodeIndex)
            else:
                self.moveItemsTo(
                    maxIndex + maxNodeIndex, 
                    self.arrayIndexCoords(maxi, level=-4) + 
                    self.indexCoords(maxi, 2), sleepTime=wait / 10)
           
            self.highlightCode('right < N', callEnviron, wait=wait)
            if right < len(self.list):
                self.highlightCode('key(array[left]) < key(array[right])',
                                   callEnviron, wait=wait)
            if (right < len(self.list) and # If both children are present, and
                self.list[left].val < # left child has smaller key
                self.list[right].val): 
                self.highlightCode('maxi = right', callEnviron)
                maxi = right    # then use right child
                self.moveItemsTo(
                    maxIndex + maxNodeIndex, 
                    self.arrayIndexCoords(maxi, level=-4) + 
                    self.indexCoords(maxi, 2), sleepTime=wait / 10)

            self.highlightCode('itemkey < key(array[maxi])',
                               callEnviron, wait=wait)
            if (itemkey < self.list[maxi].val): # If item j less than max,
                # move a copy of the max child up to node j
                self.highlightCode('array[j] = array[maxi]',
                                   callEnviron)
                maxNode = self.getNode(maxi)
                copyVal = tuple(
                    self.copyCanvasItem(i) 
                    for i in self.list[maxi].items + 
                    maxNode.drawnValue.items[1:])
                callEnviron |= set(copyVal)
                self.moveItemsOnCurve(
                    copyVal,
                    (self.cellCoords(j), self.cellCenter(j),
                     *self.nodeItemCoords(j)[1:]),
                    sleepTime=wait / 10)
                for item in self.list[j].items:
                    self.canvas.delete(item)
                self.list[j].val = self.list[maxi].val
                self.list[j].items = copyVal[0:2]
                jNode.drawnValue.val = self.list[maxi].val
                jNode.drawnValue.items = (
                    jNode.drawnValue.items[0],) + copyVal[2:]
                callEnviron -= set(copyVal)
                
                self.highlightCode('j = maxi', callEnviron)
                # Advance j to max child, move original item along with j Index
                delta = (0, self.cellCenter(maxi)[1] - self.cellCenter(j)[1])
                toMove = jIndex + itemCopy + (itemLabel,)
                toPositions = tuple(V(self.canvas.coords(t)) + V(delta * 2)
                                    for t in toMove)
                delta = V(maxNode.center) - V(jNode.center)
                toMove += jNodeIndex + nodeCopy
                toPositions += tuple(V(self.canvas.coords(t)) + V(delta * 2)
                                     for t in (jNodeIndex + nodeCopy))
                self.moveItemsTo(toMove, toPositions, sleepTime=wait / 10)
                j = maxi
                jNode = self.getNode(j)
                 
            else:              # If item j's key is greater than or equal
                self.highlightCode('break', callEnviron, wait=wait)
                break          # to larger child, then found position
            
            self.highlightCode('j < firstleaf', callEnviron, wait=wait)

        # Move copied item into appropriate location
        self.highlightCode('array[j] = item', callEnviron, wait=wait)
        self.moveItemsBy(itemCopy + nodeCopy, V(self.siftDelta) * -1,
                         sleepTime=wait / 10)
        for item in self.list[j].items:
            self.canvas.delete(item)
        self.list[j].val, self.list[j].items = downItem.val, itemCopy
        jNode.drawnValue.val = downItem.val
        jNode.drawnValue.items = (jNode.drawnValue.items[0],) + nodeCopy
        callEnviron -= set(itemCopy + nodeCopy)

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    def createTreeNode(self, index, parent=None, children=False,
                       center=None, radius=None, color=None, font=None):
        '''Create a tree node at a particular node index copying the
        values from the heap array and filling in any links to existing
        children.  The parent link is only made visible (non-zero length)
        if the parent is provided.  If children is true, the links from
        existing children are moved to connect to this node.
        The center, radius, color, and font can all be set.
        '''
        item = self.list[index]
        if color is None: 
            color = self.canvas.itemconfigure(item.items[0], 'fill')[-1]
        if center is None:
            center = self.nodeCenter(index)

        # generate a tag
        tag = self.generateTag()
      
        # create the canvas items and the drawnValue object
        drawnValueObj = drawnValue(item.val, *self.createNodeShape(
            *center, item.val, tag, color=color, radius=radius, font=font,
            parent=self.getNode(parent).center if parent else None))
      
        # create the Node object
        node = Node(drawnValueObj, center, tag)

        # add the node object to the internal representation
        self.nodes[index] = node

        # Connect it with any existing children, if requested
        if children:
            self.restoreChildLinks(index, node)

        return node

    def restoreChildLinks(self, index, node=None):
        if node is None:
            node = self.getNode(index)
        for child in (self.getLeftChildIndex(index),
                      self.getRightChildIndex(index)):
            childNode = self.getNode(child)
            if childNode:    # Restore link from child to parent
                self.canvas.coords(childNode.drawnValue.items[0],
                                   *childNode.center, *node.center)
    
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
        leaves = [self.createTreeNode(j, font=self.SMALL_FONT, radius=0,
                                      center=self.cellCenter(j))
                  for j in range(heapLo, N)]
        leafCoords = [self.nodeItemCoords(j) for j in range(heapLo, N)]
        self.moveItemsLinearly(
            flat(*(leaf.drawnValue.items for leaf in leaves)),
            flat(*leafCoords), sleepTime=wait / 10, startFont=self.SMALL_FONT,
            endFont=self.VALUE_FONT)
        for l, leaf in enumerate(leaves):
            leaf.center = leafCoords[l][2]
        
        self.highlightCode('heapLo > 0', callEnviron, wait=wait)
        localVars = NIndex + heapLoIndex
        while heapLo > 0:        # Heapify until the entire array is a heap
            self.highlightCode('heapLo -= 1', callEnviron, wait=wait)
            heapLo -= 1           # Decrement heap's lower boundary
            self.moveItemsTo(heapLoIndex, self.arrayIndexCoords(heapLo),
                             sleepTime=wait / 10)
            if heapLo > 0:
                leaf = self.createTreeNode(
                    heapLo, font=self.SMALL_FONT, radius=0, 
                    center=self.cellCenter(heapLo))
                leafCoords = self.nodeItemCoords(heapLo)
                self.moveItemsLinearly(
                    leaf.drawnValue.items, leafCoords, sleepTime=wait / 10,
                    startFont=self.SMALL_FONT, endFont=self.VALUE_FONT)
                leaf.center = leafCoords[2]
            
            self.highlightCode('siftDown(array, heapLo, N, key)',
                               callEnviron)
            colors = self.fadeNonLocalItems(localVars)
            self.siftDown(heapLo, N) # Sift down item at heapLo
            self.restoreLocalItems(localVars, colors)

            self.highlightCode('heapLo > 0', callEnviron, wait=wait)

        # Adjust nItems pointer to indicate heap condition is satisfied
        self.nItems = N
        self.moveItemsTo(self.nItemsIndex, self.arrayIndexCoords(self.nItems),
                         sleepTime=wait / 10)
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
              
    # lets user input an int argument that determines max size of the Heap
    def newArray(self):
        #gets rid of old elements in the list
        del self.list[:]
        self.nItems = 0
        self.heapSize = 2
        self.emptyTree()
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
        outBoxCoords = self.outputBoxCoords(N=1)
        outBoxCenter = V(V(outBoxCoords[:2]) + V(outBoxCoords[2:])) // 2
        outputBox = self.canvas.create_rectangle(
            *outBoxCoords, fill=self.OPERATIONS_BG)
        callEnviron.add(outputBox)

        if self.nItems > 0:
            self.highlightCode(['return', 'self._arr[0]'], callEnviron)
            # create the value to move to output box
            valueOutput = self.copyCanvasItem(self.list[0].items[1])
            callEnviron.add(valueOutput)
            self.moveItemsTo(valueOutput, outBoxCenter, sleepTime=wait / 10)
            # Convert to output font
            self.canvas.itemconfig(valueOutput, font=self.outputFont)
            root = self.list[0].val

        else:
            self.highlightCode('return None', callEnviron)
            root = None
            
        # finish animation
        self.cleanUp(callEnviron)
        return root

    removeMaxCode = '''
def remove(self):
   if self.isEmpty():
      raise Exception("Heap underflow")
   root = self._arr[0]
   self._nItems -= 1
   self._arr[0] = self._arr[self._nItems]
   self._siftDown(0)
   return root
'''
    
    def removeMax(self, code=removeMaxCode, start=True):
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
        rootNode = self.getRoot()
        outBoxCoords = self.outputBoxCoords(N=1)
        outBoxCenter = V(V(outBoxCoords[:2]) + V(outBoxCoords[2:])) // 2
        outputBox = self.canvas.create_rectangle(
            *outBoxCoords, fill=self.OPERATIONS_BG)
        callEnviron.add(outputBox)
        callEnviron.add(self.canvas.create_text(
            outBoxCoords[0] - 10, outBoxCenter[1], text='root', anchor=E,
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR))
        keyCopies = tuple(self.copyCanvasItem(item) for item in
                          (root.items[1], rootNode.drawnValue.items[2]))
        callEnviron |= set(keyCopies)
        self.moveItemsTo(keyCopies, (outBoxCenter, outBoxCenter),
                         sleepTime=wait / 10)
        for keyCopy in keyCopies:
            self.canvas.itemconfigure(keyCopy, font=self.outputFont)

        self.highlightCode('self._nItems -= 1', callEnviron)
        lastItem = self.list[self.nItems - 1]
        lastNode = self.nodes[self.nItems - 1]
        self.nItems = min(self.nItems - 1, len(self.list) - 1)
        lastIndexCoords = self.arrayIndexCoords(self.nItems)
        self.moveItemsTo(self.nItemsIndex, lastIndexCoords, sleepTime=wait / 10)

        itemsToMove = [] if self.nItems <= 0 else tuple(
            self.copyCanvasItem(i) 
            for i in lastItem.items + lastNode.drawnValue.items[1:])
        self.highlightCode('self._arr[0] = self._arr[self._nItems]',
                           callEnviron, wait=0 if itemsToMove else wait)
        if itemsToMove:
            cellCoords = self.cellCoords(0)
            cellCenter = self.cellCenter(0)
            startAngle = 90 * 50 / (
                50 + abs(cellCoords[1] - lastIndexCoords[0][1]))
            self.moveItemsOnCurve(
                itemsToMove, 
                (cellCoords, cellCenter) + self.nodeItemCoords(0)[1:],
                startAngle=startAngle, sleepTime=wait / 10)
            self.list[0] = drawnValue(lastItem.val, *itemsToMove[:2])
            rootNode.drawnValue.val = lastItem.val
            rootNode.drawnValue.items = (
                rootNode.drawnValue.items[0],) + itemsToMove[2:]
        for item in lastNode.drawnValue.items + (
                lastItem.items if lastItem is self.list[-1] else ()):
            self.canvas.delete(item)
        if lastItem is self.list[-1]:
            self.list.pop()
        
        self.highlightCode('self._siftDown(0)', callEnviron)
        self._siftDown(0)
        
        # Finish animation
        self.highlightCode('return root', callEnviron, wait=wait)
        self.cleanUp(callEnviron)
        return root.val
    
    def randomFill(self, val):
        self.heapSize = max(self.heapSize, val)
        
        self.emptyTree()
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
    
    def outputBoxCoords(self, font=None, padding=6, N=None):
        '''Coordinates for an output box in lower right of canvas with enough
        space to hold N values, defaulting to current heap size.  Normally
        it is centered under the tree.'''
        if N is None: N = len(self.list)
        if font is None: font = self.VALUE_FONT
        spacing = self.outputBoxSpacing(font)
        canvasDims = self.widgetDimensions(self.canvas)
        left = max(0, self.RECT[0] + self.RECT[2] - N * spacing - padding) // 2
        return (left, canvasDims[1] - abs(font[1]) * 2 - padding,
                left + N * spacing + padding, canvasDims[1] - padding)
        
    def display(self):
        self.canvas.delete("all")

        for i in range(self.heapSize):  # Draw grid of cells
            self.createArrayCell(i)

        #make a new arrow pointing to the top of the Heap
        self.nItemsIndex = self.createArrayIndex(self.nItems, color='black')

        # go through each drawnValue in the list
        for i, n in enumerate(self.list):
            # create display objects for the associated drawnValues
            n.items = self.createCellValue(i, n.val)
            if i < self.nItems:
                self.createNode(
                    n.val, parent=self.getNode((i - 1) // 2),
                    direction=Child.LEFT if i % 2 == 1 else Child.RIGHT)

    def fixPositions(self):  # Move canvas display items to exact cell coords
        for i, dValue in enumerate(self.list):
            self.canvas.coords(dValue.items[0], *self.cellCoords(i))
            self.canvas.coords(dValue.items[1], *self.cellCenter(i))
            node = self.getNode(i)
            if i < self.nItems:
                self.restoreNodes([node])
            elif node:
                self.removeNodeDrawing(node, line=True)
                self.removeNodeInternal(node)
            
        # Restore array cell borders in case they were moved
        for i, item in enumerate(self.canvas.find_withtag('arrayCell')):
            if i >= self.heapSize: # Delete any extra cell borders
                self.canvas.delete(item)
            else:
                self.canvas.coords(item, *self.arrayCellCoords(i))
            
        # Restore nItems index to one past end of array
        arrowCoords, labelCoords = self.arrayIndexCoords(self.nItems)
        self.canvas.coords(self.nItemsIndex[0], arrowCoords)
        self.canvas.coords(self.nItemsIndex[1], labelCoords)

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
            helpText='Insert an item in the heap')
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
