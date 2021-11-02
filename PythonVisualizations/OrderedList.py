from tkinter import *

try:
    from drawnValue import *
    from coordinates import *
    from LinkedList import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .coordinates import *
    from .LinkedList import *
    from .VisualizationApp import *

V = vector

class OrderedList(LinkedList):
    
    def __init__(self, title="Ordered List", **kwargs):
        super().__init__(title=title, **kwargs)

    # Creates the LinkedList objeect that is the head of the list
    def linkedListNode(self):
        x, y = self.x_y_offset(0)
        rect = self.canvas.create_rectangle(
            x + self.CELL_WIDTH * 2 // 3, y,
            x + self.CELL_WIDTH, y + self.CELL_HEIGHT,
            fill=self.SORTED_BACKGROUND, tags=("LinkedList", "cell"))
        oval = self.createDot(0, 'LinkedList')
        ovalCoords = self.canvas.coords(oval)
        firstText = self.canvas.create_text(
            (ovalCoords[0] + ovalCoords[2]) / 2, (y + ovalCoords[1]) / 2,
            text="first", font=('Courier', -10))
        nameText = self.canvas.create_text(
            x, y + self.CELL_HEIGHT // 2, font=('Courier', -14),
            text='OrderedList')
        
    ### ANIMATION METHODS###
            
    newLinkedListCode = """
def __init__(self, key=identity):
   self.__first = None
   self.__key = key
"""

    # Erases old linked list and draws empty list
    def newLinkedList(self, code=newLinkedListCode):
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=False)
        wait = 0.1
        self.startAnimations(enableStops=False)
        self.highlightCode('self.__first = None', callEnviron, wait=wait)
        self.first = None
        self.list = []
        self.display()

        self.highlightCode('self.__key = key', callEnviron, wait=wait)
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        
    insertCode = '''
def insert(self, newDatum={val!r}):
   goal = self.__key(newDatum)
   previous = self
   while (previous.getNext() is not None and
          self.__key(previous.getNext().getData()) < goal):
      previous = previous.getNext()
   newLink = Link(newDatum, previous.getNext())
   previous.setNext(newLink)
'''
    
    def insert(self, val, code=insertCode, start=True):
        'Insert a new Link node in order based on its key value'
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        wait = 0.1

        previous, column = 0, -1
        self.highlightCode('goal = self.__key(newDatum)', callEnviron)
        goalText = self.canvas.create_text(
            *self.cellText(column), text='goal = {}'.format(val),
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(goalText)
        
        self.highlightCode('previous = self', callEnviron)
        previousIndex = self.createIndex(previous, 'previous')
        callEnviron |= set(previousIndex)
        self.wait(wait)

        self.highlightCode(
            'previous.getNext() is not None', callEnviron, wait=wait)
        if self.first:
            self.highlightCode(
                'self.__key(previous.getNext().getData()) < goal', callEnviron,
                wait=wait)
                       
        while previous < len(self.list) and self.list[previous].key < val:
            self.highlightCode(
                'previous = previous.getNext()', callEnviron)
            previous += 1
            column = (column - 1) % self.LEN_ROW - self.LEN_ROW
            self.moveItemsTo(
                previousIndex + (goalText,),
                (self.indexCoords(previous), self.indexLabelCoords(previous)) +
                (self.cellText(column),), sleepTime=wait/10)

            self.highlightCode(
                'previous.getNext() is not None', callEnviron, wait=wait)
            if previous < len(self.list):
                self.highlightCode(
                    'self.__key(previous.getNext().getData()) < goal',
                    callEnviron,
                    wait=wait)

        self.highlightCode(
            'newLink = Link(newDatum, previous.getNext())', callEnviron)
        self.canvas.delete(goalText)
        callEnviron.discard(goalText)
        nodeID = self.generateID()
        newNode = Node(
            val, self.first, nodeID,
            *self.createLink(
                column, val, nodeID,
                nextNode=self.list[previous] if previous < len(self.list) 
                else None))
        callEnviron |= set(newNode.items())
        newLinkIndex = self.createIndex(column, 'newLink')
        callEnviron |= set(newLinkIndex)
        self.wait(wait)

        self.highlightCode('previous.setNext(newLink)', callEnviron)
        if self.first is None or previous >= len(self.list):
            self.linkNext(previous, 0)
        insertLink = (self.first if previous == 0 else
                      self.list[previous - 1].nextPointer)
        self.moveItemsLinearly(
            insertLink, self.nextLinkCoords(previous, column - previous),
            sleepTime=wait/5)
            
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
        self.moveItemsLinearly(toMove, toCoords, sleepTime=wait/5)
        self.list[previous:previous] = [newNode]
        callEnviron -= set(newNode.items())
            
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
    
    deleteCode = """
def delete(self, goal={goal!r}):
   if self.isEmpty():
      raise Exception("Cannot delete from empty linked list")

   previous = self
   while (previous.getNext() is not None and
          self.__key(previous.getNext().getData()) < goal):
      previous = previous.getNext()
   if (previous.getNext() is None or
       goal != self.__key(previous.getNext().getData())):
      raise Exception("No datum with matching key found in list")

   toDelete = previous.getNext()
   previous.setNext(previous.getNext().getNext())
   return toDelete.getData()
"""

    # Delete a link from the linked list by finding a matching goal key
    def delete(self, goal, code=deleteCode, start=True, wait=0.1):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)

        previous, column = 0, -1
        goalText = self.canvas.create_text(
            *self.cellText(column), text='goal = {}'.format(goal), 
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
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
        previousIndex = self.createIndex(previous, 'previous')
        callEnviron |= set(previousIndex)
        self.wait(wait)

        self.highlightCode(
            'previous.getNext() is not None', callEnviron, wait=wait)
        if previous < len(self.list):
            self.highlightCode(
                'self.__key(previous.getNext().getData()) < goal', callEnviron,
                wait=wait)
            
        while previous < len(self.list) and self.list[previous].key < goal:
            
            self.highlightCode('previous = previous.getNext()', callEnviron)
            previous += 1
            column = (column - 1) % self.LEN_ROW - self.LEN_ROW
            self.moveItemsTo(
                previousIndex + (goalText, ),
                (self.indexCoords(previous), self.indexLabelCoords(previous),
                 self.cellText(column)),
                sleepTime=wait/10)
            
            self.highlightCode(
                'previous.getNext() is not None', callEnviron, wait=wait)
            if previous < len(self.list):
                self.highlightCode(
                    'self.__key(previous.getNext().getData()) < goal',
                    callEnviron, wait=wait)

        found = previous < len(self.list) and self.list[previous].key == goal
        self.highlightCode('previous.getNext() is None', callEnviron, wait=wait)
        if previous < len(self.list):
            self.highlightCode(
                'goal != self.__key(previous.getNext().getData())',
                callEnviron, wait=wait)
        if not found:
            self.highlightCode(
                'raise Exception("No datum with matching key found in list")',
                callEnviron, color=self.EXCEPTION_HIGHLIGHT, wait=wait)
            self.cleanUp(callEnviron)
            return
        
        foundHighlight = self.createFoundHighlight(previous + 1)
        callEnviron.add(foundHighlight)
        self.highlightCode('toDelete = previous.getNext()', callEnviron, 
                           wait=wait)
        toDelete = self.list[previous]
        toDeleteIndex = self.createIndex(previous + 1, 'toDelete')
        callEnviron |= set(toDeleteIndex)
        
        # Prepare to update next pointer from previous
        self.highlightCode(
            'previous.setNext(previous.getNext().getNext())', callEnviron)
        updateFirst = previous == 0
        node = self.list[previous]
        nextPointer = node.nextPointer
        toMove = (self.first if updateFirst else
                  self.list[previous - 1].nextPointer,
                  *toDeleteIndex, node.cell, node.value, foundHighlight)
        self.canvas.changeAnchor(E, toDeleteIndex[1])
        toCoords = (self.nextLinkCoords(previous, d=2 if nextPointer else 0),
                    self.indexCoords(-1), self.indexLabelCoords(-1),
                    self.cellCoords(-1), self.cellText(-1), self.cellCoords(-1))
        self.dispose(callEnviron, node.dot, node.nextPointer)
        for item in toMove:
            self.canvas.tag_raise(item)
        self.moveItemsLinearly(toMove, toCoords, sleepTime=wait / 10)
        self.dispose(callEnviron, goalText)

        if nextPointer is None:
            if updateFirst:
                self.canvas.delete(self.first)
                self.first = None
            else:
                self.canvas.delete(self.list[previous - 1].nextPointer)
                self.list[previous - 1].nextPointer = None
        self.list[previous:previous + 1] = []

        # Reposition all remaining links
        self.restorePositions()

        self.highlightCode('return toDelete.getData()', callEnviron)
        self.dispose(callEnviron, foundHighlight)
        self.outputData(node, callEnviron, copy=False)
                    
        self.cleanUp(callEnviron)
        return toDelete.key

    findCode = """
def find(self, goal={goal!r}):
   link = self.getFirst()
   while (link is not None and
          self.__key(link.getData()) < goal):
      link = link.getNext()
   return link
"""

    def find(self, goal, code=findCode):
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))
        wait = 0.1

        column = -1
        goalText = self.canvas.create_text(
            *self.cellText(column), text='goal = {}'.format(goal), 
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(goalText)

        self.highlightCode('link = self.getFirst()', callEnviron)
        link = 1
        linkIndex = self.createIndex(link, 'link')
        callEnviron |= set(linkIndex)
        self.wait(wait)

        self.highlightCode('link is not None', callEnviron, wait=wait)
        if link <= len(self.list):
            self.highlightCode(
                'self.__key(link.getData()) < goal', callEnviron, wait=wait)

        while link <= len(self.list) and self.list[link - 1].key < goal:
            # Advance to next Link
            self.highlightCode('link = link.getNext()', callEnviron)
            link += 1
            column = (column - 1) % self.LEN_ROW - self.LEN_ROW
            self.moveItemsTo(
                linkIndex + (goalText, ),
                (self.indexCoords(link), self.indexLabelCoords(link),
                 self.cellText(column)),
                sleepTime=wait/10)

            self.highlightCode('link is not None', callEnviron, wait=wait)
            if link <= len(self.list):
                self.highlightCode(
                    'self.__key(link.getData()) < goal', callEnviron, wait=wait)
            
        # Return link at or just after goal or None
        self.highlightCode('return link', callEnviron)
        self.cleanUp(callEnviron)
        return link
        
    searchCode = """
def search(self, goal={goal!r}):
   link = self.find(goal)
   if (link is not None and
       self.__key(link.getData()) == goal):
      return link.getData()
"""

    def search(self, goal, code=searchCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)
        wait = 0.1

        self.highlightCode('link = self.find(goal)', callEnviron)
        link = self.find(goal)
        
        linkIndex = self.createIndex(link, 'link')
        callEnviron |= set(linkIndex)
        goalText = self.canvas.create_text(
            *self.cellText(-1), text='goal = {}'.format(goal), 
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(goalText)

        self.highlightCode('link is not None', callEnviron, wait=wait)
        result = None
        if link <= len(self.list):
            self.highlightCode(
                'self.__key(link.getData()) == goal', callEnviron, wait=wait)
        
            if self.list[link - 1].key == goal:
                self.highlightCode('return link.getData()', callEnviron)
                callEnviron.add(self.createFoundHighlight(link))
                self.canvas.delete(goalText)
                callEnviron.discard(goalText)
                self.outputData(link, callEnviron)
                result = goal

        if result is None:
            self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        return result
    
    def makeButtons(self):
        vcmd = (self.window.register(self.validate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Insert item in ordered list')
        searchButton = self.addOperation(
            "Search", lambda: self.clickSearch(), numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Search for item in ordered list')
        deleteButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1,
            validationCmd=vcmd, argHelpText=['item'], 
            helpText='Delete item from ordered list')
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
    
        return [searchButton, insertButton, deleteButton, deleteFirstButton,
                newLinkedListButton, getFirstButton, traverseButton]
   
if __name__ == '__main__':
    ll = OrderedList()
    try:
        for arg in sys.argv[1:]:
            if len(arg) > ll.maxArgWidth: arg = arg[:ll.maxArgWidth]
            ll.insert(arg)
    except UserStop:
        pass
    ll.cleanUp()
    ll.runVisualization()
