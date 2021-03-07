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

    def createFlagText(self, flagValue):
        return self.canvas.create_text(
            self.RECT[0] + 10, self.ROOT_Y0, text='flag = {}'.format(flagValue),
            anchor=W, font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        
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
