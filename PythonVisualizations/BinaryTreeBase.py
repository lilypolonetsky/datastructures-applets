from tkinter import *
import random, re
from enum import Enum

try:
    from coordinates import *
    from drawnValue import *
    from tkUtilities import *
    from Signatures import *
    from VisualizationApp import *
    from OutputBox import *
    from TableDisplay import *
except ModuleNotFoundError:
    from .coordinates import *
    from .drawnValue import *
    from .tkUtilities import *
    from .Signatures import *
    from .VisualizationApp import *
    from .OutputBox import *
    from .TableDisplay import *

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
        # return "<Node: key: {}, @{}, items: {}".format(
        #         self.getKey(), self.center, self.drawnValue.items)
        return "<Node: {}>".format(self.getKey())

class BinaryTreeBase(VisualizationApp):
    # -------- CONSTANTS ------------------
    FONT_SIZE = -16
    VALUE_FONT = ('Helvetica', FONT_SIZE)
    FOUND_FONT = ('Helvetica', FONT_SIZE)
    nextColor = 0
    valMax = 99
    STACK_CELL_MIN_SIZE = (50, 10)
    STACK_DEFAULT_SIZE = (100, None)
    NONE_DOT_RADIUS = 2
    NONE_DOT_COLOR = 'red'
    DEPTH_BOUNDARY_COLOR = 'gray80'
    DEPTH_BOUNDARY_DASH = (5, 10)

    def __init__(self, RECT=None, CIRCLE_SIZE=None, VAL_MAX=valMax, 
               ARROW_HEIGHT=None, MAX_LEVEL=None, **kwargs):
        """Build a VisualizationApp that will show a binary tree on part of the
        canvas within the rectangle bounded by RECT (X0, Y0, X1, Y1) which
        defaults to (0, 0, canvas_width, canvas_height - output_box_height).
        CIRCLE_SIZE is the radius of the circles used for each node in the tree.
        ARROW_HEIGHT is the length of a pointer arrow to point at a node.
        MAX_LEVEL is one more than the maximum node level allowed in the tree.
        """
        super().__init__(**kwargs)
        self.outputFont = (self.VALUE_FONT[0], self.VALUE_FONT[1] * 9 // 10)
        self.size = 0
        self.valMax = VAL_MAX

        self.setTreeSize(RECT, circleSize=CIRCLE_SIZE,
                         arrowHeight=ARROW_HEIGHT, maxLevel=MAX_LEVEL,
                         stackWidth=self.STACK_DEFAULT_SIZE[0])

        # tree will be stored in array
        # root will be index 0
        # root's left child will be index 1, root's right child will be index 2
        self.maxElems = 2 ** self.MAX_LEVEL - 1
        self.nodes = [None] * self.maxElems

        self.prevId = -1      # One up counter for node tags

    def __str__(self):
        return '<BinarySearchTree>'

    def setTreeSize(
            self,
            rect: 'Canvas bounding box to display tree & stack' =None,
            circleSize: 'Radius of tree nodes' =None,
            arrowHeight: 'Height of arrows for node indices' =None,
            stackWidth: 'Width of area to reserve for stack' =None,
            maxLevel: 'One than maximum node level allowed' =None,
            outputFont: 'Tk font used for node values' =None):
        if circleSize is None:
            circleSize = getattr(self, 'CIRCLE_SIZE', 15)
        self.CIRCLE_SIZE = circleSize
        if arrowHeight is None:
            arrowHeight = getattr(self, 'ARROW_HEIGHT', 5)
        self.ARROW_HEIGHT = arrowHeight
        if outputFont is None:
            outputFont = getattr(self, 'outputFont', self.VALUE_FONT)
        self.outputFont = outputFont
        if maxLevel is None:
            maxLevel = getattr(self, 'MAX_LEVEL', 5)
        self.MAX_LEVEL = max(1, maxLevel)
        if stackWidth is None:
            stackWidth = getattr(self, 'STACK_DEFAULT_SIZE', (0, 0))[0]
        self.stackWidth = max(0, stackWidth)
        outputBoxHeight = self.outputBoxHeight()
        if rect is None:
            canvasDims = (self.targetCanvasWidth, self.targetCanvasHeight)
            rect = (0, 0, canvasDims[0] - stackWidth,
                    canvasDims[1] - outputBoxHeight - 3)
        self.RECT = rect
        X0, Y0, X1, Y1 = rect
        self.ROOT_X0 = (X0 + X1) // 2        # root's center
        self.ROOT_Y0 = Y0 + circleSize + arrowHeight + 3 * abs(
            self.VARIABLE_FONT[1])
        self.TREE_WIDTH = X1 - X0 - 2 * circleSize # max tree width
        self.LEVEL_GAP = (        # the vertical gap between levels
            Y1 - circleSize - self.ROOT_Y0) / max(1, self.MAX_LEVEL - 1)
        maxItems = max(1, 3 * self.MAX_LEVEL)
        height = Y1 + outputBoxHeight - Y0
        self.STACK_FONT = (
            self.VALUE_FONT[0],
            max(-int(height * 0.7 / maxItems), self.VALUE_FONT[1]))
        self.STACK_CELL_SIZE = (
            max(self.STACK_CELL_MIN_SIZE[0], circleSize * 2),
            max(self.STACK_CELL_MIN_SIZE[1], height // maxItems))
        self.STACK_0 = (X1 + (self.stackWidth - self.STACK_CELL_SIZE[0]) // 2,
                        Y1 + outputBoxHeight - 2 * self.STACK_CELL_SIZE[1])
    
    # --------- ACCESSOR METHODS ---------------------------

    # returns the index of the node
    def getIndex(self, node):
        if isinstance(node, int):
            return node
        elif not isinstance(node, Node):
            return -1
        for i, n in enumerate(self.nodes):
            if node is n:
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

    # return difference in node's child heights
    def heightDiff(self, node):
        leftChild, rightChild = self.getChildren(node)
        left = self.getHeight(leftChild) if leftChild else 0
        right = self.getHeight(rightChild) if rightChild else 0

        return left - right

    # returns the canvas line item connecting the node to its parent
    def getLine(self, node):
        n = self.getNode(node)
        return n.getLine() if n else None

    # returns the level of the node
    def getLevel(self, node):
        if self.isRoot(node): return 0
        else: return self.getLevel(self.getParent(node)) + 1

    # returns the height of the node from its deepest leaf
    def getHeight(self, node):
        n = self.getNode(node) if isinstance(node, int) else node
        if n is None: return 0
        return max(
            self.getHeight(child) for child in self.getChildren(node)) + 1
      
    # returns a tuple of the left and right child of node
    def getChildren(self, node):
        return self.getLeftChild(node), self.getRightChild(node)

    # returns a list of all the nodes that descend from a node or node index
    def getAllDescendants(self, node):
        if isinstance(node, int):
            node = self.getNode(node)
        if node is None or not isinstance(node, Node): return []
        return [node] + (
            self.getAllDescendants(self.getLeftChild(node)) +
            self.getAllDescendants(self.getRightChild(node)))

    def getNodeTree(self, node, erase=False):
        '''Return nodes in a nested list that form a [sub-]tree.
        If erase is true, the nodes array is filled with None for each
        extracted node'''
        nodeIndex = node if isinstance(node, int) else self.getIndex(node)
        node = self.getNode(nodeIndex)
        if node is None: return
        if erase: self.nodes[nodeIndex] = None
        return [node,
                self.getNodeTree(self.getLeftChildIndex(nodeIndex),
                                 erase=erase),
                self.getNodeTree(self.getRightChildIndex(nodeIndex),
                                 erase=erase)]

    def storeNodeTree(
            self: 'Place nodes from a [sub-]tree into the nodes array ',
            nodeTree: 'Subtree in the form of a nested list of nodes',
            index: 'Index to place top of subtree',
            updateCenter:'Update center coords for new position' =True
    ) -> 'Returns tuple of nodes that could not be stored (past depth limit)':

        empty = (nodeTree is None or len(nodeTree) != 3 or
                 not isinstance(nodeTree[0], Node)) # Is this an empty node?
        cutoff = ((nodeTree[0],)              # Cutoff non-empty nodes
                  if not empty and len(self.nodes) <= index else  # Beyond limit
                  ())  # otherwise nothing to cutoff
        if index < len(self.nodes): # Store node at index if valid
            self.nodes[index] = None if empty else nodeTree[0]
            if updateCenter and self.nodes[index]: # Update center if requested
                self.nodes[index].center = self.nodeCenter(index)
        return cutoff if empty else (
            cutoff +
            self.storeNodeTree(nodeTree[1], self.getLeftChildIndex(index)) +
            self.storeNodeTree(nodeTree[2], self.getRightChildIndex(index)))

    # ----------- DRAWING METHODS -------------------
   
    # monkey patching to allow for circles to be drawn easier
    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    Canvas.create_circle = _create_circle

    def createTreeObject(
            self, label="BinarySearchTree", offsetAngle=None, offset=None,
            color='powder blue', root='root', dotColor='red', fields=[], 
            font=None, scrollToSee=True):
        '''Create the tree object that points to the root of a tree.
        The object is represented with a filled rectangle holding a list
        of fields plus a final field with an arrow pointing to the root
        of the tree.
        '''
        fieldFont, labelFont = self.treeObjectFonts(font)
        fieldWidths = self.treeObjectFieldWidths(font=fieldFont, fields=fields)
        ffHeight = textHeight(fieldFont)
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
        self.updateTreeObjectRootPointer(arrow=arrow, root=self.getRoot())
        if scrollToSee:
            self.scrollToSee(self.treeObject, sleepTime=0, steps=1)
        return self.treeObject

    def treeObjectFonts(self, font=None):
        fieldFont = (self.VARIABLE_FONT[0] if font is None else font[0],
                     -10 if font is None else font[1])
        return fieldFont, (fieldFont[0], 14 * fieldFont[1] // 10)

    def treeObjectFieldWidths(self, fields=[], font=None):
        if font is None: fieldFont, _ = self.treeObjectFonts()
        return [textWidth(fieldFont, ' {} '.format(field))
                for field in fields]
    
    def treeObjectCoords(
            self, offsetAngle=None, offset=None, fields=[], font=None):
        fieldFont, _ = self.treeObjectFonts(font)
        ffHeight = textHeight(fieldFont)
        rootWidth = textWidth(fieldFont, ' root ')
        fieldsWidth = sum(textWidth(fieldFont, ' {} '.format(field))
                          for field in fields)
        if offset is None: offset = 40
        if offsetAngle is None: offsetAngle = 180
        x0, y0 = V(self.ROOT_X0, self.ROOT_Y0) + V(
            V(V(offset + self.CIRCLE_SIZE, 0).rotate(offsetAngle)) -
            V(fieldsWidth + rootWidth, self.CIRCLE_SIZE + ffHeight))
        return (x0, y0, 
                x0 + fieldsWidth + rootWidth,
                y0 + 2 * self.CIRCLE_SIZE + ffHeight)

    def treeDotCenter(self, fields=[], font=None):
        '''Relative coords of dot center within tree object rectangle'''
        fieldFont, _ = self.treeObjectFonts(font)
        rootWidth = textWidth(fieldFont, ' root ')
        fieldsWidth = sum(textWidth(fieldFont, ' {} '.format(field))
                          for field in fields)
        ffHeight = textHeight(fieldFont)
        return fieldsWidth + rootWidth // 2, ffHeight + self.CIRCLE_SIZE

    def treeObjectArrowCoords(self, **kwargs):
        treeObjectCoords = self.treeObjectCoords(**kwargs)
        dotCenter = V(treeObjectCoords[:2]) + V(
            self.treeDotCenter(fields=kwargs.get('fields', []),
                               font=kwaargs.get('font')))
        tip = (V(self.ROOT_X0, self.ROOT_Y0) + V(self.CIRCLE_SIZE, 0).rotate(
            kwargs.get('offsetAngle', 180))) if self.getRoot() else dotCenter
        return dotCenter + tip
        
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
            self,
            nodeOrCoords: 'Node, or node index, or node center coords',
            label: 'Label name for arrow' =None,
            level: 'Length of arrow, 1 is closest to center' =1,
            color: 'Arrow and text label color' ='red',
            width: 'Arrow width' =1,
            tags: 'Canvas item tags' =['arrow'], 
            font: 'Label font' =None,
            orientation: 'Arrow orientation, 0 is horizontal' =-90,
            anchor: 'Label text anchor relation to arrow base' =SW
    ) -> '(arrow_item, label_item or None)':
        '''Create an arrow pointing at either an existing node or the
        center of a node located at the give coordinates.  Nodes can
        be passed as either a Node object or an index in the array of nodes.
        Optionally give a text label.
        '''
        if font is None: font = self.VARIABLE_FONT
        arrowCoords, labelCoords = self.indexCoords(
            nodeOrCoords, level, font, orientation)
        arrow = self.canvas.create_line(
            *arrowCoords, arrow="last", fill=color, width=width, tags=tags)
        if label is None:
            return (arrow, )
        label = self.canvas.create_text(
            *labelCoords, text=label, anchor=anchor, font=font, fill=color,
            tags=tags)
        return (arrow, label)

    def indexCoords(
            self,
            nodeOrCoords: 'Node, or node index, or node center coords',
            level: 'Length of arrow, 1 is closest to center, 0 -> no arrow' =1,
            font: 'Label font' =None,
            orientation: 'Arrow orientation, 0 is horizontal' =-90,
            **kwargs
    ) -> '(arrow_coords, label_anchor_coords)':
        '''Compute coordinates of an arrow pointing at either an existing
        node or some canvas coordinates.  Nodes can either be a Node
        object or an index to cell in the array of nodes.  Node index -1
        refers to the binary tree object.
        Return the arrow coordiantes (base + tip) and anchor coordinates of 
        the label at the arrow's base.
        '''
        if font is None: font = self.VARIABLE_FONT
        center = (nodeOrCoords.center if isinstance(nodeOrCoords, Node)
                  else self.nodeCenter(nodeOrCoords)
                  if isinstance(nodeOrCoords, int) else nodeOrCoords)
        tip = V(self.CIRCLE_SIZE, 0).rotate(orientation)
        base = V(self.CIRCLE_SIZE + (0 if level == 0 else self.ARROW_HEIGHT) +
                 level * abs(font[1]), 0).rotate(orientation)
        return (V(center) + V(base)) + (V(center) + V(tip)), V(center) + V(base)
        
    def moveArrow(
            self,
            arrow: '(line_item, text_item)',
            nodeOrCoords: 'Node, node index, or coordinates',
            numSteps: 'Number of animation steps' =10,
            sleepTime: 'Sleep time between steps' =0.02,
            **kwargs: 'Keyword args for indexCoords'):
        '''Move an arrow to point at a node.  The node can be either a Node
        object, a coordinate pair, or an index to the nodes array where index
        -1 is the binary tree object.
        '''
        if isinstance(nodeOrCoords, (int, Node)):
            newArrow, newLabel = self.indexCoords(nodeOrCoords, **kwargs)
        elif isinstance(nodeOrCoords, (list, tuple)):
            n0Arrow, n0Label = self.indexCoords(0, **kwargs)
            center = self.nodeCenter(0)
            newArrow = V(V(n0Arrow) - V(center * 2)) + V(nodeOrCoords * 2)
            newLabel = V(V(n0Label) - V(center)) + V(nodeOrCoords)
        else:
            raise ValueError('Unrecognized node type: {}'.formt(type(node)))

        self.moveItemsTo(
            arrow, (newArrow,) if len(arrow) == 1 else (newArrow, newLabel), 
            steps=numSteps, sleepTime=sleepTime)

    def nodeCenter(self, node):
        '''Calculate the coordinates for node based on its index in the nodes
        array or from its center attribute, if a Node is passed.  The index -1
        indicates the binary tree object.
        '''
        if isinstance(node, Node):
            return node.center
        if node < 0:
            treeObjectBox = (
                (0, 0, 40, 30) if getattr(self, 'treeObject', None) is None else
                self.canvas.coords(self.treeObject[0]))
            return V(V(treeObjectBox[:2]) + V(treeObjectBox[2:])) / 2 
        level, i = 0, node
        x, y = 0, 0
        while 0 < i:
            x = x / 2 + self.TREE_WIDTH / (4 if i % 2 == 0 else -4)
            y += self.LEVEL_GAP
            i = (i - 1) // 2
        return self.ROOT_X0 + x, self.ROOT_Y0 + y
        
    def nodeShapeCoordinates(self, center, radius=None):
        if radius is None: radius = self.CIRCLE_SIZE
        offset = V(radius, radius)
        return (V(center) - offset) + (V(center) + offset)

    def nodeItemCoords(self, node, parent=None, radius=None):
        '''Return coordinates for line to parent, shape, and text label items
        that represent a node.  The node and parent parameters can be either
        a node, a node index, or a coordinate tuple for the center of the node.
        '''
        if isinstance(node, (Node, int)):
            nodeCenter = self.nodeCenter(node)
        elif isinstance(node, (tuple, list)):
            nodeCenter = node
        if isinstance(parent, Node) or isinstance(parent, int) and 0 <= parent:
            parentCenter = self.nodeCenter(parent)
        elif isinstance(parent, (tuple, list)):
            parentCenter = parent
        else:
            parentCenter = nodeCenter
            
        return (nodeCenter + parentCenter, 
                self.nodeShapeCoordinates(nodeCenter, radius=radius),
                nodeCenter)

    def createNodeHighlight(
            self, node, highlightWidth=2, color=None, radius=None):
        if color is None: color = self.FOUND_COLOR
        nCoords = self.nodeShapeCoordinates(
            node.center if isinstance(node, Node) else self.nodeCenter(node),
            radius=radius)
        delta = (highlightWidth, highlightWidth)
        highlightCoords = (V(nCoords[:2]) - delta) + (V(nCoords[2:]) + delta)
        return self.canvas.create_oval(
            *highlightCoords, fill=None, outline=color, width=highlightWidth)
        
    # calculate the coordinates for the line from a node to its parent
    def lineCoordinates(self, node, parent=None):
        # get node's parent
        if parent is None:
            parent = self.getParent(node)
        return node.center + (
            self.getNode(parent).center if parent is not None else node.center)

    # highlight or unhighlight the line that points from the node to its parent
    def createHighlightedLine(
            self, node, callEnviron=None, color=None, width=4, tags=None):
        line = node.getLine()
        if line is None:
            return
        if color is None: color = drawnValue.palette[0]
        tags = ['highlight', 'line'] + (
            [] if tags is None else tags.split() if isinstance(tags, str) else
            list(tags))
        highlightLine = self.canvas.copyItem(line)
        self.canvas.tag_lower(highlightLine,
                              self.getRoot().drawnValue.items[1])

        self.canvas.itemconfig(
            highlightLine, fill=color, width=width, tags=tags)

        if callEnviron: callEnviron.add(highlightLine)

        return highlightLine

    def createNodeShape(
            self, x, y, key, tag, color=None, parent=None, radius=None,
            font=None, lineColor='black', lineWidth=1):
        '''Create canvas items for the circular node, its key label, and
        a line to the node centered at the parent coordinates. If parent
        is None, the line will be zero length to become invisible.
        Returns the line, circular background, and text label items
        '''
        if color is None: 
            color = drawnValue.palette[self.nextColor]
            self.nextColor = (self.nextColor + 1) % len(drawnValue.palette)
        if radius is None: radius = self.CIRCLE_SIZE
        if font is None: font = self.VALUE_FONT
        coords = self.nodeItemCoords((x, y), parent=parent, radius=radius)
        line = self.canvas.create_line(
            *coords[0], arrow=FIRST, tags=("line", tag + "_line"),
            fill=lineColor, width=lineWidth)
        circle = self.canvas.create_oval(
            *coords[1], tag=tag, fill=color, outline='')
        circle_text = self.canvas.create_text(
            *coords[2], text=key, font=font, tag=tag)
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
        for node in nodes: # Restore text label above shape background
            shape, text = node.drawnValue.items[1:3]
            if self.canvas.type(text):
                self.canvas.itemConfig(text, text=str(node.getKey()))
                if self.canvas.type(shape):
                    self.canvas.tag_raise(text, shape)
        
    def upperRightNodeCoords(self, level=1):
        return (self.RECT[2] - self.CIRCLE_SIZE,
                self.RECT[1] + self.CIRCLE_SIZE * (2.5 * level - 1))

    def outputBoxSpacing(self, font=None):
        if font is None: font = getattr(self, 'outputFont', self.VALUE_FONT)
        return textWidth(font, ' ' + str(self.valMax))

    def outputBoxHeight(self, circleSize=None, font=None, padding=6):
        if font is None: font = getattr(self, 'outputFont', self.VALUE_FONT)
        if circleSize is None: circleSize = getattr(self, 'CIRCLE_SIZE', 15)
        return max(2 * circleSize, abs(font[1]) * 2 + padding)
    
    def outputBoxCoords(self, font=None, padding=6, N=None, canvasDims=None):
        '''Coordinates for an output box in lower right of canvas with enough
        space to hold N values, defaulting to current tree size, and center-
        aligned with the tree root.
        '''
        if N is None: N = max(1, getattr(self, 'size', 0))
        if font is None: font = getattr(self, 'outputFont', self.VALUE_FONT)
        spacing = self.outputBoxSpacing(font)
        if canvasDims is None:
            canvasDims = widgetDimensions(self.canvas)
        width = max(2 * self.CIRCLE_SIZE, N * spacing) + 2 * padding
        center = getattr(self, 'ROOT_X0', canvasDims[0] // 2)
        left = max(0,  center - width // 2)
        height = self.outputBoxHeight(
            circleSize=self.CIRCLE_SIZE, font=font, padding=padding)
        return (left, canvasDims[1] - height - padding,
                left + width, canvasDims[1] - padding)

    def createOutputBox(self, coords=None, font=None, **kwargs):
        if coords is None:
            config = dict((k, kwargs[k])
                          for k in keywordParameters(outputBoxCoords)
                          if k in kwargs)
            coords = self.outputBoxCoords(font=font, **config)
        return OutputBox(self, coords, outputFont=font, **kwargs)
        
    def cleanUp(self, *args, **kwargs):
        '''Customize cleanUp to restore nodes when call stack is empty'''
        super().cleanUp(*args, **kwargs)
        if len(self.callStack) == 0:
            self.restoreNodes()

    # draw a line pointing to node from its parent, if any
    def createLine(self, node):
        line = self.canvas.create_line(
            *self.lineCoordinates(node), tags = ("line", node.tag + "_line"),
            arrow=FIRST)
        self.canvas.tag_lower(line)

    # remove all the line drawings
    def clearAllLines(self):
        self.canvas.delete("line")


   # ----------- SETTER METHODS --------------------
   
    # create a Node object with key and parent specified
    # parent should be a Node object
    def createNode(self, key, parent=None, direction=None, color=None, 
                   addToArray=True, center=None):
        # calculate the node index
        nodeIndex = self.getChildIndex(parent, direction) if parent else 0
        if direction is None:
            direction = Child.LEFT if nodeIndex % 2 == 1 else Child.RIGHT
      
        # calculate the node's center
        if center is None: center = self.nodeCenter(nodeIndex)

        # generate a tag
        tag = self.generateTag()
      
        # create the canvas items and the drawnValue object
        drawnValueObj = drawnValue(key, *self.createNodeShape(
            *center, key, tag, parent=None, color=color))
      
        # create the Node object
        node = Node(drawnValueObj, center, tag)

        # increment size
        self.size += 1

        # add the node object to the internal representation
        if addToArray: 
            self.setChildNode(node, direction, parent, updateLink=True)

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
    def setLeftChild(self, node, child, updateLink=False):
        index = self.getLeftChildIndex(node)
        if index != -1 and index < len(self.nodes):
            self.nodes[index] = child
            if updateLink and child and child.getLine():
                self.canvas.coords(child.getLine(), 
                                   *self.lineCoordinates(child, node))
            return index
        else:
            return -1

    # set the node's right child
    def setRightChild(self, node, child, updateLink=False):
        index = self.getRightChildIndex(node)
        if index != -1 and index < len(self.nodes):
            self.nodes[index] = child
            if updateLink and child and child.getLine():
                self.canvas.coords(child.getLine(), 
                                   *self.lineCoordinates(child, node))
            return index
        else:
            return -1

    # set the node's child
    # returns the index where the child is stored
    def setChildNode(self, child, direction, parent=None, updateLink=False):
        if parent is None or parent == -1:
            self.nodes[0] = child
            return 0

        if direction == Child.LEFT:
            return self.setLeftChild(parent, child, updateLink=updateLink)
        else:
            return self.setRightChild(parent, child, updateLink=updateLink)

    def replaceSubtree(
            self: 'Move a subtree to be the left or right child of a node',
            nodeIndex: 'Node index to get new child subtree',
            leftOrRight: 'Side of node to receive new subtree',
            replacementIndex: 'Source subtree index',
            callEnviron: 'Animation environment',
            wait: 'Wait time between animation steps' =0.1
    ) -> 'Returns tuple of nodes that could not be stored (past depth limit)':
        '''Animate the process by moving leftOrRight child link
        first (when nodeIndex points at an existing node) and then the
        nodes in the subtrees'''
        childIndex = self.getChildIndex(nodeIndex, leftOrRight)
        child = self.getNode(childIndex)
        replacementRoot = self.getNode(replacementIndex)
        replacementNodes = self.getAllDescendants(replacementIndex)
        
        if child:
            if nodeIndex < 0:  # When the parent is tree object
                childLine = None # there's no child->parent line
            else:
                # Reparent child->node line to a replacement->node line
                childLine = child.getLine()
                highlightLine = self.createHighlightedLine(child, callEnviron)
                child.setLine(None)
                replacementCenter = self.nodeCenter(
                    replacementIndex if replacementRoot else nodeIndex)
                newLineCoords = replacementCenter + self.nodeCenter(nodeIndex)
                self.moveItemsLinearly(
                    (childLine, highlightLine), (newLineCoords, newLineCoords),
                    sleepTime=wait / 10)
                self.canvas.delete(highlightLine)
                callEnviron.discard(highlightLine)
            
            # The moved line becomes the parent line of the replacemnt node
            if replacementRoot:
                self.canvas.delete(replacementRoot.getLine())
                replacementRoot.setLine(childLine)
            
            for node in self.getAllDescendants(childIndex):
                if node not in replacementNodes:
                    self.removeNodeDrawing(node)
                    self.removeNodeInternal(node)

        cutoff = self.moveSubtree(childIndex, replacementIndex)
        self.restoreNodePositions(replacementNodes, sleepTime=wait /10)
        return cutoff
        
    def moveSubtree(
            self: 'Move internal subtree from one place to another',
            toIndex: 'Destination subtree root',
            fromIndex: 'Source subtree root'
    ) -> 'Returns tuple of nodes that could not be stored (past depth limit)':
        if toIndex < 0 or len(self.nodes) <= toIndex or toIndex == fromIndex:
            return ()  # Do nothing if the to index is out of bounds or = from

        return self.storeNodeTree(self.getNodeTree(fromIndex, erase=True),
                                  toIndex)

    def generateTag(self):
        self.prevId+=1
        return "item" + str(self.prevId)

    # remove node and any of its descendants from the internal array
    def clearDescendants(self, node, subSize = True):
        if isinstance(node, Node):
            nodeIndex = self.getIndex(node)
        else:
            nodeIndex = node

        # stop if node does not exist in tree
        if not node or nodeIndex == -1 or nodeIndex >= self.maxElems: return
        
        # get the child indices
        leftIndex = 2*nodeIndex + 1
        rightIndex = 2*nodeIndex + 2
        
        # remove from tree
        self.nodes[nodeIndex] = None
        if subSize: self.size -= 1

        # recursively remove children
        self.clearDescendants(leftIndex, subSize= subSize)
        self.clearDescendants(rightIndex, subSize = subSize)

    # remove the tree's drawing
    # empty the tree's data
    def emptyTree(self):
        self.size = 0
        self.nodes = [None] * self.maxElems

    def display(self, fields=[], treeLabel="BinarySearchTree"):
        self.canvas.delete("all")
        self.treeObject = self.createTreeObject(fields=fields, label=treeLabel)
        self.fieldwidths = self.treeObjectFieldWidths(fields=fields)
        newNodes = [self.createNode(
            node.getKey(), None if i == 0 else self.nodes[(i - 1) // 2],
            Child.LEFT if i % 2 == 1 else Child.RIGHT) if node else None
                    for i, node in enumerate(self.nodes)]
        self.nodes = newNodes
        self.size = sum(1 if node else 0 for node in self.nodes)
        depthBoundary = (self.nodeCenter(len(self.nodes) + 1) +
                         self.nodeCenter(len(self.nodes) * 2))
        self.canvas.create_line(
            *depthBoundary, fill=self.DEPTH_BOUNDARY_COLOR,
            dash=self.DEPTH_BOUNDARY_DASH, tags='boundary')
        
    # remove the node's drawing and optionally its line
    def removeNodeDrawing(self, node, line=False):
        if isinstance(node, int): node = self.getNode(node)
        for item in node.drawnValue.items[0 if line else 1:]:
            self.canvas.delete(item)

    # remove the node from the internal array (can be a node index)
    def removeNodeInternal(self, node):
        nodeIndex = self.getIndex(node) if isinstance(node, Node) else node
        if 0 <= nodeIndex:
            self.nodes[nodeIndex] = None
            self.size -= 1
        
    def fill(self, values, animation=False):
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

    def removeNodesInternal(self, nodeList):
        for node in nodeList:
            self.removeNodeInternal(node)
        
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

        # Create the node off the canvas to be moved into place, if needed
        if node < self.maxElems:
            newNode = self.createNode(
                key, parent=None if parent < 0 else self.nodes[parent],
                direction=Child.LEFT
                if parent < 0 or key < self.nodes[parent].getKey() else
                Child.RIGHT, addToArray=False,
                center=self.newValueCoords() if animation else None)
            callEnviron |= set(newNode.drawnValue.items)
            
        if animation:
            nodeIndex = self.createArrow(node, label='node')
            parentIndex = self.createArrow(parent, label='parent', level=2)
            callEnviron |= set(nodeIndex + parentIndex)
            self.highlightCode(('node', 2), callEnviron, wait=wait)
        if self.getNode(node):
            existingNode = self.getNode(node)
            oldData = existingNode.drawnValue.items[1]
            newData = newNode.drawnValue.items[1]
            if animation:
                nodeHighlight = self.createNodeHighlight(node)
                callEnviron.add(nodeHighlight)
                self.highlightCode('node.data = data', callEnviron)
                self.canvas.tag_lower(newData, existingNode.drawnValue.items[2])
                self.moveItemsTo(
                    newData, self.canvas.coords(oldData), sleepTime=wait / 10)
            self.canvas.copyItemAttributes(newData, oldData, 'fill')
            if animation:
                self.canvas.delete(newData)
                callEnviron.discard(newData)
                self.highlightCode('return False', callEnviron, wait=wait)

        elif animation and self.highlightCode(
                'parent is self', callEnviron, wait=wait) or parent == -1:
            if animation:
                self.highlightCode('self.__root = self.__Node(key, data)',
                                   callEnviron, wait=wait)
                self.moveItemsTo(
                    newNode.drawnValue.items, self.nodeItemCoords(0),
                    sleepTime= wait / 10)
            newNode.center = self.nodeCenter(0)
            self.setChildNode(newNode, Child.LEFT, parent=None)
            callEnviron -= set(newNode.drawnValue.items)
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
                    '\n         key, data, right=node)', callEnviron)
                self.moveItemsLinearly(
                    newNode.drawnValue.items,
                    self.nodeItemCoords(node, parent), sleepTime=wait / 10)
                if dir == 'left':
                    self.canvas.itemConfig(nodeIndex[1], anchor=SE)
                self.moveItemsBy(
                    nodeIndex, (0, - self.LEVEL_GAP // 3), sleepTime=wait/10)
            newNode.center = self.nodeCenter(node)
            self.setChildNode(
                newNode, Child.LEFT if dir == 'left' else Child.RIGHT, parent,
                updateLink=True)
            callEnviron -= set(newNode.drawnValue.items)
            inserted = True
 
        if animation and inserted:
            self.highlightCode('return True', callEnviron, wait=wait)
            
        self.cleanUp(callEnviron)
        return inserted

    traverseExampleCode = '''
for key, data in tree.traverse({traverseType!r}):
   print(key)
'''
    
    def traverseExample(
            self, traverseType, code=traverseExampleCode, start=True, wait=0.1):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=wait / 10, 
            startAnimations=start)

        traverseTypeText = self.canvas.create_text(
            *self.upperRightNodeCoords(),
            text='traverseType: {!r}'.format(traverseType),
            anchor=E, font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(traverseTypeText)
        
        outBoxCoords = self.outputBoxCoords(font=self.outputFont)
        outBoxMidY = (outBoxCoords[1] + outBoxCoords[3]) // 2
        outputBox = self.createOutputBox(
            coords=outBoxCoords, outputOffset=(5, 10))
        callEnviron |= set(outputBox.items())
        
        iteratorCall = 'key, data in tree.traverse({traverseType!r})'.format(
            **locals())
        self.iteratorStack = []
        self.highlightCode(iteratorCall, callEnviron, wait=wait)
        dataIndex = None
        localVars = ()
        colors = self.canvas.fadeItems(localVars)
        for key, items in self.traverse(traverseType):
            self.canvas.restoreItems(localVars, colors)
            nodeindex, _  = self._find(key, animation=False, code='')
            if dataIndex is None:
                dataIndex = self.createArrow(
                    nodeindex, 'key, data', orientation=-135)
                callEnviron |= set(dataIndex)
                localVars += dataIndex
            else:
                self.moveItemsTo(
                    dataIndex, self.indexCoords(nodeindex, 1, orientation=-135),
                    sleepTime=wait / 10)

            self.highlightCode('print(key)', callEnviron, wait=wait)
            keyItem = self.canvas.copyItem(
                self.getNode(nodeindex).drawnValue.items[2])
            callEnviron.add(keyItem)
            outputBox.appendText(keyItem, sleepTime=wait / 10)
            callEnviron.discard(keyItem)

            self.highlightCode(iteratorCall, callEnviron, wait=wait)
            colors = self.canvas.fadeItems(localVars)

        self.canvas.restoreItems(localVars, colors)
        while self.iteratorStack:
            self.cleanUp(self.iteratorStack.pop())
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        
    traverseCode = '''
def traverse(self, traverseType={traverseType!r}):
   if traverseType not in ['pre', 'in', 'post']:
      raise ValueError(
         "Unknown traversal type: " + str(traverseType))

   stack = Stack()
   stack.push(self.__root)
   
   while not stack.isEmpty():
      item = stack.pop()
      if isinstance(item, self.__Node):
         if traverseType == 'post':
            stack.push((item.key, item.data))
         stack.push(item.rightChild)
         if traverseType == 'in':
            stack.push((item.key, item.data))
         stack.push(item.leftChild)
         if traverseType == 'pre':
            stack.push((item.key, item.data))
      elif item:
         yield item
'''

    def traverse(self, traverseType='in', code=traverseCode, wait=0.1):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()))

        if self.highlightCode("traverseType not in ['pre', 'in', 'post']",
                              callEnviron, wait=wait,
                              returnValue=traverseType not in
                              ['pre', 'in', 'post']):
            self.highlightCode(
                re.compile(r'raise ValueError.*\n.*str\(traverseType\)\)'),
                callEnviron, color=self.EXCEPTION_HIGHLIGHT)
            self.cleanUp(callEnviron)
            return
        
        self.highlightCode('stack = Stack()', callEnviron, wait=wait)
        self.traverseStack = Table(
            self, self.STACK_0,
            cellWidth=self.STACK_CELL_SIZE[0], cellBorderWidth=1,
            cellHeight=self.STACK_CELL_SIZE[1], vertical=True, direction=-1,
            label='stack',
            labelFont=self.VARIABLE_FONT, labelColor=self.VARIABLE_COLOR)
        callEnviron |= set(self.traverseStack.items())

        self.highlightCode('stack.push(self.__root)', callEnviron, wait=wait)
        root = self.getRoot()
        self.stackPush(root, callEnviron, wait=wait,
                       center=self.nodeCenter(0 if root else -1))

        itemArrow = None
        self.highlightCode('not stack.isEmpty()', callEnviron, wait=wait)
        while len(self.traverseStack) > 0:
            self.highlightCode('item = stack.pop()', callEnviron, wait=wait)
            if itemArrow is None:
                arrowCoords = self.traverseItemArrowCoords(None)
                center0 = BBoxCenter(self.traverseStack.cellCoords(0))
                itemArrow = self.createArrow(
                    (center0[0], arrowCoords[1][1]), 'item', level=0,
                    **self.traverseItemConfig)
                callEnviron |= set(itemArrow)
                self.canvas_coords(itemArrow[1], *arrowCoords[1])
                secondLabel = self.canvas.copyItem(itemArrow[1])
                callEnviron.add(secondLabel)
            else:
                self.moveItemsLinearly(
                    itemArrow, self.traverseItemArrowCoords(None),
                    sleepTime=0, steps=1)
            
            item = self.stackPop(callEnviron, wait=wait)
            
            if self.highlightCode(
                    'isinstance(item, self.__Node)', callEnviron, wait=wait,
                    returnValue=isinstance(item.val, Node)):
                self.moveItemsLinearly(
                    itemArrow, self.traverseItemArrowCoords(item.val),
                    sleepTime=wait / 10)
                if self.highlightCode(
                        "traverseType == 'post'", callEnviron,
                        wait=wait, returnValue=traverseType == 'post'):
                    self.highlightCode(
                        ('stack.push((item.key, item.data))', 1), callEnviron)
                    self.stackPush(item, callEnviron, wait=wait)

                self.highlightCode(
                    'stack.push(item.rightChild)', callEnviron)
                self.stackPush(
                    self.getRightChild(item.val), callEnviron, wait=wait,
                    center=self.nodeCenter(self.getRightChildIndex(item.val)))

                if self.highlightCode(
                        "traverseType == 'in'", callEnviron,
                        wait=wait, returnValue=traverseType == 'in'):
                    self.highlightCode(
                        ('stack.push((item.key, item.data))', 2), callEnviron)
                    self.stackPush(item, callEnviron, wait=wait)

                self.highlightCode(
                    'stack.push(item.leftChild)', callEnviron),
                self.stackPush(
                    self.getLeftChild(item.val), callEnviron, wait=wait,
                    center=self.nodeCenter(self.getLeftChildIndex(item.val)))

                if self.highlightCode(
                        "traverseType == 'pre'", callEnviron,
                        wait=wait, returnValue=traverseType == 'pre'):
                    self.highlightCode(
                        ('stack.push((item.key, item.data))', 3), callEnviron)
                    self.stackPush(item, callEnviron, wait=wait)
                
            elif self.highlightCode(
                    ('item', 11), callEnviron, wait=wait,
                    returnValue=item.val is not None):
                self.highlightCode('yield item', callEnviron, wait=wait)
                itemCoords = self.yieldCallEnvironment(
                    callEnviron, sleepTime=wait / 10)
                yield item.val, item.items
                self.resumeCallEnvironment(
                    callEnviron, itemCoords, sleepTime=wait / 10)
                self.dispose(callEnviron, *item.items)
                
            else:
                self.dispose(callEnviron, *item.items)
                
            self.highlightCode('not stack.isEmpty()', callEnviron, wait=wait)

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    def stackPush(
            self,
            thing: 'A Node, tuple, or None to push on the traverse stack',
            callEnviron: 'Call environment for traverse iterator',
            center: 'Center of dot representing None at child center' =None,
            wait: 'Total animation time' =0.1):
        stackHeight = len(self.traverseStack)
        cellCoords = self.traverseStack.cellCoords(stackHeight)
        cellCenter = BBoxCenter(cellCoords)
        cellSize = V(cellCoords[2:]) - V(cellCoords[:2])
        halfCell = V(cellSize) // 2
        startFont = endFont = None
        if isinstance(thing, Node):
            nodeItems = thing.drawnValue.items
            center = thing.center
            stackRect = self.canvas.create_rectangle(
                *(V(center) - V(halfCell)),
                *(V(V(center) + V(cellSize)) - V(halfCell)),
                fill=self.canvas_itemConfig(nodeItems[1], 'fill'), outline='',
                width=0)
            keyCopy = self.canvas.copyItem(nodeItems[2])
            startFont = self.getItemFont(nodeItems[2])
            endFont = self.STACK_FONT
            toMove = (stackRect, keyCopy)
            moveTo = (cellCoords, cellCenter)
            callEnviron |= set(toMove)
            
        elif isinstance(thing, drawnValue):
            toMove = thing.items
            moveTo = ((cellCoords[0] + halfCell[0], *cellCoords[1:]),
                      (cellCoords[0] + halfCell[0] // 2,
                       (cellCoords[1] + cellCoords[3]) // 2))
            key = thing.val.drawnValue.val
            newText = self.canvas_itemConfig(thing.items[1], 'text') + ', '
            self.canvas_itemConfig(thing.items[1], text=newText)
            thing = key
            
        else:
            dotRadius = V((self.NONE_DOT_RADIUS, self.NONE_DOT_RADIUS))
            noneDot = self.canvas.create_oval(
                *(V(center) - dotRadius), *(V(center) + dotRadius),
                fill=self.NONE_DOT_COLOR, outline='', width=0)
            callEnviron.add(noneDot)
            toMove = (noneDot,)
            moveTo = (
                (V(cellCenter) - dotRadius) + (V(cellCenter) + dotRadius),)
            
        self.moveItemsLinearly(toMove, moveTo, sleepTime=wait / 10,
                               startFont=startFont, endFont=endFont)
        self.traverseStack.append(drawnValue(thing, *toMove))
        callEnviron |= set(self.traverseStack.items())
        
    def stackPop(
            self,
            callEnviron: 'Call environment for traverse iterator',
            wait: 'Total animation time' =0.1):
        top = self.traverseStack[-1]
        topCenter = BBoxCenter(self.canvas_coords(top.items[0]))
        labelCoords = V(self.traverseItemLabelCoords()) + V(
            0, self.traverseStack.cellHeight)
        self.moveItemsBy(top.items, (0, labelCoords[1] - topCenter[1]),
                         sleepTime=wait / 10)
        return self.traverseStack.pop()

    traverseItemConfig = {
        'color': VisualizationApp.VARIABLE_COLOR, 'orientation': -45,
        'anchor': None}
    
    def traverseItemLabelCoords(self):
        if getattr(self, 'traverseStack', None) is None:
            raise Exception('Cannot call itemCoords before stack creation')
        labelCoords = self.traverseStack.labelCoords()
        traverseTypeCoords = self.upperRightNodeCoords()
        return labelCoords[0], traverseTypeCoords[1]

    def traverseItemArrowCoords(self, item):
        if isinstance(item, Node):
            return self.indexCoords(item, **self.traverseItemConfig)
        elif item is None or isinstance(item, tuple):
            labelCoords = self.traverseItemLabelCoords()
            return labelCoords + labelCoords, labelCoords
        
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
            self.setMessage('Key {} {}'.format(
                val,
                'inserted' if self.insert(val, start=self.startMode())
                else 'updated or not inserted'))
            self.clearArgument()

    def clickSearch(self):
        val = self.validArgument()
        if val:
            self.setMessage(
                "Key {} not found".format(val) if self.search(
                    val, start=self.startMode()) is None else 
                "Found key {}".format(val))
            self.clearArgument()

    def clickFill(self):
        val = self.validArgument()
        if val is not None:
            self.fill(val)
            self.clearArgument()
        
    def clickTraverse(self, traverseType):
        self.traverseExample(traverseType, start=self.startMode())

    def print(self, indentBy=' ' * 4, **kwargs):
        self.__pTree(self.nodes[0], "", indentBy, **kwargs)

    def __pTree(self, node, indent, indentBy, **kwargs):
        if node:
            self.__pTree(
                self.getRightChild(node), indent + indentBy, indentBy, **kwargs)
            print(indent, '{:2d}'.format(self.getIndex(node)), node, **kwargs)
            self.__pTree(
                self.getLeftChild(node), indent + indentBy, indentBy, **kwargs)
            
    def orphaned(self, **kwargs):
        allNodes = self.getAllDescendants(0)
        for i, node in enumerate(self.nodes):
            if node is not None and node not in allNodes:
                print('At {:2d} {} is an orphan'.format(i, node), **kwargs)
                parentIndex = self.getParentIndex(i)
                if 0 <= i and self.nodes[parentIndex] is not None:
                    print(' but parent at {} contains {}'.format(
                        parentIndex, self.nodes[parentIndex]), **kwargs)

if __name__ == '__main__':
    import sys, random
    random.seed(3.14159)  # Use fixed seed for testing consistency
    numArgs = [int(arg) for arg in sys.argv[1:] if arg.isdigit()]
    tree = BinaryTreeBase()
    if numArgs:
        tree.fill(numArgs)

    tree.runVisualization() # runAllVisualizations ignore
