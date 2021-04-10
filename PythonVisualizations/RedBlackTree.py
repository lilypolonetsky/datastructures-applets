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

class RedBlackTree(BinaryTreeBase):
    CIRCLE_SIZE = 15
    RING_RADIUS = 19
    RED_COLOR = 'red'
    BLACK_COLOR = 'black'
    MEASURE_MET = 'dark olive green'
    MEASURE_UNMET = 'red3'
    DEBUG = False
    
    def __init__(self, title="Red-Black Tree", values=None, **kwargs):
        super().__init__(title=title, CIRCLE_SIZE=self.CIRCLE_SIZE, **kwargs)
        self.measures = [0] * 4
        self.buttons = self.makeButtons()
        self.lastNodeClicked = (None, ) * 2
        self.lastFlipEvent, self.lastRotateEvent = (None, ) * 3,  (None, ) * 3

        # empty the tree
        self.emptyTree()
        
        # populate the tree
        self.emptyAndFill(values=2 if values is None else values)

        # Display it
        self.display()
        self.updateMeasures()

    def nodeItemCoords(self, node, parent=None, radius=None):
        base = super().nodeItemCoords(node, parent=parent, radius=radius)
        center = base[-1]
        return base + (
            self.nodeShapeCoordinates(center, radius=self.RING_RADIUS),)

    def createNodeHighlight(
            self, node, highlightWidth=2, color=None, radius=None):
        if radius is None: radius = self.RING_RADIUS
        return super().createNodeHighlight(node, highlightWidth, color, radius)

    def createNodeShape(
            self, x, y, key, tag, color=None, parent=None, radius=None,
            ringColor=None, **kwargs):
        isRoot = parent is None or parent == -1
        if ringColor is None: 
            ringColor = self.BLACK_COLOR if isRoot else self.RED_COLOR
        coords = self.nodeItemCoords((x, y), parent=parent, radius=radius)
        redBlackLabel = self.canvas.create_oval(
            *coords[3], tag=tag, outline='', fill=ringColor)
        items = super().createNodeShape(
            x, y, key, tag, color=color, parent=parent, radius=radius,
            **kwargs)
        for item in (redBlackLabel, *items[1:]):
            self.canvas.tag_bind(item, '<Button-1>', self.flipColor(key))
            self.canvas.tag_bind(item, '<Double-Button-1>', self.rotateNode(key))
        return items + (redBlackLabel,)

    def createNode(self, key, *args, ringColor=None, **kwargs):
        node = super().createNode(key, *args, **kwargs)
        if ringColor:
            self.nodeColor(node, ringColor)
        return node
    
    def nodeColor(self, node, color=None):
        nodeIndex = node if isinstance(node, int) else self.getIndex(node)
        node = self.getNode(nodeIndex)
        if node:
            if color:
                self.canvas.itemconfigure(node.drawnValue.items[3], fill=color)
            else:
                return self.canvas.itemconfigure(
                    node.drawnValue.items[3], 'fill')[-1]
            
    def display(self, fields=[], treeLabel="RedBlackTree"):
        existingItems = set(self.canvas.find_withtag('all'))
        self.treeObject = self.createTreeObject(fields=fields, label=treeLabel)
        self.fieldwidths = self.treeObjectFieldWidths(fields=fields)
        newNodes = [self.createNode(
            node.getKey(), None if i == 0 else self.nodes[(i - 1) // 2],
            Child.LEFT if i % 2 == 1 else Child.RIGHT,
            ringColor=self.nodeColor(i)) if node else None
                    for i, node in enumerate(self.nodes)]
        self.nodes = newNodes
        self.size = sum(1 if node else 0 for node in self.nodes)
        for item in existingItems:
            self.canvas.delete(item)
        self.updateMeasures()
            
    def flipNodeColor(self, node):
        color = self.nodeColor(node)
        self.nodeColor(
            node, self.BLACK_COLOR if color == self.RED_COLOR else self.RED_COLOR)
        self.updateMeasures()

    def flipColor(self, key):
        def flipHandler(event):
            if self.DEBUG:
                print('Flip node color event', event.serial, event.time)
            if (key, event.serial) == self.lastFlipEvent[:2]:
                if self.DEBUG:
                    print('Skipping duplicate flip request (dt = {} ms)'.format(
                        event.time - self.lastFlipEvent[2]))
                return
            self.lastFlipEvent = (key, event.serial, event.time)
            nodeIndex, _ = self._find(key)
            node = self.getNode(nodeIndex)
            if node:
                self.lastNodeClicked = (node, self.nodeColor(nodeIndex))
                self.cleanUp()
                self.setArgument(str(key))
                self.flipNodeColor(nodeIndex)
                if self.DEBUG:
                    print('Flipped', node, 'color to', self.nodeColor(nodeIndex))
        return flipHandler

    def rotateNode(self, key):
        def rotateHandler(event):
            if self.DEBUG:
                print('Rotate Node event', event.serial, event.time)
            if (key, event.serial) == self.lastRotateEvent[:2]:
                if self.DEBUG:
                    print('Skipping duplicate rotate request (dt = {} ms)'
                          .format(event.time - self.lastRotateEvent[2]))
                return
            self.lastRotateEvent = (key, event.serial, event.time)
            nodeIndex, _ = self._find(key)
            node = self.getNode(nodeIndex)
            if node:
                self.cleanUp()
                if self.DEBUG:
                    print('Rotate', node, '(color', self.nodeColor(nodeIndex),
                          ')', 'left' if event.state & SHIFT else 'right')
                if node is self.lastNodeClicked[0]: # Restore color before click
                    if self.DEBUG:
                        print('Restoring', node, 'color to', 
                              self.lastNodeClicked[1])
                    self.nodeColor(nodeIndex, self.lastNodeClicked[1])
                if event.state & SHIFT:
                    self.rotateLeft(nodeIndex)
                else:
                    self.rotateRight(nodeIndex)
                self.lastNodeClicked = (node, self.nodeColor(nodeIndex))
                self.updateMeasures()
        return rotateHandler

    def cleanUp(self, *args, **kwargs):
        super().cleanUp(*args, **kwargs)
        if len(args) == 0 or kwargs.get('callEnviron', None) is None:
            self.canvas.delete('measureHighlight')
        
    def rotateLeft(self, top, animation=True, wait=0.1):
        "rotate a subtree to the left and optionally animate it"
        topIndex = self.getIndex(top) if isinstance(top, Node) else top
        topNode = self.getNode(topIndex)
        topParentLine = topNode.getLine()
        toRaise = self.getRightChild(topIndex)
        if topNode is None or toRaise is None:  # Must have both nodes to rotate
            self.setMessage('Cannot rotate left without right child')
            return
        callEnviron = self.createCallEnvironment(startAnimations=animation)

        if animation:
            self.disconnectLink(topNode, sleepTime=wait / 10)

        # Get key nodes
        topLeft = self.getLeftChild(top)
        toRaiseLeft, toRaiseRight = self.getChildren(toRaise)

        if animation:
            link1 = self.moveLink(topNode, toRaise, topNode, toRaiseLeft,
                                  callEnviron, sleepTime=wait / 10)
            link2 = self.moveLink(toRaise, toRaiseLeft, toRaise, topNode,
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

        # Move nodes internally
        self.storeNodeTree(
            [toRaise, 
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
                newSubTreeItems, toPositions, sleepTime=wait / 10)
        else:
            for item, coords in zip(newSubTreeItems, toPositions):
                self.canvas.coords(item, *coords)
        self.reconnectLink(topIndex, self.getParentIndex(topIndex),
                           sleepTime=wait / 10 if animation else 0)
        
        self.cleanUp(callEnviron)
        return toRaise
        
    def rotateRight(self, top, animation=True, wait=0.1):
        "rotate a subtree to the right and optionally animate it"
        topIndex = self.getIndex(top) if isinstance(top, Node) else top
        topNode = self.getNode(topIndex)
        topParentLine = topNode.getLine()
        toRaise = self.getLeftChild(topIndex)
        if topNode is None or toRaise is None:  # Must have both nodes to rotate
            self.setMessage('Cannot rotate right without left child')
            return
        callEnviron = self.createCallEnvironment(startAnimations=animation)

        if animation:
            self.disconnectLink(topNode, sleepTime=wait / 10)

        # Get key nodes
        topRight = self.getRightChild(top)
        toRaiseLeft, toRaiseRight = self.getChildren(toRaise)

        if animation:
            link1 = self.moveLink(topNode, toRaise, topNode, toRaiseRight,
                                  callEnviron, sleepTime=wait / 10)
            link2 = self.moveLink(toRaise, toRaiseRight, toRaise, topNode,
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

        # Move nodes internally
        self.storeNodeTree(
            [toRaise, 
             toRaiseLeftTree, [topNode, toRaiseRightTree, topRightTree]],
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
                newSubTreeItems, toPositions, sleepTime=wait / 10)
        else:
            for item, coords in zip(newSubTreeItems, toPositions):
                self.canvas.coords(item, *coords)
        self.reconnectLink(topIndex, self.getParentIndex(topIndex),
                           sleepTime=wait / 10 if animation else 0)
        
        self.cleanUp(callEnviron)
        return toRaise

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
            if self.DEBUG and self.animationsStopped():
                print('Somehow state is', self.animationState)
                import pdb
                pdb.set_trace()
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
        newLine = self.copyCanvasItem(lineToMove)
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

    def updateMeasures(self):
        blackRoot = (self.getRoot() is None or
                     self.nodeColor(self.getRoot()) == self.BLACK_COLOR)
        redRedLinks = self.getRedRedLinks()
        blackHeights = self.blackHeights()
        dy = self.textHeight(self.VALUE_FONT)
        for m in range(len(self.measures)):
            if self.canvas.type(self.measures[m]) != 'text':
                self.measures[m] = self.canvas.create_text(
                    dy // 2, (m + 1) * dy, anchor=W, text='',
                    font=self.VALUE_FONT, fill=self.MEASURE_MET)
        allMet = blackRoot and len(redRedLinks) == 0 and len(blackHeights) <= 1
        for m, text, met in (
                (0, 'Root is black: {}'.format(blackRoot), blackRoot),
                (1, 'Number red-red links: {}'.format(len(redRedLinks)),
                 len(redRedLinks) == 0),
                (2, 'Black heights: {}'.format(blackHeights),
                 len(blackHeights) <= 1),
                (3, '  BALANCED!' if allMet else '', allMet)):
            self.canvas.itemconfigure(
                self.measures[m], text=text,
                fill=self.MEASURE_MET if met else self.MEASURE_UNMET,
                font=self.VALUE_FONT + (() if met else ('underline',)))

    def getRedRedLinks(self):
        links = []
        toDo = [0]
        callEnviron = self.callStack[-1] if self.callStack else None
        while toDo:
            nodeIndex = toDo.pop(0)
            parentIndex = self.getParentIndex(nodeIndex)
            node = self.getNode(nodeIndex)
            if node:
                if (nodeIndex > 0 and 
                    self.nodeColor(parentIndex) == self.RED_COLOR and
                    self.nodeColor(nodeIndex) == self.RED_COLOR):
                    links.append((parentIndex, nodeIndex))
                    highlightLine = self.createHighlightedLine(
                        node, callEnviron=callEnviron, width=8,
                        color=self.ERROR_HIGHLIGHT, tags='measureHighlight')
                    self.canvas.tag_lower(highlightLine)
                toDo.extend([self.getLeftChildIndex(nodeIndex),
                             self.getRightChildIndex(nodeIndex)])
        return links

    def blackHeights(self):
        heights = set()
        toDo = [(0, 0)]
        while toDo:
            nodeIndex, blackHeight = toDo.pop(0)
            node = self.getNode(nodeIndex)
            if node:
                if self.nodeColor(nodeIndex) == self.BLACK_COLOR:
                    blackHeight += 1
                for child in [self.getLeftChildIndex(nodeIndex),
                              self.getRightChildIndex(nodeIndex)]:
                    toDo.append((child, blackHeight))
            else:
                heights.add(blackHeight)
        return heights
        
    def _find(self, goal, **kwargs):
        current = 0
        parent = -1
        while self.getNode(current) and goal != self.nodes[current].getKey():
            parent = current
            goLeft = goal < self.nodes[current].getKey()
            current = 2 * current + (1 if goLeft else 2)
        return current, parent

    def search(self, goal, **kwwargs):
        callEnviron = self.createCallEnvironment()
        node, _ = self._find(goal)
        if self.getNode(node):
            callEnviron.add(self.createNodeHighlight(node))
            result =  self.getNode(node).getKey()
        else:
            result = None
        self.cleanUp(callEnviron)
        return result

    def insert(self, key, animation=False, **kwargs):
        inserted = super().insert(key, animation=animation, **kwargs)
        if inserted:
            node, _ = self._find(key)
            if self.getNode(node):
                self.nodeColor(
                    node, self.BLACK_COLOR if node == 0 else self.RED_COLOR)
        return inserted
        
    def delete(self, goal, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(startAnimations=start)

        node, parent = self._find(goal)

        nodeIndex = self.createArrow(node, label='node')
        parentIndex = self.createArrow(parent, label='parent', level=2)
        callEnviron |= set(nodeIndex + parentIndex)

        if self.getNode(node):
            localVars = parentIndex + nodeIndex
            colors = self.fadeNonLocalItems(localVars)
            deletedKeyAndData = self.__delete(parent, node)
            callEnviron |= set(deletedKeyAndData)
            self.restoreLocalItems(localVars, colors)

            outBoxCoords = self.outputBoxCoords(font=self.outputFont, N=1)
            outBox = self.createOutputBox(coords=outBoxCoords)
            callEnviron.add(outBox)
            outBoxCenter = V(V(outBoxCoords[:2]) + V(outBoxCoords[2:])) // 2

            self.canvas.tag_raise(deletedKeyAndData[1], outBox)
            self.canvas.tag_lower(deletedKeyAndData[0], outBox)
            self.moveItemsTo(
                deletedKeyAndData, self.nodeItemCoords(outBoxCenter)[1:],
                sleepTime=wait / 10)
            self.copyItemAttributes(deletedKeyAndData[0], outBox, 'fill')

            if self.getNode(node):
                if node % 2 == 1:
                    self.canvas.itemconfigure(nodeIndex[1], anchor=SE)
                self.moveItemsBy(
                    nodeIndex, (0, - self.LEVEL_GAP // 3), sleepTime=wait / 10)
        else:
            deletedKeyAndData = None

        self.cleanUp(callEnviron)
        return (self.canvas.itemconfigure(deletedKeyAndData[1], 'text')[-1]
                if deletedKeyAndData else None)
    
    def __delete(self, parent, node, level=1):
        'parent and node must be integer indices'
        wait = 0.1
        parentStr = str(self if parent in (-1, self) else self.getNode(parent))
        nodeStr = str(self.getNode(node))
        callEnviron = self.createCallEnvironment()

        parentIndex = self.createArrow(parent, 'parent', level=2)
        nodeIndex = self.createArrow(node, label='node')
        callEnviron |= set(parentIndex + nodeIndex)
        deletedKey = self.getNode(node).getKey()
        upperRightNodeCoords = self.upperRightNodeCoords(level)
        deletedLabel = self.canvas.create_text(
            *(V(upperRightNodeCoords) - V(self.CIRCLE_SIZE + 5, 0)), anchor=E,
            text='deleted', font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(deletedLabel)
        deletedKeyAndData = tuple(
            self.copyCanvasItem(item) 
            for item in self.getNode(node).drawnValue.items[1:])
        self.moveItemsTo(
            deletedKeyAndData, self.nodeItemCoords(upperRightNodeCoords)[1:],
            sleepTime=wait / 10)

        if self.getLeftChild(node):

            if self.getRightChild(node):
                
                localVars = (
                    deletedLabel, *deletedKeyAndData, *parentIndex, *nodeIndex)
                colors = self.fadeNonLocalItems(localVars)
                self.__promote_successor(node)
                self.restoreLocalItems(localVars, colors)
                
            else:
                if parent == -1:
                    self.replaceSubtree(
                        parent, Child.RIGHT,
                        self.getLeftChildIndex(node), callEnviron)

                else:
                    nodeIsLeft = self.getLeftChildIndex(parent) == node
                    self.replaceSubtree(
                        parent, Child.LEFT if nodeIsLeft else Child.RIGHT,
                        self.getLeftChildIndex(node), callEnviron)
        else:
            if parent == -1:
                rightChildIndex = self.getRightChildIndex(node)
                rightChild = self.getNode(rightChildIndex)
                self.replaceSubtree(
                    parent, Child.RIGHT, rightChildIndex, callEnviron)
                if rightChild is None:
                    self.updateTreeObjectRootPointer(root=self.getRoot())

            else:
                nodeIsLeft = self.getLeftChildIndex(parent) == node
                self.replaceSubtree(
                    parent, Child.LEFT if nodeIsLeft else Child.RIGHT,
                    self.getRightChildIndex(node), callEnviron)
            
        self.cleanUp(callEnviron)
        return deletedKeyAndData

    def __promote_successor(self, nodeIndex):
        wait = 0.1
        nodeStr = str(self.getNode(nodeIndex))
        callEnviron = self.createCallEnvironment()
        node = self.getNode(nodeIndex)

        nodeArrow = self.createArrow(nodeIndex, 'node')
        callEnviron |= set(nodeArrow)
        
        successor = self.getRightChildIndex(nodeIndex)
        successorIndex = self.createArrow(successor, 'successor')
        callEnviron |= set(successorIndex)

        parent = nodeIndex
        parentIndex = self.createArrow(parent, 'parent', level=2)
        callEnviron |= set(parentIndex)
        
        while self.getLeftChild(successor):
            parent = successor
            self.moveArrow(parentIndex, parent, level=2, sleepTime=wait / 10)

            successor = self.getLeftChildIndex(successor)
            self.moveArrow(successorIndex, successor, sleepTime=wait / 10)
            
        successorNode = self.getNode(successor)
        successorKey = successorNode.getKey()
        successorDataItem, successorKeyItem = tuple(
            self.copyCanvasItem(item) 
            for item in successorNode.drawnValue.items[1:3])
        callEnviron |= set((successorDataItem, successorKeyItem))
        self.moveItemsTo(
            successorKeyItem, self.nodeCenter(nodeIndex), sleepTime=wait / 10)
        self.copyItemAttributes(successorKeyItem, node.drawnValue.items[2],
                                'text')

        self.moveItemsTo(
            successorDataItem, self.canvas.coords(node.drawnValue.items[1]),
            sleepTime=wait / 10)
        self.copyItemAttributes(successorDataItem, node.drawnValue.items[1],
                                'fill')
        
        localVars = nodeArrow + parentIndex + successorIndex
        colors = self.fadeNonLocalItems(localVars)
        for item in self.__delete(parent, successor, level=2):
            self.canvas.delete(item)
        self.restoreLocalItems(localVars, colors)
        
        self.cleanUp(callEnviron)

    def emptyAndFill(self, values, animation=False):
        '''Empty the tree and then fill it with values which is either a
        list of integers or an integer number of random values'''
        callEnviron = self.createCallEnvironment()
        
        nums = random.sample(range(self.valMax), values) if (
            isinstance(values, int)) else values
        self.emptyTree()
        for num in nums:
            self.insert(num, animation=animation)
        self.display()

        self.cleanUp(callEnviron)
    
    def clickDelete(self):
        val = self.validArgument()
        if val is not None:
            deleted = self.delete(val, start=self.startMode())
            if deleted:
                self.updateMeasures()
            msg = ("Deleted {}".format(val) if deleted else
                   "Value {} not found".format(val))
            self.setMessage(msg)
            self.clearArgument()

    def clickInsert(self):
        val = self.validArgument()
        if val is not None:
            inserted = self.insert(val, animation=False)
            if inserted:
                self.updateMeasures()
            self.setMessage('Key {} {}'.format(
                val, 'inserted' if inserted else 'updated or not inserted'))
            self.clearArgument()

    def clickFill(self):
        val = self.validArgument()
        if val is not None:
            self.emptyAndFill(val)
            self.updateMeasures()
            self.clearArgument()

    def clickFlip(self):
        val = self.validArgument()
        if val is not None:
            node, _ = self._find(val)
            if self.getNode(node):
                self.flipNodeColor(node)
                self.clearArgument()
            else:
                self.setMessage('Key {} not in tree'.format(val))
                self.setArgumentHighlight(color=self.ERROR_HIGHLIGHT)

    def clickRotate(self, direction):
        val = self.validArgument()
        if val is not None:
            node, _ = self._find(val)
            if self.getNode(node):
                if direction == Child.LEFT:
                    self.rotateLeft(node)
                else:
                    self.rotateRight(node)
                self.clearArgument()
            else:
                self.setMessage('Key {} not in tree'.format(val))
                self.setArgumentHighlight(color=self.ERROR_HIGHLIGHT)

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        insertButton = self.addOperation(
            "Insert", self.clickInsert, numArguments=1, validationCmd=vcmd,
            argHelpText=['item'], helpText='Insert item in tree')
        searchButton = self.addOperation(
            "Search", self.clickSearch, numArguments=1, validationCmd=vcmd,
            argHelpText=['item'], helpText='Search for item in tree')
        deleteButton = self.addOperation(
            "Delete", self.clickDelete, numArguments=1, validationCmd=vcmd,
            argHelpText=['item'], helpText='Delete item from tree')
        fillButton = self.addOperation(
            "Erase & Random fill", self.clickFill, numArguments=1,
            validationCmd=vcmd, argHelpText=['number of items'], 
            helpText='Empty tree and fill it\nwith a number of random items')
        flipButton = self.addOperation(
            "Flip color", self.clickFlip, numArguments=1, validationCmd=vcmd,
            argHelpText=['item'], helpText='Flip red/black color of item')
        rotateLeftButton = self.addOperation(
            "Rotate left", lambda: self.clickRotate(Child.LEFT), 
            numArguments=1, validationCmd=vcmd, argHelpText=['item'],
            helpText='Rotate left around item')
        rotateRightButton = self.addOperation(
            "Rotate right", lambda: self.clickRotate(Child.RIGHT),
            numArguments=1, validationCmd=vcmd, argHelpText=['item'],
            helpText='Rotate right around item')
        self.addAnimationButtons()
        return [fillButton, searchButton, insertButton, deleteButton,
                flipButton, rotateLeftButton, rotateRightButton]

if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    numArgs = [int(arg) for arg in sys.argv[1:] if arg.isdigit()]
    tree = RedBlackTree(values=numArgs if len(numArgs) > 0 else None)

    tree.runVisualization()
