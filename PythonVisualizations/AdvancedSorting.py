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
        self.ARRAY_Y0 = 75

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

    def shellSort(self, code=shellSortCode):
        wait = 0.1
        moveWait = wait / 10
        descend = (0, 16) * 2
        callEnviron = self.createCallEnvironment(code=code)
        self.startAnimations()

        # calculate h
        h = 1
        hLabel = None
        hLabel = self.adjustHLabel(h, 0, None)
        callEnviron |= set(hLabel)
        self.highlightCode('h = 1', callEnviron, wait=wait)
        
        self.highlightCode('h * 3 < len(self)', callEnviron, wait=wait)
        while h * 3 < len(self.list):
            self.highlightCode('h = 3 * h + 1', callEnviron)
            h = 3 * h + 1
            self.adjustHLabel(h, 0, hLabel)
            
            self.highlightCode('h * 3 < len(self)', callEnviron, wait=wait)
            
        nShifts = 0
        nShiftsPos = (10, self.ARRAY_Y0 // 3)
        nShiftsValue = "nShifts: {}"
        nShiftsLabel = self.canvas.create_text(
            *nShiftsPos, anchor=W, text=nShiftsValue.format(nShifts),
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        callEnviron.add(nShiftsLabel)
        self.highlightCode('nShifts = 0', callEnviron, wait=wait)

        tempLabel, outerArrow, innerArrow = None, None, None
        toRestore = []
        self.highlightCode('h > 0', callEnviron, wait=wait)
        while h > 0:
            if outerArrow is None:
                outerArrow = self.createIndex(h, name="outer", level=-2)
                callEnviron |= set(outerArrow)
            
            self.highlightCode('outer in range(h, len(self))', callEnviron,
                               wait=wait)
            for outer in range(h, len(self.list)):
                # move outer index
                arrowPos = self.indexCoords(outer, level=-2)
                outerCoords = self.canvas.coords(outerArrow[0])
                if outerCoords != arrowPos:
                    self.moveItemsTo(outerArrow, (arrowPos, arrowPos[:2]), 
                                     sleepTime=moveWait)
                    self.adjustHLabel(h, outer - h, hLabel)

                # Move cells being worked down
                toMove = [j for j in range(outer if h > 1 else -1, -1, -h)]
                itemsToMove = list(flat(*[
                    self.list[j].items + (self.arrayCells[j],) for j in toMove]))
                toMoveCoords = [add_vector(self.canvas.coords(i), descend)
                                for i in itemsToMove]
                itemsToRestore = list(flat(*[
                    self.list[j].items + (self.arrayCells[j],) for j in toRestore]))
                toRestoreCoords = list(flat(*[
                    [self.fillCoords(self.list[j].val, self.cellCoords(j))] +
                    ([self.cellCenter(j)] if len(self.list[j].items) > 1 
                     else []) +
                    [self.arrayCellCoords(j)] for j in toRestore]))
                if len(itemsToMove + itemsToRestore) > 0:
                    self.moveItemsTo(
                        itemsToMove + itemsToRestore, 
                        toMoveCoords + toRestoreCoords, sleepTime=moveWait)
                toRestore = toMove
                
                # assign outer to temp
                self.highlightCode('temp = self.get(outer)', callEnviron)
                temp = self.list[outer]
                tempVal, tempLabel = self.assignToTemp(
                    outer, callEnviron, varName="temp", existing=tempLabel)
                callEnviron |= set(tempVal.items + (tempLabel,))

                # create the inner index
                inner = outer
                if innerArrow is None:
                    innerArrow = self.createIndex(inner, name="inner", level=-1)
                    callEnviron |= set(innerArrow)
                    self.highlightCode('inner = outer', callEnviron, wait=wait)
                else:
                    arrowPos = self.indexCoords(inner, level=-1)
                    self.moveItemsTo(innerArrow, (arrowPos, arrowPos[:2]),
                                     sleepTime=moveWait)

                self.highlightCode('inner >= h', callEnviron, wait=wait)
                if inner >= h:
                    self.highlightCode('temp < self.get(inner-h)', callEnviron,
                                       wait=wait)
                    
                while inner >= h and tempVal.val < self.list[inner-h].val:
                    self.highlightCode('self.set(inner, self.get(inner-h))',
                                       callEnviron)
                    self.assignElement(
                        inner-h, inner, callEnviron, sleepTime=moveWait,
                        startAngle=90 * 11 / (10 + abs(inner-h)))

                    # move the inner index
                    self.highlightCode('inner -= h', callEnviron)
                    inner -= h
                    arrowPos = self.indexCoords(inner, level=-1)
                    self.moveItemsTo(innerArrow, (arrowPos, arrowPos[:2]),
                                     sleepTime=moveWait)

                    nShifts += 1
                    self.canvas.itemconfigure(
                        nShiftsLabel, text=nShiftsValue.format(nShifts))
                    self.highlightCode('nShifts += 1', callEnviron, wait=wait)
                    
                    self.highlightCode('inner >= h', callEnviron, wait=wait)
                    if inner >= h:
                        self.highlightCode('temp < self.get(inner-h)',
                                           callEnviron, wait=wait)

                self.highlightCode('inner < outer', callEnviron, wait=wait)
                if inner < outer:
                    self.highlightCode('self.set(inner, temp)', callEnviron)
                    self.assignFromTemp(inner, tempVal, tempLabel, delete=False,
                                        sleepTime=moveWait)
                    
                    # Take temp out of the cleanup set since it should persist
                    callEnviron -= set(tempVal.items)

                    nShifts += 1
                    self.canvas.itemconfigure(
                        nShiftsLabel, text=nShiftsValue.format(nShifts))
                    self.highlightCode('nShifts += 1', callEnviron, wait=wait)
                    
                    self.highlightCode('outer in range(h, len(self))',
                                       callEnviron)
                else:
                    for item in tempVal.items:
                        self.canvas.delete(item)
                    
            # change h
            self.highlightCode('h = (h - 1) // 3', callEnviron)
            h = (h - 1) // 3
            self.adjustHLabel(h, 0, hLabel)
            
            self.highlightCode('h > 0', callEnviron, wait=wait)
        
        self.highlightCode('return nShifts', callEnviron, wait=wait)
        self.cleanUp(callEnviron)
        return nShifts

    def adjustHLabel(
            self, h, leftCell, hLabel, steps=10, sleepTime=0.01, font=None,
            color=None):
        'Adjust or make the h span label'
        if font is None:
            font = self.VARIABLE_FONT
        leftCenter = self.cellCenter(leftCell)[0]
        spanCoords = self.hSpanCoords(h, leftCenter)
        spanCenter = ((spanCoords[0] + spanCoords[-2]) // 2, spanCoords[5])
        textPattern = "h: {}"
        hText = textPattern.format(h)
        textWidth = self.textWidth(font, hText)
        boxCoords = (spanCenter[0] - textWidth / 2 - 1, spanCoords[1],
                     spanCenter[0] + textWidth / 2 + 1, spanCoords[3])
        if hLabel:  # Adjust existing hLabel: (span, box, text)
            currentCoords = self.canvas.coords(hLabel[0])
            currentText = self.canvas.itemconfigure(hLabel[2], 'text')[-1]
            startH = int(currentText[3:]) if currentText != hText else h
            if currentCoords != spanCoords or currentText != hText:
                for step in range(steps):
                    sCoords = divide_vector(
                        add_vector(multiply_vector(currentCoords,
                                                   steps - 1 - step),
                                   multiply_vector(spanCoords, step + 1)),
                        steps)
                    sCenter = ((sCoords[0] + sCoords[-2]) // 2, sCoords[5])
                    if startH != h:
                        text = 'h: {:3.1f}'.format(
                            (startH * (steps - 1 - step) + h * (step + 1)) /
                            steps)
                        textWidth = self.textWidth(font, text)
                    bCoords = (sCenter[0] - textWidth / 2 - 1, sCoords[1],
                               sCenter[0] + textWidth / 2 + 1, sCoords[3])
                    for i, coords in zip(hLabel, (sCoords, bCoords, sCenter)):
                        self.canvas.coords(i, *coords)
                    if startH != h:
                        self.canvas.itemconfigure(hLabel[2], text=text)
                    self.wait(sleepTime)
                    
                for i, coords in zip(hLabel, 
                                     (spanCoords, boxCoords, spanCenter)):
                    self.canvas.coords(i, *coords)
                self.canvas.itemconfigure(hLabel[2], text=hText)
                        
        else: # Create new hLabel
            if color is None:
                color = self.VARIABLE_COLOR
            span = self.canvas.create_line(*spanCoords, fill=color)
            box = self.canvas.create_rectangle(*boxCoords,
                fill=self.DEFAULT_BG, width=0, outline='')
            text = self.canvas.create_text(
                *spanCenter, text=hText, font=font, fill=color)
            hLabel = (span, box, text)
        return hLabel   # Return created or adjusted canvas items
                
    def hSpanCoords(self, h, leftCenter):
        width = h * self.CELL_WIDTH
        height = 18
        _, y0, x, y = self.indexCoords(0, level=1)
        x0, x1 = leftCenter, leftCenter + width
        return (x0, y0 - height // 2, x0, y0 + height // 2,
                x0, y0, x1, y0,
                x1, y0 - height // 2, x1, y0 + height // 2)
    
    def makeButtons(self, maxRows=4):
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
        increasingFillButton = self.addOperation(
            "Increasing Fill", lambda: self.linearFill(), maxRows=maxRows,
            helpText='Fill all array cells with increasing keys')
        decreasingFillButton = self.addOperation(
            "Decreasing Fill", lambda: self.linearFill(False), maxRows=maxRows,
            helpText='Fill all array cells with decreasing keys')
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
                   randomFillButton, decreasingFillButton, increasingFillButton,
                   shuffleButton, deleteRightmostButton,
                   quicksortButton, shellSortButton]
        return buttons  # Buttons managed by play/pause/stop controls
        
if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    array = AdvancedArraySort()

    array.runVisualization()
