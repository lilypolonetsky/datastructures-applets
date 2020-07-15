from tkinter import *
import time, random

try:
    from drawable import *
    from VisualizationApp import *
    from BinaryTreeBase import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *
    from .BinaryTreeBase import *

class BinaryTree(BinaryTreeBase):
    def __init__(self, title="Binary Search Tree", **kwargs):
        super().__init__(title=title, **kwargs)
        self.buttons = self.makeButtons()
        self.title = title

        # populate the tree
        self.fill(20)

    #Fill the tree with n nodes
    def fill(self, n):
        callEnviron = self.createCallEnvironment()

        # empty the tree
        self.emptyTree()

        #randomly generate a tree
        nums = list(range(1, 99))
        random.shuffle(nums)
        while self.size < n and nums:
            num = nums.pop()
            self.insertElem(nums.pop(), animation=False)

        self.cleanUp(callEnviron)


    # find node with given key k
    # return the associated data or None
    def find(self, key):
        if self.size == 0: return None, None

        callEnviron = self.createCallEnvironment()
        self.startAnimations()

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
                self.cleanUp(callEnviron)
                return cur, parent

            parent = cur
            level += 1
            # go left ?
            if key < cur.getKey():
                cur = self.getLeftChild(cur)
            # go right
            else:
                cur = self.getRightChild(cur)
            
        self.cleanUp(callEnviron)
        return None, None

    def insertElem(self, key, animation=True):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        inserted = False

        # if tree is empty, then initialize root to the new node
        if not self.getRoot():
            self.createNode(key, None)
            self.cleanUp(callEnviron)
            return True

        # start at the root
        cur = self.getRoot()
        level = 1

        # create arrow
        if animation:
            arrow = self.createArrow(cur)
            callEnviron |= set(arrow)

        while not inserted:
            # if the key is to the left of current node, follow to the left
            if key < cur.getKey():
                # if no left child, insert on left
                if not self.getLeftChild(cur):
                    if animation:
                        # calculate where new node will be
                        coords = self.calculateCoordinates(cur, level, Child.LEFT)
                        # move arrow to new node
                        self.moveArrow(arrow, coords)
                        self.wait(0.2)

                    self.createNode(key, cur, Child.LEFT)
                    inserted = True
                cur = self.getLeftChild(cur)

            # otherwise, key must be to right of current node
            else:  
                if not self.getRightChild(cur):
                    if animation:
                        # calculate where new node will be
                        coords = self.calculateCoordinates(cur, level, Child.RIGHT)
                        # move arrow to new node
                        self.moveArrow(arrow, coords)
                        self.wait(0.2)

                    self.createNode(key, cur, Child.RIGHT)
                    inserted = True
                cur = self.getRightChild(cur)

            level+=1

            # move arrow
            if animation and not inserted:
                self.moveArrow(arrow, cur)
                self.wait(0.3)

            if level >= self.MAX_LEVEL and not inserted:
                self.setMessage("Error! Can't go down another level. Maximum depth of tree is " + str(self.MAX_LEVEL)) if animation else None
                self.cleanUp(callEnviron)
                return False

        self.cleanUp(callEnviron)
        return True

    def delete(self, key):
        # find the node with the key
         cur, parent = self.find(key)

        # node with key does not exist
         if not cur: return None
                
        # node with key does exist
        # determine the direction of cur
         direction = self.getChildDirection(cur)

        # go through the process of deleting the item
         return self.__delete(parent, cur, direction)
        
    def __delete(self, parent, cur, direction):
        # get rid of the highlighted value
        self.cleanUp()

        # create a call environment and start the animations
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        #save the deleted key and its index
        deleted = cur.getKey()

        #remove the drawing
        self.removeNodeDrawing(cur)
        
        #determine the correct process for removing the node from the tree
        if self.getLeftChild(cur):
            if self.getRightChild(cur):                                              # cur has left and right child
                self.__promoteSuccessor(parent, cur, direction)
            
            else:                                                                   # cur only has left child
                # get cur's left child that will be moving up
                curLeft = self.getLeftChild(cur)
                # get cur's grandchildren (or cur's left child's children)
                # so we can reattach them after moving cur's left up
                curLeftChildren = self.getChildren(curLeft)

                if self.isRoot(cur):                                                # delete the root that only has left child
                    self.removeAndReconnectNodes(cur, parent, 
                                            self.setRoot, 
                                            curLeft, curLeftChildren)

                elif self.isLeftChild(cur):                                         #parent's left is cur, cur only has a left
                    self.removeAndReconnectNodes(cur, parent, 
                                            self.setLeftChild, 
                                            curLeft, curLeftChildren)

                else:                                                               #parent's right is cur, cur only has a left
                    self.removeAndReconnectNodes(cur, parent, 
                                            self.setRightChild, 
                                            curLeft, curLeftChildren)
        else:                                                                       #a right child exists or no children
            # get cur's right child that will be moving up
            curRight = self.getRightChild(cur)
            # get cur's grandchildren (or cur's right child's children)
            # so we can reattach them after moving cur's right up
            curRightChildren = self.getChildren(curRight)

            if self.isRoot(cur):                                                    # deleting the root
                self.removeAndReconnectNodes(cur, parent, 
                                            self.setRoot, 
                                            curRight, curRightChildren)

            elif self.isLeftChild(cur):                                             #parent's left is cur, cur has a right child / no child
                self.removeAndReconnectNodes(cur, parent, 
                                            self.setLeftChild, 
                                            curRight, curRightChildren)

            else:                                                                   #parent's right is cur, cur has a right child / no child
                self.removeAndReconnectNodes(cur, parent, 
                                            self.setRightChild, 
                                            curRight, curRightChildren)

        self.cleanUp(callEnviron)
        return deleted

    def reconnect(self, node, leftChild, rightChild):
        if not node: return
        # save each of their children before reconnecting with parent
        leftChildren = self.getChildren(leftChild)
        rightChildren = self.getChildren(rightChild)

        # reconnect the children with their parent
        self.setLeftChild(node, leftChild)
        self.setRightChild(node, rightChild)

        # reconnect the children of the left child
        self.reconnect(leftChild, *leftChildren)
        # reconnect the children of the right child
        self.reconnect(rightChild, *rightChildren)
    
    def removeAndReconnectNodes(self, cur, parent, commandToSetChild, curRightOrLeft, curRightOrLeftChildren):
        # 1. delete the key
        self.removeNodeInternal(cur)

        # 2. move cur's right/left up
        if commandToSetChild != self.setRoot:
            commandToSetChild(parent, curRightOrLeft)
        else:
            commandToSetChild(cur)

        # 3. reconnect cur's right/left and its children
        self.reconnect(curRightOrLeft, *curRightOrLeftChildren)

        # 4. move cur's right/left and its children up in the drawing
        # 4a. does cur have children?
        if curRightOrLeft:
            moveItems = [curRightOrLeft] + self.getAllDescendants(curRightOrLeft)
            self.moveNodesToPos(moveItems)
        # 4b. cur was a leaf, redraw none shape in new location
        else:
            # did we remove a left node?
            if commandToSetChild == self.setLeftChild:
                self.createNoneShape(parent, 
                                self.getLevel(parent), 
                                self.canvas.coords(self.getLeftLine(parent)), 
                                Child.LEFT, 
                                parent.tag)
            # did we remove a right node?
            elif commandToSetChild == self.setRightChild:
                self.createNoneShape(parent, 
                                self.getLevel(parent), 
                                self.canvas.coords(self.getRightLine(parent)), 
                                Child.RIGHT, 
                                parent.tag)

    def __promoteSuccessor(self, parent, node, direction):
        successor = self.getRightChild(node)
        self.highlightCircle(successor)
        newParent = node
                
        #hunt for the right child's most left child
        self.highlightLeftLine(successor)
        self.wait(0.2)
        self.unHighlightCircle(successor)
        while self.getLeftChild(successor):
            newParent = successor
            successor = self.getLeftChild(successor)
            self.wait(0.2)
            self.unHighlightLeftLine(newParent)
            self.highlightLeftLine(successor)

        self.wait(0.2)
        self.unHighlightLeftLine(successor)
        self.highlightCircle(successor)
        self.wait(0.2)
        self.unHighlightCircle(successor)

        # delete the node that is to be deleted
        self.removeNodeInternal(node)

        # copy the items associated with successor
        # 1. generate a new tag
        newTag = self.generateTag()
        # 2. copy the circle and the value
        circle = self.copyCanvasItem(successor.drawable.display_shape)
        circle_text = self.copyCanvasItem(successor.drawable.display_val)
        # 3. add the appropiate tags
        self.canvas.itemconfig(circle, tags=(newTag))
        self.canvas.itemconfig(circle_text, tags=(newTag))
        # 4. create a drawable
        successorCopyDrawable = drawable(successor.getKey(), self.canvas.itemconfigure(circle, 'fill')[-1], *(circle, circle_text))

        # 5. create the lines
        leftLine = self.copyCanvasItem(self.getLeftLine(successor))
        rightLine = self.copyCanvasItem(self.getRightLine(successor))
        # 6. add the appropiate tags
        self.canvas.itemconfig(leftLine, tags=(newTag, "left line"))
        self.canvas.itemconfig(rightLine, tags=(newTag, "right line"))
        # 7. create the node object
        successorCopy = Node(successorCopyDrawable, successor.coords, newTag)

        # insert the successor internally
        if direction == Child.RIGHT: self.setRightChild(parent, successorCopy)
        else: self.setLeftChild(parent, successorCopy)

        self.moveNodesToPos([successorCopy])

        self.wait(0.2)

        self.__delete(newParent, successor, Child.LEFT)

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val
            else:
                self.setMessage("Input value must be an integer from 0 to 99.")

    def clickInsert(self):
        val = self.validArgument()
        if val:
            self.insertElem(val)
            self.window.update()
        self.clearArgument()

    def clickFind(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            result, parent = self.find(val)
            if result != None:
                msg = "Found {}!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()

    def clickFill(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            val = int(val)
            if val < 32:
                self.fill(val)
            else:
                self.setMessage("Input value must be an integer from 0 to 31.")
        self.clearArgument()

    def clickDelete(self):
        val = self.validArgument()
        if val < 100:
            deleted = tree.delete(val)
            msg = "Deleted!" if deleted else "Value not found"
        else:
            msg = "Input value must be an integer from 0 to 99."
        self.setMessage(msg)
        self.clearArgument()

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        fillButton = self.addOperation(
            "Fill", lambda: self.clickFill(), numArguments=1,
            validationCmd=vcmd)
        findButton = self.addOperation(
            "Find", lambda: self.clickFind(), numArguments=1,
            validationCmd=vcmd)
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd= vcmd)
        deleteButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1,
            validationCmd= vcmd)
        #this makes the pause, play and stop buttons 
        self.addAnimationButtons()
        return [fillButton, findButton, 
                insertButton,deleteButton]

if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    tree = BinaryTree()

    tree.runVisualization()