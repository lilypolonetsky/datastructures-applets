from tkinter import *
import random
import sys

try:
    from VisualizationApp import *
    from BinaryTreeBase import *
except ModuleNotFoundError:
    from .VisualizationApp import *
    from .BinaryTreeBase import *

class AVLTree(BinaryTreeBase):
    def __init__(self, title="AVL Tree", **kwargs):
        super().__init__(title=title, **kwargs)
        self.buttons = self.makeButtons()
        self.display(treeLabel='AVLtree')

    def newTree(self):
        self.emptyTree()
        self.display(treeLabel='AVLtree')

    def randomFill(self, numNodes):
        callEnviron = self.createCallEnvironment()

        # empty the tree
        self.emptyTree()

        #randomly generate a tree
        nums = list(range(1, 99))
        random.shuffle(nums)
        while self.size < numNodes and nums:
            num = nums.pop()
            self.insert(nums.pop(), animation=False)

        self.cleanUp(callEnviron)

    insertCode = '''
def insert(self, key={key}, data):
   self.__root, flag = self.__insert(self.__root, key, data)
   return flag
'''
      
    def insert(self, key, animation=True, code=insertCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()) if animation else '', 
            startAnimations=animation and start)

        # create arrow
        if animation:
            self.highlightCode(
                'self.__root, flag = self.__insert(self.__root, key, data)',
                callEnviron)

        root, flag = self.__insert(self.getRoot(), key, animation=animation)
        if animation:
            flagText = self.createFlagText(flag)
            callEnviron.add(flagText)
        self.setRoot(root)
        self.updateTreeObjectRootPointer(root=self.getRoot())

        if animation:
            self.highlightCode('return flag', callEnviron)
        self.cleanUp(callEnviron)
        return flag

    __insertCode = '''
def __insert(self, node={nodeKey}, key={key}, data):
   if node is None:
      return self.__Node(key, data), True
   
   if key == node.key:
      node.data = data
      return node, False
       
   elif key < node.key:
      node.left, flag = self.__insert(node.left, key, data)
      if node.heightDiff() > 1:
         if node.left.key < key:
            node.left = self.rotateLeft(node.left) 
         node = self.rotateRight(node)
       
   else:
      node.right, flag = self.__insert(node.right, key, data)
      if node.heightDiff() < -1:
         if key < node.right.key:
            node.right = self.rotateRight(node.right) 
         node = self.rotateLeft(node)
    
   node.updateHeight()
   return node, flag
'''

    def __insert(
            self, node, key, animation=True, arrow=None, code=__insertCode):
        wait = 0.1
        nodeIndex = self.getIndex(node)
        node = self.getNode(nodeIndex)
        callEnviron = self.createCallEnvironment(
            code=code.format(
                nodeKey=node.getKey() if node else None, **locals()) 
            if animation else '', 
            startAnimations=animation)

        # Check for empty subtree
        if animation:
            nodeArrow = self.createArrow(nodeIndex, 'node')
            callEnviron |= set(nodeArrow)
            localVars = nodeArrow
            self.highlightCode('node is None', callEnviron, wait=wait)
        if node is None:
            if animation:
                self.highlightCode('return self.__Node(key, data), True',
                                   callEnviron)
            insertedNode = self.createNode(
                key, nodeIndex, parent=None, addToArray=False)
            self.cleanUp(callEnviron)
            return insertedNode, True
        
        # Check for existing key
        if animation:
            self.highlightCode('key == node.key', callEnviron, wait=wait)
        if key == node.getKey():
            if animation:
                self.setMessage(("Key {} already exists\n" +
                                 "Updating value.").format(key))
                self.highlightCode('return node, False', callEnviron)
            self.cleanUp(callEnviron)
            return node, False

        # don't insert past MAX_LEVEL
        if self.getLevel(node) == self.MAX_LEVEL-1:
            if animation:
                self.setMessage(
                    "Error! Cannot insert at level " + str(self.MAX_LEVEL+1) + 
                    " or below")
            self.cleanUp(callEnviron)
            return node, False
          
        # Does the key belong in left subtree?
        if animation:
            self.highlightCode('key < node.key', callEnviron, wait=wait)
        if key < node.getKey():
            if animation:
                self.highlightCode(
                    'node.left, flag = self.__insert(node.left, key, data)',
                    callEnviron, wait=wait)
                colors = self.fadeNonLocalItems(localVars)
                
            # insert on left and update the left link
            newLeft, flag = self.__insert(
                self.getLeftChildIndex(nodeIndex), key, animation=animation)
            self.setLeftChild(node, newLeft)
            self.canvas.coords(newLeft.getLine(), 
                               *self.lineCoordinates(newLeft, node))
            if animation:
                self.restoreLocalItems(localVars, colors)
                flagText = self.createFlagText(flag)
                callEnviron.add(flagText)
                localVars += (flagText,)
                self.highlightCode('node.heightDiff() > 1', callEnviron,
                                   wait=wait)

          # If insert made node left heavy
            if self.heightDiff(node, callEnviron, wait / 20) > 1:
                if animation:
                    self.highlightCode('node.left.key < key', callEnviron)
                    
                leftChild = self.getLeftChild(node)
                if leftChild.getKey() < key:                             
                    if animation:
                        self.highlightCode(
                            'node.left = self.rotateLeft(node.left)', 
                            callEnviron)
                        colors = self.fadeNonLocalItems(localVars)
                    self.setLeftChild(
                        node, self.rotateLeft(leftChild, animation=animation),
                        updateLink=True)
                    if animation:
                        self.restoreLocalItems(localVars, colors)

                if animation:
                    self.highlightCode('node = self.rotateRight(node)',
                                       callEnviron)
                    colors = self.fadeNonLocalItems(localVars)
                node = self.rotateRight(node, animation=animation)
                if animation:
                    self.restoreLocalItems(localVars, colors)
          
        # Otherwise key belongs in right subtree
        else:
            if animation:
                self.highlightCode(
                    'node.right, flag = self.__insert(node.right, key, data)',
                    callEnviron, wait=wait)
                colors = self.fadeNonLocalItems(localVars)
            # Insert it on right and update the right link 
            newRight, flag = self.__insert(
                self.getRightChildIndex(nodeIndex), key, animation=animation)
            self.setRightChild(node, newRight)
            self.canvas.coords(newRight.getLine(), 
                               *self.lineCoordinates(newRight, node))
            if animation:
                self.restoreLocalItems(localVars, colors)
                flagText = self.createFlagText(flag)
                callEnviron.add(flagText)
                localVars += (flagText,)
                self.highlightCode('node.heightDiff() < -1', callEnviron,
                                   wait=wait)
            
            # If insert made node right heavy
            if self.heightDiff(node, callEnviron, wait / 20) < -1:
                if animation:
                    self.highlightCode('key < node.right.key', callEnviron)
                    
                rightChild = self.getRightChild(node)
                if key < rightChild.getKey():
                    if animation:
                        self.highlightCode(
                            'node.right = self.rotateRight(node.right)', 
                            callEnviron)
                        colors = self.fadeNonLocalItems(localVars)
                    self.setRightChild(
                        node, self.rotateRight(rightChild, animation=animation),
                        updateLink=True)
                    if animation:
                        self.restoreLocalItems(localVars)
                if animation:
                    self.highlightCode('node = self.rotateLeft(node)',
                                       callEnviron)
                    colors = self.fadeNonLocalItems(localVars)
                node = self.rotateLeft(node, animation=animation)
                if animation:
                    self.restoreLocalItems(localVars)

        if animation:
            self.highlightCode('node.updateHeight()', callEnviron)
        self.updateHeight(node, animation=animation)

        if animation:
            self.highlightCode('return node, flag', callEnviron)
        self.cleanUp(callEnviron)
        return node, flag       # Return the updated node & insert flag

    rotateLeftCode = '''
def rotateLeft(self, top):
   toRaise = top.right
   top.right = toRaise.left
   toRaise.left = top
   top.updateHeight()
   toRaise.updateHeight()
   return toRaise
'''
    
    def rotateLeft(self, top, animation=True, code=rotateLeftCode, wait=0.1):
        "rotate a subtree to the left in the array and animate it"
        callEnviron = self.createCallEnvironment(
            code=code if animation else '', startAnimations=animation,
            sleepTime=wait / 10)

        topIndex = self.getIndex(top) if isinstance(top, Node) else top
        topNode = self.getNode(topIndex)
        topParentLine = topNode.getLine()
        if animation:
            self.disconnectLink(topNode, sleepTime=wait / 10)
            topArrow = self.createArrow(topIndex, 'top', level=2)
            callEnviron |= set(topArrow)
            
        # the node to raise is top's right child
        if animation:
            self.highlightCode('toRaise = top.right', callEnviron, wait=wait)
        toRaise = self.getRightChild(top)
        if animation:
            toRaiseArrow = self.createArrow(toRaise, 'toRaise')
            callEnviron |= set(toRaiseArrow)

        # save subtrees
        topLeft = self.getLeftChild(top)
        topLeftTree = self.getNodeTree(topLeft)
        toRaiseNode = self.getNode(toRaise)
        toRaiseLeft, toRaiseRight = self.getChildren(toRaise)
        toRaiseLeftTree = self.getNodeTree(toRaiseLeft)
        toRaiseRightTree = self.getNodeTree(toRaiseRight)

        if animation:
            self.highlightCode('top.right = toRaise.left', callEnviron)
            link1 = self.moveLink(top, toRaise, top, toRaiseLeft, callEnviron, 
                                  sleepTime=wait / 10)
            self.highlightCode('toRaise.left = top', callEnviron)
            link2 = self.moveLink(toRaise, toRaiseLeft, toRaise, top,
                                  callEnviron, sleepTime=wait / 10)
            if toRaiseLeft:
                toRaiseLeft.setLine(link1)
                callEnviron.discard(link1)
            topNode.setLine(link2)
            callEnviron.discard(link2)
        else:
            topNode.setLine(toRaise.getLine())

        # Move nodes internally
        self.storeNodeTree(
            [toRaiseNode, 
             [topNode, topLeftTree, toRaiseLeftTree], toRaiseRightTree],
            topIndex)
        toRaise.setLine(topParentLine)

        # Move canvas items to new positions to match internal structure
        newSubTree = self.getAllDescendants(topIndex)
        newSubTreeItems = flat(*(
            node.drawnValue.items for node in newSubTree))[1:]
        toPositions = flat(*(
            self.nodeItemCoords(node, parent=self.getParent(node)) 
            for node in newSubTree))[1:]
        if animation:
            self.moveItemsLinearly(
                newSubTreeItems + topArrow + toRaiseArrow, 
                toPositions + self.indexCoords(topNode, 2) +
                self.indexCoords(toRaiseNode, 1), sleepTime=wait / 10)
        else:
            for item, coords in zip(newSubTreeItems, toPositions):
                self.canvas.coords(item, *coords)
                
        # Update heights of rotated nodes
        if animation:
            self.highlightCode('top.updateHeight()', callEnviron)
        self.updateHeight(top, animation=animation)
        if animation:
            self.highlightCode('toRaise.updateHeight()', callEnviron)
        self.updateHeight(topIndex, animation=animation)
        
        # Return raised node to update parent
        if animation:
            self.highlightCode('return toRaise', callEnviron)
        self.cleanUp(callEnviron)
        return toRaise

    rotateRightCode = '''
def rotateRight(self, top):
   toRaise = top.left
   top.left = toRaise.right
   toRaise.right = top
   top.updateHeight()
   toRaise.updateHeight()
   return toRaise
'''
    
    def rotateRight(self, top, animation=True, code=rotateRightCode, wait=0.1):
        "rotate a subtree to the right in the array and animate it"
        callEnviron = self.createCallEnvironment(
            code=code if animation else '', startAnimations=animation,
            sleepTime=wait / 10)

        topIndex = self.getIndex(top) if isinstance(top, Node) else top
        topNode = self.getNode(topIndex)
        topParentLine = topNode.getLine()
        if animation:
            self.disconnectLink(topNode, sleepTime=wait / 10)
            topArrow = self.createArrow(topIndex, 'top', level=2)
            callEnviron |= set(topArrow)
            
        # the node to raise is top's left child
        if animation:
            self.highlightCode('toRaise = top.left', callEnviron, wait=wait)
        toRaise = self.getLeftChild(top)
        if animation:
            toRaiseArrow = self.createArrow(toRaise, 'toRaise')
            callEnviron |= set(toRaiseArrow)

        # save subtrees
        topRight = self.getRightChild(top)
        topRightTree = self.getNodeTree(topRight)
        toRaiseNode = self.getNode(toRaise)
        toRaiseLeft, toRaiseRight = self.getChildren(toRaise)
        toRaiseRightTree = self.getNodeTree(toRaiseRight)
        toRaiseLeftTree = self.getNodeTree(toRaiseLeft)

        if animation:
            self.highlightCode('top.left = toRaise.right', callEnviron)
            link1 = self.moveLink(top, toRaise, top, toRaiseRight, callEnviron, 
                                  sleepTime=wait / 10)
            self.highlightCode('toRaise.right = top', callEnviron)
            link2 = self.moveLink(toRaise, toRaiseRight, toRaise, top,
                                  callEnviron, sleepTime=wait / 10)
            if toRaiseRight:
                toRaiseRight.setLine(link1)
                callEnviron.discard(link1)
            topNode.setLine(link2)
            callEnviron.discard(link2)
        else:
            topNode.setLine(toRaise.getLine())

        # Move nodes internally
        self.storeNodeTree(
            [toRaiseNode, toRaiseLeftTree, 
             [topNode, toRaiseRightTree, topRightTree]],
            topIndex)
        toRaise.setLine(topParentLine)

        # Move canvas items to new positions to match internal structure
        newSubTree = self.getAllDescendants(topIndex)
        newSubTreeItems = flat(*(
            node.drawnValue.items for node in newSubTree))[1:]
        toPositions = flat(*(
            self.nodeItemCoords(node, parent=self.getParent(node)) 
            for node in newSubTree))[1:]
        if animation:
            self.moveItemsLinearly(
                newSubTreeItems + topArrow + toRaiseArrow, 
                toPositions + self.indexCoords(topNode, 2) +
                self.indexCoords(toRaiseNode, 1), sleepTime=wait / 10)
        else:
            for item, coords in zip(newSubTreeItems, toPositions):
                self.canvas.coords(item, *coords)
                
        # Update heights of rotated nodes
        if animation:
            self.highlightCode('top.updateHeight()', callEnviron)
        self.updateHeight(top, animation=animation)
        if animation:
            self.highlightCode('toRaise.updateHeight()', callEnviron)
        self.updateHeight(topIndex, animation=animation)
        
        # Return raised node to update parent
        if animation:
            self.highlightCode('return toRaise', callEnviron)
        self.cleanUp(callEnviron)
        return toRaise

    def createFlagText(self, flagValue):
        return self.canvas.create_text(
            self.RECT[0] + 10, self.ROOT_Y0, text='flag = {}'.format(flagValue),
            anchor=W, font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)

    def disconnectLink(self, node, sleepTime=0.01):
        'Shorten the link from a node to its parent before a rotation'
        parent = self.getParent(node)
        if parent:
            line = node.getLine()
            currentCoords = self.canvas.coords(line)
            delta = V(currentCoords[2:]) - V(currentCoords[:2])
            distance = V(delta).vlen()
            newCoords = (V(currentCoords[2:]) - V(
                V(V(delta) / distance) * (distance - self.CIRCLE_SIZE * 2))
                        ) + tuple(currentCoords[2:])
            self.moveItemsLinearly(line, newCoords, sleepTime=sleepTime)
        
    def moveLink(self, fromParent, fromChild, toParent, toChild, callEnviron,
                 sleepTime=0.01, updateNodeLine=False):
        '''Reposition a link between parent and child as part of a rotation.
        The new link must share either the parent or the child with the
        existing link.  Update the line in the child node if requested.
        '''
        sharedParent = fromParent == toParent
        child = self.getNode(fromChild if sharedParent and fromChild else
                             toParent)
        lineToMove = child.getLine()
        newLine = self.copyCanvasItem(lineToMove)
        self.canvas.tag_lower(newLine)
        callEnviron.add(newLine)
        lineToMoveCoords = self.canvas.coords(lineToMove)

        # Make old line zero length, hence, invisible
        self.canvas.coords(
            lineToMove, *lineToMoveCoords[:2], *lineToMoveCoords[:2])
        newLineCoords = (
            self.nodeCenter(toChild if toChild else toParent)
            + self.nodeCenter(toParent) if sharedParent else
            (self.nodeCenter(toParent) + 
             (self.nodeCenter(toChild if toChild else toParent))))
        self.moveItemsLinearly(newLine, newLineCoords, sleepTime=sleepTime)
        if updateNodeLine:
            callEnviron.add(child.getLine())
            if newLineCoords[:2] == newLineCoords[2:]:
                self.canvas.coords(newLine, child.center + child.center)
            child.setLine(newLine)
            callEnviron.discard(newLine)
        return newLine
        
    # create a Node object with a given key at a particular nodeIndex or center
    def createNode(
            self, key, nodeIndex, center=None, parent=None, color=None,
            addToArray=True):
      
        # calculate the node's center, if not provided
        if center is None:
            center = self.nodeCenter(nodeIndex)

        # generate a tag
        tag = self.generateTag()
      
        # create the canvas items and the drawnValue object
        drawnValueObj = drawnValue(key, *self.createNodeShape(
            *center, key, tag, height=1, parent=parent.center if parent else None,
            color=color))
      
        # create the Node object
        node = Node(drawnValueObj, center, tag)

        # increment size
        self.size += 1

        # add the node object to the internal representation
        if addToArray and 0 <= nodeIndex and nodeIndex < len(self.nodes):
            self.nodes[nodeIndex] = node

        return node

    def nodeHeightCoords(self, x, y, radius=None, font=None):
        if radius is None: radius = self.CIRCLE_SIZE
        if font is None: font = self.VALUE_FONT
        return x + 3, int(y - radius - abs(font[1]))
   
    def nodeItemCoords(self, node, radius=None, **kwargs):
        '''Return coordinates for line to parent, shape, text label, and
        height items that represent a node.  The node can be either a
        Node, a node index, or a coordinate tuple for the center of the node.
        '''
        center = self.nodeCenter(node) if isinstance(node, (Node, int)) else node
        font = kwargs.get('font', self.VALUE_FONT)
        return super().nodeItemCoords(node, radius=radius, **kwargs) + (
            self.nodeHeightCoords(*center, radius=radius, font=font),)
      
    def createNodeShape(self, x, y, key, tag, height=1, **kwargs):
        font = kwargs.get('font', self.VALUE_FONT)
        return super().createNodeShape(x, y, key, tag, **kwargs) + (
            self.canvas.create_text(
                *self.nodeHeightCoords(
                    x, y, radius=kwargs.get('radius', None), font=font), 
                anchor=W, text=str(height), font=font, fill='orange',
                tags = (tag, "height")),)
    
    def heightDiff(self, node, callEnviron=None, sleepTime=0):
        '''Return difference in node's child heights.  Animate calculation
        if callEnviron is provided.'''
        leftChild, rightChild = self.getChildren(node)
        left = self.getHeight(leftChild) if leftChild else 0
        right = self.getHeight(rightChild) if rightChild else 0

        if callEnviron:
            font = self.VALUE_FONT
            leftText = (
                self.copyCanvasItem(leftChild.drawnValue.items[-1])
                if leftChild else
                self.canvas.create_text(
                    *self.nodeHeightCoords(
                        *self.nodeCenter(self.getLeftChildIndex(node))),
                    font=font, anchor=W, text=str(left), fill='orange',
                    tags="height"))
            rightText = (
                self.copyCanvasItem(rightChild.drawnValue.items[-1])
                if rightChild else
                self.canvas.create_text(
                    *self.nodeHeightCoords(
                        *self.nodeCenter(self.getRightChildIndex(node))),
                    font=font, anchor=W, text=str(right), fill='orange',
                    tags="height"))
            middle = V(V(self.canvas.coords(leftText)) +
                       V(self.canvas.coords(rightText))) / 2
            middleText = self.canvas.create_text(
                *middle, anchor=W, text=' - ', font=font, fill='orange')
            callEnviron |= set((leftText, middleText, rightText))
            middleWidth = self.textWidth(font, ' - ')
            delta = (middleWidth // 2, 0)
            self.moveItemsTo(
                (leftText, rightText), 
                (V(middle) - V(delta), V(middle) + V(delta)), 
                sleepTime=sleepTime)
            self.wait(sleepTime * 3)
            self.moveItemsTo(
                (leftText, rightText), (middle, middle), sleepTime=sleepTime)
            self.canvas.delete(leftText)
            self.canvas.delete(rightText)
            callEnviron -= set((leftText, rightText))
            self.canvas.itemconfigure(middleText, text=str(left - right))
            self.wait(sleepTime * 10)
            self.canvas.delete(middleText)
            callEnviron.discard(middleText)

        return left - right

    # override height from BinaryTreeBase.py
    def getHeight(self, node):
        if not node or (isinstance(node, int) and not self.getNode(node)):
            return 0

        rightChild = self.getRightChild(node)
        leftChild = self.getLeftChild(node)

        return max(self.getHeight(rightChild), self.getHeight(leftChild)) + 1

    def clickInsert(self):
        val = self.validArgument()
        if val:
            self.insert(val, start=self.startMode())
            self.window.update()
        self.clearArgument()

    def clickRandomFill(self):
        val = self.validArgument()
        if val:
            self.randomFill(val)
            self.window.update()
        self.clearArgument()

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                    '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.insertButton = self.addOperation(
            "Insert", self.clickInsert, numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Insert item in tree')
        searchButton = self.addOperation(
            "Search", self.clickSearch, numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Search for an item in tree')
        randomFillButton = self.addOperation(
            "Random Fill", self.clickRandomFill, numArguments=1,
            validationCmd= vcmd, argHelpText=['nuber of items'],
            helpText='Fiill tree with N random items')
        newTreeButton = self.addOperation(
            "New Tree", self.newTree,
            helpText='Create an empty tree')
        inOrderButton = self.addOperation(
            "In-order Traverse", lambda: self.clickTraverse('in'), 
            helpText='Traverse tree in in-order')
        #this makes the pause, play and stop buttons 
        self.addAnimationButtons()
        return [self.insertButton, randomFillButton]

if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    tree = AVLTree()
    for arg in sys.argv[1:]:
        tree.setArgument(arg)
        tree.insertButton.invoke()
    tree.runVisualization()
