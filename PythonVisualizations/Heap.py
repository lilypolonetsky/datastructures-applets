from tkinter import *
import random, math

try:
    from drawnValue import *
    from coordinates import *
    from BinaryTreeBase import *
    from TableDisplay import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .coordinates import *
    from .BinaryTreeBase import *
    from .TableDisplay import *

V = vector

class Heap(BinaryTreeBase):
    nextColor = 0
    MAX_SIZE = 31
    CELL_WIDTH = 25
    CELL_HEIGHT = 11
    CELL_BORDER = 1
    CELL_BORDER_COLOR = 'black'
    ARRAY_X0 = 80
    ARRAY_Y0 = 35

    def __init__(self, heapSize=2, valMax=99, title="Heap", **kwargs):
        self.maxLevel = int(math.ceil(math.log(self.MAX_SIZE, 2)))
        self.arrayCopyDelta = (2 * self.CELL_WIDTH, 0)
        self.siftArrDelta = (3 * self.CELL_WIDTH, 0)
        self.siftDelta = (3 * self.CELL_WIDTH // 2, - self.CELL_WIDTH * 3 // 4)
        canvasDims = (kwargs.get('canvasWidth', 800),
                      kwargs.get('canvasHeight', 400))
        padY = 0
        gap = 5
        self.outputFont = (self.VALUE_FONT[0], self.VALUE_FONT[1] * 9 // 10)
        self.VARIABLE_FONT = (self.VARIABLE_FONT[0], -12)
        super().__init__(
            title=title, VAL_MAX=valMax, MAX_LEVEL=self.maxLevel, **kwargs)
        outputBoxCoords = self.outputBoxCoords()
        self.setTreeSize(
            (self.ARRAY_X0 + self.siftArrDelta[0] + self.CELL_WIDTH, padY,
             canvasDims[0] - gap, outputBoxCoords[1] - gap))
        self.heapSize = heapSize
        self._arr = Table(
            self, (self.ARRAY_X0, self.ARRAY_Y0), *([None] * heapSize),
            cellWidth=self.CELL_WIDTH, cellHeight=self.CELL_HEIGHT,
            label='_arr', labelFont=self.VARIABLE_FONT,
            labelColor=self.CELL_BORDER_COLOR, vertical=True,
            labeledArrowFont=(self.VARIABLE_FONT[0], -10),
            cellBorderWidth=self.CELL_BORDER,
            cellBorderColor=self.CELL_BORDER_COLOR)
        self.nItems = 0
        self.valMax = valMax
        self.buttons = self.makeButtons()
        self.display()

    def __str__(self):
        return str([cell.val for cell in self._arr])

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
        if self.heapSize <= self.nItems:
            self.highlightCode('self._growHeap()', callEnviron)
            self._growHeap()

        # Create new item near top left corner
        startPosition = V(self._arr.cellCoords(-1.4)) - V(self.siftArrDelta * 2)
        cellPair = self.createCellValue(startPosition, val)
        callEnviron |= set(cellPair)
        nodeKey = self.canvas.copyItem(cellPair[1])
        callEnviron.add(nodeKey)

        # Place it in the array
        self.highlightCode('self._arr[self._nItems] = item', callEnviron)
        moveTo = (self._arr.cellCoords(self.nItems), 
                  self._arr.cellCenter(self.nItems),
                  self.nodeCenter(self.nItems))
        self.moveItemsTo(cellPair + (nodeKey,), moveTo, sleepTime=wait / 10)
    
        # Fill in the array cell and tree node
        d = drawnValue(val, *cellPair)
        node = self.createNode(
            val, parent=self.getNode((self.nItems - 1) // 2),
            direction=Child.LEFT if self.nItems % 2 == 1 else Child.RIGHT,
            color=self.canvas.itemConfig(cellPair[0], 'fill'))
        self.canvas.delete(nodeKey)
        callEnviron.discard(nodeKey)
        
        if self.nItems == len(self._arr):
            self._arr.append(d)    # store item at the end of the _arr
            self.nItems = len(self._arr)
        else:
            self._arr[self.nItems] = d
            self.nItems += 1
        callEnviron -= set(cellPair)
        isHeap = self.nItems <= 1    # New item could violate heap condition
        try:
            
            # Move nItems index to one past inserted item
            self.highlightCode('self._nItems += 1', callEnviron)
            self.moveItemsTo(
                self.nItemsIndex, self._arr.labeledArrowCoords(self.nItems), 
                sleepTime=wait / 10)
            
            self.highlightCode('self._siftUp(self._nItems - 1)', callEnviron)
            self.siftUp(self.nItems - 1)  # Sift up new item
            isHeap = True
        except UserStop:
            if not isHeap:
                self.setMessage('Sift up interrupted.\n'
                                'Only top item in heap')
                self.nItems = 1
                for item, coords in zip(self.nItemsIndex,
                                        self._arr.labeledArrowCoords(self.nItems)):
                    self.canvas.coords(item, *coords)
                for i in range(self.nItems, len(self.nodes)):
                    if self.nodes[i]:
                        self.removeNodeDrawing(node, line=True)
                        self.removeNodeInternal(i)
            raise UserStop()
                    
        # finish the animation
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    growHeapCode = '''
def _growHeap(self):
   current = self._arr
   self._arr = [None] * max(1, 2 * len(self._arr))
   for i in range(self._nItems):
      self._arr[i] = current[i]
'''
    
    def _growHeap(self, code=growHeapCode):
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code)

        oldTableColor = 'blue2'
        self.highlightCode('current = self._arr', callEnviron)
        current = Table(
            self, V((self._arr.x0, self._arr.y0)) + V(self.arrayCopyDelta),
            [None] * self.heapSize, label='current',
            cellWidth=self.CELL_WIDTH, cellHeight=self.CELL_HEIGHT,
            labelFont=self.SMALL_FONT, labelColor=oldTableColor, vertical=True,
            labeledArrowFont=(self.VARIABLE_FONT[0], -10),
            cellBorderWidth=self.CELL_BORDER, cellBorderColor=oldTableColor)
        callEnviron |= set(current.items())

        values = flat(*(v.items for v in self._arr))
        self.moveItemsBy(values, self.arrayCopyDelta, sleepTime=wait / 10)
            
        # Grow the the array 
        self.highlightCode('self._arr = [None] * max(1, 2 * len(self._arr))',
                           callEnviron)
        newSize = max(1, min(self.heapSize * 2, self.MAX_SIZE))
        self._arr.extend([None] * (newSize - self.heapSize))
        self.heapSize = newSize
            
        #copying the values back into the larger array 
        self.highlightCode(
            'i in range(self._nItems)', callEnviron, wait=wait / 5)
        iArrowConfig = {'level': -1}
        iArrow = current.createLabeledArrow(0, 'i', **iArrowConfig)
        callEnviron |= set(iArrow)
        for i in range(self.nItems):
            self.highlightCode('self._arr[i] = current[i]', callEnviron)
            v = self._arr[i]
            newValue = tuple(self.canvas.copyItem(i) for i in v.items)
            callEnviron |= set(newValue)
            self.moveItemsBy(newValue, V(self.arrayCopyDelta) * -1,
                             sleepTime=wait / 10)
            self.highlightCode('i in range(self._nItems)', callEnviron,
                               wait=wait / 10)
            self.moveItemsTo(
                iArrow, current.labeledArrowCoords(i + 1, **iArrowConfig),
                sleepTime=wait / 10, steps=5)

        # Move old cells back to original positions in one step
        self.highlightCode([], callEnviron)
        self.moveItemsBy(values, V(self.arrayCopyDelta) * -1, steps=1)
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

        iIndexConfig = {'level': -1}
        iIndex = self._arr.createLabeledArrow(i, 'i', **iIndexConfig)
        iNodeConfig = {'orientation': -150, 'anchor': SE, 'level': 2}
        iNodeIndex = self.createArrow(
            i, label='i', color=self.VARIABLE_COLOR, **iNodeConfig)
        callEnviron |= set(iIndex + iNodeIndex)
        self.highlightCode('i <= 0', callEnviron, wait=wait)
        if i <= 0:
            self.highlightCode('return', callEnviron)
            self.cleanUp(callEnviron)
            return
        
        self.highlightCode('item = self._arr[i]', callEnviron, wait=wait)
        upItem = self._arr[i].copy()
        itemCopy = tuple(self.canvas.copyItem(j) for j in upItem.items)
        node = self.getNode(i)
        nodeCopy = tuple(self.canvas.copyItem(j) 
                         for j in node.drawnValue.items[1:])
        toMove = itemCopy + nodeCopy
        callEnviron |= set(toMove)
        moveTo = tuple(V(self.canvas.coords(it)) + V(self.siftArrDelta * 2)
                       for it in itemCopy) + tuple(
                               V(self.canvas.coords(it)) + V(self.siftDelta * 2)
                               for it in nodeCopy)
        self.moveItemsTo(
            itemCopy + nodeCopy, moveTo, sleepTime=wait / 10)

        self.highlightCode('itemkey = self._key(item)', callEnviron, wait=wait)
        itemCopyCenter = self.canvas.coords(itemCopy[1])
        itemLabel = self.canvas.create_text(
            *(V(itemCopyCenter) - V(0, self.CELL_HEIGHT)), text='itemkey',
            font=self.SMALL_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(itemLabel)

        parentIndex = None
        self.highlightCode('0 < i', callEnviron, wait=wait)
        while 0 < i:
            self.highlightCode('parent = self.parent(i)', callEnviron)
            parent = (i - 1) // 2
            if parentIndex is None:
                parentIndex = self._arr.createLabeledArrow(parent, 'parent')
                pNodeIndex = self.createArrow(
                    parent, label='parent', level=2, color=self.VARIABLE_COLOR)
                callEnviron |= set(parentIndex + pNodeIndex)
            else:
                self.moveItemsTo(
                    parentIndex + pNodeIndex, 
                    self._arr.labeledArrowCoords(parent) + self.indexCoords(parent, 2),
                    sleepTime=wait / 10)

            self.highlightCode('self._key(self._arr[parent]) < itemkey',
                               callEnviron, wait=wait)
            if self._arr[parent] < upItem: # if parent less than item sifting up
                self.highlightCode('self._arr[i] = self._arr[parent]',
                                   callEnviron)
                # move a copy of the parent down to node i
                copyVal = tuple(
                    self.canvas.copyItem(j) for j in self._arr[parent].items)
                parentNode = self.getNode(parent)
                parentNodeCopy = tuple(
                    self.canvas.copyItem(j) 
                    for j in parentNode.drawnValue.items[1:])
                callEnviron |= set(copyVal + parentNodeCopy)
                self.moveItemsOnCurve(
                    copyVal + parentNodeCopy,
                    (self._arr.cellCoords(i), self._arr.cellCenter(i), 
                     *self.nodeItemCoords(i)[1:]),
                    startAngle=-90 * 11 / (10 + i - parent),
                    sleepTime=wait / 10)
                for item in self._arr[i].items:
                    self.canvas.delete(item)
                self._arr[i].val = self._arr[parent].val
                self._arr[i].items = copyVal
                callEnviron -= set(copyVal)
                for item in node.drawnValue.items[1:]:
                    self.canvas.delete(item)
                node.drawnValue = drawnValue(
                    parentNode.getKey(), node.drawnValue.items[0], 
                    *parentNodeCopy)
                callEnviron -= set(parentNodeCopy)
                
                # Advance i to parent, move original item along with i Index
                self.highlightCode('i = parent', callEnviron)
                delta = (0, self._arr.cellCenter(parent)[1] -
                         self._arr.cellCenter(i)[1])
                toMove = iIndex + itemCopy + (itemLabel,)
                moveTo = tuple(V(self.canvas.coords(t)) + V(delta * 2)
                               for t in toMove)
                delta = V(parentNode.center) - V(node.center)
                toMove += iNodeIndex + nodeCopy
                moveTo += tuple(V(self.canvas.coords(t)) + V(delta * 2)
                                for t in (iNodeIndex + nodeCopy))
                self.moveItemsTo(toMove, moveTo, sleepTime=wait / 10)
                i = parent
                node = self.getNode(i)
            else:
                self.highlightCode('break', callEnviron, wait=wait)
                break

            self.highlightCode('0 < i', callEnviron, wait=wait)
            
        # Move copied item into appropriate location
        self.highlightCode('self._arr[i] = item', callEnviron)
        self.moveItemsTo(
            itemCopy + nodeCopy,
            self._arr.cellAndCenters(i) + self.nodeItemCoords(i)[1:],
            sleepTime=wait / 10)
        for item in self._arr[i].items:
            self.canvas.delete(item)
        self._arr[i].val, self._arr[i].items = upItem.val, itemCopy
        callEnviron -= set(itemCopy)
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
        
        iIndexConfig = {'level': -1}
        iIndex = self._arr.createLabeledArrow(i, 'i', **iIndexConfig)
        iNodeConfig = {'orientation': -150, 'anchor': SE, 'level': 2}
        iNodeIndex = self.createArrow(
            i, label='i', color=self.VARIABLE_COLOR, **iNodeConfig)
        callEnviron |= set(iIndex + iNodeIndex)
        iNode = self.getNode(i)

        self.highlightCode('firstleaf = len(self) // 2', callEnviron, wait=wait)
        firstleaf = self.nItems // 2 # Get index of first leaf
        leafIndex = self._arr.createLabeledArrow(firstleaf, 'firstleaf')
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
        downItem = self._arr[i].copy()   # Store item at cell i
        itemCopy = tuple(self.canvas.copyItem(j) for j in downItem.items)
        nodeCopy = tuple(
            self.canvas.copyItem(j) for j in iNode.drawnValue.items[1:])
        toMove = itemCopy + nodeCopy
        callEnviron |= set(toMove)
        moveTo = tuple(V(self.canvas.coords(it)) + V(self.siftArrDelta * 2)
                       for it in itemCopy) + tuple(
                               V(self.canvas.coords(it)) + V(self.siftDelta * 2)
                               for it in nodeCopy)
        self.moveItemsTo(
            itemCopy + nodeCopy, moveTo, sleepTime=wait / 10)

        self.highlightCode('itemkey = self._key(item)', callEnviron, wait=wait)
        itemCopyCenter = self.canvas.coords(itemCopy[1])
        itemLabel = self.canvas.create_text(
            *(V(itemCopyCenter) - V(0, self.CELL_HEIGHT)), text='itemkey',
            font=self.SMALL_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(itemLabel)
        
        leftIndex, rightIndex, maxIndex = None, None, None
        leftIndexConfig = {'level': -1}
        rightIndexConfig = leftIndexConfig
        maxIndexConfig = {'level': -4}
        itemkey = downItem.val # key
        
        self.highlightCode('i < firstleaf', callEnviron, wait=wait)
        while i < firstleaf:  # While i above leaf level, find children

            self.highlightCode(
                'left, right = self.leftChild(i), self.rightChild(i)',
                callEnviron)
            left, right = i + i + 1, i + i + 2
            if leftIndex is None:
                leftIndex = self._arr.createLabeledArrow(
                    left, 'left', **leftIndexConfig)
                leftNodeIndex = self.createArrow(
                    left, label='left', color=self.VARIABLE_COLOR)
                rightIndex = self._arr.createLabeledArrow(
                    right, 'right', **rightIndexConfig)
                rightNodeIndex = self.createArrow(
                    right, label='right', color=self.VARIABLE_COLOR)
                callEnviron |= set(leftIndex + leftNodeIndex +
                                   rightIndex + rightNodeIndex)
            else:
                self.moveItemsTo(
                    leftIndex + leftNodeIndex + rightIndex + rightNodeIndex, 
                    self._arr.labeledArrowCoords(left, level=-1) +
                    self.indexCoords(left, 1) +
                    self._arr.labeledArrowCoords(right, level=-1) +
                    self.indexCoords(right, 1),
                    sleepTime=wait / 10)

            self.highlightCode('maxi = left', callEnviron)
            maxi = left        # Assume left child has larger key
            if maxIndex is None:
                maxIndex = self._arr.createLabeledArrow(
                    maxi, 'maxi', **maxIndexConfig)
                maxNodeIndex = self.createArrow(
                    maxi, label='maxi', level=2, color=self.VARIABLE_COLOR)
                callEnviron |= set(maxIndex + maxNodeIndex)
            else:
                self.moveItemsTo(
                    maxIndex + maxNodeIndex, 
                    self._arr.labeledArrowCoords(maxi, level=-4) + 
                    self.indexCoords(maxi, 2), sleepTime=wait / 10)
           
            self.highlightCode('right < len(self)', callEnviron, wait=wait)
            if right < self.nItems:
                self.highlightCode(
                    'self._key(self._arr[left]) < self._key(self._arr[right])',
                    callEnviron, wait=wait)
            if (right < self.nItems and # If both children are present, and
                self._arr[left].val < # left child has smaller key
                self._arr[right].val): 
                self.highlightCode('maxi = right', callEnviron)
                maxi = right    # then use right child
                self.moveItemsTo(
                    maxIndex + maxNodeIndex, 
                    self._arr.labeledArrowCoords(maxi, level=-4) + 
                    self.indexCoords(maxi, 2), sleepTime=wait / 10)

            self.highlightCode('itemkey < self._key(self._arr[maxi])',
                               callEnviron, wait=wait)
            if (itemkey < self._arr[maxi].val): # If item i less than max,
                # move a copy of the max child up to node i
                self.highlightCode('self._arr[i] = self._arr[maxi]',
                                   callEnviron)
                maxNode = self.getNode(maxi)
                copyVal = tuple(
                    self.canvas.copyItem(j) 
                    for j in self._arr[maxi].items + 
                    maxNode.drawnValue.items[1:])
                callEnviron |= set(copyVal)
                self.moveItemsOnCurve(
                    copyVal, 
                    (self._arr.cellCoords(i), self._arr.cellCenter(i),
                     *self.nodeItemCoords(i)[1:]),
                    sleepTime=wait / 10)
                for item in self._arr[i].items:
                    self.canvas.delete(item)
                self._arr[i].val = self._arr[maxi].val
                self._arr[i].items = copyVal[:2]
                iNode.drawnValue.val = self._arr[maxi].val
                iNode.drawnValue.items = (
                    iNode.drawnValue.items[0],) + copyVal[2:]
                callEnviron -= set(copyVal)
                
                self.highlightCode('i = maxi', callEnviron)
                # Advance i to max child, move original item along with i Index
                delta = (0, self._arr.cellCenter(maxi)[1] -
                         self._arr.cellCenter(i)[1])
                toMove = iIndex + itemCopy + (itemLabel,)
                moveTo = tuple(V(self.canvas.coords(t)) + V(delta * 2)
                               for t in toMove)
                delta = V(maxNode.center) - V(iNode.center)
                toMove += iNodeIndex + nodeCopy
                moveTo += tuple(V(self.canvas.coords(t)) + V(delta * 2)
                                for t in (iNodeIndex + nodeCopy))
                self.moveItemsTo(toMove, moveTo, sleepTime=wait / 10)
                i = maxi
                iNode = self.getNode(i)
                 
            else:              # If item i's key is greater than or equal
                self.highlightCode('break', callEnviron, wait=wait)
                break          # to larger child, then found position
            
            self.highlightCode('i < firstleaf', callEnviron, wait=wait)

        # Move copied item into appropriate location
        self.highlightCode('self._arr[i] = item', callEnviron, wait=wait)
        self.moveItemsTo(
            itemCopy + nodeCopy,
            self._arr.cellAndCenters(i) + self.nodeItemCoords(i)[1:],
            sleepTime=wait / 10)
        for item in self._arr[i].items:
            self.canvas.delete(item)
        self._arr[i].val, self._arr[i].items = downItem.val, itemCopy
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
        '''Sift item j down to preserve heap condition as part of heapify.
        Show code and animate when code is provided.
        '''
        wait = 0.1 if code else 0
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()) if code else '')

        if code:
            jIndexConfig = {'level': -1}
            jIndex = self._arr.createLabeledArrow(j, 'j', **jIndexConfig)
            jNodeConfig = {'orientation': -150, 'anchor': SE, 'level': 2}
            jNodeIndex = self.createArrow(
                j, label='j', color=self.VARIABLE_COLOR, **jNodeConfig)
            callEnviron |= set(jIndex + jNodeIndex)
        jNode = self.getNode(j)
        if jNode is None:
            jNode = self.createTreeNode(j)
        self.restoreChildLinks(j, jNode)

        NIndexConfig = {'level': 5}
        if N is not None:
            if code:
                NIndex = self._arr.createLabeledArrow(N, 'N', **NIndexConfig)
                callEnviron |= set(NIndex)
                self.highlightCode('N is None', callEnviron, wait=wait)
        else:
            N = len(self._arr)
            if code:
                self.highlightCode('N is None', callEnviron, wait=wait)
                self.highlightCode('N = len(array)', callEnviron, wait=wait)
                NIndex = self._arr.createLabeledArrow(N, 'N', **NIndexConfig)
                callEnviron |= set(NIndex)

        if code:
            self.highlightCode('firstleaf = N // 2', callEnviron, wait=wait)
        firstleaf = N // 2
        if code:
            leafIndex = self._arr.createLabeledArrow(firstleaf, 'firstleaf')
            leafNodeIndex = self.createArrow(
                firstleaf, label='firstleaf', orientation=-135,
                color=self.VARIABLE_COLOR)
            callEnviron |= set(leafIndex + leafNodeIndex)
        
            self.highlightCode('j >= firstleaf', callEnviron, wait=wait)
        if j >= firstleaf: # If item j is at or below leaf level, nothing to do
            if code:
                self.highlightCode('return', callEnviron)
            self.cleanUp(callEnviron)
            return      

        if code:
            self.highlightCode('item = array[j]', callEnviron, wait=wait)
        downItem = self._arr[j].copy()   # Store item at cell j
        itemCopy = tuple(self.canvas.copyItem(i) for i in downItem.items)
        nodeCopy = tuple(
            self.canvas.copyItem(i) for i in jNode.drawnValue.items[1:])
        toMove = itemCopy + nodeCopy
        callEnviron |= set(toMove)
        moveTo = tuple(V(self.canvas.coords(it)) + V(self.siftArrDelta * 2)
                       for it in itemCopy) + tuple(
                               V(self.canvas.coords(it)) + V(self.siftDelta * 2)
                               for it in nodeCopy)
        self.moveItemsTo(toMove, moveTo, sleepTime=wait / 10)

        if code:
            self.highlightCode('itemkey = key(item)', callEnviron, wait=wait)
        itemCopyCenter = self.canvas.coords(itemCopy[1])
        if code:
            itemLabel = self.canvas.create_text(
                *(V(itemCopyCenter) - V(0, self.CELL_HEIGHT)), text='itemkey',
                font=self.SMALL_FONT, fill=self.VARIABLE_COLOR)
            callEnviron.add(itemLabel)
        
        leftIndex, rightIndex, maxIndex = None, None, None
        leftIndexConfig = {'level': -1}
        rightIndexConfig = leftIndexConfig
        maxIndexConfig = {'level': -4}
        itemkey = downItem.val # key

        if code:
            self.highlightCode('j < firstleaf', callEnviron, wait=wait)
        while j < firstleaf:  # While j above leaf level, find children
            left, right = j + j + 1, j + j + 2
            if code:
                self.highlightCode(
                    'left, right = j + j + 1, j + j + 2', callEnviron)
                if leftIndex is None:
                    leftIndex = self._arr.createLabeledArrow(
                        left, 'left', **leftIndexConfig)
                    leftNodeIndex = self.createArrow(
                        left, label='left', color=self.VARIABLE_COLOR)
                    rightIndex = self._arr.createLabeledArrow(
                        right, 'right', **rightIndexConfig)
                    rightNodeIndex = self.createArrow(
                        right, label='right', color=self.VARIABLE_COLOR)
                    callEnviron |= set(leftIndex + leftNodeIndex +
                                       rightIndex + rightNodeIndex)
                else:
                    self.moveItemsTo(
                        leftIndex + leftNodeIndex + rightIndex + rightNodeIndex,
                        self._arr.labeledArrowCoords(left, level=-1) +
                        self.indexCoords(left, 1) +
                        self._arr.labeledArrowCoords(right, level=-1) +
                        self.indexCoords(right, 1),
                        sleepTime=wait / 10)

                self.highlightCode('maxi = left', callEnviron)
            maxi = left        # Assume left child has larger key
            if code:
                if maxIndex is None:
                    maxIndex = self._arr.createLabeledArrow(
                        maxi, 'maxi', **maxIndexConfig)
                    maxNodeIndex = self.createArrow(
                        maxi, label='maxi', level=2, color=self.VARIABLE_COLOR)
                    callEnviron |= set(maxIndex + maxNodeIndex)
                else:
                    self.moveItemsTo(
                        maxIndex + maxNodeIndex, 
                        self._arr.labeledArrowCoords(maxi, level=-4) + 
                        self.indexCoords(maxi, 2), sleepTime=wait / 10)
           
                self.highlightCode('right < N', callEnviron, wait=wait)
            if right < len(self._arr):
                if code:
                    self.highlightCode('key(array[left]) < key(array[right])',
                                       callEnviron, wait=wait)
            if (right < len(self._arr) and # If both children are present, and
                self._arr[left].val < # left child has smaller key
                self._arr[right].val):
                maxi = right          # then use right child
                if code:
                    self.highlightCode('maxi = right', callEnviron)
                    self.moveItemsTo(
                        maxIndex + maxNodeIndex, 
                        self._arr.labeledArrowCoords(maxi, level=-4) + 
                        self.indexCoords(maxi, 2), sleepTime=wait / 10)

            if code:
                self.highlightCode('itemkey < key(array[maxi])',
                                   callEnviron, wait=wait)
            if (itemkey < self._arr[maxi].val): # If item j less than max,
                # move a copy of the max child up to node j
                if code:
                    self.highlightCode('array[j] = array[maxi]',
                                       callEnviron)
                maxNode = self.getNode(maxi)
                copyVal = tuple(self.canvas.copyItem(i) 
                                for i in self._arr[maxi].items +
                                maxNode.drawnValue.items[1:])
                callEnviron |= set(copyVal)
                self.moveItemsOnCurve(
                    copyVal,
                    (self._arr.cellCoords(j), self._arr.cellCenter(j),
                     *self.nodeItemCoords(j)[1:]),
                    sleepTime=wait / 10)
                for item in self._arr[j].items:
                    self.canvas.delete(item)
                self._arr[j].val = self._arr[maxi].val
                self._arr[j].items = copyVal[0:2]
                jNode.drawnValue.val = self._arr[maxi].val
                jNode.drawnValue.items = (
                    jNode.drawnValue.items[0],) + copyVal[2:]
                callEnviron -= set(copyVal)

                if code:
                    self.highlightCode('j = maxi', callEnviron)
                # Advance j to max child, move original item along with j Index
                delta = (0, self._arr.cellCenter(maxi)[1] -
                         self._arr.cellCenter(j)[1])
                toMove = itemCopy + ((itemLabel, *jIndex) if code else ())
                moveTo = tuple(V(self.canvas.coords(t)) + V(delta * 2)
                               for t in toMove)
                delta = V(maxNode.center) - V(jNode.center)
                nodesToMove = nodeCopy + (jNodeIndex if code else ())
                toMove += nodesToMove
                moveTo += tuple(V(self.canvas.coords(t)) + V(delta * 2)
                                for t in nodesToMove)
                self.moveItemsTo(toMove, moveTo, sleepTime=wait / 10)
                j = maxi
                jNode = self.getNode(j)
                 
            else:              # If item j's key is greater than or equal
                if code:
                    self.highlightCode('break', callEnviron, wait=wait)
                break          # to larger child, then found position

            if code:
                self.highlightCode('j < firstleaf', callEnviron, wait=wait)

        # Move copied item into appropriate location
        if code:
            self.highlightCode('array[j] = item', callEnviron, wait=wait)
        self.moveItemsTo(
            itemCopy + nodeCopy,
            self._arr.cellAndCenters(j) + self.nodeItemCoords(j)[1:],
            sleepTime=wait / 10)
        for item in self._arr[j].items:
            self.canvas.delete(item)
        self._arr[j].val, self._arr[j].items = downItem.val, itemCopy
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
        item = self._arr[index]
        if color is None: 
            color = self.canvas.itemConfig(item.items[0], 'fill')
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
        '''Organize an array of N items to satisfy the heap condition.
        Show code and animate operation if code provided.
        '''
        wait = 0.1 if code else 0
        callEnviron = self.createCallEnvironment(
            code=code or '', startAnimations=start)
        if code:
            self.highlightCode('N is None', callEnviron, wait=wait)
        if N is None:            # If N is not supplied,
            N = len(self._arr)   # then use number of items in _arr
            if code:
                self.highlightCode('N = len(array)', callEnviron, wait=wait)
                NIndexConfig = {'level': 5}
                NIndex = self._arr.createLabeledArrow(N, 'N', **NIndexConfig)
                callEnviron |= set(NIndex)

        if code:
            self.highlightCode('heapLo = N // 2', callEnviron, wait=wait)
        heapLo = N // 2          # The heap lies in the range [heapLo, N)
        if code:
            heapLoIndex = self._arr.createLabeledArrow(heapLo, 'heapLo')
            callEnviron |= set(heapLoIndex)
        leaves = [self.createTreeNode(j, font=self.SMALL_FONT, radius=0,
                                      center=self._arr.cellCenter(j))
                  for j in range(max(1, heapLo), N)]
        leafCoords = [self.nodeItemCoords(j) for j in range(max(1, heapLo), N)]
        for leaf, coords in zip(leaves, leafCoords):
            leaf.center = coords[2]
            callEnviron |= set(leaf.drawnValue.items)
        self.moveItemsLinearly(
            flat(*(leaf.drawnValue.items for leaf in leaves)),
            flat(*leafCoords), sleepTime=wait / 10, startFont=self.SMALL_FONT,
            endFont=self.VALUE_FONT)

        if code:
            self.highlightCode('heapLo > 0', callEnviron, wait=wait)
            localVars = NIndex + heapLoIndex
        while heapLo > 0:        # Heapify until the entire array is a heap
            heapLo -= 1          # Decrement heap's lower boundary
            if code:
                self.highlightCode('heapLo -= 1', callEnviron, wait=wait)
                self.moveItemsTo(heapLoIndex, self._arr.labeledArrowCoords(heapLo),
                                 sleepTime=wait / 10)
            if heapLo > 0:
                leaf = self.createTreeNode(
                    heapLo, font=self.SMALL_FONT, radius=0, 
                    center=self._arr.cellCenter(heapLo))
                leafCoords = self.nodeItemCoords(heapLo)
                leaf.center = leafCoords[2]
                callEnviron |= set(leaf.drawnValue.items)
                leaves.append(leaf)
                self.moveItemsLinearly(
                    leaf.drawnValue.items, leafCoords, sleepTime=wait / 10,
                    startFont=self.SMALL_FONT, endFont=self.VALUE_FONT)

            if code:
                self.highlightCode('siftDown(array, heapLo, N, key)',
                                   callEnviron)
                colors = self.canvas.fadeItems(localVars)
            self.siftDown(heapLo, N, code=self.siftDownCode if code else None)
            if code:
                self.canvas.restoreItems(localVars, colors)

                self.highlightCode('heapLo > 0', callEnviron, wait=wait)

        # Adjust nItems pointer to indicate heap condition is satisfied
        self.nItems = N
        for leaf in leaves:  # Leaves are no longer temporary
            callEnviron -= set(leaf.drawnValue.items)
        self.moveItemsTo(self.nItemsIndex, self._arr.labeledArrowCoords(self.nItems),
                         sleepTime=wait / 10)
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

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
        outBoxCenter = BBoxCenter(outBoxCoords)
        outputBox = self.createOutputBox(outBoxCoords)
        callEnviron |= set(outputBox.items())

        if self.nItems > 0:
            self.highlightCode(['return', 'self._arr[0]'], callEnviron)
            root = self._arr[0].val

            # create the items to move to output box
            outputValues = tuple(self.canvas.copyItem(i) for i in
                                 self.getRoot().drawnValue.items[1:] +
                                 (self._arr[0].items[1],))
            callEnviron |= set(outputValues)
            outputBox.setToText(
                outputValues,
                coords=self.nodeItemCoords(outBoxCenter)[1:] + (outBoxCenter,),
                sleepTime=wait / 10, color=True)
            callEnviron -= set(outputValues)

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
        root = self._arr[0]
        rootNode = self.getRoot()
        outBoxCoords = self.outputBoxCoords(N=1)
        outBoxCenter = BBoxCenter(outBoxCoords)
        outputBox = self.createOutputBox(
            outBoxCoords, label='root', labelPosition=W, labelAnchor=E)
        callEnviron |= set(outputBox.items())
        itemCopies = tuple(self.canvas.copyItem(item) for item in
                            rootNode.drawnValue.items[1:] + (root.items[1],))
        callEnviron |= set(itemCopies)
        outputBox.setToText(
            itemCopies,
            coords=self.nodeItemCoords(outBoxCenter)[1:] + (outBoxCenter,),
            color=True, sleepTime=wait / 10)
        callEnviron -= set(itemCopies)
        
        isHeap = True
        itemsToMove = ()
        toRemove = set()
        try:
            self.highlightCode('self._nItems -= 1', callEnviron)
            lastItem = self._arr[self.nItems - 1]
            lastNode = self.nodes[self.nItems - 1]
            self.nItems = min(self.nItems - 1, len(self._arr) - 1)
            lastIndexCoords = self._arr.labeledArrowCoords(self.nItems)
            self.moveItemsTo(self.nItemsIndex, lastIndexCoords,
                             sleepTime=wait / 10)

            if self.nItems == 0:     # When last item is removed, empty tree
                toRemove = set(self._arr[0].items)  # Only cell 0 to be replaced
                for item in rootNode.drawnValue.items: # root node gone now
                    self.canvas.delete(item)
            else:                 # Otherwise prepare to move copies and remove
                itemsToMove = tuple( # originals later
                    self.canvas.copyItem(i)
                    for i in lastItem.items + lastNode.drawnValue.items[1:])
                toRemove = set(self._arr[0].items +
                               rootNode.drawnValue.items[1:] +
                               lastNode.drawnValue.items)
                callEnviron |= set(itemsToMove)
            
            self.highlightCode('self._arr[0] = self._arr[self._nItems]',
                               callEnviron, wait=0 if itemsToMove else wait)
            if itemsToMove:
                cellCoords = self._arr.cellCoords(0)
                cellCenter = self._arr.cellCenter(0)
                startAngle = 90 * 50 / (
                    50 + abs(cellCoords[1] - lastIndexCoords[0][1]))
                self.moveItemsOnCurve(
                    itemsToMove, 
                    (cellCoords, cellCenter) + self.nodeItemCoords(0)[1:],
                    startAngle=startAngle, sleepTime=wait / 10)
                self._arr[0] = drawnValue(lastItem.val, *itemsToMove[:2])
                rootNode.drawnValue.val = lastItem.val
                rootNode.drawnValue.items = (
                    rootNode.drawnValue.items[0],) + itemsToMove[2:]
                isHeap = self.nItems <= 1  # heap condition might no longer hold
                callEnviron -= set(itemsToMove)
                itemsToMove = ()
            if lastItem is self._arr[-1]:   # Whan last item is removed
                for item in toRemove | set(lastItem.items):
                    self.canvas.delete(item) # remove last and obsolete items
                self._arr.pop()
            else:                          # Otherwise keep extra items in array
                for item in toRemove - set(
                        self._arr[0].items + 
                        (rootNode.drawnValue.items if self.nItems > 0 else ())):
                    self.canvas.delete(item)
            self.nodes[self.nItems] = None

            self.highlightCode('self._siftDown(0)', callEnviron)
            self._siftDown(0)
            isHeap = True
        except UserStop:
            if not isHeap:
                self.setMessage('Sift down interrupted.\n'
                                'Only top item in heap')
                self.nItems = min(self.nItems, 1)
                for item, coords in zip(self.nItemsIndex,
                                        self._arr.labeledArrowCoords(self.nItems)):
                    self.canvas.coords(item, *coords)
            for node in self.nodes[self.nItems:]:
                if node:
                    self.removeNodeDrawing(node, line=True)
                    self.removeNodeInternal(node)
            for item in toRemove if len(itemsToMove) == 0 else itemsToMove:
                self.canvas.delete(item)
        
        # Finish animation
        self.highlightCode('return root', callEnviron, wait=wait)
        self.cleanUp(callEnviron)
        return root.val

    traverseExampleCode = '''
for item in heap.traverse():
   print(item)
'''
    
    def traverseExample(self, code=traverseExampleCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code, sleepTime=wait / 10, startAnimations=start)
        
        outBoxCoords = self.outputBoxCoords(font=self.outputFont, N=self.nItems)
        outBoxCenter = BBoxCenter(outBoxCoords)
        outputBox = self.createOutputBox(
            coords=outBoxCoords, outputOffset=(5, 10))
        callEnviron |= set(outputBox.items())
        
        self.highlightCode('item in heap.traverse()', callEnviron, wait=wait)
        arrayIndex, treeIndex = None, None
        localVars = ()
        colors = self.canvas.fadeItems(localVars)
        for i, item in self.traverse():
            self.canvas.restoreItems(localVars, colors)
            if arrayIndex is None:
                arrayIndex = self._arr.createLabeledArrow(i, 'item')
                treeIndex = self.createArrow(i, 'item')
                indices = arrayIndex + treeIndex
                callEnviron |= set(indices)
                localVars += (indices)
            else:
                self.moveItemsTo(
                    indices, 
                    self._arr.labeledArrowCoords(i) + self.indexCoords(i, 1),
                    sleepTime=wait / 10)

            self.highlightCode('print(item)', callEnviron, wait=wait)
            outputValues = tuple(self.canvas.copyItem(i) for i in
                                 (item.drawnValue.items[2],
                                  self._arr[i].items[1]))
            callEnviron |= set(outputValues)
            outputBox.appendText(outputValues, sleepTime=wait / 10)
            callEnviron -= set(outputValues)

            self.highlightCode('item in heap.traverse()', callEnviron, wait=wait)
            colors = self.canvas.fadeItems(localVars)

        self.canvas.restoreItems(localVars, colors)
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    traverseCode = '''
def traverse(self):
   for i in range(len(self)):
      yield self._arr[i]
'''

    def traverse(self, traverseType='in', code=traverseCode):
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code, sleepTime=wait / 10)

        self.highlightCode('i in range(len(self)', callEnviron, wait=wait)
        iArrayIndex, iArrow = None, None
        for i in range(self.nItems):
            if iArrayIndex is None:
                iArrayIndex = self._arr.createLabeledArrow(i, 'i')
                iArrow = self.createArrow(i, 'i', orientation=-110)
                indices = iArrayIndex + iArrow
                callEnviron |= set(indices)
            else:
                self.moveItemsTo(
                    indices,
                    self._arr.labeledArrowCoords(i) + 
                    self.indexCoords(i, 1, orientation=-110),
                    sleepTime=wait / 10)
                
            self.highlightCode('yield self._arr[i]', callEnviron, wait=wait)
            itemCoords = self.yieldCallEnvironment(
                callEnviron, sleepTime=wait / 10)
            yield i, self.getNode(i)
            self.resumeCallEnvironment(
                callEnviron, itemCoords, sleepTime=wait / 10)
            self.highlightCode('i in range(len(self)', callEnviron, wait=wait)
        
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)
    
    def randomFill(self, val, makeHeap=False):
        self.heapSize = val
        
        self.emptyTree()
        self._arr[:] = [drawnValue(random.randrange(self.valMax + 1))
                        for i in range(val)]
        self.nItems = min(val, 1)
        self.display()
        if makeHeap:
            self.heapify(code=None, start=True)

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
            rectPos = self._arr.cellCoords(indexOrCoords)
            valPos = self._arr.cellCenter(indexOrCoords)
        else:
            rectPos = indexOrCoords
            valPos = BBoxCenter(rectPos)

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
        
    def display(self):
        self.canvas.delete("all")

        self._arr.drawLabel()  # Draw label for array
        self._arr.drawCells()  # Draw grid of cells

        # Make an arrow pointing to the top of the Heap
        self.nItemsIndex = self._arr.createLabeledArrow(
            self.nItems, '_nItems', color='black')

        # go through each drawnValue in the _arr
        for i, n in enumerate(self._arr):
            # create display objects for the associated drawnValues
            if isinstance(n, drawnValue):
                n.items = self.createCellValue(i, n.val)
                if i < self.nItems:
                    self.createNode(
                        n.val, parent=self.getNode((i - 1) // 2),
                        direction=Child.LEFT if i % 2 == 1 else Child.RIGHT,
                        color=self.canvas.itemConfig(n.items[0], 'fill'))

    def fixPositions(self):  # Move canvas display items to exact cell coords
        for i, dValue in enumerate(self._arr):
            if isinstance(dValue, drawnValue):
                self.canvas.coords(dValue.items[0], *self._arr.cellCoords(i))
                self.canvas.coords(dValue.items[1], *self._arr.cellCenter(i))
                node = self.getNode(i)
            else:
                node = None
            if i < self.nItems and node:
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
        for item, coords in zip(self.nItemsIndex,
                                self._arr.labeledArrowCoords(self.nItems)):
            self.canvas.coords(item, coords)

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
        randomHeapButton = self.addOperation(
            "Make Random Heap ", lambda: self.clickRandomFill(makeHeap=True),
            numArguments=1, validationCmd=vcmd, argHelpText=['number of items'],
            helpText='Fill empty heap with N random items')
        randomFillButton = self.addOperation(
            "Erase & Random Fill ", lambda: self.clickRandomFill(),
            numArguments=1, validationCmd=vcmd, argHelpText=['number of items'],
            helpText='Fill empty array with N random items')
        self.peekButton = self.addOperation(
            "Peek", self.clickPeek, maxRows=maxRows,
            helpText='Peek at maximum item')
        self.removeMaxButton = self.addOperation(
            "Remove Max", self.clickRemoveMax, maxRows=maxRows,
            helpText='Remove maximum item from heap')
        self.heapifyButton = self.addOperation(
            "Heapify", self.clickHeapify, maxRows=maxRows,
            helpText='Organize items into heap')
        traverseButton = self.addOperation(
            "Traverse", self.clickTraverse, maxRows=maxRows,
            helpText='Organize items into heap')
        self.addAnimationButtons(maxRows=maxRows)
        return [self.insertButton, randomHeapButton, randomFillButton,
                self.peekButton, self.removeMaxButton, self.heapifyButton,
                traverseButton]

    # Button functions
    def clickInsert(self):
        if self.nItems >= self.MAX_SIZE:
            self.setMessage("Error! Heap is already full.")
            self.clearArgument()
        else:
            val = self.validArgument()
            if val is not None:
                self.insert(val, start=self.startMode())
                self.setMessage("Value {} inserted".format(val))
                self.clearArgument()
        
    def clickPeek(self):
        val = self.peek(start=self.startMode())
        if val is None:
            self.setMessage("Error! Heap is empty.")
        else:
            self.setMessage("{} is the root value".format(val))

    def clickRemoveMax(self):
        val = self.removeMax(start=self.startMode())
        if val is None:
            self.setMessage('Heap is empty!')
        else:
            self.setMessage("{} was removed".format(val))

    def clickRandomFill(self, makeHeap=False):
        val = self.validArgument()
        if val is not None and self.MAX_SIZE < val:
            self.setMessage(
                "Input value must be between 0 and {}.".format(self.MAX_SIZE))
            self.setArgumentHighlight(color=self.ERROR_HIGHLIGHT)
        elif val is not None:
            self.randomFill(val, makeHeap=makeHeap)
            self.clearArgument()

    def clickHeapify(self):
        self.heapify(start=self.startMode())
        
    def clickTraverse(self):
        self.traverseExample(start=self.startMode())

if __name__ == '__main__':
    nonneg, signed, options, otherArgs = categorizeArguments(sys.argv[1:],
                                                             signed=True)
    if '-r' not in options:  # Use fixed seed for testing consistency unless
        random.seed(3.14159) # random option specified
    heap = Heap()
    try:
        if signed:
            fill = min(Heap.MAX_SIZE, *(abs(int(arg)) for arg in signed))
            makeHeap = all(arg.startswith('+') for arg in signed)
            heap.randomFill(fill, makeHeap=makeHeap)
        for arg in nonneg:
            heap.setArgument(arg)
            heap.insertButton.invoke()
    except UserStop:
        heap.cleanUp()
    heap.runVisualization()
