from tkinter import *
import random, sys, re, math

try:
    from tkUtilities import *
    from VisualizationApp import *
    from BinaryTreeBase import *
except ModuleNotFoundError:
    from .tkUtilities import *
    from .VisualizationApp import *
    from .BinaryTreeBase import *

class Node234(object):
    def __init__(self, dValue, *children, center=(0, 0)):
        '''Construct a 2-3-4 node with the given drawnValue and child
        nodes.  The keys are in the val attribute of the drawn value.
        The number of children must be one more than the number of keys,
        or 0 for a leaf node
        '''
        keyLabels = dValue.items[4:4 + Tree234.maxKeys]
        keys = dValue.val
        if len(keys) < 1 or len(keys) > Tree234.maxKeys:
            raise Exception('Too many items, {}, in 2-3-4 tree node'.format(
                len(keys)))
        if not all(keys[i] < keys[i + 1] for i in range(len(keys) - 1)):
            raise Exception(  # Verify that keys are monotonically ordered
                'Item keys in 2-3-4 tree node must be ordered')
        if not(len(children) == 0 or len(children) == len(keys) + 1):
            raise Exception(
                'Number of child links, {}, not appropriate for a 2-3-4 '
                'tree node with {} items'.format(
                    len(children), len(keys)))
        if not all(isinstance(x, type(self)) for x in children):
            raise Exception(  # Verify type of children
                'All children of 2-3-4 tree nodes must be more nodes')
        self.dValue = dValue
        self.nKeys = len(keys)
        self.keys = [None] * Tree234.maxKeys
        self.keys[0:len(keys)] = keys
        self.nChild = len(children)
        self.children = [None] * Tree234.maxLinks
        self.children[0:len(children)] = children
        self.center = center

    def keyItems(self):
        "Get the key items from this node's drawnValue"
        return self.dValue.items[4:4 + Tree234.maxKeys]

    def dataItems(self):
        "Get the data items from this node's drawnValue"
        return self.dValue.items[4 + Tree234.maxKeys:4 + 2 * Tree234.maxKeys]

    def __str__(self):      # Represent a node as a string of keys
        return '<Node234 {}>'.format(
            '|'.join(str(k) for k in self.keys[:self.nKeys]))
      
    def isLeaf(self):       # Test for leaf nodes
        return self.nChild == 0

class Tree234(BinaryTreeBase):
    maxLinks = 4
    maxKeys = maxLinks - 1
    NODE_COLOR = 'gray90'
    
    def __init__(self, title="2-3-4 Tree", **kwargs):
        self.outputFont = (self.VALUE_FONT[0], self.VALUE_FONT[1] * 9 // 10)
        outputBoxHeight = abs(self.outputFont[1]) * 2 + 6
        self.CIRCLE_SIZE = 12
        canvasWidth = kwargs.get('canvasWidth', 800)
        canvasHeight = kwargs.get('canvasHeight', 400)
        canvasBounds = (-canvasWidth // 2, 0, canvasWidth // 2, canvasHeight)
        self.activeColor, self.leftoverColor = 'black', 'gray30'
        super().__init__(
            title=title, CIRCLE_SIZE=self.CIRCLE_SIZE, RECT=canvasBounds,
            canvasBounds=canvasBounds, **kwargs)
        self.ROOT_X0, self.ROOT_Y0 = 0, 0
        self.LEVEL_GAP = self.CIRCLE_SIZE * 8
        self.scale, self.fontScale = 1.0, abs(self.FONT_SIZE)
        self.buttons = self.makeButtons()
        self.newTree()
        
    def __str__(self):
        return '<Tree234>'
    
    def getRoot(self):
        return self.rootNode

    def isEmpty(self):
        return self.rootNode is None

    def emptyTree(self):
        self.rootNode = None
        self.maxLevel = -1
    
    def newTree(self):
        self.emptyTree()
        self.scale, self.fontScale = 1.0, abs(self.FONT_SIZE)
        self.setCanvasBounds(self.desiredTreeBounds(-1), expandOnly=False)
        self.display(treeLabel='Tree234')

    def desiredTreeBounds(self, maxLevel, minWidth=None, minHeight=None):
        '''Compute desired canvas bounds to show a 2-3-4 tree with the
        given maximum level of leaf node and current scale'''
        if minWidth is None:
            minWidth = getattr(self, 'targetCanvasWidth', 800)
        if minHeight is None:
            minHeight = getattr(self, 'targetCanvasHeight', 400)
        width = math.ceil(self.scale * max(
            minWidth,
            2 * self.CIRCLE_SIZE * (
                self.maxLinks ** max(1, maxLevel + 1) + 1)))
        height = math.ceil(self.scale * max(
            minHeight, maxLevel * self.LEVEL_GAP + 2 * self.CIRCLE_SIZE))
        halfWidth = width // 2
        return (-halfWidth, 0, width - halfWidth, height)

    def updateMaxLevelAndBounds(self, maxLevel):
        desiredBounds = self.desiredTreeBounds(maxLevel)
        self.maxLevel = maxLevel
        if BBoxContains(self.canvasBounds, desiredBounds):
            return
        # self.setCanvasBounds(BBoxUnion(self.canvasBounds, desiredBounds))
                    
    def childCoords(self, node, childNum, level=None, scale=None):
        '''Compute the center coordinates for one of a node's children.
        The node can be specified as either Node234 object, the tree
        object (self), or a tuple for the node's center coordinates.
        If it is specified as a tuple the level in the tree must be
        specified.  If it is a Node234, level can either be specified
        or computed by finding the node in the tree.
        '''
        if node is self:
            return self.ROOT_X0, self.ROOT_Y0
        if scale is None: scale = self.scale
        center = node.center if isinstance(node, Node234) else node
        if level is None:
            if isinstance(node, Node234) and node.nKeys > 0:
                level, _ = self.getLevelAndChild(node.keys[0])
                level += 1
        nodeWidth = self.CIRCLE_SIZE * Tree234.maxKeys * 2 * scale
        bounds = self.desiredTreeBounds(max(1, self.maxLevel))
        treeWidth = bounds[2] - bounds[0] - nodeWidth
        levelDX = treeWidth / (Tree234.maxLinks ** level)
        dY = (0 if levelDX > self.CIRCLE_SIZE * Tree234.maxKeys * 2 * scale
              else self.CIRCLE_SIZE * 5 * scale / 2)
        halfKeys = Tree234.maxKeys / 2
        return V(center) + V(levelDX * (childNum - halfKeys),
                             (self.LEVEL_GAP + dY * (childNum - halfKeys)) *
                             scale)
                           
    def recenterNodes(
            self, node, parent=None, level=None, childNum=None, byLevel=False):
        if node is None:
            return
        if byLevel:
            if level is None or childNum is None:
                raise ValueError(
                    'Cannot recenter nodes without level and childNum')
            node.center = ((self.ROOT_X0, self.ROOT_Y0) if parent is self else
                           self.childCoords(parent, childNum, level))
        else:
            node.center = tuple(self.canvas.coords(node.keyItems()[1]))
        for ci in range(node.nChild):
            self.recenterNodes(node.children[ci], node, 
                               None if level is None else level + 1, ci,
                               byLevel=byLevel)

    def scaleItems(self, *args, **kwargs):
        '''After scale changes, update node centers for new scale'''
        super().scaleItems(*args, **kwargs)
        self.recenterNodes(self.rootNode, self, 0, 0)
        
    def getAllDescendants(self, node):
        if isinstance(node, Node234):
            return (node, *flat(*(self.getAllDescendants(node.children[c]) 
                                  for c in range(node.nChild))))
        return () 

    def getLevelAndChild(self, itemOrNode):
        '''Return the level and child number index for the given item or Node.
        If itemOrNode is an integer, the keys are searched and if it's
        a Node234 obejct, the children are searched.  Return None if
        the itemOrNode cannot be found. '''
        node, level = self.rootNode, 0
        if isinstance(itemOrNode, int):
            key = itemOrNode
            while node:
                childNum = 0
                while childNum < node.nKeys and node.keys[childNum] < key:
                    childNum += 1
                if childNum < node.nKeys and node.keys[childNum] == key:
                    return level, childNum
                if childNum < node.nChild:
                    node, level = node.children[childNum], level + 1
                else:
                    return None, None
        else:
            queue = [(node, level, 0)]
            while queue:
                node, level, childNum = queue.pop(0)
                if node == itemOrNode:
                    return level, childNum
                for i, child in enumerate(node.children[:node.nChild]):
                    queue.append((child, level + 1, i))
        return None, None

    def nodeChildAnchor(self, node, childNum, radius=None, scale=None):
        "Coords where a node's child points its parent link"
        center = node.center if isinstance(node, Node234) else node
        if radius is None: radius = self.CIRCLE_SIZE
        if scale is None: scale = self.scale
        radius *= scale
        midKey = Tree234.maxKeys / 2
        return V(center) + V(radius * 1.9 * (childNum - midKey), 0)

    def nodeItemCoords(
            self, center, radius=None, parent=None, childNum=0, scale=None):
        '''Return canvas coordinates for the node lozenge and its parent link
        - line to parent, 
        - left circle
        - center rectangle
        - right circle
        - text label centers (there are maxKeys of these)
        - cell boundary squares (there are maxKeys - 2 of these)
        The center is either a Node234 object or a tuple coordinate center.
        The parent must be either None or a Node234 object of which this
        node is linked by the childNum index.
        '''
        origin = center.center if isinstance(center, Node234) else center
        x, y = origin
        if radius is None: radius = self.CIRCLE_SIZE
        if scale is None: scale = self.scale
        radius *= scale
        top, bottom = y - radius, y + radius
        midKey = Tree234.maxKeys / 2
        linkCoords = origin + (
            self.nodeChildAnchor(parent, childNum, radius=None, scale=scale)
            if isinstance(parent, Node234) else origin)
        leftCircle = (x - 2 * radius * midKey, top,
                      x - 2 * radius * (midKey - 1), bottom)
        rightCircle = (x + 2 * radius * (midKey - 1), top,
                       x + 2 * radius * midKey, bottom)
        centerRect = (x - 2 * radius * (midKey - 0.5), top,
                      x + 2 * radius * (midKey - 0.5), bottom)
        textCenters = tuple([(x + radius * 2 * (j - midKey + 0.5), y)
                             for j in range(Tree234.maxKeys)])
        dataCircles = tuple([(x + radius * 2 * (j - midKey), top,
                              x + radius * 2 * (j + 1 - midKey), bottom)
                             for j in range(Tree234.maxKeys)])
        cellRects = tuple([(x + 2 * radius * (j - midKey), top,
                            x + 2 * radius * (j + 1 - midKey), bottom - 1)
                           for j in range(1, Tree234.maxKeys - 1)])
        return (linkCoords, leftCircle, centerRect, rightCircle, *textCenters,
                *dataCircles, *cellRects)
      
    def createNodeShapes(
            self, center, keys, data=None, parent=None, childNum=0, radius=None,
            scale=None, lineColor='black', lineWidth=1, font=None, 
            fill=None, border='SkyBlue3'):
        if font is None: font = self.VALUE_FONT
        if fill is None: fill = self.NODE_COLOR
        if scale is None: scale = self.scale
        if data is None:
            data = []
        while len(data) < len(keys):
            data.append(drawnValue.palette[self.nextColor])
            self.nextColor = (self.nextColor + 1) % len(drawnValue.palette)
        coords = self.nodeItemCoords(
            center, parent=parent, childNum=childNum, radius=radius, 
            scale=scale)
        link, lcircle, crect, rcircle = coords[:4]
        textCenters = coords[4:4 + Tree234.maxKeys]
        dataCircles = coords[4 + Tree234.maxKeys:4 + 2 * Tree234.maxKeys]
        cellRects = coords[4 + 2 * Tree234.maxKeys:]
        linkItem = self.canvas.create_line(
            *link, fill=lineColor, width=lineWidth, arrow=FIRST, tags='link')
        self.canvas.tag_lower(linkItem)
        self.scaleLineItem(linkItem, self.scale)
        lcItem, rcItem = tuple([self.canvas.create_oval(
            *coords, fill=fill, width=0, tags=('lozenge', 'end'))
                                for coords in (lcircle, rcircle)])
        rectItem = self.canvas.create_rectangle(
            *crect, fill=fill, width=0, tags=('lozenge', 'rect'))
        cellItems = tuple([self.canvas.create_rectangle(
            *coords, fill='', width=lineWidth, outline=border,
            tags=('lozenge', 'cell'))
                           for coords in cellRects])
        dataItems = tuple([self.canvas.create_oval(
            *dataCircles[j], width=0,
            fill=data[j] if j < len(keys) else '', tags='data')
                           for j in range(Tree234.maxKeys)])
        textItems = tuple([self.canvas.create_text(
            *textCenters[j], text=str(keys[j]) if j < len(keys) else '',
            font=font, tags='keytext',
            fill=self.activeColor if j < len(keys) else self.leftoverColor)
                           for j in range(Tree234.maxKeys)])
        for i, textItem in enumerate(textItems):
            self.scaleTextItem(textItem, self.scale)
            handler = self.textItemClickHandler(textItem)
            self.canvas.tag_bind(textItem, '<Button>', handler)
            self.canvas.tag_bind(
                lcItem if i == 0 else rcItem if i == Tree234.maxKeys - 1 else
                cellItems[i - 1], '<Button>', handler)

        return (linkItem, lcItem, rectItem, rcItem,
                *textItems, *dataItems, *cellItems)

    def textItemClickHandler(self, textItem):
        def textItemClick(e=None):
            self.setArgument(self.canvas.itemConfig(textItem, 'text'))
        return textItemClick
                
    def treeObjectCoords(
            self, offsetAngle=None, offset=None, fields=[], font=None,
            scale=None):
        fieldFont, _ = self.treeObjectFonts(font)
        ffHeight = textHeight(fieldFont)
        rootWidth = textWidth(fieldFont, ' root ')
        fieldsWidth = sum(textWidth(fieldFont, ' {} '.format(field))
                          for field in fields)
        if offset is None: offset = 80
        if offsetAngle is None: offsetAngle = 180
        if scale is None: scale = self.scale
        halfWidth = Tree234.maxKeys * self.CIRCLE_SIZE
        x0, y0 = V(self.ROOT_X0, self.ROOT_Y0) + V(
            V(V((offset + halfWidth) * scale, 0).rotate(offsetAngle)) -
            V(V(fieldsWidth + rootWidth, self.CIRCLE_SIZE + ffHeight) * scale))
        return (x0, y0, 
                x0 + (fieldsWidth + rootWidth) * scale,
                y0 + (2 * self.CIRCLE_SIZE + ffHeight) * scale)

    def treeDotCenter(self, *args, **kwargs):
        return V(super().treeDotCenter(*args, **kwargs)) * self.scale

    def treeObjectArrowCoords(self, **kwargs):
        treeObjectCoords = self.treeObjectCoords(**kwargs)
        dotCenter = V(treeObjectCoords[:2]) + V(
            self.treeDotCenter(fields=kwargs.get('fields', []),
                               font=kwargs.get('font')))
        halfWidth = Tree234.maxKeys * self.CIRCLE_SIZE * self.scale
        tip = (V(self.ROOT_X0, self.ROOT_Y0) + V(halfWidth, 0).rotate(
            kwargs.get('offsetAngle', 180))) if self.getRoot() else dotCenter
        return dotCenter + tip

    def updateTreeObjectRootPointer(
            self, arrow=None, root=None, see=True, sleepTime=0):
        '''Extend pointer of tree object to point at the root node if present
        otherwise make it zero length to be invisible'''
        if arrow is None and getattr(self, 'treeObject', None) is None:
            return
        if arrow is None:
            arrow = self.treeObject[1]
        if sleepTime > 0:
            self.moveItemsTo(arrow, self.treeObjectArrowCoords(),
                             sleepTime=sleepTime, 
                             see=see and getattr(self, 'treeObject', []))
        else:
            self.canvas.coords(arrow, self.treeObjectArrowCoords())
            if see:
                self.scrollToSee((arrow, *getattr(self, 'treeObject', [])),
                                 sleepTime=sleepTime)

    def createArrow(
            self, node, label=None, level=1, keyNum=None, color=None, width=1,
            tags=['arrow'], font=None, orientation=-90, anchor=SW, see=True,
            sleepTime=0):
        '''Create an arrow pointing at an existing node or the tree object.
        The arrow is oriented the given number of degress from horizontal
        Optionally give a text label for the arrow.  Optionally provide a
        particular key number within the node to point at.  Optionally
        scroll to see the new arrow.
        '''
        if font is None: font = self.VARIABLE_FONT
        if color is None: color = self.VARIABLE_COLOR
        arrowCoords, labelCoords = self.indexCoords(
            node, level, keyNum=keyNum, font=font, orientation=orientation)
        arrow = self.canvas.create_line(
            *arrowCoords, arrow="last", fill=color, width=width, tags=tags)
        self.scaleLineItem(arrow, self.scale)
        if label is not None:
            label = self.canvas.create_text(
                *labelCoords, text=label, anchor=anchor, font=font, fill=color,
                tags=tags)
            self.scaleTextItem(label, self.scale)

        result = (arrow, label)[:2 if label is not None else 1]
        if see:
            self.scrollToSee(
                result + (node.dValue.items[1:] if isinstance(node, Node234) else ()),
                sleepTime=sleepTime)
        return result

    def indexCoords(
            self, node, level=1, keyNum=None, font=None, orientation=-90,
            anchor=SW, scale=None):
        '''Compute coordinates of an arrow index pointing at an existing node,
        node center coordinates, or the tree object, as well as the
        anchor coordinates of label at the arrow's base.  If keyNum is
        provided, the tip of the arrow is centered on the particular key
        within the node.
        '''
        if font is None: font = self.VARIABLE_FONT
        if scale is None: scale = self.scale
        if node is self:
            treeObjectCoords = self.treeObjectCoords()
            center = V(treeObjectCoords[:2]) + V(
                self.treeDotCenter()[0], self.CIRCLE_SIZE * scale)
        elif isinstance(node, Node234):
            center = node.center
        else:
            center = node
        tip = V(center) - V(0, self.CIRCLE_SIZE * scale)
        if keyNum is not None and node is not self:
            tip = V(tip) + V(self.CIRCLE_SIZE * scale *
                             (keyNum * 2 + 1 - Tree234.maxKeys), 0)
        base = V(tip) + (V(V(self.ARROW_HEIGHT + level * abs(font[1]), 0)
                           .rotate(orientation)) * scale)
        return base + tip, base

    def moveArrowsTo(self, arrow, node, config, wait, see=True):
        'Move one or more arrow tuples and keep all of their node items visible'
        if not all(isinstance(arg, (list, tuple)) 
                   for arg in (arrow, node, config)):
            arrow = [arrow]
            node = [node]
            config = [config]
        self.moveItemsTo(
            flat(*arrow),
            flat(*(self.indexCoords(n, **c) for n, c in zip(node, config))),
            sleepTime=wait / 10, 
            see=flat(*(n.dValue.items[1:] for n in node)))
            
    def outputBoxCoords(self, font=None, padding=6, N=None, canvasDims=None,
                        scale=None):
        '''Coordinates for an output box at top of canvas with enough
        space to hold N values, defaulting to current tree item count.
        This makes use of negative y coordinates to extend the canvas
        bounds above the tree root.'''
        if N is None: N = sum(
                node.nKeys for node in
                self.getAllDescendants(getattr(self, 'rootNode', None)))
        N = max(1, N)
        if font is None: font = self.VALUE_FONT
        if scale is None: scale = getattr(self, 'scale', 1)
        spacing = self.outputBoxSpacing(font)
        left = max(self.canvasBounds[0],
                   self.ROOT_X0 - (N * spacing - padding) // 2)
        bottom = self.ROOT_Y0 - 4 * self.CIRCLE_SIZE * scale - padding
        return (left, bottom - abs(font[1]) * 2,
                left + N * spacing + padding, bottom)
        
    def upperRightNodeCoords(self, level=1):
        child3 = self.childCoords((self.ROOT_X0, self.ROOT_Y0), 3, 1)
        return (child3[0], 
                self.ROOT_Y0 + self.CIRCLE_SIZE * self.scale * (2.5 * level - 1))

    insertCode = '''
def insert(self, key={key}, value):
   node, p = self.__find(key, self.__root, self, prepare=True)
   if node is None:
      if p is self:
         self.__root = self.__Node(key, value)
         return True
      raise Exception('__find did not find 2-3-4 node for insertion')
   return node.insertKeyValue(key, value)
'''
    
    def insert(self, key, code=insertCode, start=True, animation=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code='' if not animation else code.format(**locals()),
            startAnimations=start if animation else False)
        if animation:
            self.highlightCode(
                'node, p = self.__find(key, self.__root, self, prepare=True)',
                callEnviron)
        node, p = self._find(key, self.rootNode, self, prepare=True, wait=wait,
                             animation=animation)

        if animation:
            indexConfig = {'keyNum': -0.2, 'orientation': -135, 'anchor': SE}
            pArrow = self.createArrow(p, 'p', **indexConfig)
            nodeArrow = self.createArrow(
                node if node else self.childCoords(p, 1), 'node', **indexConfig)
            callEnviron |= set(nodeArrow + pArrow)
            
            self.highlightCode('node is None', callEnviron, wait=wait)
        if node is None:
            if animation:
                self.highlightCode('p is self', callEnviron, wait=wait)
            if p is self:
                center = (self.ROOT_X0, self.ROOT_Y0)
                newItemCoords = self.newValueCoords() if animation else center
                newNodeItems = self.createNodeShapes(newItemCoords, [key])
                if animation:
                    self.highlightCode('self.__root = self.__Node(key, value)',
                                       callEnviron)
                    self.moveItemsTo(newNodeItems,
                                     self.nodeItemCoords(center),
                                     sleepTime=wait / 10, see=True)
                self.rootNode = Node234(drawnValue([key], *newNodeItems),
                                        center=center)
                self.updateMaxLevelAndBounds(self.maxLevel + 1)
                self.updateTreeObjectRootPointer(root=self.rootNode)
                
                if animation:
                    self.highlightCode('return True', callEnviron)
                self.cleanUp(callEnviron)
                return True

            if animation:
                self.highlightCode(
                    "raise Exception"
                    "('__find did not find 2-3-4 node for insertion')",
                    callEnviron, color=self.EXCEPTION_HIGHLIGHT)
                raise UserStop
            self.cleanUp(callEnviron)
            return None
        
        if animation:
            self.highlightCode('node.insertKeyValue(key, value)', callEnviron)
        result = self.insertKeyValue(node, key, animation=animation, wait=wait)
        
        if animation:
            self.highlightCode('return node.insertKeyValue(key, value)',
                               callEnviron)
        self.cleanUp(callEnviron)
        return result

    _findCode = '''
def __find(self, goal={goal}, current={currentStr}, parent={parentStr}, prepare={prepare}):
   if current is None:
      return (current, parent)
   i = 0
   while i < current.nKeys and current.keys[i] < goal:
      i += 1
   if i < current.nKeys and goal == current.keys[i]:
      return (current, parent)
   if prepare and current.nKeys == Tree234.maxKeys:
      current, parent = self.__splitNode(current, parent, goal)
      i = 0 if goal < current.keys[0] else 1
   return ((prepare and current, parent)
           if current.isLeaf() else 
           self.__find(goal, current.children[i], current, prepare)
'''

    last1 = re.compile(r'\s(1)\s') # to match the 1 in ' else 1'

    def _find(self, goal, current, parent, prepare=True, code=_findCode,
              animation=True, wait=0.1):
        currentStr = str(current)
        parentStr = str(parent)
        callEnviron = self.createCallEnvironment(
            code='' if not animation else code.format(**locals()),
            startAnimations=animation, sleepTime=wait / 10)
        if animation:
            indexConfig = {'keyNum': -0.2, 'orientation': -135, 'anchor': SE}
            currentArrow = self.createArrow(
                current if current else self.childCoords(parent, 1),
                'current', **indexConfig)
            parentArrow = self.createArrow(parent, 'parent', **indexConfig)
            localVars = currentArrow + parentArrow
            callEnviron |= set(localVars)
            self.highlightCode('current is None', callEnviron, wait=wait)
            
        if current is None:
            if animation:
                self.highlightCode('return (current, parent)', callEnviron)
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return current, parent

        i = 0
        if animation:
            self.highlightCode('i = 0', callEnviron)
            arrowConfig = {'keyNum': i, 'level': 1}
            iArrow = self.createArrow(current, 'i', **arrowConfig)
            callEnviron |= set(iArrow)
            localVars += iArrow
            self.highlightCode('i < current.nKeys', callEnviron, wait=wait)
            if i < current.nKeys:
                self.highlightCode('current.keys[i] < goal', callEnviron,
                                   wait=wait)
        while i < current.nKeys and current.keys[i] < goal:
            if animation:
                self.highlightCode('i += 1', callEnviron, wait=wait)
            i += 1
            if animation:
                arrowConfig['keyNum'] = i
                self.moveArrowsTo(iArrow, current, arrowConfig, wait)
                self.highlightCode('i < current.nKeys', callEnviron, wait=wait)
                if i < current.nKeys:
                    self.highlightCode('current.keys[i] < goal', callEnviron,
                                       wait=wait)

        if animation:
            self.highlightCode(('i < current.nKeys', 2), callEnviron, wait=wait)
            if i < current.nKeys:
                self.highlightCode('goal == current.keys[i]', callEnviron,
                                   wait=wait)
        if i < current.nKeys and goal == current.keys[i]:
            if animation:
                self.highlightCode(('return (current, parent)', 2), callEnviron)
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return current, parent

        if animation:
            self.highlightCode(('prepare', 2), callEnviron, wait=wait)
            if prepare:
                self.highlightCode('current.nKeys == Tree234.maxKeys',
                                   callEnviron, wait=wait)
        if prepare and current.nKeys == Tree234.maxKeys:
            if animation:
                self.highlightCode(
                    'current, parent = self.__splitNode(current, parent, goal)',
                    callEnviron)
                colors = self.canvas.fadeItems(localVars)
            current, parent = self._splitNode(
                current, parent, goal, animation=animation, wait=wait)
            if animation:
                self.canvas.restoreItems(localVars, colors)
                self.moveArrowsTo(
                    (currentArrow, parentArrow, iArrow), 
                    (current, parent, current),
                    (indexConfig, indexConfig, arrowConfig), wait)
                
                self.highlightCode('goal < current.keys[0]', callEnviron, 
                                   wait=wait)
                self.highlightCode(('i = 0', 2) if goal < current.keys[0] else
                                   (('i =', 2), (self.last1, 2)), callEnviron)
            i = 0 if goal < current.keys[0] else 1
            if animation:
                arrowConfig['keyNum'] = i
                self.moveArrowsTo(iArrow, current, arrowConfig, wait)

        if animation:
            self.highlightCode('current.isLeaf()', callEnviron, wait=wait)
        if current.isLeaf():
            if animation:
                self.highlightCode(
                    (('return', 3), '(prepare and current, parent)'), callEnviron)
            result = (prepare and current, parent)
        else:
            if animation:
                self.highlightCode(
                    (('return', 3), 
                     'self.__find(goal, current.children[i], current, prepare)'),
                    callEnviron)
                colors = self.canvas.fadeItems(localVars)
            result = self._find(
                goal, current.children[i], current, prepare,
                animation=animation, wait=wait)
            if animation:
                self.canvas.restoreItems(localVars, colors)
                self.scrollToSee(currentArrow + current.dValue.items[1:])
                
        self.cleanUp(callEnviron, sleepTime=wait / 10)
        return result

    _splitNodeCode = '''
def __splitNode(self, toSplit={toSplitStr}, 
                parent={parentStr}, goal={goal}):
   if toSplit.isLeaf():
      newNode = self.__Node(toSplit.keys[2], toSplit.data[2])
   else:
      newNode = self.__Node(toSplit.keys[2], toSplit.data[2],
                        *toSplit.children[2:toSplit.nChild])
   toSplit.nKeys = 1
   toSplit.nChild = max(0, toSplit.nChild - 2)
   if parent is self:
      self.__root = self.__Node(toSplit.keys[1], toSplit.data[1],
                                toSplit, newNode)
      parent = self.__root
   else:
      parent.insertKeyValue(toSplit.keys[1], toSplit.data[1], newNode)
   return (toSplit if goal < toSplit.keys[1] else newNode, parent)
'''
    
    def _splitNode(self, toSplit, parent, goal,
                  code=_splitNodeCode, animation=True, wait=0.1):
        toSplitStr = str(toSplit)
        parentStr = str(parent)
        callEnviron = self.createCallEnvironment(
            code='' if not animation else code.format(**locals()),
            startAnimations=animation)
        if animation:
            indexConfig = {'keyNum': -0.2, 'orientation': -135, 'anchor': SE}
            toSplitArrow = self.createArrow(toSplit, 'toSplit', **indexConfig)
            parentArrow = self.createArrow(parent, 'parent', **indexConfig)
            localVars = toSplitArrow + parentArrow
            callEnviron |= set(localVars)
            self.highlightCode('toSplit.isLeaf()', callEnviron, wait=wait)
        
            self.highlightCode(
                (re.compile(r'newNode = self.__Node\(toSplit.*.data\[2\]{}'
                            .format(r'\)' if toSplit.isLeaf() else r',')),) +
                (() if toSplit.isLeaf() else 
                 (re.compile(r' \*toSplit.children\[2:toSplit.nChild\]\)'),)),
                callEnviron)

        newNodeChildNum = 1 if parent is self else parent.nChild
        newNodeCenter = (V(toSplit.center) +
                         V(V(Tree234.maxLinks * 2, 2.5) *
                           (self.CIRCLE_SIZE * self.scale)))
        newNodeItems = self.createNodeShapes(
            toSplit.center if animation else newNodeCenter, 
            [toSplit.keys[2]], 
            data=[self.canvas.itemConfig(toSplit.dataItems()[2], 'fill')],
            parent=None,  # Don't connect to parent yet
            childNum=1 if parent is self else parent.nKeys + 1)
        childrenToRemove = toSplit.children[2:toSplit.nChild]
        newNode = Node234(drawnValue([toSplit.keys[2]], *newNodeItems),
                          *childrenToRemove, center=newNodeCenter)
        if animation:
            newNodeConfig = {'keyNum': -0.2, 'orientation': -135, 'anchor': SW,
                             'level': 2}
            newNodeArrow = self.createArrow(newNode, 'newNode', **newNodeConfig)
            callEnviron |= set(newNodeArrow)
            localVars += newNodeArrow
            links = tuple([c.dValue.items[0] for c in childrenToRemove if c])
            newLinkCoords = tuple([tuple(self.canvas.coords(link)[:2]) + 
                                   self.nodeChildAnchor(newNodeCenter, i)
                                   for i, link in enumerate(links)])
            self.moveItemsLinearly(
                newNodeItems + links, 
                self.nodeItemCoords(
                    newNodeCenter, parent=None, # Don't connect to parent yet
                    childNum=newNodeChildNum) + newLinkCoords,
                sleepTime=wait / 10, see=newNodeItems)
            self.highlightCode('toSplit.nKeys = 1', callEnviron, wait=wait)
        toSplit.nKeys = 1
        self.canvas.itemConfig(toSplit.keyItems()[2], text='')
        self.canvas.itemConfig(toSplit.dataItems()[2], fill='')
        toSplit.keys[2] = None
        for i in range(toSplit.nKeys, Tree234.maxKeys):
            self.canvas.itemConfig(toSplit.keyItems()[i],
                                   fill=self.leftoverColor)

        if animation:
            self.highlightCode('toSplit.nChild = max(0, toSplit.nChild - 2)',
                               callEnviron, wait=wait)
        toSplit.nChild = max(0, toSplit.nChild - 2)

        if animation:
            self.highlightCode('parent is self', callEnviron, wait=wait)
        if parent is self:
            if animation:
                self.highlightCode(
                    'self.__root = self.__Node(toSplit.keys[1], toSplit.data[1],\n'
                    '                                toSplit, newNode)',
                    callEnviron)
            rootCenter = (self.ROOT_X0, self.ROOT_Y0)
            newRootOffset = (0, -self.CIRCLE_SIZE * 3)
            newRootCenter = V(rootCenter) + V(newRootOffset)
            newRootItems = self.createNodeShapes(
                newRootCenter if animation else rootCenter,
                [toSplit.keys[1]], data=[self.canvas.itemConfig(
                    toSplit.dataItems()[1], 'fill')])
            self.rootNode = Node234(
                drawnValue([toSplit.keys[1]], *newRootItems),
                toSplit, newNode, 
                center=newRootCenter if animation else rootCenter)
            self.updateMaxLevelAndBounds(self.maxLevel + 1)
            if animation:
                links = (self.treeObject[1], toSplit.dValue.items[0], 
                         newNode.dValue.items[0])
                newLinkCoords = tuple([
                    tuple(self.canvas.coords(link)[:2]) + tip
                    for link, tip in zip(
                            links, (V(newRootCenter) - V(Tree234.maxKeys *
                                                         self.CIRCLE_SIZE, 0),
                                    self.nodeChildAnchor(newRootCenter, 0),
                                    self.nodeChildAnchor(newRootCenter, 1)))])
                self.moveItemsLinearly(
                    links, newLinkCoords, sleepTime=wait / 10, see=True)
                self.restoreNodePositions(
                    self.rootNode, sleepTime=wait / 10, see=True,
                    nodeIndices=((toSplit, indexConfig, toSplitArrow),
                                 (newNode, newNodeConfig, newNodeArrow)))
                self.scrollToSee(toSplitArrow + toSplit.dValue.items[1:],
                                 sleepTime=wait / 10)
            else:
                self.restoreNodePositions(self.rootNode, sleepTime=0)

            if animation:
                self.highlightCode('parent = self.__root', callEnviron)
            parent = self.rootNode
            if animation:
                self.moveArrowsTo(parentArrow, parent, indexConfig, wait)
        else:
            if animation:
                self.highlightCode(
                    'parent.insertKeyValue(toSplit.keys[1], toSplit.data[1], '
                    'newNode)', callEnviron)
                colors = self.canvas.fadeItems(localVars)
            self.insertKeyValue(
                parent, toSplit.keys[1], newNode, animation=animation, 
                wait=wait,
                keyData=(toSplit.keyItems()[1], toSplit.dataItems()[1]))
            if animation:
                self.canvas.restoreItems(localVars, colors)
                
        self.restoreNodePositions(
            parent, sleepTime=wait / 10 if animation else 0,
            nodeIndices=((toSplit, indexConfig, toSplitArrow),
                         (newNode, newNodeConfig, newNodeArrow),
                         (parent, indexConfig, parentArrow))
            if animation else (), see=True)

        if animation:
            self.scrollToSee(toSplitArrow + toSplit.dValue.items[1:],
                             sleepTime=wait / 10)
            self.highlightCode('goal < toSplit.keys[1]', callEnviron, wait=wait)
            self.highlightCode(
                ('return',
                 ('toSplit', 17) if goal < toSplit.keys[1] else ('newNode', 5),
                 ('parent', 5)), callEnviron)

        self.canvas.itemConfig(toSplit.keyItems()[1], text='')
        self.canvas.itemConfig(toSplit.dataItems()[1], fill='')
        self.cleanUp(callEnviron)
        return (toSplit if goal < toSplit.keys[1] else newNode,
                parent)

    insertKeyValueCode = '''
def insertKeyValue(self={selfStr}, key={key}, data, subtree={subtreeStr}):
   i = 0
   while (i < self.nKeys and self.keys[i] < key):
      i += 1
   if i == Tree234.maxKeys:
      raise Exception('Cannot insert key into full 2-3-4 node')
   if self.keys[i] == key:
      self.data[i] = data
      return False
   j = self.nKeys
   if j == Tree234.maxKeys:
      raise Exception('Cannot insert key into full 2-3-4 node')
   while i < j:
      self.keys[j] = self.keys[j-1]
      self.data[j] = self.data[j-1]
      self.children[j+1] = self.children[j]
      j -= 1
   self.keys[i] = key
   self.data[i] = data
   self.nKeys += 1
   if subtree:
      self.children[i + 1] = subtree
      self.nChild += 1
   return True
'''
    
    def insertKeyValue(
            self, node, key, subtree=None, code=insertKeyValueCode, 
            animation=True, wait=0.1, keyData=None):
        '''Insert a key in a (non-full) node, optionally adding a subtree
        as the child link before the key.  If keyData is provided, it
        should be a tuple of the existing canvas items for the key and data.
        '''
        selfStr = str(node)
        subtreeStr = str(subtree)
        callEnviron = self.createCallEnvironment(
            code='' if not animation else code.format(**locals()),
            startAnimations=animation)
        i = 0
        subtreeArrow = None
        if animation:
            if subtree:
                subtreeConfig = {'level': 2, 'orientation': -135, 'keyNum': -0.2}
                subtreeArrow = self.createArrow(
                    subtree, 'subtree', **subtreeConfig)
                callEnviron |= set(subtreeArrow)
            iConfig = {'level': 1, 'keyNum': i}
            self.highlightCode('i = 0', callEnviron, wait=wait)
            iArrow = self.createArrow(node, 'i', **iConfig)
            callEnviron |= set(iArrow)
            self.scrollToSee(node.dValue.items[1:], sleepTime=wait / 10)

            self.highlightCode('i < self.nKeys', callEnviron, wait=wait)
            if i < node.nKeys:
                self.highlightCode('self.keys[i] < key', callEnviron, wait=wait)
                
        while i < node.nKeys and node.keys[i] < key:
            if animation:
                self.highlightCode('i += 1', callEnviron, wait=wait)
            i += 1
            if animation:
                iConfig['keyNum'] = i
                self.moveArrowsTo(iArrow, node, iConfig, wait)
                self.highlightCode('i < self.nKeys', callEnviron, wait=wait)
                if i < node.nKeys:
                    self.highlightCode('self.keys[i] < key', callEnviron,
                                       wait=wait)

        if animation:
            self.highlightCode('i == Tree234.maxKeys', callEnviron, wait=wait)
        if i == Tree234.maxKeys:
            if animation:
                self.highlightCode(
                    "raise Exception('Cannot insert key into full 2-3-4 node')",
                    callEnviron, color=self.EXCEPTION_HIGHLIGHT)
            raise UserStop

        # Prepare items for key and data to be inserted
        if keyData is None:
            newItemCoords = self.newValueCoords() 
            newNode = self.createNodeShapes(newItemCoords, [key])
            keyItem, dataItem = newNode[4], newNode[4 + Tree234.maxKeys]
            for item in newNode:
                if item not in (keyItem, dataItem):
                    self.canvas.delete(item)
        else:
            center = self.canvas.coords(keyData[0])
            offset = (self.CIRCLE_SIZE, self.CIRCLE_SIZE)
            keyItem, dataItem = tuple(
                self.canvas.copyItem(item) for item in keyData)
            self.canvas.tag_lower(dataItem, keyData[0])
        for item in node.keyItems():
            self.canvas.tag_lower(dataItem, item)
        callEnviron |= set((keyItem, dataItem))

        if animation:
            self.highlightCode('self.keys[i] == key', callEnviron, wait=wait)
        if node.keys[i] == key:
            if animation:
                self.highlightCode('self.data[i] = data', callEnviron, 
                                   wait=wait)
                self.moveItemsTo(
                    dataItem, self.canvas.coords(node.dataItems()[i]),
                    sleepTime=wait / 10)

                self.highlightCode('return False', callEnviron, wait=wait)
            self.canvas.copyItemAttributes(dataItem, node.dataItems()[i],
                                           'fill')
            self.cleanUp(callEnviron)
            return False

        j = node.nKeys
        if animation:
            self.highlightCode('j = self.nKeys', callEnviron, wait=wait)
            jConfig = {'level': 2, 'keyNum': j}
            jArrow = self.createArrow(node, 'j', **jConfig)
            callEnviron |= set(jArrow)

            self.highlightCode('j == Tree234.maxKeys', callEnviron, wait=wait)
        if j == Tree234.maxKeys:
            if animation:
                self.highlightCode(
                    ("raise Exception"
                     "('Cannot insert key into full 2-3-4 node')", 2),
                    callEnviron, color=self.EXCEPTION_HIGHLIGHT)
            raise UserStop

        if animation:
            self.highlightCode('i < j', callEnviron, wait=wait)
        while i < j:
            jKey, jData = node.keyItems()[j], node.dataItems()[j]
            if animation:
                self.highlightCode('self.keys[j] = self.keys[j-1]', callEnviron)
                keyCopy = self.canvas.copyItem(node.keyItems()[j - 1])
                callEnviron.add(keyCopy)
                self.moveItemsOnCurve(
                    keyCopy, self.canvas.coords(jKey), sleepTime=wait / 10, 
                    see=node.dValue.items[1:])
            self.canvas.itemConfig(
                jKey,
                text=self.canvas.itemConfig(node.keyItems()[j - 1], 'text'))
            node.keys[j] = node.keys[j - 1]
            
            if animation:
                self.canvas.delete(keyCopy)
                callEnviron.discard(keyCopy)
                self.highlightCode('self.data[j] = self.data[j-1]', callEnviron,
                                   wait=wait)
                dataCopy = self.canvas.copyItem(node.dataItems()[j - 1])
                for item in node.keyItems()[j - 1:j+1]:
                    self.canvas.tag_lower(dataCopy, item)
                callEnviron.add(dataCopy)
                self.moveItemsOnCurve(
                    dataCopy, self.canvas.coords(jData), sleepTime=wait / 10, 
                    see=node.dValue.items[1:])
                self.highlightCode(
                    'self.children[j+1] = self.children[j]', callEnviron)
            self.canvas.copyItemAttributes(node.dataItems()[j - 1], jData,
                                           'fill')
            node.children[j + 1] = node.children[j]
            child = node.children[j + 1]
            if child:
                newLinkCoords = child.center + self.nodeChildAnchor(node, j + 1)
                if animation:
                    self.moveItemsLinearly(
                        child.dValue.items[0], newLinkCoords, 
                        sleepTime=wait / 10,
                        see=child.dValue.items + node.dValue.items[1:])
                else:
                    self.canvas.coords(child.dValue.items[0], newLinkCoords)
                
            j -= 1
            if animation:
                self.highlightCode('j -= 1', callEnviron)
                jConfig['keyNum'] = j
                self.moveArrowsTo(jArrow, node, jConfig, wait)
                
            if animation:
                self.highlightCode('i < j', callEnviron, wait=wait)

        if animation:
            self.highlightCode('self.keys[i] = key', callEnviron)
            circleCoords = self.canvas.coords(dataItem)
            self.canvas.coords(
                keyItem, *(V(V(circleCoords[:2]) + V(circleCoords[2:])) / 2))
            self.canvas.itemConfig(
                keyItem, fill=self.leftoverColor if i >= node.nKeys else
                self.activeColor)
            self.moveItemsTo(keyItem, self.canvas.coords(node.keyItems()[i]),
                             sleepTime=wait / 10)
        self.canvas.itemConfig(node.keyItems()[i], text=str(key))
        node.keys[i] = key
        
        iData = node.dataItems()[i]
        if animation:
            self.canvas.delete(keyItem)
            callEnviron.discard(keyItem)
            self.highlightCode(('self.data[i] = data', 2), callEnviron)
            self.moveItemsTo(
                dataItem, self.canvas.coords(iData), sleepTime=wait / 10)
        self.canvas.copyItemAttributes(dataItem, iData, 'fill')

        if animation:
            self.canvas.delete(dataItem)
            callEnviron.discard(dataItem)
            self.highlightCode('self.nKeys += 1', callEnviron, wait=wait)

        self.canvas.itemConfig(
            node.keyItems()[node.nKeys], fill=self.activeColor)
        node.nKeys += 1

        if animation:
            self.highlightCode(('subtree', 2), callEnviron, wait=wait)

        if subtree:
            if animation:
                self.highlightCode('self.children[i + 1] = subtree',
                                   callEnviron, wait=wait)
                # Animate connection of subtree
            node.children[i + 1] = subtree
            
            if animation:
                link = subtree.dValue.items[0]
                self.moveItemsLinearly(
                    link, subtree.center + self.nodeChildAnchor(node, i + 1),
                    sleepTime=wait / 10, 
                    see=subtree.dValue.items + node.dValue.items[1:])
                self.highlightCode('self.nChild += 1',
                                   callEnviron, wait=wait)
            node.nChild += 1
            self.restoreNodePositions(
                node, parent=None, sleepTime=wait / 10 if animation else 0,
                nodeIndices=((node, iConfig, iArrow), (node, jConfig, jArrow),
                             (subtree, subtreeConfig, subtreeArrow))
                if animation else (), see=True)
        
        if animation:
            self.highlightCode('return True', callEnviron)
        self.cleanUp(callEnviron)
        return True
    
    def randomFill(self, quantity, animation=False):
        values = random.sample(range(self.valMax + 1), quantity)
        for value in values:
            self.insert(value, animation=animation)
        self.scrollToSee(
            flat(*(n.dValue.items 
                   for n in self.getAllDescendants(self.rootNode))),
            sleepTime=0)
            
    searchCode = '''
def search(self, goal={goal}):
   node, p = self.__find(goal, self.__root, self, prepare=False)
   if node:
      return (node.data[0]
              if node.nKeys < 2 or goal < node.keys[1]
              else node.data[1] if goal == node.keys[1]
              else node.data[2])
'''
    
    def search(self, goal, code=searchCode, start=True):
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start, 
            sleepTime=wait / 10)

        self.highlightCode(
            'node, p = self.__find(goal, self.__root, self, prepare=False)',
            callEnviron)
        node, p = self._find(
            goal, self.rootNode, self, prepare=False, wait=wait)
        indexConfig = {'keyNum': -0.2, 'orientation': -135, 'anchor': SE}
        if node:
            indexConfig['keyNum'] = node.keys.index(goal)
            nodeArrow = self.createArrow(node, 'node', **indexConfig)
        else:
            pIsNode = isinstance(p, Node234)
            child = 0
            while pIsNode and child < p.nKeys and goal > p.keys[child]:
                child += 1
            nodeCenter = V(self.childCoords(p, child)) - V(
                    0, self.LEVEL_GAP * self.scale // 4)
            noneText = self.canvas.create_text(
                *nodeCenter, text='None', font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
            self.scaleTextItem(noneText, self.scale)
            callEnviron.add(noneText)
            nodeArrow = self.createArrow(nodeCenter, 'node', **indexConfig)
        pArrow = self.createArrow(p, 'p', **indexConfig)
        callEnviron |= set(nodeArrow + pArrow)

        self.highlightCode(('node', 2), callEnviron, wait=wait)
        if node:
            self.highlightCode('node.nKeys < 2', callEnviron, wait=wait)
            if node.nKeys >= 2:
                self.highlightCode('goal < node.keys[1]', callEnviron,
                                   wait=wait)
            if node.nKeys < 2 or goal < node.keys[1]:
                self.highlightCode(('return', 'node.data[0]'), callEnviron)

            elif self.highlightCode('goal == node.keys[1]', callEnviron,
                                    wait=wait) or goal == node.keys[1]:
                self.highlightCode(('return', 'node.data[1]'), callEnviron)
            else:
                self.highlightCode(('return', 'node.data[2]'), callEnviron)
        else:
            self.highlightCode((), callEnviron)

        self.cleanUp(callEnviron)
        return node if node else None
        
    def delete(self, goal, start=True):
        self.setMessage('Not yet implemented')
        print('Visible canvas coords = {}'.format(
            self.visibleCanvas()))
        
    def restoreNodes(self, nodes=None):
        if self.rootNode and (nodes is None or nodes[0] is self.rootNode):
            self.restoreNodePositions(self.rootNode, sleepTime=0, see=False)
        elif nodes:
            for node in nodes:
                self.restoreNodePositions(node, sleepTime=0, see=False)
                for i, key in enumerate(node.keys):
                    self.canvas.itemConfig(
                        node.keyItems()[i], 
                        text='' if node.keys[i] is None else str(node.keys[i]),
                        fill=self.activeColor if i < node.nKeys else
                        self.leftoverColor)
                for j in range(node.nChild, Tree234.maxLinks):
                    node.children[j] = None
        self.updateTreeObjectRootPointer(root=self.rootNode, see=False)
        
    def restoreNodePositions(
            self, subtreeRoot, parent=None, childNum=None, sleepTime=0.05,
            setChildCenters=True, nodeIndices=(), see=False):
        '''Moves all the nodes in the subtree rooted at subtreeRoot to their
        proper place on the canvas and adjusts their links to parents.
        If sleepTime is 0, no animation is done, just update the coords.
        If setChildCenters is True, the position of each child node is set
        based on its relationship to its parent.  The subtree root node's
        position and link are only updated if the parent is provided or it
        it is the root of the whole tree (and hence is only linked to the
        tree object).  The nodeIndices list holds (node, config, indexItems) 
        tuples for nodes and their arrow indices that should move with the
        subtree nodes.  The config is a dictionary that supplies the keyword
        arguments to the indexCoords method like level and keyNum.
        When see is true, the canvas scrolls to see moved items.
        '''
        if childNum is None and isinstance(parent, Node234):
            pChildren = parent.children[:parent.nChild]
            if subtreeRoot in pChildren:
                childNum = pChildren.index(subtreeRoot)
            else:
                raise ValueError(
                    "Given node {} is not among parent's {} children".format(
                        subtreeRoot, parent))
        items, coords = self.subtreeItemCoords( # Collect canvas items & coords
            subtreeRoot, parent, childNum, level=None,
            setChildCenters=setChildCenters)
        nodeIndexItems, nodeIndexCoords = (), ()
        for node, config, indexItems in nodeIndices:
            nodeIndexItems += indexItems
            nodeIndexCoords += self.indexCoords(node, **config)
        if subtreeRoot is self.rootNode:
            arrow = self.treeObject[1]
            arrowCoords = self.canvas.coords(arrow)
            newArrowCoords = self.treeObjectArrowCoords()
            if distance2(arrowCoords, newArrowCoords) > 1:
                items += (arrow,)
                coords += (newArrowCoords,)

        if sleepTime > 0:
            self.moveItemsLinearly(
                nodeIndexItems + items, nodeIndexCoords + coords,
                sleepTime=sleepTime, see=see)
        else:
            for item, coord in zip(nodeIndexItems + items,
                                   nodeIndexCoords + coords):
                self.canvas.coords(item, coord)

    def subtreeItemCoords(
            self, node, parent, childNum, level=None, setChildCenters=True):
        '''Return a node's canvas items and their coordinates after
        optionally setting its center based on its relation to its parent.
        Recursively descend through all the nodes descendants.
        '''
        if node is None:
            return [], []
        if level is None: # ASSUME no empty nodes so there are always 1+ keys
            if parent is self:
                level = 0
            else:
                level, _ = self.getLevelAndChild(node.keys[0])
            if level is None:
                raise Exception('Unable to get level for {}'.format(node))
        if setChildCenters and (parent or node is self.rootNode):
            node.center = (
                (self.ROOT_X0, self.ROOT_Y0) if node is self.rootNode else
                self.childCoords(parent, childNum, level))
        excludeParentLink = 0 if parent or node is self.rootNode else 1
        items = node.dValue.items[excludeParentLink:]
        coords = self.nodeItemCoords(node, parent=parent, childNum=childNum)[
            excludeParentLink:]
        for ci in range(node.nChild):
            citems, ccoords = self.subtreeItemCoords(
                node.children[ci], node, ci, level + 1, setChildCenters)
            items += citems
            coords += ccoords
        return items, coords

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

        traverseTypeText = self.canvas.create_text(
            *self.upperRightNodeCoords(),
            text='traverseType: "{}"'.format(traverseType),
            anchor=E, font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(traverseTypeText)
        
        outBoxCoords = self.outputBoxCoords(font=self.outputFont)
        outBoxMidY = (outBoxCoords[1] + outBoxCoords[3]) // 2
        outputBox = self.createOutputBox(coords=outBoxCoords)
        callEnviron.add(outputBox)
        outputText = self.canvas.create_text(
            outBoxCoords[0] + 5, outBoxMidY, text='', anchor=W, 
            font=self.outputFont)
        callEnviron.add(outputText)
        self.scrollToSee(
            (outputText, traverseTypeText, outputBox), expand=True,
            sleepTime=0)
        
        iteratorCall = 'key, data in tree.traverse("{traverseType}")'.format(
            **locals())
        self.iteratorStack = []
        self.highlightCode(iteratorCall, callEnviron, wait=wait)
        dataIndex = None
        localVars = ()
        dataIndexConfig = {'level': 2, 'orientation': -100, 'keyNum': 0}
        colors = self.canvas.fadeItems(localVars)
        for node, key, items in self.traverse(traverseType):
            self.canvas.restoreItems(localVars, colors)
            keyNum = node.keys.index(key)
            dataIndexConfig['keyNum'] = keyNum
            if dataIndex is None:
                dataIndex = self.createArrow(node, 'key, data',
                                             **dataIndexConfig)
                callEnviron |= set(dataIndex)
                localVars += dataIndex
                self.scrollToSee(dataIndex + items, sleepTime=wait / 10)
            else:
                self.moveArrowsTo(dataIndex, node, dataIndexConfig, wait)

            self.highlightCode('print(key)', callEnviron, wait=wait)
            keyItem = self.canvas.copyItem(node.keyItems()[keyNum])
            callEnviron.add(keyItem)
            keyItemFont = self.canvas.getItemFont(keyItem)
            currentText = self.canvas.itemConfig(outputText, 'text')
            textBBox = self.canvas.bbox(outputText)
            newTextWidth = textWidth(self.outputFont, ' ' + str(key))
            self.moveItemsTo(
                keyItem, (textBBox[2] + newTextWidth // 2, outBoxMidY),
                startFont=keyItemFont, endFont=self.outputFont, 
                see=((outputBox,)), sleepTime=wait / 10)
            self.canvas.itemConfig(
                outputText,
                text=currentText + (' ' if len(currentText) > 0 else '') +
                str(key))
            self.canvas.delete(keyItem)
            callEnviron.discard(keyItem)

            self.highlightCode(iteratorCall, callEnviron, wait=wait)
            colors = self.canvas.fadeItems(localVars)

        self.canvas.restoreItems(localVars, colors)
        while self.iteratorStack:
            self.cleanUp(self.iteratorStack.pop())
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        
    _traverseCode = '''
def __traverse(self, node={nodeStr}, traverseType="{traverseType}"):
   if node is None:
      return

   for c in range(max(node.nChild, node.nKeys +
                      (1 if traverseType == "post" else 0))):
      if traverseType == "pre" and c < node.nKeys:
         yield (node.keys[c], node.data[c])
      if c < node.nChild:
         for childKey, childData in self.__traverse(
               node.children[c], traverseType):
            yield (childKey, childData)
      if traverseType == "in" and c < node.nKeys:
         yield (node.keys[c], node.data[c])
      if (traverseType == "post" and
          0 < c and c - 1 < node.nKeys):
         yield (node.keys[c - 1], node.data[c - 1])
'''

    def _traverse(self, node, traverseType, code=_traverseCode):
        nodeStr = str(node)
        wait = 0.1
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=wait / 10)

        nodeConfig = {'keyNum': -0.2, 'orientation': -120, 'level': 1,
                      'anchor': SE}
        nodeArrow = self.createArrow(
            node if node else self.childCoords(self, 1), 'node', **nodeConfig)
        callEnviron |= set(nodeArrow)

        self.highlightCode('node is None', callEnviron, wait=wait)
        if node is None:
            self.highlightCode('return', callEnviron)
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return

        self.highlightCode('traverseType == "post"', callEnviron, wait=wait)
        extra = 1 if traverseType == "post" else 0
        addend = re.compile(r'\D{}\D'.format(extra))
            
        self.highlightCode(
            ('c in range(max(node.nChild, node.nKeys +', addend),
            callEnviron, wait=wait)

        childLoopIter = re.compile(
            r'childKey, childData in self.__traverse\(\s.*, traverseType\)')
        localVars = nodeArrow
        cArrow, childArrow = None, None
        cArrowConfig = {'keyNum': 0, 'orientation': -90, 'level': 1}
        childArrowConfig = {'keyNum': 0, 'orientation': -90, 'level': 2}
        for c in range(max(node.nChild, node.nKeys + extra)):
            cArrowConfig['keyNum'] = c
            if cArrow is None:
                cArrow = self.createArrow(node, 'c', **cArrowConfig)
                callEnviron |= set(cArrow)
                localVars += cArrow
            else:
                self.moveArrowsTo(cArrow, node, cArrowConfig, wait)

            self.highlightCode('traverseType == "pre"', callEnviron, wait=wait)
            if traverseType == "pre":
                self.highlightCode('c < node.nKeys', callEnviron, wait=wait)
                
                if c < node.nKeys:
                    self.highlightCode('yield (node.keys[c], node.data[c])',
                                       callEnviron)
                    itemCoords = self.yieldCallEnvironment(
                        callEnviron, sleepTime=wait / 10)
                    yield (node, node.keys[c], node.keyItems())
                    self.resumeCallEnvironment(
                        callEnviron, itemCoords, sleepTime=wait / 10)
                    
            self.highlightCode('c < node.nChild', callEnviron, wait=wait)
            if c < node.nChild:
                self.highlightCode(childLoopIter, callEnviron, wait=wait)
                colors = self.canvas.fadeItems(localVars)
                
                for child, childKey, childKeyItems in self._traverse(
                        node.children[c], traverseType):
                    self.canvas.restoreItems(localVars, colors)
                    keyNum = child.keys.index(childKey)
                    childArrowConfig['keyNum'] = keyNum
                    if childArrow is None:
                        childArrow = self.createArrow(child, 'childData',
                                                      **childArrowConfig)
                        callEnviron |= set(childArrow)
                        localVars += childArrow
                    else:
                        self.moveArrowsTo(childArrow, child, childArrowConfig,
                                          wait)

                    self.highlightCode('yield (childKey, childData)',
                                       callEnviron, wait=wait)
                    itemCoords = self.yieldCallEnvironment(
                        callEnviron, sleepTime=wait / 10)
                    yield (child, childKey, childKeyItems)
                    self.resumeCallEnvironment(
                        callEnviron, itemCoords, sleepTime=wait / 10)
                
                    self.highlightCode(childLoopIter, callEnviron, wait=wait)
                    colors = self.canvas.itemsColor(localVars)

            self.highlightCode('traverseType == "in"', callEnviron, wait=wait)
            if traverseType == "in":
                self.highlightCode(('c < node.nKeys', 2), callEnviron, wait=wait)
                
                if c < node.nKeys:
                    self.highlightCode(
                        ('yield (node.keys[c], node.data[c])', 2), callEnviron)
                    itemCoords = self.yieldCallEnvironment(
                        callEnviron, sleepTime=wait / 10)
                    yield (node, node.keys[c], node.keyItems())
                    self.resumeCallEnvironment(
                        callEnviron, itemCoords, sleepTime=wait / 10)

            self.highlightCode(('traverseType == "post"', 2), callEnviron,
                               wait=wait)
            if traverseType == "post":
                self.highlightCode('0 < c', callEnviron, wait=wait)
                if 0 < c:
                    self.highlightCode('c - 1 < node.nKeys', callEnviron,
                                       wait=wait)

                    if c - 1 < node.nKeys:
                        self.highlightCode(
                            'yield (node.keys[c - 1], node.data[c - 1])',
                            callEnviron)
                        itemCoords = self.yieldCallEnvironment(
                            callEnviron, sleepTime=wait / 10)
                        yield (node, node.keys[c - 1], node.keyItems())
                        self.resumeCallEnvironment(
                            callEnviron, itemCoords, sleepTime=wait / 10)

            self.highlightCode(
                ('c in range(max(node.nChild, node.nKeys +', addend),
                callEnviron, wait=wait)

        self.highlightCode((), callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 10)
    
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
            "New Tree", self.newTree, maxRows=3,
            helpText='Create an empty tree')
        zoomInButton = self.addOperation(
            "Zoom In", lambda: self.zoom(5/4), maxRows=3,
            helpText='Zoom in around center')
        zoomOutButton = self.addOperation(
            "Zoom Out", lambda: self.zoom(4/5), maxRows=3,
            helpText='Zoom out around center')
        self.setupCanvasZoomHandlers(zoomBy=5/4)
        preOrderTraverseButton = self.addOperation(
            "Pre-order Traverse", lambda: self.clickTraverse('pre'), maxRows=3,
            helpText='Traverse the tree pre-order')
        inOrderTraverseButton = self.addOperation(
            "In-order Traverse", lambda: self.clickTraverse('in'), maxRows=3,
            helpText='Traverse the tree in-order')
        postOrderTraverseButton = self.addOperation(
            "Post-order Traverse", lambda: self.clickTraverse('post'),
            maxRows=3, helpText='Traverse the tree post-order')
        self.addAnimationButtons()
        return [self.insertButton, searchButton, randomFillButton, 
                newTreeButton, inOrderTraverseButton]
    
    def zoom(self, scale, fixPoint=None):
        newScale, newFontScale = self.scale * scale, self.fontScale * scale
        if newFontScale < 1:
            self.setMessage('Maximum zoom out reached')
        else:
            if abs(newScale - 1.0) < 0.01:
                newScale, newFontScale = 1.0, abs(self.FONT_SIZE)
            visibleCanvas = self.visibleCanvas()
            if fixPoint is None:
                fixPoint = V(V(visibleCanvas[:2]) + V(visibleCanvas[2:])) / 2
            self.scaleItems(
                self.ROOT_X0, self.ROOT_X0, scale, 
                newFontScale / abs(self.FONT_SIZE),
                fixPoint=fixPoint, updateBounds=True)
            self.scale, self.fontScale = newScale, newFontScale

    def setupCanvasZoomHandlers(
            self, zoomBy=5/4, x0=0, y0=0, updateBounds=True):
        if any(x is None for x in 
               (self.canvasBounds, self.canvasHScroll, self.canvasVScroll)):
            return
        def clickZoomHandler(event):
            fixPoint = (self.canvas.canvasx(event.x), 
                        self.canvas.canvasy(event.y))
            scaleBy = (1 / zoomBy) if event.state & SHIFT else zoomBy
            self.zoom(scaleBy, fixPoint=fixPoint)
        self.canvas.bind('<Double-Button-1>', clickZoomHandler)
        def scrollWheelZoomHandler(event):
            if ((event.state & SHIFT) if event.type is EventType.MouseWheel else
                (event.num in (4, 5))):
                fixPoint = (self.canvas.canvasx(event.x), 
                            self.canvas.canvasy(event.y))
                zoomIn = ((event.delta > 0)
                          if event.type is EventType.MouseWheel else
                          (event.num == 4))
                scaleBy = zoomBy if zoomIn else (1 / zoomBy)
                self.zoom(scaleBy, fixPoint=fixPoint)
        for eventType in ('<MouseWheel>', '<Button-4>', '<Button-5>'):
            self.canvas.bind(eventType, scrollWheelZoomHandler)
            
    def clickRandomFill(self):
        val = self.validArgument()
        if val:
            self.randomFill(val)
        self.clearArgument()

    def print(self, indent=4, **kwargs):
        self._print(self.rootNode, prefix='', indent=indent, **kwargs)

    def _print(self, node, prefix='', indent=4, **kwargs):
        if node is None:
            return
        if node.isLeaf():
            print('{}{}'.format(prefix, node), **kwargs)
        else:
            for c in range(node.nChild - 1, -1, -1):
                if c < node.nKeys:
                    print('{}{} of {}'.format(prefix, node.keys[c], node),
                          **kwargs)
                self._print(node.children[c], prefix + ' ' * indent, indent,
                            **kwargs)
            
if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    tree = Tree234()
    for arg in sys.argv[1:]:
        tree.setArgument(arg)
        tree.insertButton.invoke()

    tree.runVisualization()
