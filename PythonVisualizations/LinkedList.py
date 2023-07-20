from tkinter import *

try:
    from drawnValue import *
    from coordinates import *
    from tkUtilities import *
    from VisualizationApp import *
    from OutputBox import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .coordinates import *
    from .tkUtilities import *
    from .VisualizationApp import *
    from .OutputBox import *

V = vector

class Node(object):
    
    # create a linked list node
    #id is used to link the different parts of each node visualization
    def __init__(
            self, k, nextNode=None, id='',
            cell=None, value=None, dot=None, nextPointer=None):
        self.key = k
        self.id = id
        self.next = nextNode  # reference to next item in list
        self.cell = cell
        self.value = value
        self.dot = dot
        self.nextPointer = nextPointer

    def items(self):    # Return list of canvas items used to draw Node
        return tuple(
            i for i in (self.cell, self.value, self.dot, self.nextPointer)
            if i is not None)
        
    def __str__(self):
        return "{" + str(self.key) + "}"

class LinkedList(VisualizationApp):
    nextColor = 0
    WIDTH = 800
    HEIGHT = 400
    CELL_SIZE = 50
    CELL_BORDER = 2 
    CELL_WIDTH = 120
    CELL_HEIGHT = 50
    CELL_GAP = 20
    DOT_SIZE = 10
    LL_X0 = 115
    LL_Y0 = 110
    MAX_SIZE=20
    LEN_ROW = 5
    ROW_GAP = 50  
    MAX_ARG_WIDTH = 8
    SORTED_BACKGROUND = 'honeydew3'
    UNSORTED_BACKGROUND = 'powder blue'
    
    def __init__(self, title="Linked List", maxArgWidth=MAX_ARG_WIDTH, **kwargs):
        super().__init__(title=title, maxArgWidth = maxArgWidth, **kwargs)
        self.first = None   # Canvas ID for first pointer arrow
        self.list = []      # List of Link nodes in linked list
        self.prev_id = -1
        self.buttons = self.makeButtons()
        self.display()
        self.canvas.bind('<Configure>', self.resizeCanvas)

    def __len__(self):
        return len(self.list)

    def isEmpty(self):
        return not self.first
    
    def generateID(self):
        self.prev_id+=1
        return "item" + str(self.prev_id)
    
    # Calculate coordinates of cell parts
    # Position 0 is the LinkedList cell.  The Links start at postiion 1.
    # Negative position means row above the Linked List node 
    # Position -1 is directly above position 1, -2 is above 2, etc.
    # Posittion -self.LEN_ROW is directly above the Linked List node
    def x_y_offset(self, pos):
        x_offset = self.LL_X0 + abs(pos) % self.LEN_ROW * (
            self.CELL_WIDTH + self.CELL_GAP)
        y_offset = self.LL_Y0 + max(1 - self.LEN_ROW, pos) // self.LEN_ROW * (
            self.CELL_HEIGHT + self.ROW_GAP) 
        return x_offset, y_offset
    
    def indexTip(self, pos): # Compute position of index pointer tip
        if pos == 0:
            nextDotCenter = self.cellNext(pos)
            return V(nextDotCenter) - V((0, self.CELL_HEIGHT // 2))
        return V(self.x_y_offset(pos)) + ( # Goes to middle top for normal
            V((self.CELL_WIDTH // 2, 0)) if pos > 0 else # position, else
            V((0, self.CELL_HEIGHT // 2))) # left middle for pos <= 0

    def indexCoords(self, pos, level=0):
        tip = self.indexTip(pos)
        delta = (0, self.CELL_SIZE // 5) if pos >= 0 else (
            self.CELL_SIZE * 4 // 5, 0)
        offset = V(0, abs(self.VARIABLE_FONT[1])) * level
        start = V(V(tip) - V(delta)) - V(offset)
        return (*start, *tip)

    def indexLabelCoords(self, pos, level=0):
        arrowCoords = self.indexCoords(pos, level)
        return arrowCoords[:2]
        
    def cellCoords(self, pos):  # Bounding box for a Link node rectangle
        x, y = self.x_y_offset(pos)
        return x, y, x + self.CELL_WIDTH, y + self.CELL_HEIGHT

    # Calculate coordinates for the center of a Link node's text
    def cellText(self, pos):
        x, y = self.x_y_offset(pos)
        return x + self.CELL_HEIGHT, y + self.CELL_HEIGHT // 2

    # Calculate coordinates for the center of a node's next pointer
    def cellNext(self, pos):
        x, y = self.x_y_offset(pos)
        return x + self.CELL_HEIGHT * 2, y + self.CELL_HEIGHT // 2

    def nextDot(self, pos):  # Bounding box for the dot of the next pointer
        x, y = self.cellNext(pos)
        radius = self.DOT_SIZE // 2
        return x - radius, y - radius, x + radius, y + radius
    
    def display(self):      # Set up the permanent canvas items
        self.canvas.delete('all')
        self.linkedListNode()
        if self.first:      # If there was a displayed first pointer, recreate
            self.first = self.linkNext(0)
            
    def resizeCanvas(self, event=None):   # Handle canvas resize events
        if (self.canvas and self.canvas.winfo_ismapped() and
            self.animationsStopped()):
            width, height = widgetDimensions(self.canvas)
            new_row_length = max(2, (width - self.LL_X0 + self.CELL_GAP) // (
                self.CELL_WIDTH + self.CELL_GAP))
            change = self.LEN_ROW != new_row_length
            self.LEN_ROW = new_row_length
            if change:
                self.restorePositions()
    
    # Create a dot for the next pointer of a Link or LinkedList node
    def createDot(self, coordsOrPos, id):
        coords = (coordsOrPos if isinstance(coordsOrPos, (list, tuple))
                  else self.nextDot(coordsOrPos))
        return self.canvas.create_oval(
            *coords, fill="RED", outline="RED", tags=('next dot', id))

    # Compute coordinaes of the link pointer from pos to pos+d (where d is
    # usually 1)
    # When pos is 0, creates the arrow for the LinkedList first pointer
    # and pos -1 creates an arrow for a new node above the LinkedList
    def nextLinkCoords(self, pos, d=1):
        cell0 = self.cellNext(pos)
        if d == 0:                  # Empty link (to be animated)
            return cell0 * 4
        cell1index = pos + d
        if cell1index == 0: cell1index = 1 # Cannot point to Linked List head
        cell1 = self.cellNext(cell1index)
        dy = cell1[1] - cell0[1]    # Difference of cell Y coordinates
        if abs(dy) < 1: dy = 0      # ignore small differences
        stairstep = dy != 0 and pos != 0
        
        # Determine position for the tip of the arrow
        tip = V(cell1) - V(
            (0, (1 if dy > 0 else -1) * self.CELL_HEIGHT // 2) if stairstep
            else (self.CELL_HEIGHT * 2, 0))
        delta3 = V(V(tip) - V(cell0)) * 0.33
        p0 = cell0
        p1 = V(cell0) + ( V((0, dy // 2)) if stairstep else V(delta3) )
        p2 = V(tip)   - ( V((0, (1 if dy > 0 else -1) * self.ROW_GAP // 2))
                          if stairstep else V(delta3) )
        return (*p0, *p1, *p2, *tip)

    # Create the arrow linking a Link node to the next Link
    def linkNext(self, pos, d=1, updateInternal=True):
        arrow = self.canvas.create_line(
            *self.nextLinkCoords(pos, d), arrow=LAST, tags=('link pointer', ))
        if updateInternal:
            if pos <= 0:
                self.first = arrow
            else:
                self.list[pos - 1].nextPointer = arrow
        return arrow
    
    #accesses the next color in the pallete
    #used to assign a node's color
    def chooseColor(self):
        color = drawnValue.palette[self.nextColor]
        self.nextColor = (self.nextColor + 1) % len(drawnValue.palette)
        return color
    
    def linkCoords(self, pos): # Return coords for cell, text, and dot of a Link
        return (self.cellCoords(pos), self.cellText(pos), self.nextDot(pos))

    def createLink(           # Create  the canvas items for a Link node
            self,             # This will be placed according to coordinates
            coordsOrPos=-1,   # or list index position (-1 = above position 1)
            val='', id='link', color=None, nextNode=None, updateInternal=False):
        coords = (coords if isinstance(coordsOrPos, (list, tuple)) 
                  else self.linkCoords(coordsOrPos))
        if color == None:
            color = self.chooseColor()
        cell_rect = self.canvas.create_rectangle(
            *coords[0], fill= color, tags=('cell', id))
        cell_text = self.canvas.create_text(
            *coords[1], text=val, font=self.VALUE_FONT, fill=self.VALUE_COLOR,
            tags = ('cell', id))
        cell_dot = self.createDot(coords[2], id)
        self.canvas.tag_bind(id, '<Button>', 
                             lambda e: self.setArgument(str(val)))
        if nextNode in self.list and isinstance(coordsOrPos, int):
            nextNodeIndex = self.list.index(nextNode)
            linkPointer = (self.linkNext(coordsOrPos,
                                         nextNodeIndex + 1 - coordsOrPos,
                                         updateInternal=updateInternal), )
        else:
            linkPointer = ()
        return (cell_rect, cell_text, cell_dot) + linkPointer

    # Creates the LinkedList objeect that is the head of the list
    def linkedListNode(self):
        x, y = self.x_y_offset(0)
        rect = self.canvas.create_rectangle(
            x + self.CELL_WIDTH * 2 // 3, y,
            x + self.CELL_WIDTH, y + self.CELL_HEIGHT,
            fill=self.UNSORTED_BACKGROUND, tags=("LinkedList", "cell"))
        oval = self.createDot(0, 'LinkedList')
        ovalCoords = self.canvas.coords(oval)
        firstText = self.canvas.create_text(
            (ovalCoords[0] + ovalCoords[2]) / 2, (y + ovalCoords[1]) / 2,
            text="first", font=('Courier', -10))
        nameText = self.canvas.create_text(
            x, y + self.CELL_HEIGHT // 2, font=('Courier', -14),
            text='LinkedList')
        
    ### ANIMATION METHODS###
    def createIndex(self, pos, name=None, level=0):
        arrow = self.canvas.create_line(
            *self.indexCoords(pos, level), arrow=LAST,
            fill=self.VARIABLE_COLOR)
        if name:
            name = self.canvas.create_text(
                *self.indexLabelCoords(pos, level), text=name,
                font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR,
                anchor=SW if pos >= 0 else E)
        return (arrow, name) if name else (arrow,)

    def outputData(self, posOrNode=1, callEnviron=None, copy=True, wait=0.1):
        localEnviron = callEnviron or self.createCallEnvironment()

        outputBoxCoords = self.outputBoxCoords(full=False)
        for item in self.createOutputBox(full=False):
            localEnviron.add(item)
        localEnviron |= set(self.createOutputBox(full=False))

        node = (posOrNode if isinstance(posOrNode, Node)
                else self.list[posOrNode - 1])
        toMove = (node.cell, node.value)
        if copy:
            toMove = tuple(self.canvas.copyItem(item) for item in toMove)
            localEnviron |= set(toMove)
        self.outputBox.setToText(
            toMove, sleepTime=wait / 10,
            color=self.canvas.itemConfig(toMove[0], 'fill'))

        if localEnviron != callEnviron:
            self.cleanUp(localEnviron)
        return node.key

    def outputBoxCoords(self, full=False):
        return (self.LL_X0 // 5, self.LL_Y0 // 5,
                self.LL_X0 // 5 + (self.CELL_WIDTH + self.CELL_GAP) *
                (self.LEN_ROW if full else 1) - self.CELL_GAP,
                self.LL_Y0 // 5 + self.CELL_HEIGHT)

    def outputLabelCoords(self):
        oBox = self.outputBoxCoords()
        pad = 0
        return oBox[0] - pad, (oBox[1] + oBox[3]) // 2
    
    def createOutputBox(self, full=False):
        self.outputBox = OutputBox(self, self.outputBoxCoords(full))
        return self.outputBox.items()
    
    firstCode = """
def first(self):
   if self.isEmpty():
      raise Exception("No first item in empty list")
   return self.getFirst().getData()
"""
    
    def firstData(self, code=firstCode, animateOutput=True, start=True):
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)
        wait = 0.1
        
        self.highlightCode('self.isEmpty()', callEnviron, wait=wait)
        if self.first is None:
            self.highlightCode(
                'raise Exception("No first item in empty list")', callEnviron,
                wait=wait, color=self.EXCEPTION_HIGHLIGHT)
        else:
            self.highlightCode(
                'return self.getFirst().getData()', callEnviron)
            if animateOutput:
                self.outputData(1, callEnviron)
            else:
                self.wait(wait)

        self.cleanUp(callEnviron)
        return self.list[0].key if self.first else None
    
    deleteFirstCode = """
def deleteFirst(self):
   if self.isEmpty():
      raise Exception("Cannot delete from empty linked list")
   
   first = self.getFirst()
   self.setNext(first.getNext())
   return first.getData()
"""
    
    def deleteFirst(self, code=deleteFirstCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)
        wait = 0.1
        
        self.highlightCode('self.isEmpty()', callEnviron, wait=wait)
        if self.first is None:
            self.highlightCode(
                'raise Exception("Cannot delete from empty linked list")',
                callEnviron, wait=wait, color=self.EXCEPTION_HIGHLIGHT)
            self.cleanUp(callEnviron)
            return
        
        self.highlightCode('first = self.getFirst()', callEnviron, wait=wait)
        firstIndex = self.createIndex(1, 'first')
        callEnviron |= set(firstIndex)
        
        self.highlightCode('self.setNext(first.getNext())', callEnviron,
                           wait=wait)
        previous = 0
        first = self.list[previous]
        nextPointer = first.nextPointer
        toMove = (self.first, *firstIndex, first.cell, first.value)
        toCoords = (
            self.nextLinkCoords(previous, d=2 if nextPointer else 0),
            self.indexCoords(-1), self.indexLabelCoords(-1),
            self.cellCoords(-1), self.cellText(-1))
        self.canvas.changeAnchor(E, firstIndex[1])
        self.canvas.tag_raise(self.first)
        self.dispose(callEnviron, first.dot, first.nextPointer)
        self.moveItemsLinearly(toMove, toCoords, sleepTime=wait / 10)
        if nextPointer is None:
            self.canvas.delete(self.first)
            self.first = None

        self.list[0:1] = []
        callEnviron |= set(first.items())

        self.restorePositions()      # Reposition all links

        self.highlightCode('return first.getData()', callEnviron)
        self.dispose(callEnviron, first.dot, first.nextPointer)
        self.outputData(first, callEnviron, copy=False)
        
        self.cleanUp(callEnviron)
        return first.key

    traverseCode = """
def traverse(self, func=print):
   link = self.getFirst()
   while link is not None:
      func(link.getData())
      link = link.getNext()
"""
    
    def traverse(self, code=traverseCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)
        wait = 0.1

        outputBoxCoords = self.outputBoxCoords(full=True)
        callEnviron |= set(self.createOutputBox(full=True))
        outputFont = ('Courier', -18)
        outX = outputBoxCoords[0] + abs(outputFont[1])
        outY = outputBoxCoords[1] + abs(outputFont[1])
        sepX = textWidth(outputFont, ' ')
        sepY = textHeight(outputFont, ' ')

        self.highlightCode('link = self.getFirst()', callEnviron)
        link = 1
        linkIndex = self.createIndex(link, name='link')
        callEnviron |= set(linkIndex)
        self.wait(wait)
        
        self.highlightCode('link is not None', callEnviron, wait=wait)
        while link <= len(self.list):
            self.highlightCode('func(link.getData())', callEnviron)
            node = self.list[link - 1]
            self.outputBox.appendText(
                self.canvas.copyItem(node.value), sleepTime=wait / 10)
            
            self.highlightCode('link = link.getNext()', callEnviron)
            link += 1
            self.moveItemsTo(
                linkIndex,
                (self.indexCoords(link), self.indexLabelCoords(link)),
                sleepTime=0.02)
            self.highlightCode('link is not None', callEnviron, wait=wait)

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
            
    newLinkedListCode = """
def __init__(self):
   self.__first = None
"""

    # Erases old linked list and draws empty list
    def newLinkedList(self, code=newLinkedListCode):
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=False)
        self.startAnimations(enableStops=False)
        self.highlightCode('self.__first = None', callEnviron)
        self.first = None
        self.list = []
        self.display()

        self.wait(0.1)
        self.cleanUp(callEnviron)
        
    insertCode = '''
def insert(self, datum={val!r}):
   link = Link(datum, self.getFirst())
   self.setFirst(link)
'''
    
    def insert(self, val, code=insertCode, start=True, wait=0.1):
        'Insert a new Link node at the front with a specific value'
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        
        self.highlightCode('link = Link(datum, self.getFirst())', callEnviron)
        nodeID = self.generateID()
        newNode = Node(
            val, self.first, nodeID,
            *self.createLink(
                -1, val, nodeID, nextNode=self.list[0] if self.first else None))
        callEnviron |= set(newNode.items())
        
        linkIndex = self.createIndex(-1, 'link')
        callEnviron |= set(linkIndex)
        self.wait(wait * 2)

        self.highlightCode('self.setFirst(link)', callEnviron)
        previous = 0
        insertLinkCoords = self.nextLinkCoords(previous, -(previous + 1))
        insertLink = (self.first if previous == 0 else
                      self.list[previous].nextPointer)
        if self.first is None or previous >= len(self.list):
            self.linkNext(previous, 0)
            insertLink = (self.first if previous == 0 else
                          self.list[previous].nextPointer)
        self.moveItemsLinearly(
            insertLink, insertLinkCoords, sleepTime=wait / 10)
            
        toMove = [insertLink] + list(newNode.items())
        for node in self.list[previous:]:
            toMove.extend(node.items())
        toCoords = [self.nextLinkCoords(previous)] + [
            self.canvas.coords(item) for node in self.list[previous:]
            for item in node.items()] + list(self.linkCoords(len(self.list) + 1))
        # When list already contains some items, splice in the target 
        # coordinates for the final next pointer
        if previous < len(self.list):
            toCoords[-3:-3] = [self.nextLinkCoords(len(self.list))]
        self.moveItemsLinearly(toMove, toCoords, sleepTime=wait / 10)
        self.list[previous:previous] = [newNode]
        callEnviron -= set(newNode.items())
            
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
    
    deleteCode = """
def delete(self, goal={goal!r}, key=identity):
   if self.isEmpty():
      raise Exception("Cannot delete from empty linked list")

   previous = self
   while previous.getNext() is not None:
      link = previous.getNext()
      if goal == key(link.getData()):
         previous.setNext(link.getNext())
         return link.getData()
      previous = link
        
   raise Exception("No item with matching key found in list")
"""

    # Delete a link from the linked list by finding a matching goal key
    def delete(self, goal, code=deleteCode, start=True, wait=0.1):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)

        goalText = self.canvas.create_text(
            *self.outputLabelCoords(), text='goal = {}'.format(goal), 
            anchor=W, font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(goalText)

        # check if empty
        self.highlightCode('self.isEmpty()', callEnviron, wait=wait)
        if not self.first:
            self.highlightCode(
                'raise Exception("Cannot delete from empty linked list")',
                callEnviron, color=self.EXCEPTION_HIGHLIGHT, wait=wait)
            self.cleanUp(callEnviron)
            return None

        self.highlightCode('previous = self', callEnviron)
        previous = 0
        previousIndex = self.createIndex(previous, 'previous', level=1)
        callEnviron |= set(previousIndex)
        self.wait(wait)

        linkIndex = None

        self.highlightCode(
            'previous.getNext() is not None:', callEnviron, wait=wait)
        while previous < len(self.list):
            
            self.highlightCode('link = previous.getNext()', callEnviron)
            link = previous + 1
            if linkIndex:
                self.moveItemsTo(
                    linkIndex, 
                    (self.indexCoords(link), self.indexLabelCoords(link)),
                    sleepTime=wait / 10)
            else:
                linkIndex  = self.createIndex(link, 'link')
                callEnviron |= set(linkIndex)
                self.wait(wait)
            
            self.highlightCode(
                'goal == key(link.getData())', callEnviron, wait=wait)
            found = self.list[previous].key == goal
            if found:
                foundHighlight = self.createFoundHighlight(link)
                callEnviron.add(foundHighlight)
                                
                # Prepare to update next pointer from previous
                self.highlightCode(
                    'previous.setNext(link.getNext())', callEnviron)
                updateFirst = previous == 0
                node = self.list[previous]
                nextPointer = node.nextPointer
                toMove = (self.first if updateFirst else
                          self.list[previous - 1].nextPointer,
                          *linkIndex, node.cell, node.value, foundHighlight)
                self.canvas.changeAnchor(E, linkIndex[1])
                toCoords = (self.nextLinkCoords(previous,
                                                d=2 if nextPointer else 0),
                            self.indexCoords(-1), self.indexLabelCoords(-1),
                            self.cellCoords(-1), self.cellText(-1),
                            self.cellCoords(-1))
                self.dispose(callEnviron, node.dot, node.nextPointer)
                self.canvas.tag_raise(self.first)
                self.moveItemsLinearly(toMove, toCoords, sleepTime=wait / 10)

                if nextPointer is None:
                    if updateFirst:
                        self.canvas.delete(self.first)
                        self.first = None
                    else:
                        self.canvas.delete(self.list[previous - 1].nextPointer)
                        self.list[previous - 1].nextPointer = None
                self.list[previous:link] = []

                # Reposition all remaining links
                self.restorePositions()
                    
                self.highlightCode('return link.getData()', callEnviron,
                                   wait=wait)
                self.dispose(callEnviron, foundHighlight, goalText)
                self.outputData(node, callEnviron, copy=False)
                self.cleanUp(callEnviron)
                return node.key

            # Advance to next Link
            self.highlightCode('previous = link', callEnviron)
            previous = link
            self.moveItemsTo(
                previousIndex,
                (self.indexCoords(link, level=1), 
                 self.indexLabelCoords(link, level=1)),
                sleepTime=wait / 10)
            self.highlightCode(
                'previous.getNext() is not None:', callEnviron, wait=wait)
            
        # Failed to find goal key
        self.highlightCode(
            'raise Exception("No item with matching key found in list")',
            callEnviron, color=self.EXCEPTION_HIGHLIGHT, wait=wait)
        self.cleanUp(callEnviron)        
        
    def restorePositions(  # Move all links on the canvas to their correct
            self,          # positions.  Include any additional items to move
            addItems=[], addCoords=[], # to some target coordinates
            sleepTime=0.01):
        if self.first is None: return  # No first pointer -> nothing to restore
        items = [self.first, *addItems]
        toCoords = [self.nextLinkCoords(0), *addCoords]
        for i, node in enumerate(self.list):
            items.extend(node.items())
            toCoords.extend(self.linkCoords(i + 1))
            if node.nextPointer:
                toCoords.append(self.nextLinkCoords(i + 1))
        if sleepTime > 0:
            try:
                stopped = self.animationsStopped()
                if stopped:
                    self.startAnimations(enableStops=False)
                self.moveItemsLinearly(items, toCoords, sleepTime=sleepTime)
                if stopped:
                    self.stopAnimations()
            except UserStop:
                pass
        else:
            for item, coords in zip(items, toCoords):
                self.canvas.coords(item, coords)
                    
    def cleanUp(self,   # Customize cleanup to restore link positions
                callEnvironment=None, **kwargs):
        super().cleanUp(callEnvironment, **kwargs)
        if len(self.callStack) == 0:
            self.restorePositions(sleepTime=0)

    findCode = """
def find(self, goal={goal!r}, key=identity):
   link = self.getFirst()
   while link is not None:
      if key(link.getData()) == goal:
         return link
      link = link.getNext()
"""

    def find(self, goal, code=findCode):
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))
        wait = 0.1

        callEnviron.add(self.canvas.create_text(
            *self.outputLabelCoords(), text='goal = {}'.format(goal), 
            anchor=W, font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR))

        self.highlightCode('link = self.getFirst()', callEnviron)
        link = 1
        linkIndex = self.createIndex(link, 'link')
        callEnviron |= set(linkIndex)
        self.wait(wait)

        self.highlightCode('link is not None', callEnviron, wait=wait)

        while link <= len(self.list):
            self.highlightCode('key(link.getData()) == goal', callEnviron,
                               wait=wait)

            if self.list[link - 1].key == goal:
                self.highlightCode('return link', callEnviron, wait=wait)
                self.cleanUp(callEnviron)
                return link

            # Advance to next Link
            self.highlightCode('link = link.getNext()', callEnviron)
            link += 1
            self.moveItemsTo(
                linkIndex, 
                (self.indexCoords(link), self.indexLabelCoords(link)),
                sleepTime=wait / 10)

            self.highlightCode('link is not None', callEnviron, wait=wait)
            
        # Failed to find goal key
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        
    searchCode = """
def search(self, goal={goal!r}, key=identity):
   link = self.find(goal, key)
   if link is not None:
      return link.getData()
"""

    def search(self, goal, code=searchCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        wait = 0.1

        self.highlightCode('link = self.find(goal, key)', callEnviron)
        link = self.find(goal)
        
        linkIndex = self.createIndex(
            len(self.list) + 1 if link is None else link, 'link')
        callEnviron |= set(linkIndex)
        goalText = self.canvas.create_text(
            *self.outputLabelCoords(), text='goal = {}'.format(goal), 
            anchor=W, font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(goalText)

        self.highlightCode('link is not None', callEnviron, wait=wait)
        if link is not None:
            callEnviron.add(self.createFoundHighlight(link))
            self.highlightCode('return link.getData()', callEnviron)
            self.canvas.delete(goalText)
            callEnviron.discard(goalText)
            self.outputData(link, callEnviron)
        else:
            self.highlightCode([], callEnviron)

        self.cleanUp(callEnviron)
        return goal if link else None
            
    def createFoundHighlight(self, pos): # Highlight the Link cell at pos
        bbox = self.cellCoords(pos)
        return self.canvas.create_rectangle(
            *bbox, fill='', outline=self.FOUND_COLOR, width=4,
            tags='found item')
    
    ### BUTTON FUNCTIONS##
    def clickSearch(self):
        val = self.getArgument()
        result = self.search(val, start=self.startMode())
        if result != None:
            msg = "Found {}!".format(val)
        else:
            msg = "Item {} not found".format(val)
        self.setMessage(msg)
        self.clearArgument()
    
    def clickInsert(self):
        val = self.getArgument()
        if len(self) >= self.MAX_SIZE:
            self.setMessage("Error! Linked List is already full.")
            self.clearArgument()
        else:  
            self.insert(val, start=self.startMode())

    def clickDelete(self):
        empty = self.first is None  # check whether linked list is empty or not
        val = self.getArgument()
        result = self.delete(val, start=self.startMode())
        self.setMessage(
            'Error! Linked list is empty' if empty else
            '{} deleted'.format(val) if result else
            'Item {} not found'.format(val))
        if result:
            self.clearArgument()        
        
    def clickDeleteFirst(self):
        result = self.deleteFirst(start=self.startMode())
        self.setMessage('Error! Queue is empty' if result is None else
                        'Deleted {}'.format(result))
        
    def clickNewLinkedList(self):
        self.newLinkedList()
    
    def clickGetFirst(self):
        first = self.firstData(start=self.startMode())
        self.setMessage('Error! Queue is empty' if first is None else
                        "The first link's data is {}".format(first))

    def clickTraverse(self):
        self.traverse(start=self.startMode())
    
    def makeButtons(self):
        vcmd = (self.window.register(self.validate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Insert item at front of list')
        searchButton = self.addOperation(
            "Search", lambda: self.clickSearch(), numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Search for item in list')
        deleteButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Delete item from list')
        newLinkedListButton = self.addOperation(
            "New", lambda: self.clickNewLinkedList(), 
            helpText='Create new, empty list')
        deleteFirstButton = self.addOperation(
            "Delete First", lambda: self.clickDeleteFirst(), 
            helpText='Delete first item from list')
        getFirstButton = self.addOperation(
            "Get First", lambda: self.clickGetFirst(), 
            helpText='Get copy of first item from list')
        traverseButton = self.addOperation(
            "Traverse", lambda: self.clickTraverse(), 
            helpText='Traverse items in list')
        self.addAnimationButtons()
    
        return [searchButton, self.insertButton, deleteButton,
                deleteFirstButton, newLinkedListButton, getFirstButton,
                traverseButton]
            
    ##allow letters or numbers to be typed in                  
    def validate(self, action, index, value_if_allowed,
                 prior_value, text, validation_type, trigger_type, widget_name):
        return len(value_if_allowed)<= self.maxArgWidth
   
if __name__ == '__main__':
    ll = LinkedList()
    try:
        for arg in sys.argv[1:]:
            if len(arg) > ll.maxArgWidth: arg = arg[:ll.maxArgWidth]
            ll.insert(arg)
    except UserStop:
        pass
    ll.cleanUp()
    ll.runVisualization()
