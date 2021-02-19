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
    '''Drawing of a node in a binary tree.  The node is represented by
    a shape with some text centered at particular place on the canvas. A
    line connects it with its parent (unless it's the root node).  The
    drawn value's items should be the (line, shape, text) items on the canvas.
    '''
    def __init__(self, drawnValue, center, tag):
        self.drawnValue = drawnValue
        self.center = center
        self.tag = tag

    def getKey(self):
        return self.drawnValue.val

    def setKey(self, key):
        self.drawnValue.val = key

    def getLine(self):
        return self.drawnValue.items[0]

    def setLine(self, lineItem):
        self.drawnValue.items = (lineItem,) + self.drawnValue.items[1:] 

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
        self.RECT = RECT
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

    # return's the node or node index's left child index
    def getLeftChildIndex(self, node):
        return self.getChildIndex(node, Child.LEFT)

    # return's the node or node index's right child index
    def getRightChildIndex(self, node):
        return self.getChildIndex(node, Child.RIGHT)

    def getChildIndex(self, node, leftOrRight):
        nodeIndex = self.getIndex(node) if isinstance(node, Node) else node
        return max(0, 2 * nodeIndex + (2 if leftOrRight == Child.RIGHT else 1))

    # return's the node or node index's parent index
    def getParentIndex(self, node):
        nodeIndex = self.getIndex(node) if isinstance(node, Node) else node
        return max(-1, (nodeIndex - 1) // 2)

    # returns the node's left child node
    def getLeftChild(self, node):
        return self.getChild(node, Child.LEFT)

    # returns the node's right child node
    def getRightChild(self, node):
        return self.getChild(node, Child.RIGHT)

    def getChild(self, node, leftOrRight):
        childIndex = self.getChildIndex(node, leftOrRight)
        return self.getNode(childIndex)

    def getNode(self, nodeIndex):  # Get a node by its index, if valid
        if isinstance(nodeIndex, Node):
            return nodeIndex
        if 0 <= nodeIndex and nodeIndex < self.maxElems:
            return self.nodes[nodeIndex]
        
    # returns the node or node index's parent node
    def getParent(self, node):
        if self.isRoot(node): return None
        return self.getNode(self.getParentIndex(node))

    # returns the root node
    def getRoot(self):
        return self.nodes[0]

    # returns True if node or node index is the root
    def isRoot(self, node):
        return (
            (self.nodes[0] is node) if isinstance(node, Node) else (node == 0))

    # returns True if the node has no children, false otherwise
    def isLeaf(self, node):
        # if neither a right or left child exists
        return not (self.getRightChild(node) or self.getLeftChild(node))

    # returns enum if node or node index is right or left child of its parent
    # returns None if node is None or the root
    def getChildDirection(self, node):
        if node is None or self.isRoot(node):
            return None
        nodeIndex = self.getIndex(node) if isinstance(node, Node) else node
        return Child.RIGHT if nodeIndex % 2 == 0 else Child.LEFT

    # returns the level of the node
    def getLevel(self, node):
        if node is None: return -1
        return 0 if self.isRoot(node) else self.getLevel(
            self.getParent(node)) + 1

    def getHeight(self, node):
        if not node: return -1
        return max(self.getHeight(self.getRightChild(node)),
                   self.getHeight(self.getLeftChild(node))) + 1
      
    # returns a tuple of the left and right child of node
    def getChildren(self, node):
        return self.getLeftChild(node), self.getRightChild(node)

    # returns a list of all the nodes that descend from a node or node index
    def getAllDescendants(self, node):
        if isinstance(node, int):
            node = self.getNode(node)
        if node is None or not isinstance(node, (int, Node)): return []
        return [node] + (
            self.getAllDescendants(self.getLeftChild(node)) +
            self.getAllDescendants(self.getRightChild(node)))

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
                             V(root.center) - V(self.CIRCLE_SIZE, 0)))
        
    def createArrow(
            self, node, label=None, level=1, color='red', width=1,
            tags=['arrow'], font=None, orientation=-90):
        '''Create an arrow pointing at either an existing node or an index
        to cell in the array of nodes.  Optionally give a text label.
        '''
        if font is None: font = self.VARIABLE_FONT
        x0, y0, x1, y1 = self.indexCoords(node, level, font, orientation)
        arrow = self.canvas.create_line(
            x0, y0, x1, y1, arrow="last", fill=color, width=width, tags=tags)
        if label is None:
            return (arrow, )
        label = self.canvas.create_text(
            x0, y0, text=label, anchor=SW, font=font, fill=color, tags=tags)
        return (arrow, label)

    def indexCoords(self, node, level, font=None, orientation=-90):
        '''Compute coordinates of an arrow pointing at either an existing
         node or an index to cell in the array of nodes.
        '''
        if font is None: font = self.VARIABLE_FONT
        center = (node.center if isinstance(node, Node)
                  else self.nodeCenter(node))
        tip = V(self.CIRCLE_SIZE, 0).rotate(orientation)
        base = V(self.CIRCLE_SIZE + self.ARROW_HEIGHT + level * abs(font[1]),
                 0).rotate(orientation)
        return (V(center) + V(base)) + (V(center) + V(tip))
        
    def moveArrow(
            self, arrow, node, level=1, numSteps=10, sleepTime=0.02, font=None,
            orientation=-90):
        '''Move an arrow to point at a node.  The node can be either a Node
        object, a coordinate pair, or an index to the nodes array where index
        -1 is the binary tree object.
        '''
        if isinstance(node, (int, Node)):
            newCoords = self.indexCoords(node, level, font, orientation)
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
        return V(parent.center) + V(
            -dx if childDirection == Child.LEFT else dx, self.LEVEL_GAP)

    def nodeCenter(self, nodeIndex):
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

    def nodeItemCoords(self, node, parent=None):
        '''Return coordinates for line to parent, shape, and text label items
        that represent a node.  The node and parent parameters can be either
        a node, a node index, or a coordinate tuple for the center of the node.
        '''
        if isinstance(node, Node):
            nodeCenter = node.center
        elif isinstance(node, int):
            nodeCenter = self.getNode(node).center
        elif isinstance(node, (tuple, list)):
            nodeCenter = node
        if isinstance(parent, Node):
            parentCenter = parent.center
        elif isinstance(parent, int) and 0 <= parent:
            parentCenter = self.getNode(parent).center
        elif isinstance(parent, (tuple, list)):
            parentCenter = parent
        else:
            parentCenter = nodeCenter
            
        return (nodeCenter + parentCenter, 
                self.nodeShapeCoordinates(nodeCenter), nodeCenter)

    def createNodeHighlight(self, node, highlightWidth=2, color=None):
        if color is None: color = self.FOUND_COLOR
        nCoords = self.nodeShapeCoordinates(
            node.center if isinstance(node, Node) else self.nodeCenter(node))
        delta = (highlightWidth, highlightWidth)
        highlightCoords = (V(nCoords[:2]) - delta) + (V(nCoords[2:]) + delta)
        return self.canvas.create_oval(
            *highlightCoords, fill=None, outline=color, width=highlightWidth)
        
    # calculate the coordinates for the line attached to the node
    def calculateLineCoordinates(self, node, parent=None):
        # get node's parent
        if parent is None:
            parent = self.getParent(node)
        return parent.center + node.center

    # highlight or unhighlight the line that points from the node to its parent
    def createHighlightedLine(self, node, callEnviron=None, color=None):
        line = node.getLine()
        if line is None:
            return
        if color is None: color = drawnValue.palette[0]
        highlightLine = self.copyCanvasItem(line)
        self.canvas.tag_lower(highlightLine,
                              self.getRoot().drawnValue.items[1])

        self.canvas.itemconfig(
            highlightLine, fill=color, width=4, tags= "highlight line")

        if callEnviron: callEnviron.add(highlightLine)

        return highlightLine

    def createHighlightedCircle(self, node, callEnviron=None, color=None):
        if color is None: color = drawnValue.palette[0]
        circle = self.copyCanvasItem(node.drawnValue.items[1])
        self.canvas.itemconfig(circle, outline=color, fill= '', width=2,
                               tags="highlight circle")

        if callEnviron: callEnviron.add(circle)

        return circle

    # creates a highlighted value on top of the normal value associated with the node
    def createHighlightedValue(self, node, callEnviron=None, color=None):
        if color is None: color = drawnValue.palette[0]
        text = self.canvas.create_text(
            *node.center, text=node.getKey(), font=self.VALUE_FONT, fill=color,
            tags="highlight value")
      
        if callEnviron: callEnviron.add(text)

        return text

    def createNodeShape(
            self, x, y, key, tag, color=None, parent=None, lineColor='black',
            lineWidth=1):
        '''Create canvas items for the circular node, its key label, and
        a line to the node centered at the parent coordinates. If parent
        is None, the line will be zero length to become invisible.
        Returns the line, circular background, and text label items
        '''
        if color is None: color = drawnValue.palette[2]
        circle = self.canvas.create_circle(
            x, y, self.CIRCLE_SIZE, tag = tag, fill=color, outline='')
        circle_text = self.canvas.create_text(
            x, y, text=key, font=self.VALUE_FONT, tag = tag)
        line = self.canvas.create_line(
            x, y, *(parent if parent else (x, y)),
            tags = ("line", tag + "_line"), fill=lineColor, width=lineWidth)
        self.canvas.tag_lower(line)
        for item in (circle, circle_text):
            self.canvas.tag_bind(
                item, '<Button>', lambda e: self.setArgument(key))

        return line, circle, circle_text

    def restoreNodePositions(self, nodes, sleepTime=0.05, includeLines=True):
        '''Moves all the nodes to their proper place on the canvas
        as defined by their indices in the array.  Lines are moved if
        requested.  If sleepTime is 0, no animation is done, just update'''
        # get the coords for the node to move to
        moveItems, moveCoords = [], []
        for node in nodes:
            nodeIndex = self.getIndex(node)
            if nodeIndex < 0:
                continue
            node.center = self.nodeCenter(nodeIndex)
            i = 0
            for item, coords in zip(
                    node.drawnValue.items,
                    self.nodeItemCoords(node.center, 
                                        parent=self.getParentIndex(nodeIndex))):
                if item and (includeLines or i > 0):
                    moveItems.append(item)
                    moveCoords.append(coords)
                i += 1
      
        if sleepTime > 0:
            self.moveItemsLinearly(moveItems, moveCoords, sleepTime=sleepTime)
        else:
            for item, coords in zip(moveItems, moveCoords):
                self.canvas.coords(item, coords)

    def restoreNodes(self, nodes=None):
        '''Restore canvas items to match internal representation of nodes.
        If nodes in None, all nodes in the tree are restored.'''
        if nodes is None:
            nodes = self.getAllDescendants(self.getRoot())
        self.restoreNodePositions(nodes, sleepTime=0)
        for node in nodes:
            key = node.getKey()
            self.canvas.itemconfigure(node.drawnValue.items[2], text=str(key))

    def outputBoxSpacing(self, font=None):
        if font is None: font = self.VALUE_FONT
        return self.textWidth(font, ' ' + str(self.valMax))
    
    def outputBoxCoords(self, font=None, padding=6, N=None):
        '''Coordinates for an output box in lower right of canvas with enough
        space to hold N values, defaulting to current tree size'''
        if N is None: N = self.size
        if font is None: font = self.VALUE_FONT
        spacing = self.outputBoxSpacing(font)
        canvasDims = self.widgetDimensions(self.canvas)
        left = max(0, canvasDims[0] - N * spacing - padding) // 2
        return (left, canvasDims[1] - abs(font[1]) * 2 - padding,
                left + N * spacing + padding, canvasDims[1] - padding)

    def createOutputBox(self, coords=None, font=None):
        if coords is None: coords = self.outputBoxCoords(font=font)
        return self.canvas.create_rectangle(*coords, fill=self.OPERATIONS_BG)
        
    def cleanUp(self, *args, **kwargs):
        '''Customize cleanUp to restore nodes when call stack is empty'''
        super().cleanUp(*args, **kwargs)
        if len(self.callStack) == 0:
            self.restoreNodes()

    # draw a line pointing to node
    def createLine(self, node):
        parent = self.getParent(node)
        lineCoords = self.calculateLineCoordinates(node, parent)
        line = self.canvas.create_line(
            *lineCoords, tags = ("line", node.tag + "_line"))
        self.canvas.tag_lower(line)

    # remove all the line drawings
    def clearAllLines(self):
        self.canvas.delete("line")


    # ----------- SETTER METHODS --------------------
   
    # create a Node object with key and parent specified
    # parent should be a Node object
    def createNode(self, key, parent = None, direction = None):
        # calculate the node index
        nodeIndex = self.getChildIndex(parent, direction) if parent else 0
      
        # calculate the node's center
        center = self.nodeCenter(nodeIndex)

        # generate a tag
        tag = self.generateTag()
      
        # create the canvas items and the drawnValue object
        drawnValueObj = drawnValue(key, *self.createNodeShape(
            *center, key, tag, parent=parent.center if parent else None))
      
        # create the Node object
        node = Node(drawnValueObj, center, tag)

        # increment size
        self.size += 1

        # add the node object to the internal representation
        self.setChildNode(node, direction, parent)

        return node 

    # create a copy of a Node object
    def copyNode(self, node):
        # create a tag
        tag = self.generateTag()

        # get the key
        key = node.getKey()
        
        # create the shapes and drawnValue obj
        drawnValueObj = drawnValue(key, *self.createNodeShape(
            *node.center, node.getKey(), tag))
      
        return Node(drawnValueObj, node.center, tag)

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

    def replaceSubtree(
            self, nodeIndex, leftOrRight, replacementIndex, callEnviron,
            wait=0.1):
        '''Move the subtree at replacementIndex to be the left or right
        child of the node at nodeIndex. Discard the current subtree of
        that node.'''
        childIndex = self.getChildIndex(nodeIndex, leftOrRight)
        child = self.getNode(childIndex)
        replacement = self.getNode(replacementIndex)
        replacementSubtree = self.getAllDescendants(replacementIndex)
        
        if child:
            if nodeIndex < 0:  # When the parent is tree object
                childLine = None # there's no child->parent line
            else:
                # Reparent child->node line to a replacement->node line
                childLine = child.getLine()
                highlightLine = self.createHighlightedLine(child, callEnviron)
                child.setLine(None)
                replacementCenter = self.nodeCenter(
                    replacementIndex if replacement else nodeIndex)
                newLineCoords = replacementCenter + self.nodeCenter(nodeIndex)
                self.moveItemsLinearly(
                    (childLine, highlightLine), (newLineCoords, newLineCoords),
                    sleepTime=wait / 10)
                self.canvas.delete(highlightLine)
                callEnviron.discard(highlightLine)
            
            # The moved line becomes the parent line of the replacemnt node
            if replacement:
                self.canvas.delete(replacement.getLine())
                replacement.setLine(childLine)
            
            for node in self.getAllDescendants(childIndex):
                if node not in replacementSubtree:
                    self.removeNodeDrawing(node)
                    self.removeNodeInternal(node)

        self.moveSubtree(childIndex, replacementIndex)
        self.restoreNodePositions(replacementSubtree, sleepTime=wait /10)
        
    def moveSubtree(self, toIndex, fromIndex):
        "Move internal subtree rooted at fromIndex to be rooted at toIndex"
        if (toIndex < 0 or toIndex >= len(self.nodes) or
            fromIndex < 0 or fromIndex >= len(self.nodes)):
            return           # Do nothing if to or from index out of bounds
        toDo = [(toIndex, fromIndex)] # Queue of assignments to make
        while len(toDo):      # While there are subtrees to move
            tIndex, fIndex = toDo.pop(0) # Get next move from front of queue
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
        self.size = sum(1 if node else 0 for node in self.nodes)
        
    # remove the node's drawing and optionally its line
    def removeNodeDrawing(self, node, line=False):
        if isinstance(node, int): node = self.getNode(node)
        self.canvas.delete(node.tag)
        # should the line pointing to the node be removed?
        if line: 
            self.canvas.delete(node.getLine())

    # remove the node from the internal array (can be a node index)
    def removeNodeInternal(self, node):
        nodeIndex = self.getIndex(node) if isinstance(node, Node) else node
        self.nodes[nodeIndex] = None
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
