from tkinter import *
import random

try:
    from coordinates import *
    from drawnValue import *
    from VisualizationApp import *
    from BinaryTreeBase import *
except ModuleNotFoundError:
    from .coordinates import *
    from .drawnValue import *
    from .VisualizationApp import *
    from .BinaryTreeBase import *

V = vector

class BinaryTree(BinaryTreeBase):
    def __init__(self, title="Binary Search Tree", values=None, **kwargs):
        super().__init__(title=title, **kwargs)
        self.buttons = self.makeButtons()

        # empty the tree
        self.emptyTree()
        
        # populate the tree
        self.fill(values=20 if values is None else values)

        # Display it
        self.display()
    
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

            outBoxCoords = self.outputBoxCoords(font=self.outputFont, N=1)
            callEnviron.add(self.createOutputBox(coords=outBoxCoords))
            outBoxCenter = V(V(outBoxCoords[:2]) + V(outBoxCoords[2:])) // 2
            
            upperRightNodeCoords = self.upperRightNodeCoords(level=1)
            deletedKey = self.canvas.create_text(
                *upperRightNodeCoords, text=str(result), font=self.VALUE_FONT,
                fill=self.VALUE_COLOR)
            callEnviron.add(deletedKey)
            self.moveItemsTo(deletedKey, outBoxCenter, sleepTime=wait / 10)

            if self.getNode(node):
                if node % 2 == 1:
                    self.canvas.itemconfigure(nodeIndex[1], anchor=SE)
                self.moveItemsBy(
                    nodeIndex, (0, - self.LEVEL_GAP // 3), sleepTime=wait / 10)
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
        upperRightNodeCoords = self.upperRightNodeCoords(level)
        deletedLabel = self.canvas.create_text(
            *(V(upperRightNodeCoords) - V(self.CIRCLE_SIZE + 5, 0)), anchor=E,
            text='deleted', font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(deletedLabel)
        deletedNode = self.createNodeShape(
            *self.nodeCenter(node), deleted, 'deleted')
        callEnviron |= set(deletedNode)
        self.moveItemsTo(deletedNode, self.nodeItemCoords(upperRightNodeCoords),
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

    def clickDelete(self):
        val = self.validArgument()
        if val is not None:
            deleted = self.delete(val, start=self.startMode())
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
