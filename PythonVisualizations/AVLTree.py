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
        self.makeButtons()
        self.display(treeLabel='AVLtree')
        self.HEIGHT_COLOR = 'orange'

    def newTree(self):
        self.emptyTree()
        self.display(treeLabel='AVLtree')

    def randomFill(self, numNodes):
        callEnviron = self.createCallEnvironment()

        #randomly generate a tree
        nums = list(range(self.valMax + 1))
        random.shuffle(nums)
        nums = nums[:numNodes]
        while nums:
            self.insert(nums.pop(), animation=False)
        self.cleanUp(callEnviron)

    updateHeightCode = '''
def updateHeight(self):
   self.height = max(
      child.height if child else 0
      for child in (self.left, self.right)
   ) + 1
'''
    def updateHeight(
            self,
            node: 'Node in tree to update',
            code: 'Code to display' =updateHeightCode,
            animation: 'Animate the update' =True,
            wait: 'Wait time between steps' =0.1):
        callEnviron = self.createCallEnvironment(
            code=code if animation else '', startAnimations=animation)

        heightText = self.getNode(node).drawnValue.items[-1]
        height = 0
        childArrow, childArrowConfig = None, {'orientation': -160, 'anchor': SE}
        childHeightTexts = []
        for side in Child:
            childIndex = self.getChildIndex(node, side)
            child = self.getNode(childIndex)
            if animation:
                nodeCenter = self.nodeItemCoords(node)[2]
                childCenter = self.nodeItemCoords(childIndex)[2]
                childHeightCoords = self.nodeHeightCoords(*childCenter)
                childHeightCenter = (nodeCenter[0], childHeightCoords[1])
                if childArrow is None:
                    childArrow = self.createArrow(
                        childIndex, 'child', **childArrowConfig)
                    callEnviron |= set(childArrow)
                else:
                    self.moveItemsTo(
                        childArrow,
                        self.indexCoords(childIndex, **childArrowConfig),
                        sleepTime=wait / 50)
                self.highlightCode(
                    ('child in', ('child', 2), 'self.' + side.name.lower(),
                     'child.height' if child else '0'),
                    callEnviron, wait=wait)
            childHeight = self.getHeight(child)
            height = max(height, childHeight)
            if animation:
                childHeightText = (
                    self.canvas.create_text(
                        *childHeightCoords, text='{} '.format(childHeight),
                        fill=self.HEIGHT_COLOR, font=self.VALUE_FONT, anchor=E)
                    if side is Child.LEFT else
                    self.canvas.create_text(
                        *childHeightCoords, text=' {}'.format(childHeight),
                        fill=self.HEIGHT_COLOR, font=self.VALUE_FONT, anchor=W))
                callEnviron.add(childHeightText)
                childHeightTexts.append(childHeightText)
                self.moveItemsTo(
                    childHeightText, childHeightCenter, sleepTime=wait / 20)

        if animation:
            self.dispose(callEnviron, *childArrow)
            self.highlightCode(('self.height = max(', ') + 1'),
                               callEnviron, wait=wait)
            nodeHeightCenter = self.nodeHeightCoords(*nodeCenter)
            self.moveItemsTo(
                childHeightTexts, (nodeHeightCenter,) * 2, sleepTime=wait / 20)
            self.dispose(callEnviron, *childHeightTexts)

        self.canvas.itemConfig(heightText, text=str(height + 1))
        if animation:
            self.highlightCode([], callEnviron)
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
        nodeIndex = max(0, self.getIndex(node))
        node = self.getNode(nodeIndex)
        callEnviron = self.createCallEnvironment(
            code=code.format(
                nodeKey=node.getKey() if node else None, **locals()) 
            if animation else '', startAnimations=animation, sleepTime=wait / 10)

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
                key, nodeIndex, parent=None, addToArray=False,
                center=self.newValueCoords() if animation else None)
            self.setLeftChild(nodeIndex, None) # Ensure that inserted node
            self.setRightChild(nodeIndex, None) # is a leaf node
            if animation:
                itemCoords = self.nodeItemCoords(nodeIndex)
                self.moveItemsTo(insertedNode.drawnValue.items, itemCoords,
                                 sleepTime=wait / 10)
                insertedNode.center = itemCoords[2]
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return insertedNode, True
        
        # Check for existing key
        if animation:
            self.highlightCode('key == node.key', callEnviron, wait=wait)
        if key == node.getKey():
            link, dataItem, keyItem, heightItem = self.createNodeShape(
                *self.newValueCoords(buffer=50), key, node.tag)
            for item in (link, keyItem, heightItem):
                self.canvas.delete(item)
            callEnviron.add(dataItem)
            nodeItems = node.drawnValue.items
            if animation:
                self.canvas.tag_lower(dataItem, nodeItems[2])
                self.highlightCode('node.data = data', callEnviron, wait=wait)
                self.moveItemsTo(dataItem, self.canvas.coords(nodeItems[1]),
                                 sleepTime=wait / 10)
            self.canvas.copyItemAttributes(dataItem, nodeItems[1], 'fill')

            if animation:
                self.highlightCode('return node, False', callEnviron)
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return node, False

        # don't insert past MAX_LEVEL
        if self.getLevel(node) == self.MAX_LEVEL-1:
            if animation:
                self.setMessage(
                    "Error! Cannot insert at level " + str(self.MAX_LEVEL) + 
                    " or below")
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return node, False
          
        # Does the key belong in left subtree?
        if animation:
            self.highlightCode('key < node.key', callEnviron, wait=wait)
        if key < node.getKey():
            if animation:
                self.highlightCode(
                    'node.left, flag = self.__insert(node.left, key, data)',
                    callEnviron, wait=wait)
                colors = self.canvas.fadeItems(localVars)
                
            # insert on left and update the left link
            newLeft, flag = self.__insert(
                self.getLeftChildIndex(nodeIndex), key, animation=animation)
            self.setLeftChild(node, newLeft)
            link = newLeft.getLine()
            if animation:
                self.canvas.restoreItems(localVars, colors)
                linkCoords = self.canvas.coords(link)
                if distance2(linkCoords[:2], linkCoords[2:]) < 1:
                    self.canvas.coords(link, node.center + node.center)
                self.moveItemsLinearly(
                    link, self.lineCoordinates(newLeft, node), 
                    sleepTime=wait / 10)
            else:
                self.canvas.coords(link, 
                                   *self.lineCoordinates(newLeft, node))
            if animation:
                flagText = self.createFlagText(flag)
                callEnviron.add(flagText)
                localVars += (flagText,)
                self.highlightCode('node.heightDiff() > 1', callEnviron,
                                   wait=wait)

            # If insert made node left heavy
            if self.heightDiff(node, callEnviron, wait / 10) > 1:
                if animation:
                    self.highlightCode('node.left.key < key', callEnviron)
                    
                leftChild = self.getLeftChild(node)
                if leftChild.getKey() < key:                             
                    if animation:
                        self.highlightCode(
                            'node.left = self.rotateLeft(node.left)', 
                            callEnviron)
                        colors = self.canvas.fadeItems(localVars)
                    self.setLeftChild(
                        node, self.rotateLeft(leftChild, animation=animation),
                        updateLink=True)
                    if animation:
                        self.canvas.restoreItems(localVars, colors)

                if animation:
                    self.highlightCode('node = self.rotateRight(node)',
                                       callEnviron)
                    colors = self.canvas.fadeItems(localVars)
                node = self.rotateRight(node, animation=animation)
                if animation:
                    self.canvas.restoreItems(localVars, colors)
          
        # Otherwise key belongs in right subtree
        else:
            if animation:
                self.highlightCode(
                    'node.right, flag = self.__insert(node.right, key, data)',
                    callEnviron, wait=wait)
                colors = self.canvas.fadeItems(localVars)
            # Insert it on right and update the right link 
            newRight, flag = self.__insert(
                self.getRightChildIndex(nodeIndex), key, animation=animation)
            self.setRightChild(node, newRight)
            link = newRight.getLine()
            if animation:
                self.canvas.restoreItems(localVars, colors)
                linkCoords = self.canvas.coords(link)
                if distance2(linkCoords[:2], linkCoords[2:]) < 1:
                    self.canvas.coords(link, node.center + node.center)
                self.moveItemsLinearly(
                    link, self.lineCoordinates(newRight, node), 
                    sleepTime=wait / 10)
            else:
                self.canvas.coords(link, 
                                   *self.lineCoordinates(newRight, node))
            if animation:
                flagText = self.createFlagText(flag)
                callEnviron.add(flagText)
                localVars += (flagText,)
                self.highlightCode('node.heightDiff() < -1', callEnviron,
                                   wait=wait)
            
            # If insert made node right heavy
            if self.heightDiff(node, callEnviron, wait / 10) < -1:
                if animation:
                    self.highlightCode('key < node.right.key', callEnviron)
                    
                rightChild = self.getRightChild(node)
                if key < rightChild.getKey():
                    if animation:
                        self.highlightCode(
                            'node.right = self.rotateRight(node.right)', 
                            callEnviron)
                        colors = self.canvas.fadeItems(localVars)
                    self.setRightChild(
                        node, self.rotateRight(rightChild, animation=animation),
                        updateLink=True)
                    if animation:
                        self.canvas.restoreItems(localVars, colors)
                if animation:
                    self.highlightCode('node = self.rotateLeft(node)',
                                       callEnviron)
                    colors = self.canvas.fadeItems(localVars)
                node = self.rotateLeft(node, animation=animation)
                if animation:
                    self.canvas.restoreItems(localVars, colors)

        if animation:
            self.highlightCode('node.updateHeight()', callEnviron)
        self.updateHeight(node, animation=animation)

        if animation:
            self.highlightCode('return node, flag', callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)
        return node, flag       # Return the updated node & insert flag

    rotateLeftCode = '''
def rotateLeft(self, top={topKey}):
   toRaise = top.right
   top.right = toRaise.left
   toRaise.left = top
   top.updateHeight()
   toRaise.updateHeight()
   return toRaise
'''
    
    def rotateLeft(self, top, animation=True, code=rotateLeftCode, wait=0.1):
        "rotate a subtree to the left in the array and animate it"
        topIndex = self.getIndex(top) if isinstance(top, Node) else top
        topNode = self.getNode(topIndex)
        topParentLine = topNode.getLine()
        callEnviron = self.createCallEnvironment(
            code=code.format(topKey=topNode.getKey() if topNode else None) if
            animation else '', startAnimations=animation, sleepTime=wait / 10)

        if animation:
            topArrow = self.createArrow(topIndex, 'top', level=2)
            callEnviron |= set(topArrow)
            self.disconnectLink(topNode, sleepTime=wait / 10)
            
        # the node to raise is top's right child
        if animation:
            self.highlightCode('toRaise = top.right', callEnviron, wait=wait)
        toRaise = self.getRightChild(top)
        if animation:
            toRaiseArrow = self.createArrow(toRaise, 'toRaise')
            callEnviron |= set(toRaiseArrow)

        # Get key nodes
        topLeft = self.getLeftChild(top)
        toRaiseNode = self.getNode(toRaise)
        toRaiseLeft, toRaiseRight = self.getChildren(toRaise)

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

        # Extract current subtrees
        topLeftTree = self.getNodeTree(topLeft, erase=True)
        toRaiseLeftTree = self.getNodeTree(toRaiseLeft, erase=True)
        toRaiseRightTree = self.getNodeTree(toRaiseRight, erase=True)

        # Move nodes internally, noting any nodes cutoff past depth limit
        cutoff = self.storeNodeTree(
            [toRaiseNode, 
             [topNode, topLeftTree, toRaiseLeftTree], toRaiseRightTree],
            topIndex)
        toRaise.setLine(topParentLine)

        # Move canvas items to new positions to match internal structure
        newSubTree = self.getAllDescendants(topIndex)
        newSubTreeItems = flat(*(
            node.drawnValue.items for node in newSubTree + list(cutoff)))[1:]
        toPositions = flat(*(
            self.nodeItemCoords(node, parent=self.getParent(node)) 
            for node in newSubTree + [len(self.nodes) * 3] * len(cutoff)))[1:]
        if animation:
            self.moveItemsLinearly(
                newSubTreeItems + topArrow + toRaiseArrow, 
                toPositions + self.indexCoords(topNode, 2) +
                self.indexCoords(toRaiseNode, 1), sleepTime=wait / 10)
        else:
            for item, coords in zip(newSubTreeItems, toPositions):
                self.canvas.coords(item, *coords)
        if cutoff and animation:
            self.setMessage(
                'Removed node{} {} that went beyond level {}'.format(
                    '' if len(cutoff) == 1 else 's',
                    ', '.join(str(node.getKey()) for node in cutoff),
                self.MAX_LEVEL - 1))
        self.dispose(callEnviron,
                     *flat(*(node.drawnValue.items for node in cutoff)))
                
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
def rotateRight(self, top={topKey}):
   toRaise = top.left
   top.left = toRaise.right
   toRaise.right = top
   top.updateHeight()
   toRaise.updateHeight()
   return toRaise
'''
    
    def rotateRight(self, top, animation=True, code=rotateRightCode, wait=0.1):
        "rotate a subtree to the right in the array and animate it"
        topIndex = self.getIndex(top) if isinstance(top, Node) else top
        topNode = self.getNode(topIndex)
        topParentLine = topNode.getLine()
        callEnviron = self.createCallEnvironment(
            code=code.format(topKey=topNode.getKey() if topNode else None) if
            animation else '', startAnimations=animation, sleepTime=wait / 10)

        if animation:
            topArrow = self.createArrow(topIndex, 'top', level=2)
            callEnviron |= set(topArrow)
            self.disconnectLink(topNode, sleepTime=wait / 10)
            
        # the node to raise is top's left child
        if animation:
            self.highlightCode('toRaise = top.left', callEnviron, wait=wait)
        toRaise = self.getLeftChild(top)
        if animation:
            toRaiseArrow = self.createArrow(toRaise, 'toRaise')
            callEnviron |= set(toRaiseArrow)

        # Get key nodes
        topRight = self.getRightChild(top)
        toRaiseNode = self.getNode(toRaise)
        toRaiseLeft, toRaiseRight = self.getChildren(toRaise)

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
            
        # Extract current subtrees
        topRightTree = self.getNodeTree(topRight, erase=True)
        toRaiseRightTree = self.getNodeTree(toRaiseRight, erase=True)
        toRaiseLeftTree = self.getNodeTree(toRaiseLeft, erase=True)

        # Move nodes internally, noting any nodes cutoff past depth limit
        cutoff = self.storeNodeTree(
            [toRaiseNode,
             toRaiseLeftTree, [topNode, toRaiseRightTree, topRightTree]],
            topIndex)
        toRaise.setLine(topParentLine)

        # Move canvas items to new positions to match internal structure
        newSubTree = self.getAllDescendants(topIndex)
        newSubTreeItems = flat(*(
            node.drawnValue.items for node in newSubTree + list(cutoff)))[1:]
        toPositions = flat(*(
            self.nodeItemCoords(node, parent=self.getParent(node)) 
            for node in newSubTree + [len(self.nodes) * 3] * len(cutoff)))[1:]
        if animation:
            self.moveItemsLinearly(
                newSubTreeItems + topArrow + toRaiseArrow, 
                toPositions + self.indexCoords(topNode, 2) +
                self.indexCoords(toRaiseNode, 1), sleepTime=wait / 10)
        else:
            for item, coords in zip(newSubTreeItems, toPositions):
                self.canvas.coords(item, *coords)
        if cutoff and animation:
            self.setMessage(
                'Removed node{} {} that went beyond level {}'.format(
                    '' if len(cutoff) == 1 else 's',
                    ', '.join(str(node.getKey()) for node in cutoff),
                self.MAX_LEVEL - 1))
        self.dispose(callEnviron,
                     *flat(*(node.drawnValue.items for node in cutoff)))
                
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

    deleteCode = '''
def delete(self, goal={goal}):
   self.__root, flag = self.__delete(self.__root, goal)
   return flag
'''
    
    def delete(self, goal, code=deleteCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        root = self.getRoot()
        self.highlightCode(
            'self.__root, flag = self.__delete(self.__root, goal)', callEnviron)
        newRoot, flag = self.__delete(root, goal)

        if newRoot != root and self.getIndex(newRoot) > 0:
            self.moveSubtree(0, self.getIndex(newRoot))
            if newRoot:
                link = newRoot.getLine()
                childCenter = self.canvas.coords(link)[:2]
                for step, steps in self.moveItemsOffCanvasSequence(
                        root.drawnValue.items):
                    self.canvas.coords(
                        link, *childCenter,
                        *(V(V(V(childCenter) * (step + 1)) +
                            V(V(root.center) * (steps - 1 - step))) 
                          / steps))
                    self.wait(wait / 10)
                for item in root.drawnValue.items:
                    self.canvas.delete(item)
                self.restoreNodePositions(self.getAllDescendants(newRoot),
                                          sleepTime=wait /10)
            else:
                self.moveItemsOffCanvas(
                    root.drawnValue.items, sleepTime=wait / 10)
                for item in root.drawnValue.items:
                    self.canvas.delete(item)
        self.updateTreeObjectRootPointer(root=self.getRoot())
        callEnviron.add(self.createFlagText(flag))
        
        self.highlightCode('return flag', callEnviron)
        self.cleanUp(callEnviron)
        return flag
        
    __deleteCode = '''
def __delete(self, node={nodeKey}, goal={goal}):
   if node is None:
      return None, False
   
   if goal < node.key:
      node.left, flag = self.__delete(node.left, goal)
      node = self.__balanceLeft(node)

   elif goal > node.key:
      node.right, flag = self.__delete(node.right, goal)
      node = self.__balanceRight(node)

   elif node.left is None:
      return node.right, True
   elif node.right is None:
      return node.left, True

   else:
      node.key, node.data, node.right= self.__deleteMin(node.right)
      node = self.__balanceRight(node)
      flag = True

   node.updateHeight()
   return node, flag
'''

    def __delete(self, node, goal, code=__deleteCode):
        wait = 0.1
        nodeIndex = -1 if node is None else (
            node if isinstance(node, int) else self.getIndex(node))
        node = self.getNode(nodeIndex)
        callEnviron = self.createCallEnvironment(code=code.format(
            nodeKey=None if node is None else node.getKey(), **locals()),
                                                 sleepTime=wait / 10)

        nodeArrow = self.createArrow(node or 0, 'node', level=1)
        callEnviron |= set(nodeArrow)
        localVars = nodeArrow
        
        self.highlightCode('node is None', callEnviron, wait=wait)
        if node is None or self.getNode(node) is None:
            self.highlightCode('return None, False', callEnviron)
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return None, False

        self.highlightCode('goal < node.key', callEnviron, wait=wait)
        if goal < node.getKey():
            self.highlightCode(
                'node.left, flag = self.__delete(node.left, goal)', callEnviron)
            leftChildIndex = self.getLeftChildIndex(nodeIndex)
            leftChild = self.getNode(leftChildIndex)
            colors = self.canvas.fadeItems(localVars)
            newLeft, flag = self.__delete(leftChild, goal)
            self.canvas.restoreItems(localVars, colors)
            if self.getIndex(newLeft) != leftChildIndex:
                self.moveSubtree(leftChildIndex, self.getIndex(newLeft))
                if leftChild and leftChild.getKey() == goal:
                    leftLink = leftChild.getLine()
                    childCenter = self.canvas.coords(leftLink)[:2]
                    newChildCenter = (newLeft if newLeft else node).center
                    for step, steps in self.moveItemsOffCanvasSequence(
                            leftChild.drawnValue.items[1:]):
                        self.canvas.coords(
                            leftLink,
                            *(V(V(V(newChildCenter) * (step + 1)) +
                                V(V(childCenter) * (steps - 1 - step))) 
                              / steps), *node.center)
                        self.wait(wait / 10)
                    for item in leftChild.drawnValue.items[1 if newLeft else 0:]:
                        self.canvas.delete(item)
                if newLeft and newLeft != leftChild:
                    self.canvas.delete(newLeft.getLine())
                    newLeft.setLine(leftLink)
                    self.restoreNodePositions(self.getAllDescendants(newLeft),
                                              sleepTime=wait /10)
            else:
                self.reconnectLink(
                    leftChildIndex, nodeIndex, sleepTime=wait / 10)
            flagText = self.createFlagText(flag)
            callEnviron.add(flagText)
            localVars += (flagText,)

            self.highlightCode('node = self.__balanceLeft(node)', callEnviron)
            colors = self.canvas.fadeItems(localVars)
            newNode = self.__balanceLeft(nodeIndex)
            self.canvas.restoreItems(localVars, colors)
            if newNode != node:
                self.moveItemsTo(nodeArrow, self.indexCoords(newNode, 1),
                                 sleepTime=wait / 10)
                node = newNode

        elif (self.highlightCode('goal > node.key', callEnviron, wait=wait) or
              goal > node.getKey()):
            self.highlightCode(
                'node.right, flag = self.__delete(node.right, goal)',
                callEnviron)
            colors = self.canvas.fadeItems(localVars)
            rightChildIndex = self.getRightChildIndex(nodeIndex)
            rightChild = self.getNode(rightChildIndex)
            newRight, flag = self.__delete(rightChild, goal)
            self.canvas.restoreItems(localVars, colors)
            if self.getIndex(newRight) != rightChildIndex:
                self.moveSubtree(rightChildIndex, self.getIndex(newRight))
                if rightChild and rightChild.getKey() == goal:
                    rightLink = rightChild.getLine()
                    childCenter = self.canvas.coords(rightLink)[:2]
                    newChildCenter = (newRight if newRight else node).center
                    for step, steps in self.moveItemsOffCanvasSequence(
                            rightChild.drawnValue.items[1:]):
                        self.canvas.coords(
                            rightLink,
                            *(V(V(V(newChildCenter) * (step + 1)) +
                                V(V(childCenter) * (steps - 1 - step))) 
                              / steps), *node.center)
                        self.wait(wait / 10)
                    for item in rightChild.drawnValue.items[1 if newRight else 0:]:
                        self.canvas.delete(item)

                if newRight and newRight != rightChild:
                    self.canvas.delete(newRight.getLine())
                    newRight.setLine(rightLink)
                    self.restoreNodePositions(self.getAllDescendants(newRight),
                                              sleepTime=wait /10)
            else:
                self.reconnectLink(
                    rightChildIndex, nodeIndex, sleepTime=wait / 10)
            flagText = self.createFlagText(flag)
            callEnviron.add(flagText)
            localVars += (flagText,)

            self.highlightCode('node = self.__balanceRight(node)', callEnviron)
            colors = self.canvas.fadeItems(localVars)
            newNode = self.__balanceRight(nodeIndex)
            self.canvas.restoreItems(localVars, colors)
            if newNode != node:
                self.moveItemsTo(nodeArrow, self.indexCoords(newNode, 1),
                                 sleepTime=wait / 10)
                node = newNode
            
        elif (self.highlightCode('node.left is None', callEnviron, wait=wait) or
              self.getNode(self.getLeftChildIndex(nodeIndex)) is None):
            self.highlightCode('return node.right, True', callEnviron)
            if self.getRightChild(nodeIndex) is None:
                self.removeNodeInternal(nodeIndex)
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return self.getRightChild(nodeIndex), True

        elif (self.highlightCode('node.right is None', callEnviron, wait=wait) or
              self.getNode(self.getRightChildIndex(nodeIndex)) is None):
            self.highlightCode('return node.left, True', callEnviron)
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return self.getLeftChild(nodeIndex), True
        
        else:
            self.highlightCode(
                'node.key, node.data, node.right= self.__deleteMin(node.right)',
                callEnviron)
            colors = self.canvas.fadeItems(localVars)
            successor, newRight = self.__deleteMin(
                self.getRightChildIndex(nodeIndex))
            self.canvas.restoreItems(localVars, colors)
            if successor != node:
                for item in successor.drawnValue.items[1:3]:
                    self.canvas.tag_raise(item)
                self.moveItemsTo(
                    successor.drawnValue.items[1:3], 
                    self.nodeItemCoords(nodeIndex)[1:3], sleepTime=wait / 10)
                self.canvas.itemConfig(
                    successor.drawnValue.items[1], 
                    fill=self.canvas.itemConfig(node.drawnValue.items[1],
                                                'fill'))
                for item in node.drawnValue.items[1:3]:
                    self.canvas.delete(item)
                node.drawnValue.items = (
                    node.drawnValue.items[0], *successor.drawnValue.items[1:3],
                    *node.drawnValue.items[3:])
                node.drawnValue.val = successor.drawnValue.val
                for i in (0, 3):
                    self.canvas.delete(successor.drawnValue.items[i])

            self.replaceSubtree(nodeIndex, Child.RIGHT, self.getIndex(newRight),
                                callEnviron, wait=wait)

            self.highlightCode('node = self.__balanceRight(node)', callEnviron)
            colors = self.canvas.fadeItems(localVars)
            newNode = self.__balanceRight(node)
            self.canvas.restoreItems(localVars, colors)
            if newNode != node:
                self.moveItemsTo(nodeArrow, self.indexCoords(newNode, 1),
                                 sleepTime=wait / 10)
                node = newNode

            self.highlightCode('flag = True', callEnviron, wait=wait)
            flag = True
            flagText = self.createFlagText(flag)
            callEnviron.add(flagText)

        self.highlightCode('node.updateHeight()', callEnviron)
        self.updateHeight(node)
            
        self.highlightCode('return node, flag', callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)
        return node, flag

    __deleteMinCode = '''
def __deleteMin(self, node={nodeKey}):
   if node.left is None:
      return (node.key, node.data, node.right)
   key, data, node.left = self.__deleteMin(node.left)
   node = self.__balanceLeft(node)
   node.updateHeight()
   return (key, data, node)
'''

    def __deleteMin(self, node, code=__deleteMinCode):
        wait = 0.1
        nodeIndex = -1 if node is None else (
            node if isinstance(node, int) else self.getIndex(node))
        node = self.getNode(nodeIndex)
        callEnviron = self.createCallEnvironment(code=code.format(
            nodeKey=None if node is None else node.getKey(), **locals()),
                                                 sleepTime=wait / 10)

        nodeArrow = self.createArrow(nodeIndex, 'node')
        callEnviron |= set(nodeArrow)
        localVars = nodeArrow
        
        self.highlightCode('node.left is None', callEnviron, wait=wait)
        leftChildIndex = self.getLeftChildIndex(nodeIndex)
        leftChild = self.getNode(leftChildIndex)
        if leftChild is None:     # If no left child, this node is the successor
            self.highlightCode('return (node.key, node.data, node.right)',
                               callEnviron)
            self.moveSuccessor(node, sleepTime=wait / 10)
            rightChild = self.getRightChild(nodeIndex)
            self.nodes[nodeIndex] = None    # Take successor node out of array
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return node, rightChild

        self.highlightCode('key, data, node.left = self.__deleteMin(node.left)',
                           callEnviron)
        colors = self.canvas.fadeItems(localVars)
        keyData, newLeft = self.__deleteMin(self.getLeftChildIndex(nodeIndex))
        self.canvas.restoreItems(localVars, colors)
        keyDataArrow = self.createArrow(keyData, 'key, data', anchor=SE)
        callEnviron |= set(keyDataArrow)
        localVars += keyDataArrow
        if newLeft != leftChild:
            self.replaceSubtree(nodeIndex, Child.LEFT, self.getIndex(newLeft),
                                callEnviron, wait=wait)
        
        self.highlightCode('node = self.__balanceLeft(node)', callEnviron)
        colors = self.canvas.fadeItems(localVars)
        newNode = self.__balanceLeft(nodeIndex)
        self.canvas.restoreItems(localVars, colors)
        if newNode != node:
            self.restoreNodePositions(self.getAllDescendants(newNode),
                                      sleepTime=wait /10)
            node = newNode
        
        self.highlightCode('node.updateHeight()', callEnviron)
        self.updateHeight(nodeIndex)

        self.highlightCode('return (key, data, node)', callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)
        return keyData, node

    def moveSuccessor(self, successor, sleepTime=0.01, color='LemonChiffon2'):
        newCenter = V(successor.center) - V(V(0.7, 2.2) * self.CIRCLE_SIZE)
        self.canvas.itemConfig(successor.drawnValue.items[1], fill=color)
        self.canvas.itemConfig(successor.drawnValue.items[-1], text='')
        self.moveItemsLinearly(successor.drawnValue.items, 
                               self.nodeItemCoords(newCenter, parent=None),
                               sleepTime=sleepTime)
        successor.center = newCenter
        
    __balanceLeftCode = '''
def __balanceLeft(self, node={nodeKey}):
   if node.heightDiff() < -1:
      if node.right.heightDiff() > 0:
         node.right = self.rotateRight(node.right)
         
      node = self.rotateLeft(node)
   return node
'''

    def __balanceLeft(self, node, code=__balanceLeftCode):
        wait = 0.1
        nodeIndex = -1 if node is None else (
            node if isinstance(node, int) else self.getIndex(node))
        node = self.getNode(nodeIndex)
        callEnviron = self.createCallEnvironment(code=code.format(
            nodeKey=None if node is None else node.getKey(), **locals()))
        nodeArrow = self.createArrow(node, 'node', anchor=SE)
        callEnviron |= set(nodeArrow)

        self.highlightCode('node.heightDiff() < -1', callEnviron)
        if self.heightDiff(node, callEnviron, wait / 10) < -1:
            rightChild = self.getRightChild(nodeIndex)
            self.highlightCode('node.right.heightDiff() > 0', callEnviron)
            if self.heightDiff(rightChild, callEnviron, wait / 10) > 0:
                self.highlightCode(
                    'node.right = self.rotateRight(node.right)', callEnviron)
                self.setRightChild(node, self.rotateRight(rightChild),
                                   updateLink=True)
                    
            self.highlightCode('node = self.rotateLeft(node)', callEnviron)
            node = self.rotateLeft(node)
            
        self.highlightCode('return node', callEnviron)
        self.cleanUp(callEnviron)
        return node

    __balanceRightCode = '''
def __balanceRight(self, node={nodeKey}):
   if node.heightDiff() > 1:
      if node.left.heightDiff() < 0:
         node.left = self.rotateLeft(node.left)
         
      node = self.rotateRight(node)
   return node
'''

    def __balanceRight(self, node, code=__balanceRightCode):
        wait = 0.1
        nodeIndex = -1 if node is None else (
            node if isinstance(node, int) else self.getIndex(node))
        node = self.getNode(nodeIndex)
        callEnviron = self.createCallEnvironment(code=code.format(
            nodeKey=None if node is None else node.getKey(), **locals()))
        nodeArrow = self.createArrow(node, 'node', anchor=SE)
        callEnviron |= set(nodeArrow)

        self.highlightCode('node.heightDiff() > 1', callEnviron)
        if self.heightDiff(node, callEnviron, wait / 10) > 1:
            leftChild = self.getLeftChild(nodeIndex)
            self.highlightCode('node.left.heightDiff() < 0', callEnviron)
            if self.heightDiff(leftChild, callEnviron, wait / 10) < 0:
                self.highlightCode(
                    'node.left = self.rotateLeft(node.left)', callEnviron)
                self.setLeftChild(
                    node, self.rotateLeft(leftChild), updateLink=True)
                    
            self.highlightCode('node = self.rotateRight(node)', callEnviron)
            node = self.rotateRight(node)
            
        self.highlightCode('return node', callEnviron)
        self.cleanUp(callEnviron)
        return node
    
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

    def reconnectLink(self, childIndex, nodeIndex, sleepTime=0.01):
        'Reconnect the link from a child to its parent after a rotation'
        child, parent = self.getNode(childIndex), self.getNode(nodeIndex)
        line = child.getLine()
        currentCoords = self.canvas.coords(line)
        newCoords = child.center + (parent.center if parent else child.center)
        if distance2(currentCoords, newCoords) > 1:
            self.moveItemsLinearly(line, newCoords, sleepTime=sleepTime)
            
    def moveLink(self, fromParent, fromChild, toParent, toChild, callEnviron,
                 sleepTime=0.01, updateNodeLine=False):
        '''Reposition a link between parent and child as part of a tree
        transformation by copying the existing link and moving it.
        The new link must share either the parent or the child with
        the existing link. All node arguments must be Nodes, not indices.
        Update the line in the child node if requested, otherwise leave
        the new copy in the call environment.
        '''
        sharedParent = fromParent == toParent
        child = fromChild if fromChild else toParent
        lineToMove = child.getLine()
        newLine = self.canvas.copyItem(lineToMove)
        self.canvas.tag_lower(newLine)
        callEnviron.add(newLine)
        lineToMoveCoords = self.canvas.coords(lineToMove)

        # Make old line zero length, hence, invisible
        self.canvas.coords(
            lineToMove, *lineToMoveCoords[:2], *lineToMoveCoords[:2])
        newLineCoords = (
            (toChild if toChild else toParent).center + toParent.center 
            if sharedParent else
            toParent.center + (toChild if toChild else toParent).center)
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
        dX = 3 if (y - self.ROOT_Y0) // self.LEVEL_GAP < self.MAX_LEVEL - 1 else 0
        return x + dX, int(y - radius - abs(font[1]))
   
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
                anchor=W, text=str(height), font=font, fill=self.HEIGHT_COLOR,
                tags = (tag, "height")),)
    
    def heightDiff(self, node, callEnviron=None, sleepTime=0):
        '''Return difference in node's child heights.  Animate calculation
        if callEnviron is provided.'''
        leftChild, rightChild = self.getChildren(node)
        left = self.getHeight(leftChild) if leftChild else 0
        right = self.getHeight(rightChild) if rightChild else 0
        fill=self.HEIGHT_COLOR

        if callEnviron:
            font = self.VALUE_FONT
            leftText = (
                self.canvas.copyItem(leftChild.drawnValue.items[-1])
                if leftChild else
                self.canvas.create_text(
                    *self.nodeHeightCoords(
                        *self.nodeCenter(self.getLeftChildIndex(node))),
                    font=font, anchor=W, text=str(left), fill=fill,
                    tags="height"))
            rightText = (
                self.canvas.copyItem(rightChild.drawnValue.items[-1])
                if rightChild else
                self.canvas.create_text(
                    *self.nodeHeightCoords(
                        *self.nodeCenter(self.getRightChildIndex(node))),
                    font=font, anchor=W, text=str(right), fill=fill,
                    tags="height"))
            middle = V(V(self.canvas.coords(leftText)) +
                       V(self.canvas.coords(rightText))) / 2
            middleText = self.canvas.create_text(
                *middle, anchor=W, text=' - ', font=font, fill=fill)
            callEnviron |= set((leftText, middleText, rightText))
            middleWidth = textWidth(font, ' - ')
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
            self.canvas.itemConfig(middleText, text=str(left - right))
            self.wait(sleepTime * 20)
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
            self.setMessage('Value {}{} inserted'.format(
                val, 
                '' if self.insert(val, start=self.startMode()) else ' not'))
            self.clearArgument()

    def clickDelete(self):
        val = self.validArgument()
        if val:
            self.setMessage('Value {}{} deleted'.format(
                val, 
                '' if self.delete(val, start=self.startMode()) else ' not'))
            self.clearArgument()

    def clickRandomFill(self):
        val = self.validArgument()
        if val:
            self.randomFill(val)
        self.clearArgument()

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                    '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.insertButton = self.addOperation(
            "Insert", self.clickInsert, numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Insert item in tree')
        self.searchButton = self.addOperation(
            "Search", self.clickSearch, numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Search for an item in tree')
        self.deleteButton = self.addOperation(
            "Delete", self.clickDelete, numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Delete item from tree')
        self.randomFillButton = self.addOperation(
            "Random Fill", self.clickRandomFill, numArguments=1,
            validationCmd= vcmd, argHelpText=['number of items'],
            helpText='Fill tree with N random items')
        self.newTreeButton = self.addOperation(
            "New Tree", self.newTree,
            helpText='Create an empty tree')
        self.inOrderButton = self.addOperation(
            "In-order Traverse", lambda: self.clickTraverse('in'), 
            helpText='Traverse tree in in-order')
        #this makes the pause, play and stop buttons 
        self.addAnimationButtons()

if __name__ == '__main__':
    nonneg, negative, options, otherArgs = categorizeArguments(sys.argv[1:])
    if '-r' not in options:  # Use fixed seed for testing consistency unless
        random.seed(3.14159) # random option specified
    tree = AVLTree()
    for arg in nonneg:
        tree.setArgument(arg)
        tree.insertButton.invoke()
    for arg in negative:
        tree.setArgument(arg[1:])
        tree.randomFillButton.invoke()
    tree.runVisualization()
