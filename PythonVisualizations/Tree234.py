from tkinter import *
import random
import sys

try:
    from VisualizationApp import *
    from BinaryTreeBase import *
except ModuleNotFoundError:
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
    
    def __str__(self):      # Represent a node as a string of keys
        # return '<Node234-{} @{}>'.format('-'.join(str(k) for k in self.keys),
        #                                  self.center)
        return '<Node234 {}>'.format(
            '|'.join(str(k) for k in self.keys[:self.nKeys]))
      
    def isLeaf(self):       # Test for leaf nodes
        return self.nChild == 0

class Tree234(BinaryTreeBase):
    maxLinks = 4
    maxKeys = maxLinks - 1
    
    def __init__(self, title="2-3-4 Tree", **kwargs):
        self.outputFont = (self.VALUE_FONT[0], self.VALUE_FONT[1] * 9 // 10)
        outputBoxHeight = abs(self.outputFont[1]) * 2 + 6
        circleRadius = 12
        self.maxCanvas = (1500, 400)
        RECT = (0, 0, self.maxCanvas[0],
                self.maxCanvas[1] - outputBoxHeight - circleRadius)
        super().__init__(
            title=title, CIRCLE_SIZE=circleRadius, RECT=RECT, MAX_LEVEL=4,
            canvasBounds=(0, 0, *self.maxCanvas), **kwargs)
        self.buttons = self.makeButtons()
        self.window.update()
        visible = self.visibleCanvas()
        xRange = (visible[2] - visible[0]) / self.maxCanvas[0]
        self.canvas.xview_moveto(max(0, 0.33 - xRange / 2))
        self.display(treeLabel='Tree234')
        self.activeColor, self.leftoverColor = 'black', 'gray40'
        self.rootNode = None

    def __str__(self):
        return '<Tree234>'
    
    def newTree(self):
        self.emptyTree()
        self.display(treeLabel='Tree234')

    def emptyTree(self):
        self.rootNode = None

    def childCoords(self, node, childNum, level=None, scale=1):
        '''Compute the center coordinates for one of a node's children.
        The node can be specified as either Node234 object, the tree
        object (self), or a tuple for the node's center coordinates.
        If it is specified as a tuple the level in the tree must be
        specified.  If it is a Node234, level can either be specified
        or computed by finding the node in the tree.
        '''
        if node is self:
            return self.ROOT_X0, self.ROOT_Y0
        center = node.center if isinstance(node, Node234) else node
        if level is None:
            if isinstance(node, Node234) and node.nKeys > 0:
                level, _ = self.getLevelAndChild(node.keys[0])
                level += 1
        treeWidth = (self.canvasBounds[2] - self.canvasBounds[0] -
                     self.CIRCLE_SIZE * Tree234.maxKeys * 2)
        levelDX = treeWidth / (Tree234.maxLinks ** level)
        dY = (0 if levelDX > self.CIRCLE_SIZE * Tree234.maxKeys * 2 
              else self.CIRCLE_SIZE * 5 // 2)
        halfKeys = Tree234.maxKeys / 2
        return V(center) + V(V(levelDX * (childNum - halfKeys),
                               self.LEVEL_GAP + dY * (childNum - halfKeys)) *
                             scale)

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

    def nodeChildAnchor(self, node, childNum, radius=None, scale=1):
        "Coords where a node's child points its parent link"
        center = node.center if isinstance(node, Node234) else node
        if radius is None: radius = self.CIRCLE_SIZE
        radius *= scale
        midKey = Tree234.maxKeys / 2
        return V(center) + V(radius * 1.9 * (childNum - midKey), 0)

    def nodeItemCoords(
            self, center, radius=None, parent=None, childNum=0, scale=1):
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
        radius *= scale
        top, bottom = y - radius, y + radius
        midKey = Tree234.maxKeys / 2
        linkCoords = origin + (
            self.nodeChildAnchor(parent, childNum, radius=radius, scale=1)
            if isinstance(parent, Node234) else origin)
        leftCircle = (x - 2 * radius * midKey, top,
                      x - 2 * radius * (midKey - 1), bottom)
        rightCircle = (x + 2 * radius * (midKey - 1), top,
                       x + 2 * radius * midKey, bottom)
        centerRect = (x - 2 * radius * (midKey - 0.5), top,
                      x + 2 * radius * (midKey - 0.5), bottom)
        textCenters = tuple([(x + radius * 2 * (j - midKey + 0.5), y)
                             for j in range(Tree234.maxKeys)])
        cellRects = tuple([(x + 2 * radius * (j - midKey), top,
                            x + 2 * radius * (j + 1 - midKey), bottom - 1)
                           for j in range(1, Tree234.maxKeys - 1)])
        return linkCoords, leftCircle, centerRect, rightCircle, *textCenters, *cellRects
      
    def createNodeShapes(
            self, center, keys, parent=None, childNum=0, radius=None, scale=1,
            lineColor='black', lineWidth=1, font=None, 
            fill='SkyBlue1', border='SkyBlue3'):
        if font is None: font = self.VALUE_FONT
        coords = self.nodeItemCoords(
            center, parent=parent, childNum=childNum, radius=radius, 
            scale=scale)
        link, lcircle, crect, rcircle = coords[:4]
        textCenters = coords[4:4 + Tree234.maxKeys]
        cellRects = coords[4 + Tree234.maxKeys:]
        linkItem = self.canvas.create_line(
            *link, fill=lineColor, width=lineWidth, arrow=FIRST, tags='link')
        self.canvas.tag_lower(linkItem)
        lcItem, rcItem = tuple([self.canvas.create_oval(
            *coords, fill=fill, width=0, tags=('lozenge', 'end'))
                                for coords in (lcircle, rcircle)])
        rectItem = self.canvas.create_rectangle(
            *crect, fill=fill, width=0, tags=('lozenge', 'rect'))
        cellItems = tuple([self.canvas.create_rectangle(
            *coords, fill='', width=lineWidth, outline=border,
            tags=('lozenge', 'cell'))
                           for coords in cellRects])
        textItems = tuple([self.canvas.create_text(
            *textCenters[j], text=str(keys[j]) if j < len(keys) else '',
            font=font, tags='keytext',
            fill=self.activeColor if j < len(keys) else self.leftoverColor)
                           for j in range(Tree234.maxKeys)])
        for i, textItem in enumerate(textItems):
            handler = self.textItemClickHandler(textItem)
            self.canvas.tag_bind(textItem, '<Button>', handler)
            self.canvas.tag_bind(
                lcItem if i == 0 else rcItem if i == Tree234.maxKeys - 1 else
                cellItems[i - 1], '<Button>', handler)

        return linkItem, lcItem, rectItem, rcItem, *textItems, *cellItems

    def textItemClickHandler(self, textItem):
        def textItemClick(e=None):
            self.setArgument(self.canvas.itemconfigure(textItem, 'text')[-1])
        return textItemClick
                
    def treeObjectCoords(
            self, offsetAngle=None, offset=None, fields=[], font=None):
        fieldFont, _ = self.treeObjectFonts(font)
        ffHeight = self.textHeight(fieldFont)
        rootWidth = self.textWidth(fieldFont, ' root ')
        fieldsWidth = sum(self.textWidth(fieldFont, ' {} '.format(field))
                          for field in fields)
        if offset is None: offset = 80
        if offsetAngle is None: offsetAngle = 180
        x0, y0 = V(self.ROOT_X0, self.ROOT_Y0) + V(
            V(V(offset + Tree234.maxKeys * self.CIRCLE_SIZE, 0).rotate(
                offsetAngle)) -
            V(fieldsWidth + rootWidth, self.CIRCLE_SIZE + ffHeight))
        return (x0, y0, 
                x0 + fieldsWidth + rootWidth,
                y0 + 2 * self.CIRCLE_SIZE + ffHeight)

    def updateTreeObjectRootPointer(self, arrow=None, root=None, see=True):
        '''Extend pointer of tree object to point at the root node if present
        otherwise make it zero length to be invisible'''
        if arrow is None and getattr(self, 'treeObject', None) is None:
            return
        if arrow is None:
            arrow = self.treeObject[1]
        arrowCoords = self.canvas.coords(arrow)
        self.canvas.coords(
            arrow, *arrowCoords[:2],
            *(arrowCoords[:2] if root is None else
              V(root.center) - V(self.CIRCLE_SIZE * Tree234.maxKeys, 0)))
        if see:
            self.scrollToSee((arrow, *getattr(self, 'treeObject', [])))

    def createArrow(
            self, node, label=None, level=1, keyNum=None, color=None, width=1,
            tags=['arrow'], font=None, orientation=-90, anchor=SW, see=True):
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
        if label is not None:
            label = self.canvas.create_text(
                *labelCoords, text=label, anchor=anchor, font=font, fill=color,
                tags=tags)
        result = (arrow, label)[:2 if label is not None else 1]
        if see:
            self.scrollToSee(result)
        return result

    def indexCoords(
            self, node, level=1, keyNum=None, font=None, orientation=-90,
            anchor=SW):
        '''Compute coordinates of an arrow index pointing at an existing node,
        node center coordinates, or the tree object, as well as the
        anchor coordinates of label at the arrow's base.  If keyNum is
        provided, the tip of the arrow is centered on the particular key
        within the node.
        '''
        if font is None: font = self.VARIABLE_FONT
        if node is self:
            treeObjectCoords = self.treeObjectCoords()
            center = V(treeObjectCoords[:2]) + V(
                self.treeDotCenter()[0], self.CIRCLE_SIZE)
        elif isinstance(node, Node234):
            center = node.center
        else:
            center = node
        tip = V(center) - V(0, self.CIRCLE_SIZE)
        if keyNum is not None and node is not self:
            tip = V(tip) + V(self.CIRCLE_SIZE * 
                             (keyNum * 2 + 1 - Tree234.maxKeys), 0)
        base = V(tip) + V(self.ARROW_HEIGHT + level * abs(font[1]), 0).rotate(
            orientation)
        return base + tip, base
    
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
            nodeArrow = self.createArrow(
                node if node else self.childCoords(p, 1), 'node', **indexConfig)
            pArrow = self.createArrow(p, 'p', **indexConfig)
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
   if prepare and current.nKeys == Tree234.maxKeys:
      current, parent = self.__splitNode(current, parent, goal)
   i = 0
   while i < current.nKeys and current.keys[i] < goal:
      i += 1
   if (i < current.nKeys and goal == current.keys[i]) or (
       current.isLeaf() and prepare):
      return (current, parent)
   return self.__find(
      goal, None if current.isLeaf() else current.children[i],
      current, prepare)
'''
    
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
                colors = self.fadeNonLocalItems(localVars)
            current, parent = self._splitNode(
                current, parent, goal, animation=animation, wait=wait)
            if animation:
                self.restoreLocalItems(localVars, colors)
                self.moveItemsTo(
                    localVars, 
                    self.indexCoords(current, **indexConfig) +
                    self.indexCoords(parent, **indexConfig),
                    sleepTime=wait / 10, see=True)

        i = 0
        if animation:
            self.highlightCode('i = 0', callEnviron)
            iArrow = self.createArrow(current, 'i', level=1, keyNum=i)
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
                self.moveItemsTo(iArrow, self.indexCoords(current, 1, keyNum=i),
                                 sleepTime=wait / 10, see=True)
                self.highlightCode('i < current.nKeys', callEnviron, wait=wait)
                if i < current.nKeys:
                    self.highlightCode('current.keys[i] < goal', callEnviron,
                                       wait=wait)

        if animation:
            self.highlightCode(('i < current.nKeys', 2), callEnviron, wait=wait)
            if i < current.nKeys:
                self.highlightCode('goal == current.keys[i]', callEnviron,
                                   wait=wait)
            if not (i < current.nKeys and goal == current.keys[i]):
                self.highlightCode('current.isLeaf()', callEnviron, wait=wait)
                if current.isLeaf():
                    self.highlightCode(('prepare', 3), callEnviron, wait=wait)
        if (i < current.nKeys and goal == current.keys[i]) or (
                current.isLeaf() and prepare):
            if animation:
                self.highlightCode(('return (current, parent)', 2), callEnviron)
            self.cleanUp(callEnviron, sleepTime=wait / 10)
            return current, parent

        if animation:
            self.highlightCode(
                'return self.__find(\n'
                '      goal, None if current.isLeaf() else current.children[i],\n'
                '      current, prepare)', callEnviron)
            colors = self.fadeNonLocalItems(localVars)
        result = self._find(
            goal, None if current.isLeaf() else current.children[i], current, 
            prepare, animation=animation, wait=wait)
        if animation:
            self.restoreLocalItems(localVars, colors)
        self.cleanUp(callEnviron, sleepTime=wait / 10)
        return result

    _splitNodeCode = '''
def __splitNode(self, toSplit={toSplitStr}, parent={parentStr}, goal={goal}):
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
      if goal == toSplit.keys[1]:
         return (self.__root, self)
      parent = self.__root
   else:
      parent.insertKeyValue(toSplit.keys[1], toSplit.data[1], newNode)
   return (toSplit if goal < toSplit.keys[1] else
           parent if goal == toSplit.keys[1] else newNode,
           parent)
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
                'newNode = self.__Node(toSplit.keys[2], toSplit.data[2]' +
                (')' if toSplit.isLeaf() else ',\n'
                 '                        *toSplit.children[2:toSplit.nChild])'),
                callEnviron)

        newNodeChildNum = 1 if parent is self else parent.nChild
        newNodeCenter = (V(toSplit.center) +
                         V(V(Tree234.maxLinks * 2, 2) * self.CIRCLE_SIZE))
        newNodeItems = self.createNodeShapes(
            toSplit.center if animation else newNodeCenter, 
            [toSplit.keys[2]], parent=None,  # Don't connect to parent yet
            childNum=1 if parent is self else parent.nKeys + 1)
        childrenToRemove = toSplit.children[2:toSplit.nChild]
        newNode = Node234(drawnValue([toSplit.keys[2]], *newNodeItems),
                          *childrenToRemove, center=newNodeCenter)
        if animation:
            newNodeConfig = {'keyNum': -0.2, 'orientation': -135, 'anchor': SW}
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
                sleepTime=wait / 10, see=True)
            self.highlightCode('toSplit.nKeys = 1', callEnviron, wait=wait)
        toSplit.nKeys = 1
        self.canvas.itemconfigure(toSplit.keyItems()[2], text='')
        for i in range(toSplit.nKeys, Tree234.maxKeys):
            self.canvas.itemconfigure(toSplit.keyItems()[i], 
                                      fill=self.leftoverColor)
        toSplit.keys[2] = None

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
                newRootCenter if animation else rootCenter, [toSplit.keys[1]])
            self.rootNode = Node234(
                drawnValue([toSplit.keys[1]], *newRootItems),
                toSplit, newNode, 
                center=newRootCenter if animation else rootCenter)
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
                self.highlightCode('goal == toSplit.keys[1]', callEnviron,
                                   wait=wait)
            else:
                self.restoreNodePositions(self.rootNode, sleepTime=0)

            if goal == toSplit.keys[1]:
                if animation:
                    self.highlightCode('return (self.__root, self)',
                                       callEnviron, wait=wait)
                self.cleanUp(callEnviron)
                return self.rootNode, parent
            else:
                if animation:
                    self.highlightCode('parent = self.__root', callEnviron)
                parent = self.rootNode
                if animation:
                    self.moveItemsTo(
                        parentArrow, self.indexCoords(parent, **indexConfig),
                        sleepTime=wait / 10, see=True)
        else:
            if animation:
                self.highlightCode(
                    'parent.insertKeyValue(toSplit.keys[1], toSplit.data[1], '
                    'newNode)', callEnviron)
                colors = self.fadeNonLocalItems(localVars)
            self.insertKeyValue(
                parent, toSplit.keys[1], newNode, animation=animation,
                wait=wait, keyFrom=toSplit.keyItems()[1])
            if animation:
                self.restoreLocalItems(localVars, colors)
                
        self.restoreNodePositions(
            parent, sleepTime=wait / 10 if animation else 0,
            nodeIndices=((parent, indexConfig, parentArrow),
                         (toSplit, indexConfig, toSplitArrow),
                         (newNode, newNodeConfig, newNodeArrow))
            if animation else (), see=True)

        if animation:
            self.highlightCode('goal < toSplit.keys[1]', callEnviron, wait=wait)
            if goal < toSplit.keys[1]:
                self.highlightCode(
                    (('return', 2), ('toSplit', 18), ',\n           parent'),
                    callEnviron)
            elif (self.highlightCode(('goal == toSplit.keys[1]', 2),
                                     callEnviron, wait=wait) or
                  goal == toSplit.keys[1]):
                self.highlightCode(
                    (('return', 2), ('parent', 5), ',\n           parent'),
                    callEnviron)
            else:                
                self.highlightCode(
                    (('return', 2), ('newNode', 5), ',\n           parent'),
                    callEnviron)
        self.canvas.itemconfigure(toSplit.keyItems()[1], text='')
        self.cleanUp(callEnviron)
        return (toSplit if goal < toSplit.keys[1] else
                parent if goal == toSplit.keys[1] else newNode,
                parent)

    insertKeyValueCode = '''
def insertKeyValue(self, key={key}, data, subtree={subtreeStr}):
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
            animation=True, wait=0.1, keyFrom=None):
        '''Insert a key in a (non-full) node, optionally adding a subtree
        as the child link before the key.  If keyFrom is provided, it
        should be an existing canvas text item for the key.
        '''
        subtreeStr = str(subtree)
        callEnviron = self.createCallEnvironment(
            code='' if not animation else code.format(**locals()),
            startAnimations=animation)
        i = 0
        subtreeArrow = None
        if animation:
            if subtree:
                subtreeConfig = {'level': 1, 'orientation': -135, 'keyNum': -0.2}
                subtreeArrow = self.createArrow(
                    subtree, 'subtree', **subtreeConfig)
                callEnviron |= set(subtreeArrow)
            iConfig = {'level': 1, 'keyNum': i}
            self.highlightCode('i = 0', callEnviron, wait=wait)
            iArrow = self.createArrow(node, 'i', **iConfig)
            callEnviron |= set(iArrow)
            self.scrollToSee(node.dValue.items, sleepTime=wait / 10)
            self.highlightCode('i < self.nKeys', callEnviron, wait=wait)
            if i < node.nKeys:
                self.highlightCode('self.keys[i] < key', callEnviron, wait=wait)

        while i < node.nKeys and node.keys[i] < key:
            if animation:
                self.highlightCode('i += 1', callEnviron, wait=wait)
            i += 1
            if animation:
                iConfig['keyNum'] = i
                self.moveItemsTo(iArrow, self.indexCoords(node, **iConfig),
                                 sleepTime=wait / 10, see=True)
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

        if animation:
            self.highlightCode('self.keys[i] == key', callEnviron, wait=wait)
        if node.keys[i] == key:
            if animation:
                self.highlightCode('self.data[i] = data', callEnviron, 
                                   wait=wait)
                # Animate updating data?
                self.highlightCode('return False', callEnviron, wait=wait)
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
            jKey = node.keyItems()[j]
            if animation:
                self.highlightCode('self.keys[j] = self.keys[j-1]', callEnviron)
                keyCopy = self.copyCanvasItem(node.keyItems()[j - 1])
                callEnviron.add(keyCopy)
                self.moveItemsOnCurve(
                    keyCopy, self.canvas.coords(jKey), sleepTime=wait / 10, 
                    see=True)
            self.canvas.itemconfigure(
                jKey, text=self.canvas.itemconfigure(node.keyItems()[j - 1], 
                                                     'text')[-1])
            node.keys[j] = node.keys[j - 1]
            
            if animation:
                self.canvas.delete(keyCopy)
                callEnviron.discard(keyCopy)
                self.highlightCode('self.data[j] = self.data[j-1]', callEnviron,
                                   wait=wait)
                self.highlightCode(
                    'self.children[j+1] = self.children[j]', callEnviron)
            node.children[j + 1] = node.children[j]
            child = node.children[j + 1]
            if child:
                newLinkCoords = child.center + self.nodeChildAnchor(node, j + 1)
                if animation:
                    self.moveItemsLinearly(child.dValue.items[0], newLinkCoords,
                                           sleepTime=wait / 10, see=True)
                else:
                    self.canvas.coords(child.dValue.items[0], newLinkCoords)
                
            j -= 1
            if animation:
                self.highlightCode('j -= 1', callEnviron)
                jConfig['keyNum'] = j
                self.moveItemsTo(jArrow, self.indexCoords(node, **jConfig),
                                 sleepTime=wait / 10, see=True)
                
            if animation:
                self.highlightCode('i < j', callEnviron, wait=wait)

        if animation:
            self.highlightCode('self.keys[i] = key', callEnviron)
            if keyFrom is None:
                newItemCoords = self.newValueCoords() 
                newNode = self.createNodeShapes(newItemCoords, [key])
                circleItem, keyItem = newNode[1], newNode[4]
                for item in newNode:
                    if item in (circleItem, keyItem):
                        callEnviron.add(item)
                    else:
                        self.canvas.delete(item)
            else:
                center = self.canvas.coords(keyFrom)
                offset = (self.CIRCLE_SIZE, self.CIRCLE_SIZE)
                circleItem = self.canvas.create_oval(
                    (V(center) - V(offset)) + (V(center) + V(offset)),
                    fill='SkyBlue1', width=0)
                keyItem = self.copyCanvasItem(keyFrom)
                for item in (node.keyItems()[i], keyFrom):
                    self.canvas.tag_lower(circleItem, item)
            circleCoords = self.canvas.coords(circleItem)
            self.canvas.coords(
                keyItem, *(V(V(circleCoords[:2]) + V(circleCoords[2:])) / 2))
            self.canvas.itemconfigure(
                keyItem, fill=self.leftoverColor if i >= node.nKeys else
                self.activeColor)
            self.moveItemsTo(keyItem, self.canvas.coords(node.keyItems()[i]),
                             sleepTime=wait / 10)
        self.canvas.itemconfigure(node.keyItems()[i], text=str(key))
        node.keys[i] = key
        
        if animation:
            self.canvas.delete(keyItem)
            callEnviron.discard(keyItem)
            self.highlightCode('self.data[i] = data', callEnviron)
            self.moveItemsTo(
                circleItem,
                V(self.canvas.coords(node.dValue.items[1])) + 
                V((self.CIRCLE_SIZE * i * 2, 0) * 2),
                sleepTime=wait / 10)
            self.canvas.delete(circleItem)
            callEnviron.discard(circleItem)

            self.highlightCode('self.nKeys += 1', callEnviron, wait=wait)
        self.canvas.itemconfigure(
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
                    sleepTime=wait / 10, see=True)
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
        nodeArrow = self.createArrow(
            node if node else self.childCoords(p, 1), 'node', **indexConfig)
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
        return node
        
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
                    self.canvas.itemconfigure(
                        node.keyItems()[i], 
                        text='' if node.keys[i] is None else str(node.keys[i]),
                        fill=self.activeColor if i < node.nKeys else
                        self.leftoverColor)
                    # if node.nKeys <= i:   NOTE allow leftover values to remain
                    #     node.keys[i] = None
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
        # Fill in child number when parent is known
        if childNum is None and parent:
            pChildren = parent.children[:parent.nChild]
            if subtreeRoot in pChildren:
                childNum = pChildren.index(subtreeRoot)
            else:
                raise ValueError(
                    "Given node {} is not among parent's {} children".format(
                        subtreeRoot, parent))
        # Traverse tree to collect canvas items and their coordinates
        items, coords = self.subtreeItemCoords(
            subtreeRoot, parent, childNum, level=None,
            setChildCenters=setChildCenters)
        for node, config, indexItems in nodeIndices:
            items += indexItems
            coords += self.indexCoords(node, **config)

        if sleepTime > 0:
            self.moveItemsLinearly(items, coords, sleepTime=sleepTime, see=see)
        else:
            for item, coord in zip(items, coords):
                self.canvas.coords(item, coord)
        if subtreeRoot is self.rootNode:
            self.updateTreeObjectRootPointer(
                root=subtreeRoot, see=sleepTime > 0)

    def subtreeItemCoords(
            self, node, parent, childNum, level=None, setChildCenters=True):
        '''Return a node's canvas items and their coordinates after
        optionally setting its center based on its relation to its parent.
        Recursively descend through all the nodes descendants.
        '''
        if node is None:
            return [], []
        if level is None: # ASSUME no empty nodes so there are always 1+ keys
            level, _ = self.getLevelAndChild(node.keys[0])
            if level is None:
                raise Exception('Unable to get level for {}'.format(node))
        if setChildCenters and (parent or node is self.rootNode):
            node.center = (
                (self.ROOT_X0, self.ROOT_Y0) if node is self.rootNode else
                self.childCoords(parent, childNum, level))
        parentLink = parent or node is self.rootNode
        items = node.dValue.items[0 if parentLink else 1:]
        coords = self.nodeItemCoords(node, parent=parent, childNum=childNum)[
            0 if parentLink else 1:]
        for ci in range(node.nChild):
            citems, ccoords = self.subtreeItemCoords(
                node.children[ci], node, ci, level + 1, setChildCenters)
            items += citems
            coords += ccoords
        return items, coords
    
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
        self.addAnimationButtons()
        return [self.insertButton, searchButton, randomFillButton, newTreeButton]

    def clickRandomFill(self):
        val = self.validArgument()
        if val:
            self.randomFill(val)
        self.clearArgument()
        # self.print(file=sys.stderr)

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
