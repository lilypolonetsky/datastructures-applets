import random
from tkinter import *
try:
    from drawnValue import *
    from VisualizationApp import *
    from SortingBase import *    
except ModuleNotFoundError:
    from .drawnValue import *
    from .VisualizationApp import *
    from .SortingBase import *    
      

class AdvancedArraySort(SortingBase):

    def __init__(self, title="Advanced Sorting", **kwargs):
        super().__init__(title=title, **kwargs)

        for i in range(self.size):
            self.list.append(drawnValue(random.randrange(self.valMax)))
        self.display()
        
        self.buttons = self.makeButtons()

    def fixGaps(self, toX=SortingBase.ARRAY_X0, toY=SortingBase.ARRAY_Y0):
        done = [False] * len(self.list)
        doneCount = 0
        while doneCount < len(self.list):
            for i in range(len(self.list)):
                # move the done elements up by dy and corresponding dx
                if not done[i]:
                    dx=0
                    dy=0
                    coords = self.canvas.coords(self.list[i].items[0])
                    curX, curY = coords[:2]

                    # calculate dx based on if the cell is to the right or to
                    # the left of its desired position
                    if curX < toX + self.CELL_SIZE*i:
                        dx = 0.5 if curX % 1 == 0 else toX + self.CELL_SIZE*i - curX
                    elif curX > toX + self.CELL_SIZE*i:
                        dx = -0.5 if curX % 1 == 0 else toX + self.CELL_SIZE*i - curX
                    # do the same for dy
                    if curY < toY:
                        dy = 0.5 if curY % 1 == 0 else toY - curY
                    elif curY > toY:
                        dy = -0.5 if curY % 1 == 0 else toY - curY
                    # if dx or dy are not zero, the cell isn't in position and still needs to be moved
                    if dx or dy:
                        self.moveItemsBy(self.list[i].items, (dx, dy))

                    # when the cell is in the correct position, mark it as done
                    else:
                        doneCount += 1
                        done[i] = True
            self.wait(0.01)
    
    # SORTING METHODS 

    def drawPartition(self, left, right):
        bottom = self.canvas.create_line(self.ARRAY_X0 + self.CELL_WIDTH*left, self.ARRAY_Y0 + self.CELL_SIZE + 90,
                           self.ARRAY_X0 + self.CELL_WIDTH*(right+1), self.ARRAY_Y0 + self.CELL_SIZE + 90, fill="red")
        l = self.canvas.create_line(self.ARRAY_X0 + self.CELL_WIDTH*left, self.ARRAY_Y0 + self.CELL_SIZE + 80,
                           self.ARRAY_X0 + self.CELL_WIDTH * left, self.ARRAY_Y0 + self.CELL_SIZE + 90, fill="red")
        r = self.canvas.create_line(self.ARRAY_X0 + self.CELL_WIDTH * (right+1), self.ARRAY_Y0 + self.CELL_SIZE + 80,
                           self.ARRAY_X0 + self.CELL_WIDTH * (right+1), self.ARRAY_Y0 + self.CELL_SIZE + 90, fill="red")

        return bottom, l, r  
            
    def medianOfThree(self, left, right):
        a = self.list

        b = random.randint(left, right)
        c = random.randint(left, right)
        d = random.randint(left, right)
        
        dVal = a[d].val
        bVal = a[b].val
        cVal = a[c].val

        if (dVal < bVal and bVal < cVal) or (cVal < bVal and bVal < dVal):
            median = b
        elif (bVal < dVal and dVal < cVal) or (cVal < dVal and dVal < bVal):
            median = d
        else:
            median = c
            
        #a[median], a[right] = a[right], a[median]
        self.swap(median, right)    
    
    def partitionIt(self, left, right):
        callEnviron = self.createCallEnvironment()
    
        x = self.ARRAY_X0 + (self.CELL_SIZE / 2)
        y0 = self.ARRAY_Y0 - 15
        y1 = self.ARRAY_Y0 - 40

        b, l, r = self.drawPartition(left, right)

        self.medianOfThree(left, right)
        a = self.list
        pivot = a[right]
        done = left
        
        doneArrow = self.createIndex(done, name="done", level=2)
        pivotArrow = self.createIndex(right, name="pivot", level=3)

        pivotCellObjects = []
        pivotCellObjects.append(pivotArrow)

        doneCellObjects = []
        doneCellObjects.append(doneArrow)
        
        curArrow = self.createIndex(left, name="cur")
        
        callEnviron |= set(doneArrow)
        callEnviron |= set(pivotArrow)
        callEnviron |= set(curArrow)
        callEnviron |= set((b, l, r))
        
        # for each position except for the pivot position
        for cur in range(left, right):
            # if the value at that position is smaller than the pivot
            # swap it so it becomes the next value of the done part
            if a[cur].val <= pivot.val:
                #a[done], a[cur] = a[cur], a[done]
                self.swap(done, cur)
                done += 1                
                self.moveItemsBy(doneArrow, (self.CELL_WIDTH, 0), sleepTime=0.02)

            self.wait(0.2)

            self.moveItemsBy(curArrow, (self.CELL_WIDTH, 0), sleepTime=0.02)

        # Move the pivot into the correct place
        #a[done], a[right] = a[right], a[done]
        self.swap(done, right, aCellObjects=doneCellObjects, bCellObjects=pivotCellObjects)
        
        self.cleanUp(callEnviron)

        # At this point, done is the location where the pivot value got placed
        self.wait(0.1)
        return done
    
    # Wrapper method 
    def quickSort(self):
        # Start animation
        self.startAnimations()
        callEnviron = self.createCallEnvironment()
        
        self.__quickSort(callEnviron)
        
        # Finish animation
        self.cleanUp()
    
    def __quickSort(self, callEnviron, left=-1, right=-1):
        # initialize things if method was called without args
        if left == -1:
            left = 0
            right = len(self.list) - 1

        # there has to be at least two elements
        if left < right:
            partition = self.partitionIt(left, right)
            self.__quickSort(callEnviron, left, partition - 1)
            self.__quickSort(callEnviron, partition + 1, right)    

    shellSortCode = """
def shellSort(self):
    h = 1
    while h * 3 < len(self):
        h = 3 * h + 1
    nShifts = 0
    while h > 0:
        for outer in range(h, len(self)):
            temp = self.get(outer)
            inner = outer
            while inner >= h and temp < self.get(inner-h):
                self.set(inner, self.get(inner-h))
                inner -= h
                nShifts += 1
            if inner < outer:
                self.set(inner, temp)
                nShifts += 1
        h = (h - 1) // 3
    return nShifts
    """

    def shellSort(self):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        # calculate h
        h = 1
        while h * 3 < len(self.list):
            h = 3 * h + 1
        hPos = (self.ARRAY_X0 // 2, self.ARRAY_Y0-40)
        hText = "h: {}".format(h)
        hLabel = self.canvas.create_text(
                *hPos, text=hText, font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
        callEnviron.add(hLabel)

        nShifts = 0
        while h > 0:
            outerArrow = self.createIndex(h, name="outer", level=3)
            callEnviron |= set(outerArrow)
            
            for outer in range(h, len(self.list)):
                # move outer index
                arrowPos = self.indexCoords(outer, level=3)
                self.moveItemsTo(outerArrow, (arrowPos, arrowPos[:2]), sleepTime=.02)

                # assign outer to temp
                temp = self.list[outer].val
                tempVal, label = self.assignToTemp(outer, callEnviron, varName="temp")
                callEnviron.add(label)
                tempAssigned = False

                # create the inner index
                inner = outer
                innerArrow = self.createIndex(inner, name="inner", level=2)
                callEnviron |= set(innerArrow)
                self.wait(0.2)

                # after temp is done being used, remove any number that is hidden behind another
                toBeRemoved = []

                while inner >= h and temp < self.list[inner-h].val:
                    toBeRemoved += self.list[inner-h].items
                    self.assignElement(inner-h, inner, callEnviron, sleepTime=0.05, startAngle=90 * 11 / (10 + abs(inner-h)))

                    # move the inner index
                    inner -= h
                    arrowPos = self.indexCoords(inner, level=2)
                    self.moveItemsTo(innerArrow, (arrowPos, arrowPos[:2]), sleepTime=.02)
                    self.wait(0.2)

                    nShifts += 1

                if inner < outer:
                    self.assignFromTemp(inner, tempVal, None, delete=False)
                    
                    # remove any number that is hidden behind another
                    for item in toBeRemoved:
                        if item is not None:
                            self.canvas.delete(item)

                    # Take it out of the cleanup set since it should persist
                    callEnviron -= set(tempVal.items)
                    tempAssigned = True
                    nShifts += 1
                # finished with outer as temp
                callEnviron.remove(label)
                self.canvas.delete(label)
                if not tempAssigned:
                    for item in tempVal.items:
                        if item is not None:
                            self.canvas.delete(item)
                # finished with inner index
                callEnviron ^= set(innerArrow)       
                self.canvas.delete(innerArrow[0])
                self.canvas.delete(innerArrow[1])   
                for item in toBeRemoved:
                        self.canvas.delete(item)   
            
            # change h
            h = (h - 1) // 3
            self.canvas.itemconfig(hLabel, text="h: {}".format(h))

            # remove outer arrow
            callEnviron ^= set(outerArrow)
            self.canvas.delete(outerArrow[0])
            self.canvas.delete(outerArrow[1])
        
        self.cleanUp(callEnviron)
        return nShifts

    def makeButtons(self, maxRows=3):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows,
            argHelpText=['item key'], helpText='Insert item in array')
        searchButton = self.addOperation(
            "Search", lambda: self.clickSearch(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows,
            argHelpText=['item key'], helpText='Search for item in array')
        deleteButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows,
            argHelpText=['item key'], helpText='Delete array item')
        newButton = self.addOperation(
            "New", lambda: self.clickNew(), numArguments=1,
            validationCmd=vcmd, maxRows=maxRows, 
            argHelpText=['number of cells'],
            helpText='Create new empty array')
        randomFillButton = self.addOperation(
            "Random Fill", lambda: self.randomFill(), maxRows=maxRows,
            helpText='Fill all array cells with random keys')
        shuffleButton = self.addOperation(
            "Shuffle", lambda: self.shuffle(), maxRows=maxRows,
            helpText='Shuffle position of all items')
        deleteRightmostButton = self.addOperation(
            "Delete Rightmost", lambda: self.deleteLast(), maxRows=maxRows,
            helpText='Delete last array item')
        quicksortButton = self.addOperation(
            "Quicksort", lambda: self.quickSort(), maxRows=maxRows,
            helpText='Sort items using quicksort algorithm')
        shellSortButton = self.addOperation(
            "Shellsort", lambda: self.shellSort(), maxRows=maxRows,
            helpText='Sort items using shellsort algorithm')
        self.addAnimationButtons(maxRows=maxRows)
        buttons = [insertButton, searchButton, deleteButton, newButton, 
                   randomFillButton, shuffleButton, deleteRightmostButton,
                   quicksortButton]
        return buttons  # Buttons managed by play/pause/stop controls
        
if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    array = AdvancedArraySort()

    array.runVisualization()
