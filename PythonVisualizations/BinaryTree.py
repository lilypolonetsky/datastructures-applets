from tkinter import *
import random

try:
    from drawnValue import *
    from VisualizationApp import *
    from BinaryTreeBase import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .VisualizationApp import *
    from .BinaryTreeBase import *

class BinaryTree(BinaryTreeBase):
    def __init__(self, title="Binary Search Tree", values=None, **kwargs):
        height = kwargs.get('canvasHeight', 400)
        width = kwargs.get('canvasWidth', 800)
        padY = 30
        super().__init__(RECT=(0, padY, width, height - padY), 
                         title=title, **kwargs)
        self.buttons = self.makeButtons()
        self.title = title

        # empty the tree
        self.emptyTree()
        
        # populate the tree
        self.fill(values=20 if values is None else values)

        # Display it
        self.display()
        
    def fill(self, values, animation=False):
        '''Fill the tree with values which is either a list of integers or
        an integer number of random values'''
        callEnviron = self.createCallEnvironment()

        
        nums = [random.randrange(self.valMax) for i in range(values)] if (
            isinstance(values, int)) else values
        self.emptyTree()
        for num in nums:
            self.insert(num, animation=animation)
        self.display()

        self.cleanUp(callEnviron)

    _findCode = '''
def __find(self, goal={goal}):
   current = self.__root
   parent = self
   while (current and goal != current.key):
      parent = current
      current = (
         current.leftChild if goal < current.key else
         current.rightChild)

   return (current, parent)
'''

    def _find(self, goal, animation=True, code=_findCode):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code='' if not animation else code.format(**locals()), 
            sleepTime=wait / 10)

        current = 0
        parent = -1
        if animation:
            self.highlightCode('current = self.__root', callEnviron, wait=wait)
            currentIndex = self.createArrow(0, label='current')
            callEnviron |= set(currentIndex)

            self.highlightCode('parent = self', callEnviron, wait=wait)
            parentIndex = self.createArrow(parent, label='parent', level=2)
            callEnviron |= set(parentIndex)

            self.highlightCode(('current', 2), callEnviron, wait=wait)
            if self.nodes[current]:
                self.highlightCode(
                    'goal != current.key', callEnviron, wait=wait)

        while self.getNode(current) and goal != self.nodes[current].getKey():
            if animation:
                self.highlightCode('parent = current', callEnviron)
                self.moveArrow(parentIndex, current, level=2)
            parent = current

            goLeft = goal < self.nodes[current].getKey()
            if animation:
                self.highlightCode('goal < current.key', callEnviron, wait=wait)
                self.highlightCode(
                    [('current = ', 2),
                     'current.leftChild' if goLeft else 'current.rightChild'],
                    callEnviron, wait=wait)
            current = 2 * current + (1 if goLeft else 2)
            
            if animation:
                self.moveArrow(currentIndex, current)
                self.highlightCode(('current', 2), callEnviron, wait=wait)
                if self.getNode(current):
                    self.highlightCode(
                        'goal != current.key', callEnviron, wait=wait)

        if animation:
            self.highlightCode(
                'return (current, parent)', callEnviron)
        self.cleanUp(callEnviron)
        return current, parent

    searchCode = '''
def search(self, goal={goal}):
   node, p = self.__find(goal)
   return node.data if node else None
'''
    def search(self, goal, code=searchCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start, 
            sleepTime=wait / 10)

        self.highlightCode('node, p = self.__find(goal)', callEnviron)
        node, p = self._find(goal)

        nodeIndex = self.createArrow(node, label='node')
        pIndex = self.createArrow(p, label='p', level=2)
        callEnviron |= set(nodeIndex + pIndex)
        self.highlightCode(('node', 3), callEnviron, wait=wait)

        if self.getNode(node):
            self.highlightCode('return node.data', callEnviron, wait=wait)
            callEnviron.add(self.createNodeHighlight(node))
            result =  self.nodes[node].getKey()
        else:
            self.highlightCode(['return', 'None'], callEnviron, wait=wait)
            result = None

        self.cleanUp(callEnviron)
        return result
        
    insertCode = '''
def insert(self, key={key}, data):
   node, parent = self.__find(key)
   if node:
      node.data = data
      return False

   if parent is self:
      self.__root = self.__Node(key, data)
   elif key < parent.key:
      parent.leftChild = self.__Node(
         key, data, right=node)
   else:
      parent.rightChild = self.__Node(
         key, data, right=node)
   return True
'''
    
    def insert(self, key, animation=True, code=insertCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code='' if not animation else code.format(**locals()),
            startAnimations=start if animation else False, sleepTime=wait / 10)
        inserted = False

        if animation:
            self.highlightCode('node, parent = self.__find(key)', callEnviron)
        node, parent = self._find(key, animation=animation)

        if animation:
            nodeIndex = self.createArrow(node, label='node')
            parentIndex = self.createArrow(parent, label='parent', level=2)
            callEnviron |= set(nodeIndex + parentIndex)
            self.highlightCode(('node', 2), callEnviron, wait=wait)
        if self.getNode(node):
            nodeHighlight = self.createNodeHighlight(node)
            callEnviron.add(nodeHighlight)
            if animation:
                self.highlightCode('node.data = data', callEnviron, wait=wait)
                self.highlightCode('return False', callEnviron, wait=wait)
            self.cleanUp(callEnviron)
            return inserted

        if animation:
            self.highlightCode('parent is self', callEnviron, wait=wait)
        if parent == -1:
            if animation:
                self.highlightCode('self.__root = self.__Node(key, data)',
                                   callEnviron, wait=wait)
            self.createNode(key)
            inserted = True
            self.updateTreeObjectRootPointer(root=self.getRoot())
            
        elif node >= self.maxElems:
            if animation:
                self.setMessage(
                    "Error! Cannot insert at level {} or below".format(
                        self.MAX_LEVEL))
                self.highlightCode([], callEnviron)

        else:
            if animation:
                self.highlightCode('key < parent.key', callEnviron, wait=wait)
                
            dir = 'left' if key < self.nodes[parent].getKey() else 'right'
            if animation:
                self.highlightCode(
                    'parent.{}Child = self.__Node('.format(dir) +
                    '\n         key, data, right=node)',
                    callEnviron, wait=wait)
            self.createNode(key, self.nodes[parent], 
                            Child.LEFT if dir == 'left' else Child.RIGHT)
            if animation:
                if dir == 'left':
                    self.canvas.itemconfigure(nodeIndex[1], anchor=SE)
                self.moveItemsBy(
                    nodeIndex, (0, - self.LEVEL_GAP // 3), sleepTime=wait/10)
            inserted = True
 
        if animation and inserted:
            self.highlightCode('return True', callEnviron, wait=wait)
            
        self.cleanUp(callEnviron)
        return inserted
    
    deleteCode = '''
def delete(self, goal={goal}):
   node, parent = self.__find(goal)
   if node is not None:
      return self.__delete(parent, node)
   return
'''

    def delete(self, goal, code=deleteCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start, 
            sleepTime=wait / 10)

        self.highlightCode('node, parent = self.__find(goal)', callEnviron)
        node, parent = self._find(goal)

        nodeIndex = self.createArrow(node, label='node')
        parentIndex = self.createArrow(parent, label='parent', level=2)
        callEnviron |= set(nodeIndex + parentIndex)

        self.highlightCode('node is not None', callEnviron, wait=wait)
        if self.getNode(node):
            self.highlightCode('return self.__delete(parent, node)',
                               callEnviron)
            localVars = parentIndex + nodeIndex
            colors = self.fadeNonLocalItems(localVars)
            result = self.__delete(parent, node)
            self.restoreLocalItems(localVars, colors)
            deletedNodeCoords = self.deletedNodeCoords(level=1)
            deletedNode = self.createNodeShape(
                *deletedNodeCoords, result, 'deleted')
            callEnviron |= set(deletedNode)

            if self.getNode(node):
                if node % 2 == 1:
                    self.canvas.itemconfigure(nodeIndex[1], anchor=SE)
                self.moveItemsBy(
                    nodeIndex, (0, - self.LEVEL_GAP // 3), sleepTime=wait/10)
        else:
            self.highlightCode(('return', 2), callEnviron, wait=wait)
            result = None

        self.cleanUp(callEnviron)
        return result
    
    __deleteCode = '''
def __delete(self, parent, node):
   deleted = node.data
   if node.leftChild:
      if node.rightChild:
         self.__promote_successor(node)
      else:
         if parent is self:
            self.__root = node.leftChild
         elif parent.leftChild is node:
            parent.leftChild = node.leftChild
         else:
            parent.rightChild = node.leftChild
   else:
      if parent is self:
         self.__root = node.rightChild
      elif parent.leftChild is node:
         parent.leftChild = node.rightChild
      else:
         parent.rightChild = node.rightChild
   return deleted
'''
    
    def __delete(self, parent, node, code=__deleteCode, level=1):
        'parent and node must be integer indices'
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code, sleepTime=wait / 10)

        parentIndex = self.createArrow(parent, 'parent', level=2)
        nodeIndex = self.createArrow(node, label='node')
        callEnviron |= set(parentIndex + nodeIndex)
        self.highlightCode('deleted = node.data', callEnviron, wait=wait)
        deleted = self.getNode(node).getKey()
        deletedNodeCoords = self.deletedNodeCoords(level)
        deletedLabel = self.canvas.create_text(
            *(V(deletedNodeCoords) - V(self.CIRCLE_SIZE + 5, 0)), anchor=E,
            text='deleted', font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(deletedLabel)
        deletedNode = self.createNodeShape(
            *self.nodeCenter(node), deleted, 'deleted')
        callEnviron |= set(deletedNode)
        self.moveItemsTo(deletedNode, self.nodeItemCoords(deletedNodeCoords),
                         sleepTime=wait / 10)

        self.highlightCode('node.leftChild', callEnviron, wait=wait)
        if self.getLeftChild(node):

            self.highlightCode('node.rightChild', callEnviron, wait=wait)
            if self.getRightChild(node):
                
                self.highlightCode('self.__promote_successor(node)', 
                                   callEnviron, wait=wait)
                localVars = deletedNode + parentIndex + nodeIndex + (
                    deletedLabel,)
                colors = self.fadeNonLocalItems(localVars)
                self.__promote_successor(node)
                self.restoreLocalItems(localVars, colors)
                
            else:
                self.highlightCode('parent is self', callEnviron, wait=wait)
                if parent == -1:
                    self.highlightCode('self.__root = node.leftChild',
                                       callEnviron)
                    self.replaceSubtree(
                        parent, Child.RIGHT,
                        self.getLeftChildIndex(node), callEnviron)

                else:
                    self.highlightCode('parent.leftChild is node',
                                       callEnviron, wait=wait)
                    nodeIsLeft = self.getLeftChildIndex(parent) == node
                    self.highlightCode(
                        'parent.leftChild = node.leftChild' if nodeIsLeft else
                        'parent.rightChild = node.leftChild',
                        callEnviron, wait=wait)
                    self.replaceSubtree(
                        parent, Child.LEFT if nodeIsLeft else Child.RIGHT,
                        self.getLeftChildIndex(node), callEnviron)
        else:
            self.highlightCode(('parent is self', 2), callEnviron, wait=wait)
            if parent == -1:
                self.highlightCode('self.__root = node.rightChild',
                                   callEnviron)
                rightChildIndex = self.getRightChildIndex(node)
                rightChild = self.getNode(rightChildIndex)
                self.replaceSubtree(
                    parent, Child.RIGHT, rightChildIndex, callEnviron)
                if rightChild is None:
                    self.updateTreeObjectRootPointer(root=self.getRoot())

            else:
                self.highlightCode(('parent.leftChild is node', 2),
                                   callEnviron, wait=wait)
                nodeIsLeft = self.getLeftChildIndex(parent) == node
                self.highlightCode(
                    'parent.leftChild = node.rightChild' if nodeIsLeft else
                    'parent.rightChild = node.rightChild',
                    callEnviron, wait=wait)
                self.replaceSubtree(
                    parent, Child.LEFT if nodeIsLeft else Child.RIGHT,
                    self.getRightChildIndex(node), callEnviron)
            
        self.highlightCode('return deleted', callEnviron)
        self.cleanUp(callEnviron)
        return deleted

    __promote_successorCode = '''
def __promote_successor(self, node):
   successor = node.rightChild
   parent = node
   while successor.leftChild:
      parent = successor
      successor = successor.leftChild
   node.key = successor.key
   node.data = successor.data
   self.__delete(parent, successor)
'''

    def __promote_successor(
            self, nodeIndex, code=__promote_successorCode):
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code, sleepTime=wait / 10)
        node = self.getNode(nodeIndex)

        nodeArrow = self.createArrow(nodeIndex, 'node')
        callEnviron |= set(nodeArrow)
        
        self.highlightCode(
            'successor = node.rightChild', callEnviron, wait=wait)
        successor = self.getRightChildIndex(nodeIndex)
        successorIndex = self.createArrow(successor, 'successor')
        callEnviron |= set(successorIndex)

        self.highlightCode('parent = node', callEnviron, wait=wait)
        parent = nodeIndex
        parentIndex = self.createArrow(parent, 'parent', level=2)
        callEnviron |= set(parentIndex)
        
        self.highlightCode('successor.leftChild', callEnviron, wait=wait)
        while self.getLeftChild(successor):
            self.highlightCode('parent = successor', callEnviron, wait=wait)
            parent = successor
            self.moveArrow(parentIndex, parent, level=2, sleepTime=wait / 10)

            self.highlightCode('successor = successor.leftChild',
                               callEnviron, wait=wait)
            successor = self.getLeftChildIndex(successor)
            self.moveArrow(successorIndex, successor, sleepTime=wait / 10)
            
            self.highlightCode('successor.leftChild', callEnviron, wait=wait)

        self.highlightCode('node.key = successor.key', callEnviron, wait=wait)
        drawnValueToDelete = node.drawnValue
        successorKey = self.getNode(successor).getKey()
        tag = self.generateTag()
        successorCopy = self.createNodeShape(
            *self.nodeCenter(successor), successorKey, tag)
        callEnviron |= set(successorCopy)
        keyCopy = self.copyCanvasItem(successorCopy[2])
        callEnviron.add(keyCopy)
        self.moveItemsTo(
            keyCopy, self.nodeCenter(nodeIndex), sleepTime=wait / 10)
        self.canvas.tag_lower(drawnValueToDelete.items[2])

        self.highlightCode('node.data = successor.data', callEnviron, wait=wait)
        self.moveItemsTo(
            successorCopy, self.nodeItemCoords(node), sleepTime=wait / 10)
        self.canvas.delete(keyCopy)
        callEnviron.discard(keyCopy)
        node.drawnValue = drawnValue(successorKey, drawnValueToDelete.items[0],
                                     *successorCopy[1:])
        node.tag = tag
        callEnviron -= set(successorCopy[1:])
        for item in drawnValueToDelete.items[1:]:
            if item:
                self.canvas.delete(item)
        
        self.highlightCode('self.__delete(parent, successor)', callEnviron)
        localVars = nodeArrow + parentIndex + successorIndex
        colors = self.fadeNonLocalItems(localVars)
        self.__delete(parent, successor, level=2)
        self.restoreLocalItems(localVars, colors)
        
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        
    def deletedNodeCoords(self, level=1):
        return (self.RECT[2] - self.CIRCLE_SIZE,
                self.RECT[1] + self.CIRCLE_SIZE * (2.5 * level - 1.5))

    traverseExampleCode = '''
for key, data in tree.traverse("{traverseType}"):
   print(key)
'''
    def traverseExample(
            self, traverseType, code=traverseExampleCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=wait / 10, 
            startAnimations=start)

        iteratorCall = 'key, data in tree.traverse("{traverseType}")'.format(
            **locals())
        self.iteratorStack = []
        self.highlightCode(iteratorCall, callEnviron, wait=wait)
        count = 1
        dataIndex = None
        localVars = ()
        colors = self.fadeNonLocalItems(localVars)
        for node, key, items in self.traverse(traverseType):
            self.restoreLocalItems(localVars, colors)
            if dataIndex is None:
                dataIndex = self.createArrow(
                    node, 'key, data', orientation=-135)
                callEnviron |= set(dataIndex)
                localVars += dataIndex
            else:
                dataCoords = self.indexCoords(node, 1, orientation=-135)
                self.moveItemsTo(dataIndex, (dataCoords, dataCoords[:2]),
                                 sleepTime=wait / 10)

            self.highlightCode('print(key)', callEnviron, wait=wait)
            nodeData = [self.copyCanvasItem(i) for i in items[1:]]
            callEnviron |= set(nodeData)
            self.moveItemsTo(
                nodeData, 
                self.nodeItemCoords(self.deletedNodeCoords(level=count))[1:],
                sleepTime=wait / 10)
            count += 1

            self.highlightCode(iteratorCall, callEnviron, wait=wait)
            colors = self.fadeNonLocalItems(localVars)

        self.restoreLocalItems(localVars, colors)
        while self.iteratorStack:
            self.cleanUp(self.iteratorStack.pop())
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        
    traverseCode = '''
def traverse(self, traverseType="{traverseType}"):
   if traverseType in ['pre', 'in', 'post']:
      return self.__traverse(self.__root, traverseType)
   
   raise Exception("Unknown traversal type: " + str(traverseType))
'''

    def traverse(self, traverseType='in', code=traverseCode):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=wait / 10)

        self.highlightCode("traverseType in ['pre', 'in', 'post']", callEnviron,
                           wait=wait)
        if traverseType in ['pre', 'in', 'post']:
            self.highlightCode(
                'return self.__traverse(self.__root, traverseType)',
                callEnviron)
            self.iteratorStack.append(callEnviron)
            return self.__traverse(0, traverseType)
            
        else:
            self.highlightCode(
                'raise Exception("Unknown traversal type: " + str(traverseType))',
                callEnviron, color=self.EXCEPTION_HIGHLIGHT)
        
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait /10)
        
    __traverseCode = '''
def __traverse(self, node={node}, traverseType="{traverseType}"):
   if node is None:
      return
   if traverseType == "pre":
      yield (node.key, node.data)
   for childKey, childData in self.__traverse(
         node.leftChild, traverseType):
      yield (childKey, childData)
   if traverseType == "in":
      yield (node.key, node.data)
   for childKey, childData in self.__traverse(
         node.rightChild, traverseType):
      yield (childKey, childData)
   if traverseType == "post":
      yield (node.key, node.data)
'''

    def __traverse(self, node, traverseType, code=__traverseCode):
        kwargs = locals().copy()
        internalNode = self.getNode(node)
        kwargs['node'] = internalNode.getKey() if internalNode else None
        code = code.format(**kwargs)
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code, sleepTime=wait / 10)

        nodeArrow = self.createArrow(node, 'node')
        callEnviron |= set(nodeArrow)

        self.highlightCode('node is None', callEnviron, wait=wait)
        if internalNode is None:
            self.highlightCode('return', callEnviron)
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return

        self.highlightCode('traverseType == "pre"', callEnviron, wait=wait)
        if traverseType == "pre":
            self.highlightCode(
                ('yield (node.key, node.data)', 1), callEnviron, wait=wait)
            itemCoords = self.yieldCallEnvironment(
                callEnviron, sleepTime=wait / 10)
            yield (node, internalNode.drawnValue.val,
                   internalNode.drawnValue.items)
            self.resumeCallEnvironment(
                callEnviron, itemCoords, sleepTime=wait / 10)

        self.highlightCode(
            ('childKey, childData in self.__traverse(\n         node.leftChild, traverseType)', 1),
            callEnviron, wait=wait)
        localVars = nodeArrow
        childArrow = None
        colors = self.fadeNonLocalItems(localVars)
        for childIndex, childKey, childData in self.__traverse(
                self.getLeftChildIndex(node), traverseType):
            self.restoreLocalItems(localVars, colors)
            if childArrow is None:
                childArrow = self.createArrow(
                    childIndex, 'childData', orientation=-115)
                callEnviron |= set(childArrow)
                localVars += childArrow
                colors = self.itemsFillColor(localVars)
            else:
                childCoords = self.indexCoords(childIndex, 1, orientation=-115)
                self.moveItemsTo(childArrow, (childCoords, childCoords[:2]),
                                 sleepTime=wait / 10)
            self.highlightCode(
                ('yield (childKey, childData)', 1), callEnviron, wait=wait)
            itemCoords = self.yieldCallEnvironment(
                callEnviron, sleepTime=wait / 10)
            yield (childIndex, childKey, childData)
            self.resumeCallEnvironment(
                callEnviron, itemCoords, sleepTime=wait / 10)

            self.highlightCode(
                ('childKey, childData in self.__traverse(\n         node.leftChild, traverseType)', 1),
                callEnviron, wait=wait)
            colors = self.fadeNonLocalItems(localVars)
        self.restoreLocalItems(localVars, colors)

        self.highlightCode('traverseType == "in"', callEnviron, wait=wait)
        if traverseType == "in":
            self.highlightCode(
                ('yield (node.key, node.data)', 2), callEnviron, wait=wait)
            itemCoords = self.yieldCallEnvironment(
                callEnviron, sleepTime=wait / 10)
            yield (node, internalNode.drawnValue.val,
                   internalNode.drawnValue.items)
            self.resumeCallEnvironment(
                callEnviron, itemCoords, sleepTime=wait / 10)

        self.highlightCode('traverseType == "post"', callEnviron, wait=wait)
        if traverseType == "post":
            self.highlightCode(
                ('yield (node.key, node.data)', 3), callEnviron, wait=wait)
            itemCoords = self.yieldCallEnvironment(
                callEnviron, sleepTime=wait / 10)
            yield (node, internalNode.drawnValue.val, 
                   internalNode.drawnValue.items)
            self.resumeCallEnvironment(
                callEnviron, itemCoords, sleepTime=wait / 10)
        
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)
    
    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val <= self.valMax:
                return val
            else:
                self.setMessage("Input value must be an integer from 0 to {}."
                                .format(self.valMax))
                self.setArgumentHighlight(color=self.ERROR_HIGHLIGHT)

    def clickInsert(self):
        val = self.validArgument()
        if val:
            if self.insert(val, start=self.startMode()):
                self.setMessage('Key {} inserted'.format(val))
            self.clearArgument()

    def clickSearch(self):
        val = self.validArgument()
        self.setMessage(
            "Key {} not found".format(val) if self.search(
                val, start=self.startMode()) is None else 
            "Found key {}!".format(val))
        self.clearArgument()

    def clickFill(self):
        val = self.validArgument()
        if val is not None:
            if val <= self.maxElems:
                self.fill(val)
            else:
                self.setMessage("Number of keys must be between 0 and {}"
                                .format(self.maxElems))
            self.clearArgument()

    def clickDelete(self):
        val = self.validArgument()
        if val is not None:
            deleted = self.delete(val, start=self.startMode())
            msg = ("Deleted {}".format(val) if deleted else
                   "Value {} not found".format(val))
            self.setMessage(msg)
            self.clearArgument()
        
    def clickTraverse(self, traverseType):
        self.traverseExample(traverseType, start=self.startMode())

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Insert item in tree')
        searchButton = self.addOperation(
            "Search", lambda: self.clickSearch(), numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Search for item in tree')
        deleteButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Delete item from tree')
        fillButton = self.addOperation(
            "Random fill", lambda: self.clickFill(), numArguments=1,
            validationCmd=vcmd, argHelpText=['number of items'], 
            helpText='Insert a number of random\nitems in an empty tree')

        preOrderButton = self.addOperation(
            "Pre-order Traverse", lambda: self.clickTraverse('pre'), 
            helpText='Traverse tree in pre-order')
        inOrderButton = self.addOperation(
            "In-order Traverse", lambda: self.clickTraverse('in'), 
            helpText='Traverse tree in in-order')
        postOrderButton = self.addOperation(
            "Post-order Traverse", lambda: self.clickTraverse('post'), 
            helpText='Traverse tree in post-order')
        self.addAnimationButtons()
        return [fillButton, searchButton, insertButton, deleteButton]

if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    numArgs = [int(arg) for arg in sys.argv[1:] if arg.isdigit()]
    tree = BinaryTree(values=numArgs if len(numArgs) > 0 else None)

    tree.runVisualization()
