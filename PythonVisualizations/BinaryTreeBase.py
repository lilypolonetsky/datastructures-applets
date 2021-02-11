from tkinter import *
import random
from enum import Enum

try:
    from coordinates import *
    from drawnValue import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .coordinates import *
    from .drawnValue import *
    from .VisualizationApp import *

V = vector

class Child(Enum):
    LEFT = 0
    RIGHT = 1

class Node(object):
    def __init__(self, drawnValue, coords, tag):
        self.drawnValue = drawnValue
        self.coords = coords
        self.tag = tag

    def getKey(self):
        return self.drawnValue.val

    def setKey(self, k):
        self.drawnValue.val = k

    def __str__(self):
        return "{" + str(self.getKey()) + "}"

class BinaryTreeBase(VisualizationApp):
    # -------- CONSTANTS ------------------
    FONT_SIZE = -16
    VALUE_FONT = ('Helvetica', FONT_SIZE)
    FOUND_FONT = ('Helvetica', FONT_SIZE)

    def __init__(self, RECT=None, CIRCLE_SIZE = 15, VAL_MAX=99, 
               ARROW_HEIGHT = 5, MAX_LEVEL = 5, **kwargs):
        """Build a VisualizationApp that will show a binary tree on part of the
        canvas within the rectangle bounded by RECT (X0, Y0, X1, Y1) which
        defaults to (0, 0, canvas width, canvas height).
        CIRCLE_SIZE is the radius of the circles used for each node in the tree.
        ARROW_HEIGHT is the length of a pointer arrow to point at a node.
        MAX_LEVEL is one more than the maximum node level allowed in the tree.
        """
        super().__init__(**kwargs)
        if RECT is None:
            RECT = (0, 0, self.targetCanvasWidth, self.targetCanvasHeight)
        X0, Y0, X1, Y1 = RECT
        self.valMax = VAL_MAX
        
        self.CIRCLE_SIZE = CIRCLE_SIZE       # radius of each node
        self.ARROW_HEIGHT = ARROW_HEIGHT     # indicator arrow height
        self.MAX_LEVEL = MAX_LEVEL           # the max level of the tree plus 1
        self.ROOT_X0 = (X0 + X1) // 2        # root's center
        self.ROOT_Y0 = Y0 + CIRCLE_SIZE + ARROW_HEIGHT + 2 * abs(
            self.VARIABLE_FONT[1])
        self.TREE_WIDTH = X1 - X0 - 2 * CIRCLE_SIZE # max tree width
        # the vertical gap between levels
        self.LEVEL_GAP = (Y1 - CIRCLE_SIZE - self.ROOT_Y0) / max(1, MAX_LEVEL - 1)

        # tree will be stored in array
        # root will be index 0
        # root's left child will be index 1, root's right child will be index 2
        self.maxElems = 2 ** self.MAX_LEVEL - 1
        self.nodes = [None] * self.maxElems
        self.size = 0

        self.prevId = -1      # One up counter for node tags

    # --------- ACCESSOR METHODS ---------------------------

    # returns the index of the node
    def getIndex(self, node):
        for i in range(len(self.nodes)):
            if self.nodes[i] is node:
                return i
      
        return -1

    # return's the node's left child's index
    def getLeftChildIndex(self, node):
        nodeIndex = self.getIndex(node)
        childIndex = 2 * nodeIndex + 1

        if childIndex >= self.maxElems: return -1
        else: return childIndex

    # return's the node's right child's index
    def getRightChildIndex(self, node):
        nodeIndex = self.getIndex(node)
        if nodeIndex == -1: return -1
        childIndex = 2 * nodeIndex + 2

        if childIndex >= self.maxElems: return -1
        else: return childIndex

    # returns the node's left child
    def getLeftChild(self, node):
        childIndex = self.getLeftChildIndex(node)

        if childIndex != -1: return self.nodes[childIndex]
        else: return None

    # returns the node's right child
    def getRightChild(self, node):
        childIndex = self.getRightChildIndex(node)

        if childIndex != -1: return self.nodes[childIndex]
        else: return None

    # returns the root node
    def getRoot(self):
        return self.nodes[0]

    # returns True if node is the root
    def isRoot(self, node):
        return self.nodes[0] is node

    # returns True if the node has no children, false otherwise
    def isLeaf(self, node):
        # if neither a right or left child exists
        if not (self.getRightChild(node) or self.getLeftChild(node)):
            return True
        else: return False

    # returns True if node is a right child, false otherwise
    def isRightChild(self, node):
        # is it the root?
        if self.isRoot(node): return False

        # right child will always be an even index
        index = self.getIndex(node)
        return index % 2 == 0

    # returns True if node is a left child, false otherwise
    def isLeftChild(self, node):
        # left child will always be an odd index
        index = self.getIndex(node)
        return index % 2 == 1

    # returns enum if node is right or left child
    # returns None if node is the root
    def getChildDirection(self, node):
        if self.isRoot(node):
            direction = None
        elif self.isRightChild(node):
            direction = Child.RIGHT
        else:
            direction = Child.LEFT
        return direction

    # returns the node's parent
    def getParent(self, node):
        # is it the root?
        if self.isRoot(node): return None

        parentIndex = self.getParentIndex(node)
        return self.nodes[parentIndex]

    def getParentIndex(self, node):
        # get node's index
        index = self.getIndex(node)
        return (index - 1) // 2

    # returns the level of the node
    def getLevel(self, node):
        if self.isRoot(node): return 0
        else: return self.getLevel(self.getParent(node)) + 1

    def getHeight(self, node):
        if not node: return -1

        rightChild = self.getRightChild(node)
        leftChild = self.getLeftChild(node)

        return max(self.getHeight(rightChild), self.getHeight(leftChild)) + 1

    # returns the line pointing to the node from its parent
    def getLine(self, node, highlight=False):
        items = self.canvas.find_withtag(node.tag + " line")
        return None if len(items) == 0 else set(items).pop()
      
    # returns a tuple of the left and right child of node
    def getChildren(self, node):
        return self.getLeftChild(node), self.getRightChild(node)

    # returns a list of all the nodes that descend from node
    def getAllDescendants(self, node):
        if not node: return []

        left, right = self.getChildren(node)
        return (([left] if left else []) + ([right] if right else []) +
                self.getAllDescendants(left) + self.getAllDescendants(right))
      

    # ----------- DRAWING METHODS -------------------
   
    # monkey patching to allow for circles to be drawn easier
    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    Canvas.create_circle = _create_circle

    def createTreeObject(
            self, label="BinarySearchTree", offsetAngle=180, offset=40,
            color='powder blue', root='root', dotColor='red', fields=[], 
            font=None):
        '''Create the tree object that points to the root of a tree.
        The object is represented with a filled rectangle holding a list
        of fields plus a final field with an arrow pointing to the root
        of the tree.
        '''
        fieldFont, labelFont = self.treeObjectFonts(font)
        fieldWidths = self.treeObjectFieldWidths(font=fieldFont, fields=fields)
        ffHeight = self.textHeight(fieldFont)
        x0, y0, x1, y1 = self.treeObjectCoords(
            offsetAngle, offset, fields, fieldFont)
        rect = self.canvas.create_rectangle(
            x0, y0, x1, y1, fill=color, tags=(label, "treeObject"))
        fieldLabels = [self.canvas.create_text(
            x0 + sum(fieldWidths[:i]) + fieldWidths[i] // 2, y0 + ffHeight,
            text=field, font=fieldFont, fill='black', anchor=S,
            tags=(label + "fieldLabel"))
                       for i, field in enumerate(fields)]
        dotCenter = V(x0, y0) + V(self.treeDotCenter(fields, fieldFont))
        arrow = self.canvas.create_line(
            *dotCenter, *dotCenter, arrow=LAST, fill='black')
        self.updateTreeObjectRootPointer(arrow=arrow, root=self.getRoot())
        rootLabel = self.canvas.create_text(
            dotCenter[0], y0 + ffHeight, text=root, font=fieldFont,
            fill='black', anchor=S, tags=(label + "fieldLabel"))
        radiusV = V((self.CIRCLE_SIZE // 2, ) * 2)
        oval = self.canvas.create_oval(
            *(V(dotCenter) - radiusV), *(V(dotCenter) + radiusV), fill=dotColor,
            width=0, tags=(label, 'dot'))
        treeLabel = self.canvas.create_text(
            x0 - 5, (y0 + y1) // 2, text=label, font=labelFont, anchor=E)
        self.treeObject = (
            rect, arrow, rootLabel, oval, *fieldLabels, treeLabel)
        return self.treeObject

    def treeObjectFonts(self, font=None):
        fieldFont = (self.VARIABLE_FONT[0] if font is None else font[0],
                     -10 if font is None else font[1])
        return fieldFont, (fieldFont[0], 14 * fieldFont[1] // 10)

    def treeObjectFieldWidths(self, fields=[], font=None):
        if font is None: fieldFont, _ = self.treeObjectFonts()
        return [self.textWidth(fieldFont, ' {} '.format(field))
                for field in fields]
    
    def treeObjectCoords(
            self, offsetAngle=180, offset=30, fields=[], font=None):
        fieldFont, _ = self.treeObjectFonts(font)
        ffHeight = self.textHeight(fieldFont)
        rootWidth = self.textWidth(fieldFont, ' root ')
        fieldsWidth = sum(self.textWidth(fieldFont, ' {} '.format(field))
                          for field in fields)
        x0, y0 = V(self.ROOT_X0, self.ROOT_Y0) + V(
            V(V(offset + self.CIRCLE_SIZE, 0).rotate(offsetAngle)) -
            V(fieldsWidth + rootWidth, self.CIRCLE_SIZE + ffHeight))
        return (x0, y0, 
                x0 + fieldsWidth + rootWidth,
                y0 + 2 * self.CIRCLE_SIZE + ffHeight)

    def treeDotCenter(self, fields=[], font=None):
        '''Relative coords of dot center within tree object rectangle'''
        fieldFont, _ = self.treeObjectFonts(font)
        rootWidth = self.textWidth(fieldFont, ' root ')
        fieldsWidth = sum(self.textWidth(fieldFont, ' {} '.format(field))
                          for field in fields)
        ffHeight = self.textHeight(fieldFont)
        return fieldsWidth + rootWidth // 2, ffHeight + self.CIRCLE_SIZE

    def updateTreeObjectRootPointer(self, arrow=None, root=None):
        '''Extend pointer of tree object to point at the root node if present
        otherwise make it zero length to be invisible'''
        if arrow is None and getattr(self, 'treeObject', None) is None:
            return
        if arrow is None:
            arrow = self.treeObject[1]
        arrowCoords = self.canvas.coords(arrow)
        self.canvas.coords(arrow, *arrowCoords[:2],
                           *(arrowCoords[:2] if root is None else
                             V(root.coords) - V(self.CIRCLE_SIZE, 0)))
        
    def createArrow(
            self, node, label=None, level=1, color='red', width=1,
            tags=['arrow'], font=None):
        '''Create an arrow pointing at either an existing node or an index
        to cell in the array of nodes.  Optionally give a text label.
        '''
        if font is None: font = self.VARIABLE_FONT
        x0, y0, x1, y1 = self.indexCoords(node, level, font)
        arrow = self.canvas.create_line(
            x0, y0, x1, y1, arrow="last", fill=color, width=width, tags=tags)
        if label is None:
            return (arrow, )
        label = self.canvas.create_text(
            x0, y0, text=label, anchor=SW, font=font, fill=color, tags=tags)
        return (arrow, label)

    def indexCoords(self, node, level, font=None):
        '''Compute coordinates of an arrow pointing at either an existing
         node or an index to cell in the array of nodes.
        '''
        if font is None: font = self.VARIABLE_FONT
        center = (node.coords if isinstance(node, Node)
                  else self.nodeCenterCoords(node))
        x0 = center[0]
        y0 = center[1] - self.CIRCLE_SIZE - self.ARROW_HEIGHT - level * abs(
            font[1])
        x1, y1 = center[0], center[1] - self.CIRCLE_SIZE
        return x0, y0, x1, y1
        
    def moveArrow(
            self, arrow, node, level=1, numSteps=10, sleepTime=0.02, font=None):
        '''Move an arrow to point at a node.  The node can be either a Node
        object, a coordinate pair, or an index to the nodes array where index
        -1 is the binary tree object.
        '''
        if isinstance(node, (int, Node)):
            newCoords = self.indexCoords(node, level, font)
        elif isinstance(node, tuple):
            if font is None: font = self.VARIABLE_FONT
            newCoords = (
                node[0], node[1] - self.CIRCLE_SIZE - self.ARROW_HEIGHT - 
                level * abs(font[1]),
                node[0], node[1] - self.CIRCLE_SIZE)
        else:
            raise ValueError('Unrecognized node type: {}'.formt(type(node)))

        self.moveItemsTo(
            arrow, 
            (newCoords,) if len(arrow) == 1 else (newCoords, newCoords[:2]), 
            steps=numSteps, sleepTime=sleepTime)

    # calculate the coordinates for the node shape based on its parent node
    def calculateCoordinates(self, parent, level, childDirection):
        if level == 0:
            return self.ROOT_X0, self.ROOT_Y0
        dx = 1/2**(level+1) * self.TREE_WIDTH
        return V(parent.coords) + V(
            -dx if childDirection == Child.LEFT else dx, self.LEVEL_GAP)

    def nodeCenterCoords(self, nodeIndex):
        '''Calculate the coordinates for node based on its index in the nodes
        array.  The index -1 indicates the binary tree object
        '''
        if nodeIndex < 0:
            treeObjectBox = (
                (0, 0, 40, 30) if getattr(self, 'treeObject', None) is None else
                self.canvas.coords(self.treeObject[0]))
            return V(V(treeObjectBox[:2]) + V(treeObjectBox[2:])) / 2 
        level, i = 0, nodeIndex
        x, y = 0, 0
        while 0 < i:
            x = x / 2 + self.TREE_WIDTH / (4 if i % 2 == 0 else -4)
            y += self.LEVEL_GAP
            i = (i - 1) // 2
        return self.ROOT_X0 + x, self.ROOT_Y0 + y
        
    def nodeShapeCoordinates(self, center):
        return (center[0] - self.CIRCLE_SIZE, center[1] - self.CIRCLE_SIZE,
                center[0] + self.CIRCLE_SIZE, center[1] + self.CIRCLE_SIZE)

    def createNodeHighlight(self, node, highlightWidth=2, color=None):
        if color is None: color = self.FOUND_COLOR
        nCoords = self.nodeShapeCoordinates(
            node.coords if isinstance(node, Node) else 
            self.nodeCenterCoords(node))
        delta = (highlightWidth, highlightWidth)
        highlightCoords = (V(nCoords[:2]) - delta) + (V(nCoords[2:]) + delta)
        return self.canvas.create_oval(
            *highlightCoords, fill=None, outline=color, width=highlightWidth)
        
    # calculate the coordinates for the line attached to the node
    def calculateLineCoordinates(self, node, parent=None):
        # get node's parent
        if parent is None:
            parent = self.getParent(node)
        return parent.coords + node.coords

    # highlight or unhighlight the line that points to the node
    def createHighlightedLine(self, node, callEnviron=None, color=None):
        line = self.getLine(node)
        if line is None:
            return
        if color is None: color = drawnValue.palette[0]
        highlightLine = self.copyCanvasItem(line)
        self.canvas.tag_lower(highlightLine,
                              self.getRoot().drawnValue.items[0])

        self.canvas.itemconfig(
            highlightLine, fill=color, width=4, tags= "highlight line")

        if callEnviron: callEnviron.add(highlightLine)

        return highlightLine

    def createHighlightedCircle(self, node, callEnviron=None, color=None):
        if color is None: color = drawnValue.palette[0]
        circle = self.copyCanvasItem(node.drawnValue.items[0])
        self.canvas.itemconfig(circle, outline=color, fill= '', width=2,
                               tags="highlight circle")

        if callEnviron: callEnviron.add(circle)

        return circle

    # creates a highlighted value on top of the normal value associated with the node
    def createHighlightedValue(self, node, callEnviron=None, color=None):
        if color is None: color = drawnValue.palette[0]
        text = self.canvas.create_text(
            *node.coords, text=node.getKey(), font=self.VALUE_FONT, fill=color,
            tags="highlight value")
      
        if callEnviron: callEnviron.add(text)

        return text

    # draws the circle and the key value
    def createNodeShape(self, x, y, key, tag, color=None):
        if color is None: color = drawnValue.palette[2]
        circle = self.canvas.create_circle(
            x, y, self.CIRCLE_SIZE, tag = tag, fill=color, outline='')
        circle_text = self.canvas.create_text(
            x, y, text=key, font=self.VALUE_FONT, tag = tag)
        for item in (circle, circle_text):
            self.canvas.tag_bind(
                item, '<Button>', lambda e: self.setArgument(key))

        return circle, circle_text

    # moves all the nodes in moveItems to their proper place
    # as defined by their place in the array
    def restoreNodesPosition(self, moveItems, sleepTime=0.05, includeLines=True):
        # get the coords for the node to move to
        items, moveCoords = [], []
        for node in moveItems:
            parent = self.getParent(node)
            node.coords = self.calculateCoordinates(parent, self.getLevel(node), self.getChildDirection(node))
            for item in self.canvas.find_withtag(node.tag):
                items.append(item)
                moveCoords.append(
                    node.coords if len(self.canvas.coords(item)) == len(node.coords)
                    else self.nodeShapeCoordinates(node.coords))
            if includeLines and parent:
                items.append(self.getLine(node))
                moveCoords.append(self.calculateLineCoordinates(node, parent))
      
        self.moveItemsLinearly(items, moveCoords, sleepTime=sleepTime)

    # draw a line pointing to node
    def createLine(self, node):
        parent = self.getParent(node)
        lineCoords = self.calculateLineCoordinates(node, parent)
        line = self.canvas.create_line(*lineCoords, tags = ("line", node.tag + " line"))
        self.canvas.tag_lower(line)

    # remove all the line drawings
    def clearAllLines(self):
        self.canvas.delete("line")

    # draw all the lines
    def drawAllLines(self):
        cur = self.getRoot()
        if cur:
            left = self.getLeftChild(cur)
            right = self.getRightChild(cur)
            self.__drawLines(left, right)

    def __drawLines(self, left, right):
        if left: 
            self.createLine(left)
            self.__drawLines(self.getLeftChild(left), self.getRightChild(left))
        if right: 
            self.createLine(right)
            self.__drawLines(self.getLeftChild(right), self.getRightChild(right))

    # remove any existing lines and draw lines
    def redrawLines(self):
        self.clearAllLines()
        self.drawAllLines()

    # ----------- SETTER METHODS --------------------
   
    # create a Node object with key and parent specified
    # parent should be a Node object
    def createNode(self, key, parent = None, direction = None):
        # calculate the level
        level = 0 if parent is None else self.getLevel(parent) + 1
      
        # calculate the coords
        coords = self.calculateCoordinates(parent, level, direction)

        # generate a tag
        tag = self.generateTag()

        # create the shape and text
        circle, circle_text = self.createNodeShape(*coords, key, tag)
      
        # create the drawnValue object
        drawnValueObj = drawnValue(key, circle, circle_text)
      
        # create the Node object
        node = Node(drawnValueObj, coords, tag)

        # increment size
        self.size += 1

        # add the node object to the internal representation
        self.setChildNode(node, direction, parent)

        # draw the lines
        if parent:
            self.createLine(node)

        return node 

    # create a copy of a Node object
    def copyNode(self, node):
        # create a tag
        tag = self.generateTag()

        # get the circle and key drawing
        circle, circle_text = self.createNodeShape(
            *node.coords, node.getKey(), tag)

        # get the key
        key = node.getKey()
        # create the drawnValue obj
        drawnValueObj = drawnValue(key, circle, circle_text)

        # add the tag
        self.canvas.itemconfig(circle, tags=tag)
        self.canvas.itemconfig(circle_text, tags=tag)
      
        return Node(drawnValueObj, node.coords, tag)

    def setRoot(self, node):
        self.nodes[0] = node

    # set the node's left child
    def setLeftChild(self, node, child):
        index = self.getLeftChildIndex(node)
        if index != -1:
            self.nodes[index] = child
            return index
        else:
            return -1

    # set the node's right child
    def setRightChild(self, node, child):
        index = self.getRightChildIndex(node)
        if index != -1:
            self.nodes[index] = child
            return index
        else:
            return -1

    # set the node's child
    # returns the index where the child is stored
    def setChildNode(self, child, direction = None, parent = None):
        if not parent:
            self.nodes[0] = child
            return 0

        if direction == Child.LEFT:
            return self.setLeftChild(parent, child)
        else:
            return self.setRightChild(parent, child)

    def moveSubtree(self, toIndex, fromIndex):
        "Move subtree rooted at fromIndex to be rooted at toIndex"
        if (toIndex < 0 or toIndex >= len(self.nodes) or
            fromIndex < 0 or fromIndex >= len(self.nodes)):
            return           # Do nothing if to or from index out of bounds
        toDo = [(toIndex, fromIndex)] # Queue of assignments to make
        while len(toDo):      # While there are subtrees to move
            top = toDo.pop(0) # Get next subtree to move from front of queue
            tIndex, fIndex = top
            fNode = self.nodes[fIndex] if fIndex < len(self.nodes) else None
            self.nodes[tIndex] = fNode
            if fNode:         # If from node exists
                for child in range(1, 3): # Loop over child's children
                    toDo.append(   # Enqueue move granchild to child position
                        (2 * tIndex + child, 2 * fIndex + child))

    def generateTag(self):
        self.prevId+=1
        return "item" + str(self.prevId)

    # remove the tree's drawing
    # empty the tree's data
    def emptyTree(self):
        self.size = 0
        self.nodes = [None] * (2**self.MAX_LEVEL)

    def display(self, fields=[]):
        self.canvas.delete("all")
        self.treeObject = self.createTreeObject(fields=fields)
        self.fieldwidths = self.treeObjectFieldWidths(fields=fields)
        newNodes = [self.createNode(
            node.getKey(), None if i == 0 else self.nodes[(i - 1) // 2],
            Child.LEFT if i % 2 == 1 else Child.RIGHT) if node else None
                    for i, node in enumerate(self.nodes)]
        self.nodes = newNodes
        
    # remove the node's drawing
    def removeNodeDrawing(self, node, line=False):
        # should the line pointing to the node be removed?
        if line: self.removeLine(node)

        self.canvas.delete(node.tag)

    # remove the line that was pointing to node
    def removeLine(self, node):
        line = self.getLine(node)
        if line: self.canvas.delete(line)

    # remove the node from the internal array
    def removeNodeInternal(self, node):
        self.nodes[self.getIndex(node)] = None
        self.size -= 1

    # rotate the node left in the array representation and animate it
    # RETURN TO FIX
    def rotateLeft(self, node):
        pass

    # rotate the nodes right in the drawing and in the array representation
    # RETURN TO FIX
    def rotateRight(self, node):
        pass

    # ----------- TESTING METHODS --------------------
   
    def inOrderTraversal(self, cur):
        if cur:
            self.inOrderTraversal(self.getLeftChild(cur))
            print(" " + str(cur), end="")
            self.inOrderTraversal(self.getRightChild(cur))

    def printTree(self, indentBy=4):
        self.__pTree(self.nodes[0], "ROOT:  ", "", indentBy)

    def __pTree(self, node, nodeType, indent, indentBy=4):
        if node:
            self.__pTree(self.getRightChild(node), "RIGHT:  ", indent + " " * indentBy, indentBy)
            print(indent + nodeType, node)
            self.__pTree(self.getLeftChild(node), "LEFT:  ", indent + " " * indentBy, indentBy)
