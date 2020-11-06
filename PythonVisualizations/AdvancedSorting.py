import random
import time
from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
    from SortingBase import *    
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *
    from .SortingBase import *    
      

class AdvancedArraySort(SortingBase):

    def __init__(self, title="Advanced Sorting", size=10, **kwargs):
        super().__init__(title=title, **kwargs)

        for i in range(size):
            self.list.append(drawable(random.randrange(99)))
        
        self.buttons = self.makeButtons() 
    
    # ARRAY FUNCTIONALITY     
    def delete(self, val):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()

        # draw an index for variable j pointing to the first cell
        indexDisplay = self.createIndex(0, 'j')
        callEnviron |= set(indexDisplay)
        
        # go through each Drawable in the list
        # look for val to be deleted
        for i in range(len(self.list)):
            n = self.list[i]

            if n.val == val:
                # get the position of the displayed cell
                cellShape = self.cellCoords(i)

                # Highlight the found element with a circle
                foundCircle = self.canvas.create_oval(
                    *add_vector(
                        cellShape,
                        multiply_vector((1, 1, -1, -1), self.CELL_BORDER)),
                    outline=self.FOUND_COLOR)
                callEnviron.add(foundCircle)

                # update the display
                self.wait(0.3)

                # remove the found circle
                callEnviron.remove(foundCircle)
                self.canvas.delete(foundCircle)

                # Slide value rectangle up and off screen
                items = (n.display_shape, n.display_val) if not self.changeSize else (n.display_shape,)
                self.moveItemsOffCanvas(items, N, sleepTime=0.02)                

                # Create an index for shifting the cells
                kIndex = self.createIndex(i, 'k')
                callEnviron |= set(kIndex)
            
                # Slide values from right to left to fill gap
                for j in range(i+1, len(self.list)):
                    self.assignElement(j, j - 1, callEnviron)
                    self.fixCells() # retain the correct shape
                    self.moveItemsBy(kIndex, (self.CELL_WIDTH, 0), sleepTime=0.01)
                    self.wait(0.1)

                # remove the last item in the list
                n = self.list.pop()
                # delete the associated display objects
                self.canvas.delete(n.display_shape)
                self.canvas.delete(n.display_val)
                
                # update window
                self.wait(0.3)

                self.cleanUp(callEnviron)
                return True

            # if not found, then move the index over one cell
            self.moveItemsBy(indexDisplay, (self.CELL_WIDTH, 0), sleepTime=0.01)
            if self.wait(0.1):
                break

        # Animation stops
        self.cleanUp(callEnviron)
        return None
        
    # SORTING METHODS 
    def split(self, index, start=0, end=-1):
        global running
        if end == -1: end = len(self.list) - 1
        # get the y coordinates of the next level down
        toY = canvas.coords(self.list[start].display_shape)[1] + CELL_SIZE + 15
        xspeed = -0.5
        yspeed = 2
        # while the cells have not been moved to the new y-coord,
        while (canvas.coords(self.list[start].display_shape)[1]) < toY:
            for i in range(start, end + 1):
                # if they are to the right (inclusive) of the split index, move them down and right
                if i <= index:
                    canvas.move(self.list[i].display_shape, xspeed, yspeed)
                    canvas.move(self.list[i].display_val, xspeed, yspeed)
                # if they ar eto the left of the split index, move them down and left
                else:
                    canvas.move(self.list[i].display_shape, -xspeed, yspeed)
                    canvas.move(self.list[i].display_val, -xspeed, yspeed)
            window.update()
            time.sleep(self.speed(0.01))
            if not running:
                return
    def merge(self, startA, startB, endB):
        global running
        # endA and endB are inclusive
        endA = startB - 1
        # create a list to hold the merged lists
        temp = [None] * (endB - startA + 1)
        curTemp = 0
        curA, curB = startA, startB
        dy = -2
        # calculate the toY position - if the sublists are on equal levels, then merge them upwards
        # to the next level up. if the sublists are on different levels, move the lower on up to the
        # level of the higher one.
        if canvas.coords(self.list[startA].display_shape)[1] > canvas.coords(self.list[startB].display_shape)[1]:
            toY = canvas.coords(self.list[startA].display_shape)[1]
        elif canvas.coords(self.list[startA].display_shape)[1] < canvas.coords(self.list[startB].display_shape)[1]:
            toY = canvas.coords(self.list[startB].display_shape)[1]
        else:
            toY = canvas.coords(self.list[startA].display_shape)[1] - CELL_SIZE - 15
        # calculate the desired toX position
        toX = canvas.coords(self.list[startA].display_shape)[0] - (-0.5 / -dy) * (
        CELL_SIZE + 15)  # -1 is the current dx in split
        curDisplayShape = None
        curDisplayVal = None
        # while you haven't gotten to the end of either sublist, select the smaller element from the front
        # of the two sublists and copy it to the next open position in the temp list
        while curA <= endA and curB <= endB:
            if self.list[curA].val <= self.list[curB].val:
                temp[curTemp] = self.list[curA]
                curDisplayShape = self.list[curA].display_shape
                curDisplayVal = self.list[curA].display_val
                curA += 1
            else:
                temp[curTemp] = self.list[curB]
                curDisplayShape = self.list[curB].display_shape
                curDisplayVal = self.list[curB].display_val
                curB += 1
            # move the selected element up to the level of the merged lists
            self.moveUp(dy, toX, toY, curDisplayShape, curDisplayVal)
            curTemp += 1
            toX += CELL_SIZE
            if not running:
                return
        # add on the remainder of the unfinished list to the merged list
        while curA <= endA:
            temp[curTemp] = self.list[curA]
            curDisplayShape = self.list[curA].display_shape
            curDisplayVal = self.list[curA].display_val
            curA += 1
            self.moveUp(dy, toX, toY, curDisplayShape, curDisplayVal)
            curTemp += 1
            toX += CELL_SIZE
            if not running:
                return
        while curB <= endB:
            temp[curTemp] = self.list[curB]
            curDisplayShape = self.list[curB].display_shape
            curDisplayVal = self.list[curB].display_val
            curB += 1
            self.moveUp(dy, toX, toY, curDisplayShape, curDisplayVal)
            curTemp += 1
            toX += CELL_SIZE
            if not running:
                return
        # copy the merged sublist into the real list
        curTemp = 0
        for i in range(startA, endB + 1):
            self.list[i] = temp[curTemp]
            curTemp += 1
        # garbage collection
        temp = None
    def mergeSort(self):
        global running
        running = True
        self.__mergeSort()
        self.fixGaps()
    def __mergeSort(self, l=0, r=-1):
        global running
        if not running:
            self.stopMergeSort()
            return
        if r == -1: r = len(self.list) - 1
        if l < r:
            # Same as (l+r)/2, but avoids overflow for
            # large l and h
            m = (l + r) // 2
            # Sort first and second halves
            self.split(m, l, r)
            self.__mergeSort(l, m)
            self.__mergeSort(m + 1, r)
            self.merge(l, m + 1, r)
            if not running:
                self.stopMergeSort()
                return

    def fixGaps(self, toX=SortingBase.ARRAY_X0, toY=SortingBase.ARRAY_Y0):
        done = [False] * len(self.list)
        doneCount = 0
        while doneCount < len(self.list):
            for i in range(len(self.list)):
                # move the done elements up by dy and corresponding dx
                if not done[i]:
                    dx=0
                    dy=0
                    curX = canvas.coords(self.list[i].display_shape)[0]
                    curY = canvas.coords(self.list[i].display_shape)[1]
                    # calculate dx based on if the cell is to the right or to the
                    # left of its desired position
                    if curX < toX + CELL_SIZE*i:
                        dx = 0.5 if curX % 1 == 0 else toX + CELL_SIZE*i - curX
                    elif curX > toX + CELL_SIZE*i:
                        dx = -0.5 if curX % 1 == 0 else toX + CELL_SIZE*i - curX
                    # do the same for dy
                    if curY < toY:
                        dy = 0.5 if curY % 1 == 0 else toY - curY
                    elif curY > toY:
                        dy = -0.5 if curY % 1 == 0 else toY - curY
                    # if dx or dy are not zero, the cell isn't in position and still needs to be moved
                    if dx or dy:
                        canvas.move(self.list[i].display_shape, dx, dy)
                        canvas.move(self.list[i].display_val, dx, dy)
                    # when the cell is in the correct position, mark it as done
                    else:
                        doneCount += 1
                        done[i] = True
            window.update()    

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
   
    def makeButtons(self):
        # get the common buttons from makeButtons() in SortingBase
        buttons, vcmd = super().makeButtons()
        quickSortButton = self.addOperation(
            "Quick Sort", lambda: self.quickSort())
        randomFillButton = self.addOperation(
            "Random Fill", lambda: self.randomFill())
        newButton = self.addOperation(
            "New", lambda: self.clickNew(), numArguments=1,
            validationCmd=vcmd)
        deleteButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1,
            validationCmd=vcmd) 
        self.addAnimationButtons()
        buttons += [quickSortButton, randomFillButton, newButton, deleteButton]
        return buttons  # Buttons managed by play/pause/stop controls
        
    def clickNew(self):
        val = self.validArgument()
        # Capture what was returned by new() for the given val 
        created = self.new(val) if val is not None else False
        if created:
            self.clearArgument()        
    
    def clickDelete(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99")
        else:
            result = self.delete(val)
            if result:
                msg = "Value {} deleted".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()    
 
if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    array = AdvancedArraySort()

    array.runVisualization()
