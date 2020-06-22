import random
import time
from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

WIDTH = 800
HEIGHT = 400

CELL_SIZE = 50
ARRAY_X0 = 100
ARRAY_Y0 = 100

class Array(object):

    colors = ['red', 'green', 'blue', 'orange', 'yellow', 'cyan', 'magenta',
              'dodgerblue', 'turquoise', 'grey', 'gold', 'pink']
    nextColor = 0

    def __init__(self, size=0):
        self.list = [0]*size

    def __str__(self):
        return str(self.list)

    # ANIMATION METHODS
    def speed(self, sleepTime):
        return (sleepTime * (scaleDefault + 50)) / (scale.get() + 50)

    def assignElement(self, fromIndex, toIndex):

        # get position of "to" cell
        posToCell = canvas.coords(self.list[toIndex].display_shape)

        # get position of "from" cell and value
        posFromCell = canvas.coords(self.list[fromIndex].display_shape)
        posFromCellVal = canvas.coords(self.list[fromIndex].display_val)

        # create new display objects that are copies of the "from" cell and value
        newCellShape = canvas.create_rectangle(posFromCell[0], posFromCell[1], posFromCell[2], posFromCell[3],
                                               fill=self.list[fromIndex][1])
        newCellVal = canvas.create_text(posFromCellVal[0], posFromCellVal[1], text=self.list[fromIndex][0],
                                        font=('Helvetica', '20'))

        # set xspeed to move in the correct direction
        xspeed = 5
        if fromIndex > toIndex:
            xspeed = -xspeed

        # move the new display objects until they are in the position of the "to" cell
        while (fromIndex < toIndex and canvas.coords(newCellShape) < posToCell) or \
                (fromIndex > toIndex and canvas.coords(newCellShape) > posToCell):
            canvas.move(newCellShape, xspeed, 0)
            canvas.move(newCellVal, xspeed, 0)
            window.update()
            time.sleep(self.speed(0.01))

        # delete the original "to" display value and the new display shape
        canvas.delete(self.list[toIndex].display_val)
        canvas.delete(self.list[toIndex].display_shape)

        # update value and display value in "to" position in the list
        self.list[toIndex].display_val = newCellVal
        self.list[toIndex].val = self.list[fromIndex].val
        self.list[toIndex].display_shape = newCellShape
        self.list[toIndex].color = self.list[fromIndex].color

        # update the window
        window.update()

    def assignToTemp(self, index, varName="temp"):

        y0 = canvas.coords(self.list[index].display_shape)[1]

        posCell = canvas.coords(self.list[index].display_shape)
        posCellVal = canvas.coords(self.list[index].display_val)

        yspeed = -5
        shape = canvas.create_rectangle(posCell[0], posCell[1], posCell[2], posCell[3], fill=self.list[index][1])
        val = canvas.create_text(posCellVal[0], posCellVal[1], text=str(self.list[index][0]),
                                 font=('Helvetica', '20'))

        while canvas.coords(shape)[1] > (y0 - CELL_SIZE - 15):
            canvas.move(shape, 0, yspeed)
            canvas.move(val, 0, yspeed)
            window.update()
            time.sleep(self.speed(0.01))

        text = canvas.create_text(posCell[0] + (CELL_SIZE / 2), y0 - CELL_SIZE - 30, text=varName,
                                  font=('Helvetica', '20'))
        temp = drawable(self.list[index][0], self.list[index][1], shape, val)

        window.update()
        return temp, text

    def assignFromTemp(self, index, temp, text):

        y0 = canvas.coords(self.list[index].display_shape)[1]

        posCell = canvas.coords(self.list[index].display_shape)
        posCellVal = canvas.coords(self.list[index].display_val)

        xspeed = 5
        moveRight = True
        if canvas.coords(temp.display_shape)[0] > posCell[0]:
            xspeed = -xspeed
            moveRight = False

        while (moveRight and canvas.coords(temp.display_shape)[0] < posCell[0]) or \
                (not moveRight and canvas.coords(temp.display_shape)[0] > posCell[0]):
            canvas.move(temp.display_shape, xspeed, 0)
            canvas.move(temp.display_val, xspeed, 0)
            canvas.move(text, xspeed, 0)
            window.update()
            time.sleep(self.speed(0.01))

        time.sleep(0.1)

        yspeed = 5
        while canvas.coords(temp.display_shape)[1] < y0:
            canvas.move(temp.display_shape, 0, yspeed)
            canvas.move(temp.display_val, 0, yspeed)
            window.update()
            time.sleep(self.speed(0.01))

        time.sleep(self.speed(0.1))
        canvas.delete(text)
        canvas.delete(self.list[index].display_shape)
        canvas.delete(self.list[index].display_val)
        self.list[index] = temp

    def swap(self, a, b, aCellObjects = [], bCellObjects = []):
        y0 = canvas.coords(self.list[a].display_shape)[1]
        if a == b:
            yspeed = -5
            shapeA = self.list[a].display_shape
            while canvas.coords(shapeA)[1] != (y0 - CELL_SIZE - 15):
                canvas.move(shapeA, 0, yspeed)
                canvas.move(self.list[a].display_val, 0, yspeed)
                for o in (aCellObjects + bCellObjects):
                    canvas.move(o, 0, yspeed)
                window.update()
                time.sleep(self.speed(0.01))

            time.sleep(self.speed(0.1))

            while canvas.coords(shapeA)[1] != y0:
                canvas.move(shapeA, 0, -yspeed)
                canvas.move(self.list[a].display_val, 0, -yspeed)
                for o in (aCellObjects + bCellObjects):
                    canvas.move(o, 0, -yspeed)
                window.update()
                time.sleep(self.speed(0.01))

            return

        # save original coordinates of b cell
        posCellB = canvas.coords(self.list[b].display_shape)

        # move a and b cells up
        yspeed = -5
        shapeA = self.list[a].display_shape
        while canvas.coords(shapeA)[1] != (y0 - CELL_SIZE - 15):
            canvas.move(shapeA, 0, yspeed)
            canvas.move(self.list[a].display_val, 0, yspeed)
            canvas.move(self.list[b].display_shape, 0, yspeed)
            canvas.move(self.list[b].display_val, 0, yspeed)
            for o in (aCellObjects + bCellObjects):
                canvas.move(o, 0, yspeed)
            window.update()
            time.sleep(self.speed(0.01))

        time.sleep(self.speed(0.1))

        # make a and b cells switch places
        xspeed = 5
        if b < a:
            xspeed = -xspeed

        # move the cells until the a cell is above the original position of the b cell
        while (a < b and canvas.coords(shapeA)[0] < posCellB[0]) or \
                (a > b and canvas.coords(shapeA)[0] > posCellB[0]):
            canvas.move(shapeA, xspeed, 0)
            canvas.move(self.list[a].display_val, xspeed, 0)
            for o in aCellObjects:
                canvas.move(o, xspeed, 0)

            canvas.move(self.list[b].display_shape, -xspeed, 0)
            canvas.move(self.list[b].display_val, -xspeed, 0)
            for o in bCellObjects:
                canvas.move(o, -xspeed, 0)

            window.update()
            time.sleep(self.speed(0.01))

        time.sleep(self.speed(0.1))

        # move the cells back down into the list
        while canvas.coords(shapeA)[1] != y0:
            canvas.move(shapeA, 0, -yspeed)
            canvas.move(self.list[a].display_val, 0, -yspeed)
            canvas.move(self.list[b].display_shape, 0, -yspeed)
            canvas.move(self.list[b].display_val, 0, -yspeed)
            for o in (aCellObjects + bCellObjects):
                canvas.move(o, 0, -yspeed)
            window.update()
            time.sleep(self.speed(0.01))

        # perform the actual swap operation in the list
        self.list[a], self.list[b] = self.list[b], self.list[a]

    def moveUp(self, dy, toX, toY, curDisplayShape, curDisplayVal):
        global running

        if not running:
            return

        # given a toX, toY, and dy, calculate the dx required to get
        # from the current position to the new position
        fromX = canvas.coords(curDisplayShape)[0]
        fromY = canvas.coords(curDisplayShape)[1]
        if toY < fromY:
            dx = dy * (toX - fromX) / (toY - fromY)

        # while the cell has not yet reached the new y position,
        # move it up using dx and dy
        while canvas.coords(curDisplayShape)[1] > toY:
            canvas.move(curDisplayShape, dx, dy)
            canvas.move(curDisplayVal, dx, dy)
            window.update()
            time.sleep(self.speed(0.01))

    def placeHolderArray(self):
        for cur in self.list:
            posCell = canvas.coords(cur.display_shape)
            posCellVal = canvas.coords(cur.display_val)

            # create new display objects that are copies of the cell
            canvas.create_rectangle(posCell[0], posCell[1], posCell[2], posCell[3],
                                               fill=cur[1])
            canvas.create_text(posCellVal[0], posCellVal[1], text=cur[0],
                                        font=('Helvetica', '20'))

    # ARRAY FUNCTIONALITY
    def isSorted(self):
        for i in range(1, len(self.list)):
            if self.list[i] < self.list[i-1]:
                return False
        return True

    def get(self, index):
        try:
            return self.list[index][0]
        except:
            print("Invalid list index")
            return -1

    def set(self, index, val):
        # reset the value of the Element at that index to val
        self.list[index].val = val

        # get the position of the displayed value
        pos = canvas.coords(self.list[index].display_val)

        # delete the displayed value and replace it with the updated value
        canvas.delete(self.list[index].display_val)
        self.list[index].display_val = canvas.create_text(pos[0], pos[1], text=str(val), font=('Helvetica', '20'))

        # update window
        window.update()

    def append(self, val):
        # create new cell and cell value display objects
        cell = canvas.create_rectangle(ARRAY_X0+CELL_SIZE*len(self.list), ARRAY_Y0, ARRAY_X0+CELL_SIZE*(len(self.list)+1), ARRAY_Y0 + CELL_SIZE, fill=Array.colors[Array.nextColor])
        cell_val = canvas.create_text(ARRAY_X0+CELL_SIZE*len(self.list) + (CELL_SIZE / 2), ARRAY_Y0 + (CELL_SIZE / 2), text=val,
                                      font=('Helvetica', '20'))

        # add a new Element to the list with the new value, color, and display objects
        self.list.append(drawable(val, Array.colors[Array.nextColor], cell, cell_val))

        # increment nextColor
        Array.nextColor = (Array.nextColor + 1) % len(Array.colors)

        # update window
        window.update()

    def removeFromEnd(self):
        # pop an Element from the list
        n = self.list.pop()

        # delete the associated display objects
        canvas.delete(n.display_shape)
        canvas.delete(n.display_val)

        # update window
        window.update()

    def display(self):
        canvas.delete("all")
        xpos = ARRAY_X0
        ypos = ARRAY_Y0

        # go through each Element in the list
        for n in self.list:
            print(n)
            # create display objects for the associated Elements
            cell = canvas.create_rectangle(xpos, ypos, xpos+CELL_SIZE, ypos+CELL_SIZE, fill=n[1])
            cell_val = canvas.create_text(xpos+(CELL_SIZE/2), ypos+(CELL_SIZE/2), text=n[0], font=('Helvetica', '20'))

            # save the display objects to the appropriate attributes of the Element object
            n.display_shape = cell
            n.display_val = cell_val

            # increment xpos
            xpos += CELL_SIZE

        window.update()

    def find(self, val):
        global cleanup, running
        running = True
        findDisplayObjects = []
        #canvas.delete(findDisplayObjects)
        self.display()

        # draw an arrow over the first cell
        x = ARRAY_X0 + (CELL_SIZE/2)
        y0 = ARRAY_Y0 - 40
        y1 = ARRAY_Y0 - 15
        arrow = canvas.create_line(x, y0, x, y1, arrow="last", fill='red')
        findDisplayObjects.append(arrow)

        # go through each Element in the list
        for n in self.list:
            window.update()

            # if the value is found
            if n.val == val:
                # get the position of the displayed cell and val
                #posCell = canvas.coords(n.display_shape)
                posVal = canvas.coords(n.display_val)

                # cover the current display value with the updated value in green
                #cell_shape = canvas.create_rectangle(posCell[0], posCell[1], posCell[2], posCell[3], fill=n[1])
                cell_val = canvas.create_text(posVal[0], posVal[1], text=str(val), font=('Helvetica', '25'), fill='green2')

                # add the green value to findDisplayObjects for cleanup later
                #findDisplayObjects.append(cell_shape)
                findDisplayObjects.append(cell_val)

                # update the display
                window.update()

                cleanup += findDisplayObjects
                #canvas.after(1000, canvas.delete, arrow)
                #canvas.after(1000, canvas.delete, cell_val)
                return True

            # if the value hasn't been found, wait 1 second, and then move the arrow over one cell
            time.sleep(self.speed(1))
            canvas.move(arrow, CELL_SIZE, 0)

            if not running:
                break

        cleanup += findDisplayObjects
        #canvas.after(1000, canvas.delete, arrow)
        return False

    def remove(self, index):
        n = self.list.pop(3)
        canvas.delete(n.display_shape)
        canvas.delete(n.display_val)
        window.update()

    def shuffle(self):
        global running
        running = True

        maxHeight = HEIGHT - 5
        maxWidth = WIDTH -5
        y = ARRAY_Y0
        for i in range(len(self.list)):
            newX = random.randint(0, len(self.list)-1)
            self.list[i], self.list[newX] = self.list[newX], self.list[i]
            finalX = ARRAY_X0 + (CELL_SIZE * newX)

        times = 0

        # while all of the elements have not yet been returned to the original position
        while times < len(self.list)*2 and running:
            for i in range(len(self.list)):
                time.sleep(self.speed(0.01))
                shuffleY = random.randint(-30, 30)
                shuffleX = random.randint(-30, 30)


                # not go off the sides
                if canvas.coords(self.list[i].display_shape)[0] + shuffleX <= 0 or canvas.coords(self.list[i].display_shape)[0] + shuffleX >= maxWidth:
                    shuffleX = -shuffleX * 2
                if canvas.coords(self.list[i].display_shape)[1] + shuffleY <= ARRAY_Y0 or canvas.coords(self.list[i].display_shape)[1] + shuffleY >= maxHeight:
                    shuffleY = -shuffleY * 2
                canvas.move(self.list[i].display_shape, shuffleX, shuffleY)
                canvas.move(self.list[i].display_val, shuffleX, shuffleY)
            times += 1
            time.sleep(self.speed(0.01))
            window.update()

        self.stopMergeSort()


    # SORTING METHODS
    def insertionSort(self):
        global running
        running = True

        # make a done arrow that points to 0'th element
        x = canvas.coords(self.list[0].display_shape)[0] + (CELL_SIZE / 2)
        y0 = canvas.coords(self.list[0].display_shape)[1] + CELL_SIZE + 15
        y1 = canvas.coords(self.list[0].display_shape)[1] + CELL_SIZE + 40
        outerArrow = canvas.create_line(x+CELL_SIZE, y0, x+CELL_SIZE, y1, arrow="first", fill='red')

        # Traverse through 1 to len(arr)
        for i in range(1, len(self.list)):

            cur, text = self.assignToTemp(i, "cur")

            # Move elements of self.list[0..i-1], that are
            # greater than key, to one position ahead
            # of their current position
            j = i - 1

            innerArrow = canvas.create_line(x+CELL_SIZE*i, y0, x+CELL_SIZE*i, y1, arrow="first", fill='blue')

            while j >= 0 and cur.val < self.list[j].val:
                #self.list[j + 1] = self.list[j]
                time.sleep(self.speed(0.1))
                self.assignElement(j, j+1)
                j -= 1

                canvas.move(innerArrow, -CELL_SIZE, 0)

                if not running:
                    canvas.delete(innerArrow)
                    break

            #self.list[j + 1] = cur
            time.sleep(self.speed(0.1))
            self.assignFromTemp(j+1, cur, text)

            canvas.delete(innerArrow)

            if not running:
                break

            # move done arrow to next element
            canvas.move(outerArrow, CELL_SIZE, 0)


        canvas.delete(outerArrow)
        self.fixGaps()

    def bubbleSort(self):
        global running
        running = True
        n = len(self.list)

        # make a done arrow that points to 0'th element
        x = ARRAY_X0 + (CELL_SIZE / 2)
        y0 = ARRAY_Y0 + CELL_SIZE + 15
        y1 = ARRAY_Y0 + CELL_SIZE + 40
        outerArrow = canvas.create_line(x, y0, x, y1, arrow="first", fill='red')


        # Traverse through all array elements
        for i in range(n):

            innerArrow = canvas.create_line(x, y0, x, y1, arrow="first", fill='blue')

            # Last i elements are already in place
            for j in range(0, n - i - 1):

                time.sleep(self.speed(0.5))

                # traverse the array from 0 to n-i-1
                # Swap if the element found is greater
                # than the next element
                if self.list[j].val > self.list[j+1].val:
                    #arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    self.swap(j, j+1)

                canvas.move(innerArrow, CELL_SIZE, 0)

                if not running:
                    canvas.delete(innerArrow)
                    break

            time.sleep(self.speed(0.5))
            canvas.delete(innerArrow)

            if not running:
                break

            # move done arrow to next element
            canvas.move(outerArrow, CELL_SIZE, 0)

        canvas.delete(outerArrow)
        self.fixGaps()

    def selectionSort(self):
        global running
        running = True

        x = ARRAY_X0 + (CELL_SIZE / 2)
        y0 = ARRAY_Y0 + CELL_SIZE + 15
        y1 = ARRAY_Y0 + CELL_SIZE + 40
        outerArrow = canvas.create_line(x, y0, x, y1, arrow="first", fill='red')

        for i in range(len(self.list)):

            # Find the minimum element in remaining
            # unsorted array
            innerArrow = canvas.create_line(x + CELL_SIZE*i, y0, x + CELL_SIZE*i, y1, arrow="first", fill='blue')

            min_idx = i
            for j in range(i + 1, len(self.list)):

                canvas.move(innerArrow, CELL_SIZE, 0)

                if self.list[min_idx].val > self.list[j].val:
                    min_idx = j

                if not running:
                    canvas.delete(innerArrow)
                    break

            canvas.delete(innerArrow)

            if not running:
                break


            # Swap the found minimum element with
            # the first element
            #A[i], A[min_idx] = A[min_idx], A[i]

            self.swap(i, min_idx)
            canvas.move(outerArrow, CELL_SIZE, 0)

        canvas.delete(outerArrow)
        self.fixGaps()

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

    def fixGaps(self, toX=ARRAY_X0, toY=ARRAY_Y0):
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

    def stopMergeSort(self, toX=ARRAY_X0, toY=ARRAY_Y0):
        # bring all cells up to original position
        # toX = ARRAY_X0
        # toY = ARRAY_Y0

        dy = -2
        dx = [0] * len(self.list)
        done = [False] * len(self.list)
        doneCount = 0

        # calculate dx for each node to move it back to original position
        for i in range(len(self.list)):
            fromX = canvas.coords(self.list[i].display_shape)[0]
            fromY = canvas.coords(self.list[i].display_shape)[1]
            if toY < fromY:
                dx[i] = dy * ((toX + CELL_SIZE * i) - fromX) / (toY - fromY)
            else:
                done[i] = True
                doneCount += 1

        # while all of the elements have not yet been returned to the original position
        while doneCount < len(self.list):
            for i in range(len(self.list)):
                # move the done elements up by dy and corresponding dx
                if not done[i]:
                    canvas.move(self.list[i].display_shape, dx[i], dy)
                    canvas.move(self.list[i].display_val, dx[i], dy)

                    # when the cell is in the correct position, mark it as done
                    if canvas.coords(self.list[i].display_shape)[1] <= toY:
                        doneCount += 1
                        done[i] = True

            window.update()
            time.sleep(self.speed(0.01))

        self.fixGaps()

    def drawPartition(self, left, right):
        bottom = canvas.create_line(ARRAY_X0 + CELL_SIZE*left, ARRAY_Y0 + CELL_SIZE + 15,
                           ARRAY_X0 + CELL_SIZE*(right+1), ARRAY_Y0 + CELL_SIZE + 15, fill="red")
        l = canvas.create_line(ARRAY_X0 + CELL_SIZE*left, ARRAY_Y0 + CELL_SIZE + 5,
                           ARRAY_X0 + CELL_SIZE * left, ARRAY_Y0 + CELL_SIZE + 15, fill="red")
        r = canvas.create_line(ARRAY_X0 + CELL_SIZE * (right+1), ARRAY_Y0 + CELL_SIZE + 5,
                           ARRAY_X0 + CELL_SIZE * (right+1), ARRAY_Y0 + CELL_SIZE + 15, fill="red")

        return bottom, l, r

    def bogoSort(self):
        global running
        running = True
        while not self.isSorted() and running:
            time.sleep(self.speed(1)) # pauses in between shuffles to show that checking if its sorted
            self.shuffle()

    def medianOfThree(self, left, right):
        a = self.list

        b = random.randint(left, right)
        c = random.randint(left, right)
        d = random.randint(left, right)

        if (a[d] < a[b] and a[b] < a[c]) or (a[c] < a[b] and a[b] < a[d]):
            median = b
        elif (a[b] < a[d] and a[d] < a[c]) or (a[c] < a[d] and a[d] < a[b]):
            median = d
        else:
            median = c

        #a[median], a[right] = a[right], a[median]
        self.swap(median, right)

    def partitionIt(self, left, right):
        x = ARRAY_X0 + (CELL_SIZE / 2)
        y0 = ARRAY_Y0 - 15
        y1 = ARRAY_Y0 - 40

        b, l, r = self.drawPartition(left, right)

        self.medianOfThree(left, right)
        a = self.list
        pivot = a[right]
        done = left

        doneArrow = canvas.create_line(x + CELL_SIZE * done, y0, x + CELL_SIZE * done, y1, arrow="first", fill="red")
        doneTxt = canvas.create_text(x + CELL_SIZE * done + CELL_SIZE/2, y1 - 5, text="done",
                                        font=('Helvetica', '15'))

        pivotArrow = canvas.create_line(x + CELL_SIZE * right, y0, x + CELL_SIZE * right, y1, arrow="first", fill="green")
        pivotTxt = canvas.create_text(x + CELL_SIZE * right + CELL_SIZE/2, y1 - 5, text="pivot",
                                        font=('Helvetica', '15'))
        pivotCellObjects = []
        pivotCellObjects.append(pivotArrow)
        pivotCellObjects.append(pivotTxt)

        doneCellObjects = []
        doneCellObjects.append(doneArrow)
        doneCellObjects.append(doneTxt)

        curArrow = canvas.create_line(x + CELL_SIZE * left, y0, x + CELL_SIZE * left, y1, arrow="first",
                                        fill="blue")
        curTxt = canvas.create_text(x + CELL_SIZE * left, y1 - 20, text="cur",
                                 font=('Helvetica', '15'))
        # for each position except for the pivot position
        for cur in range(left, right):

            output = "cur: " + str(a[cur].val) + "\npivot: " + str(pivot.val) + "\n"

            # if the value at that position is smaller than the pivot
            # swap it so it becomes the next value of the done part
            if a[cur].val <= pivot.val:
                #a[done], a[cur] = a[cur], a[done]
                self.swap(done, cur)
                done += 1
                canvas.move(doneArrow, CELL_SIZE, 0)
                canvas.move(doneTxt, CELL_SIZE, 0)
                output += "cur <= pivot --> SWAPPING"
            else:
                output += "cur > pivot"

            txt = canvas.create_text(ARRAY_X0+100, ARRAY_Y0+100, text=output, font=('Helvetica', '15'))
            window.update()
            time.sleep(self.speed(1))
            canvas.delete(txt)

            canvas.move(curArrow, CELL_SIZE, 0)
            canvas.move(curTxt, CELL_SIZE, 0)

        canvas.delete(curArrow)
        canvas.delete(curTxt)

        # Move the pivot into the correct place
        #a[done], a[right] = a[right], a[done]
        self.swap(done, right, aCellObjects=doneCellObjects, bCellObjects=pivotCellObjects)

        canvas.delete(pivotArrow)
        canvas.delete(pivotTxt)
        canvas.delete(doneArrow)
        canvas.delete(doneTxt)
        canvas.delete(b)
        canvas.delete(l)
        canvas.delete(r)

        # At this point, done is the location where the pivot value got placed
        time.sleep(self.speed(0.1))
        return done

    def quickSort(self, left=-1, right=-1):
        # initialize things if method was called without args
        if left == -1:
            left = 0
            right = len(self.list) - 1

        # there has to be at least two elements
        if left < right:
            partition = self.partitionIt(left, right)
            self.quickSort(left, partition - 1)
            self.quickSort(partition + 1, right)

    def countingSortOnDigit(self, d):
        ans = [0] * len(self.list)  # the sorted numbers will go here
        counts = [0] * 10  # the counts are accumulated here
        a = self.list[:]
        someRemaining = False
        tenPower = 10 ** d

        length = len(self.list)
        for i in range(length):
            temp = a[i].val // tenPower
            if temp > 0: someRemaining = True
            counts[temp % 10] += 1
        if someRemaining == False: return False
        # counts[j] now contains the number of values
        # in Array whose d'th digit is == j

        # convert the counts into cumulative counts:
        for j in range(1, len(counts)): counts[j] += counts[j - 1]
        # counts[j] now contains the number of values
        # in arr whose d'th digit is <= to j

        # place the values of arr into the correct slot of the answer array

        x = canvas.coords(self.list[length-1].display_shape)[0]
        y0 = canvas.coords(self.list[length-1].display_shape)[1] + CELL_SIZE/2

        curArrow = canvas.create_line(x, y0, x - CELL_SIZE, y0, arrow="first", fill="red")
        curTxt = canvas.create_text(x-30, y0-10, text="cur",
                                     font=('Helvetica', '15'))

        self.placeHolderArray()

        for i in range(length - 1, -1, -1):
            temp = (a[i].val // tenPower) % 10
            counts[temp] -= 1
            ans[counts[temp]] = a[i]

            canvas.move(self.list[i].display_shape, CELL_SIZE*3, (counts[temp]-i) * CELL_SIZE)
            canvas.move(self.list[i].display_val, CELL_SIZE*3, (counts[temp]-i) * CELL_SIZE)

            window.update()
            time.sleep(self.speed(0.8))
            canvas.move(curArrow, 0, - CELL_SIZE)
            canvas.move(curTxt, 0, - CELL_SIZE)

        canvas.delete(curArrow)
        canvas.delete(curTxt)
        window.update()
        self.list = ans
        return True

    def radixSort(self):
        global running
        # get the y coordinates of the next level down
        shapeX = canvas.coords(self.list[0].display_shape)[0]
        valX = canvas.coords(self.list[0].display_val)[0]
        canvas.config(width=1200, height=600)

        for i in range(0, len(self.list)):
            cur = self.list[i]
            canvas.move(cur.display_shape, -(canvas.coords(cur.display_shape)[0] - shapeX), CELL_SIZE*i - 30)
            canvas.move(cur.display_val, -(canvas.coords(cur.display_val)[0] - valX), CELL_SIZE*i - 30)

            window.update()
            time.sleep(self.speed(0.01))

        i = 0
        while self.countingSortOnDigit(i):
            i += 1

        canvas.config(width = WIDTH, height = HEIGHT)
        self.display()


def stop(pauseButton): # will stop after the current shuffle is done
    global running
    running = False

    if waitVar.get():
        play(pauseButton)

def pause(pauseButton):
    global waitVar
    waitVar.set(True)

    pauseButton['text'] = "Play"
    pauseButton['command'] = lambda: onClick(play, pauseButton)

    canvas.wait_variable(waitVar)

def play(pauseButton):
    global waitVar
    waitVar.set(False)

    pauseButton['text'] = 'Pause'
    pauseButton['command'] = lambda: onClick(pause, pauseButton)

def onClick(command, parameter = None):
    cleanUp()
    disableButtons()
    if parameter:
        command(parameter)
    else:
        command()
    if command not in [pause, play]:
        enableButtons()

def cleanUp():
    global cleanup
    if len(cleanup) > 0:
        for o in cleanup:
            canvas.delete(o)
    outputText.set('')
    window.update()

# Button functions
def clickFind():
    entered_text = textBox.get()
    txt = ''
    if entered_text:
        if int(entered_text) < 100:
            result = array.find(int(entered_text))
            if result:
                txt = "Found!"
            else:
                txt = "Value not found"
            outputText.set(txt)
        else:
            outputText.set("Input value must be an integer from 0 to 99.")
            textBox.delete(0, END )

def clickInsert():
    entered_text = textBox.get()
    if entered_text:
        val = int(entered_text)
        if val < 100:
            array.append(int(entered_text))
        else:
            outputText.set("Input value must be an integer from 0 to 99.")
        textBox.delete(0, END )

def close_window():
    window.destroy()
    exit()

def disableButtons():
    for button in buttons:
        button.config(state = DISABLED)

def enableButtons():
    for button in buttons:
        button.config(state = NORMAL)

def makeButtons():
    bubbleSortButton = Button(bottomframe, text="Bubble Sort", width=11, command= lambda: onClick(array.bubbleSort))
    bubbleSortButton.grid(row=0, column=0)
    selectionSortButton = Button(bottomframe, text="Selection Sort", width=14, command= lambda: onClick(array.selectionSort))
    selectionSortButton.grid(row=0, column=1)
    insertionSortButton = Button(bottomframe, text="Insertion Sort", width=14, command= lambda: onClick(array.insertionSort))
    insertionSortButton.grid(row=0, column=2)
    bogoSortButton = Button(bottomframe, text="Bogo Sort", width=9, command= lambda: onClick(array.bogoSort))
    bogoSortButton.grid(row=0, column=3)
    mergeSortButton = Button(bottomframe, text="Merge Sort", width=9, command= lambda: onClick(array.mergeSort))
    mergeSortButton.grid(row=1, column=0)
    quickSortButton = Button(bottomframe, text="Quick Sort", width=9, command= lambda: onClick(array.quickSort))
    quickSortButton.grid(row=1, column=1)
    radixSortButton = Button(bottomframe, text="Radix Sort", width=9, command= lambda: onClick(array.radixSort))
    radixSortButton.grid(row=1, column=2)
    shuffleButton = Button(bottomframe, text="Shuffle", width=7, command= lambda: onClick(array.shuffle))
    shuffleButton.grid(row=1, column=3)
    pauseButton = Button(bottomframe, text="Pause", width=8, command = lambda: onClick(pause, pauseButton))
    pauseButton.grid(row=2, column=0)
    stopButton = Button(bottomframe, text="Stop", width=7, command = lambda: onClick(stop, pauseButton))
    stopButton.grid(row=1, column=4)
    findButton = Button(bottomframe, text="Find", width=7, command= lambda: onClick(clickFind))
    findButton.grid(row=2, column=1)
    insertButton = Button(bottomframe, text="Insert", width=7, command= lambda: onClick(clickInsert))
    insertButton.grid(row=2, column=2)
    deleteButton = Button(bottomframe, text="Delete", width=7, command= lambda: onClick(array.removeFromEnd))
    deleteButton.grid(row=2, column=3)
    buttons = [bubbleSortButton, selectionSortButton, insertionSortButton, bogoSortButton, mergeSortButton,
               quickSortButton, radixSortButton, shuffleButton, findButton, insertButton, deleteButton]
    return buttons

# validate text entry
def validate(action, index, value_if_allowed,
             prior_value, text, validation_type, trigger_type, widget_name):
    if text in '0123456789':
        return True
    else:
        return False

window = Tk()
frame = Frame(window)
frame.pack()

waitVar = BooleanVar()

canvas = Canvas(frame, width=WIDTH, height=HEIGHT)
window.title("Sorting")
canvas.pack()

bottomframe = Frame(window)
bottomframe.pack(side=BOTTOM)

#Label(bottomframe, text="Find:", font="none 12 bold").grid(row=0, column=0, sticky=W)
vcmd = (window.register(validate),
        '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
textBox = Entry(bottomframe, width=20, bg="white", validate='key', validatecommand=vcmd)
textBox.grid(row=4, column=0, sticky=W)
scaleDefault = 100
scale = Scale(bottomframe, from_=1, to=200, orient=HORIZONTAL, sliderlength=15)
scale.grid(row=5, column=1, sticky=W)
scale.set(scaleDefault)
scaleLabel = Label(bottomframe, text="Speed:", font="none 10")
scaleLabel.grid(row=5, column=0, sticky=E)

# add a submit button
#Button(bottomframe, text="Find", width=6, command=lambda: array.onClick(clickFind)).grid(row=0, column=2, sticky=W)
outputText = StringVar()
outputText.set('')
output = Label(bottomframe, textvariable=outputText, font="none 12 bold")
output.grid(row=4, column=1, sticky=E)

# exit button
Button(bottomframe, text="EXIT", width=4, command=close_window).grid(row=6, column=3, sticky=W)

cleanup = []
array = Array()
buttons = makeButtons()
array.display()


for i in range(10):
    array.append(i)

window.mainloop()

'''
To Do:
- make it look pretty
- animate insert and delete
- delete/insert at index?
- label arrows for sorts (inner, outer, etc.)
- implement shell sort, radix sort, quick sort
'''
