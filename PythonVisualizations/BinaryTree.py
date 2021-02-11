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
        super().__init__(RECT=(0, 30, width, height - 30), title=title, **kwargs)
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


    # find node with given key k
    # return the associated data or None
    def find(self, key, stopAnimations=True):
        if self.size == 0: return None, None

        callEnviron = self.createCallEnvironment()

        # start at the root
        level = 0
        cur = self.getRoot()
        parent = cur
        arrow = self.createArrow(cur)
        callEnviron |= set(arrow)

        # while we haven't found the key
        while cur:
            # move arrow
            self.moveArrow(arrow, cur)
            self.wait(0.3)

            # did we find the key?
            if cur.getKey() == key:
                callEnviron.add(self.createHighlightedValue(cur))
                self.wait(0.2)
                self.cleanUp(callEnviron, stopAnimations=stopAnimations)
                return cur, parent

            parent = cur
            level += 1
            # go left ?
            if key < cur.getKey():
                cur = self.getLeftChild(cur)
            # go right
            else:
                cur = self.getRightChild(cur)
            
        self.cleanUp(callEnviron, stopAnimations=stopAnimations)
        return None, None

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
        callEnviron = self.createCallEnvironment(
            code='' if not animation else code.format(**locals()))
        wait = 0.1

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

        while (current < self.maxElems and self.nodes[current] and
               goal != self.nodes[current].getKey()):
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
                if current < self.maxElems and self.nodes[current]:
                    self.highlightCode(
                        'goal != current.key', callEnviron, wait=wait)

        if animation:
            self.highlightCode(
                'return (current, parent)', callEnviron, wait=wait)
        self.cleanUp(callEnviron)
        return current, parent
    
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
        callEnviron = self.createCallEnvironment(
            code='' if not animation else code.format(**locals()),
            startAnimations=start if animation else False)
        inserted = False
        wait = 0.1

        if animation:
            self.highlightCode('node, parent = self.__find(key)', callEnviron)
        node, parent = self._find(key, animation=animation)

        if animation:
            nodeIndex = self.createArrow(node, label='node')
            parentIndex = self.createArrow(parent, label='parent', level=2)
            callEnviron |= set(nodeIndex + parentIndex)
            self.highlightCode(('node', 2), callEnviron, wait=wait)
        if 0 <= node and node < self.maxElems and self.nodes[node]:
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
                self.moveArrow(nodeIndex, node * 2 + 2, sleepTime=0)
            inserted = True
 
        if animation and inserted:
            self.highlightCode('return True', callEnviron, wait=wait)
            
        self.cleanUp(callEnviron)
        return inserted
        
    def delete(self, key):
        # create a call environment and start the animations
        callEnviron = self.createCallEnvironment()

        # find the node with the key
        cur, parent = self.find(key, stopAnimations=False)

        # node with key does not exist
        if not cur: 
            result = None
            self.stopAnimations()
        else:
            # go through the process of deleting the item
            result = self.__delete(cur, callEnviron)
            self.updateTreeObjectRootPointer(root=self.getRoot())
        self.cleanUp(callEnviron)
        return result
        
    def __delete(self, cur, callEnviron):

        #save the deleted key and its index
        deleted = cur.getKey()
        
        #determine the correct process for removing the node from the tree
        if self.getLeftChild(cur):
            if self.getRightChild(cur):    # cur has left and right child
                self.__promoteSuccessor(cur, callEnviron)
                self.removeNodeDrawing(cur) # Remove deleted node's canvas items
            else:                          # cur only has left child
                self.removeNodeDrawing(cur) # Remove deleted node's canvas items
                # get cur's left child that will be moving up
                curLeft = self.getLeftChild(cur)
                # remove current and promote left child
                self.removeAndReconnectNodes(cur, curLeft)
        else:                        # a right child exists or no children
            self.removeNodeDrawing(cur)  # Remove deleted node's canvas items
            # get cur's right child that will be moving up
            curRight = self.getRightChild(cur)
            # remove current and promote right child
            self.removeAndReconnectNodes(cur, curRight)

        return deleted
        
    def removeAndReconnectNodes(self, cur, curRightOrLeft):
        
        # 1. Note the indices of the current node and the child to move up
        curIndex, childIndex = self.getIndex(cur), self.getIndex(curRightOrLeft)

        # 2. delete the key and line to its parent 
        line = self.getLine(cur)
        if line:
            self.canvas.delete(line)
        elif curRightOrLeft and self.getLine(curRightOrLeft):
            self.canvas.delete(self.getLine(curRightOrLeft))
        self.removeNodeInternal(cur)

        # 3. move child subtree to be rooted at current node
        self.moveSubtree(curIndex, childIndex)

        # 4. move cur's right/left and its children up in the drawing
        #does cur have children?
        if curRightOrLeft:
            moveItems = [curRightOrLeft] + self.getAllDescendants(curRightOrLeft)
            self.restoreNodesPosition(moveItems)

        self.redrawLines()

    def __promoteSuccessor(self, node, callEnviron):
        successor = self.getRightChild(node)
        parent = node

        self.createHighlightedLine(successor, callEnviron=callEnviron)
                
        #hunt for the right child's most left child
        while self.getLeftChild(successor):
            parent = successor
            successor = self.getLeftChild(successor)
            
            self.wait(0.2)
            self.createHighlightedLine(successor, callEnviron=callEnviron)

        self.wait(0.2)
        highlight = self.createHighlightedCircle(
            successor, callEnviron=callEnviron)

        # replace node to delete with successor's key and data
        newSuccessor = self.copyNode(successor)
        callEnviron |= set(newSuccessor.drawnValue.items)
        
        # a. internal replacement
        newSuccessor.coords = node.coords
        deletedIndex = self.getIndex(node)
        self.nodes[deletedIndex] = newSuccessor
        
        # b. drawing replacement
        self.restoreNodesPosition((newSuccessor,), includeLines=False)
        callEnviron -= set(newSuccessor.drawnValue.items)
        self.removeNodeDrawing(node)
        self.canvas.delete(highlight)
        callEnviron.discard(highlight)

        # remove successor node
        self.__delete(successor, callEnviron)

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
        if val is not None:
            result, parent = self.find(val)
            if result != None:
                msg = "Found {}!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()

    def clickFill(self):
        val = self.validArgument()
        if val is not None:
            if val < 32:
                self.fill(val)
            else:
                self.setMessage("Input value must be an integer from 0 to 31.")
        self.clearArgument()

    def clickDelete(self):
        val = self.validArgument()
        if val is not None:
            deleted = self.delete(val)
            msg = ("Deleted {}".format(val) if deleted else
                   "Value {} not found".format(val))
            self.setMessage(msg)
            self.clearArgument()
        
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
        #this makes the pause, play and stop buttons 
        self.addAnimationButtons()
        return [fillButton, searchButton, insertButton, deleteButton]

if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    numArgs = [int(arg) for arg in sys.argv[1:] if arg.isdigit()]
    tree = BinaryTree(values=numArgs if len(numArgs) > 0 else None)

    tree.runVisualization()
