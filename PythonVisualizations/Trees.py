from tkinter import *
import time, random

WIDTH = 1000
HEIGHT = 400

CIRCLE_SIZE = 15
ROOT_X0 = WIDTH/2
NODE_X_GAP = 400
NODE_Y_GAP = 75
ROOT_Y0 = 40
OPERATIONS_BG = 'beige'
OPERATIONS_BORDER = 'black'
FONT_SIZE = '16'
VALUE_FONT = ('Helvetica', FONT_SIZE)
VALUE_COLOR = 'black'
FOUND_FONT = ('Helvetica', FONT_SIZE)
FOUND_COLOR = 'green2'
CONTROLS_FONT = ('none', '14')
MAX_LEVEL = 5
ARROW_HEIGHT = 30
from enum import Enum

class Child(Enum):
    LEFT = 0
    RIGHT = 1

class Node(object):
    # create a tree node consisting of a key/data pair
    def __init__(self, k, coords, id = None):
        self.key = k
        self.leftChild = None
        self.rightChild = None
        self.id = id
        self.coords = coords

    def __str__(self):
        return "{" + str(self.key) + "}"


class Tree(object):
    def __init__(self, size=0):
        self.__root = None
        self.nElems = 0
        self.size = size
        self.prevId = -1

    #Fill the tree with n nodes
    def fill(self, n):
        #delete any existing nodes by looping through the tree
        canvas.delete("all")
        self.__root = None
        self.nElems = 0

        #randomly generate a tree
        nums = list(range(1, 99))
        random.shuffle(nums)
        while self.nElems < n and nums:
            num = nums.pop()
            self.insertElem(nums.pop(), False)


    # find node with given key k
    # return the associated data or None
    def find(self, k, flag="normal"):
        global cleanup, running
        running = True
        findDisplayObjects = []

        # start at the root
        level = 0
        cur = self.__root
        arrow = canvas.create_line(cur.coords[0], cur.coords[1] - CIRCLE_SIZE - ARROW_HEIGHT,
                                   cur.coords[0], cur.coords[1] - CIRCLE_SIZE, arrow="last", fill='red')
        findDisplayObjects.append(arrow)
        canvas.update()

        # while we haven't found the key
        while cur:
            canvas.delete(arrow)
            arrow = canvas.create_line(cur.coords[0], cur.coords[1] - CIRCLE_SIZE - ARROW_HEIGHT,
                                       cur.coords[0], cur.coords[1] - CIRCLE_SIZE, arrow="last", fill='red')
            findDisplayObjects.append(arrow)
            canvas.update()
            time.sleep(self.speed(1))

            if cur.key == k:
                foundText = canvas.create_text(cur.coords[0], cur.coords[1], text=cur.key, font=VALUE_FONT,
                                               fill="green")
                findDisplayObjects.append(foundText)

                canvas.update()
                cleanup += findDisplayObjects
                if flag == "normal": return cur
                else: return cur,level

            # go left ?
            if k < cur.key:
                cur = cur.leftChild
            # go right
            else:
                cur = cur.rightChild
            level += 1

        cleanup+=findDisplayObjects
        return None

    def insertElem(self, k, animation = True):
        global cleanup, running
        running = True
        findDisplayObjects = []
        inserted = False

        # if tree is empty, then initialize root to the new node
        if not self.__root:
            self.__root = self.insertChildNode(k, None, 0, None)
            self.nElems+=1
            return True

        # start at the root
        cur = self.__root
        if animation:
            arrow = canvas.create_line(ROOT_X0, ROOT_Y0 -CIRCLE_SIZE-ARROW_HEIGHT,
                                       ROOT_X0, ROOT_Y0-CIRCLE_SIZE, arrow=LAST, fill='red')
            findDisplayObjects.append(arrow)
            time.sleep(self.speed(1))

        level = 1

        while not inserted:
            window.update()
            # if the key is to the left of current node, follow to the left
            if k < cur.key:
                # if no left child, insert on left
                if not cur.leftChild:
                    cur.leftChild = self.insertChildNode(k, cur, level, Child.LEFT)
                    inserted = True
                cur = cur.leftChild

            else:  # otherwise, key must be to right of current node
                if not cur.rightChild:
                    cur.rightChild = self.insertChildNode(k, cur, level, Child.RIGHT)
                    inserted = True
                cur = cur.rightChild

            if animation:
                canvas.delete(arrow)
                arrow = canvas.create_line(cur.coords[0], cur.coords[1]-CIRCLE_SIZE-ARROW_HEIGHT,
                                           cur.coords[0], cur.coords[1]-CIRCLE_SIZE, arrow="last", fill='red')
                findDisplayObjects.append(arrow)
                time.sleep(self.speed(1))

            level+=1

            if level >= MAX_LEVEL and not inserted:
                outputText.set("Error! Can't go down another level. Maximum depth of tree is " + str(MAX_LEVEL)) if animation else None
                cleanup+=findDisplayObjects
                return False

            if not running:
                break

        self.nElems += 1
        cleanup += findDisplayObjects
        outputText.set("Inserted") if animation else None
        return True

    def insertChildNode(self, k, parent, level, childDirection):
        x,y = self.calculateCoordinates(parent, level, childDirection)
        id  = self.generate_id()

        canvas.create_circle(x, y, CIRCLE_SIZE, tag = id)
        canvas.create_text(x,y, text=k, font=VALUE_FONT, tag = id)
        if level !=0:
            x1 = parent.coords[0]
            y1 = parent.coords[1] +CIRCLE_SIZE
            x2 = x
            y2 = y-CIRCLE_SIZE
            canvas.create_line(x1, y1, x2, y2, tag = id)
        return Node(k, coords=(x,y), id = id)

    def calculateCoordinates(self, parent, level, childDirection):
        if level == 0:
            return ROOT_X0, ROOT_Y0
        elif childDirection == Child.LEFT:
            return parent.coords[0] - 1/2**level* (NODE_X_GAP-CIRCLE_SIZE), ROOT_Y0+level* NODE_Y_GAP
        else:
            return parent.coords[0] + 1/2**level* (NODE_X_GAP-CIRCLE_SIZE), ROOT_Y0+level* NODE_Y_GAP

    # generate id for nodes
    def generate_id(self):
        self.prevId+=1
        return "item" + str(self.prevId)

    def inOrderTraversal(self, cur):
        if cur:
            self.inOrderTraversal(cur.leftChild)
            print(" " + str(cur), end="")
            self.inOrderTraversal(cur.rightChild)


    def delete(self, k, animation = True):
        global cleanup, running
        running = True
        findDisplayObjects = []

        # start at the root
        cur = self.__root
        parent = self
        direction = None
        
        #if animated, show the search for the item to be deleted
        if animation:
            arrow = canvas.create_line(cur.coords[0], cur.coords[1] - CIRCLE_SIZE - ARROW_HEIGHT,
                                   cur.coords[0], cur.coords[1] - CIRCLE_SIZE, arrow="last", fill='red')
            findDisplayObjects.append(arrow)
            canvas.update()

        # while we haven't found the key
        while cur:
            #if animated, show the search
            if animation:
                canvas.delete(arrow)
                arrow = canvas.create_line(cur.coords[0], cur.coords[1] - CIRCLE_SIZE - ARROW_HEIGHT,
                                       cur.coords[0], cur.coords[1] - CIRCLE_SIZE, arrow="last", fill='red')
                findDisplayObjects.append(arrow)
                canvas.update()
                time.sleep(self.speed(1))

            #found the item to be deleted
            if cur.key == k:
                #if animated, show that we found the item to be deleted
                if animation:
                    foundText = canvas.create_text(cur.coords[0], cur.coords[1], text=cur.key, font=VALUE_FONT,
                                               fill="green")
                    findDisplayObjects.append(foundText)
                    canvas.update()
                    cleanup += findDisplayObjects

                    time.sleep(self.speed(1))
                    canvas.delete(arrow)
                    canvas.delete(foundText)
                #go through the process of deleting the item
                return self.__delete(parent, cur, direction)

            parent = cur
            # go left ?
            if k < cur.key:
                cur = cur.leftChild
                direction = Child.LEFT
            # go right
            else:
                cur = cur.rightChild
                direction = Child.RIGHT

        cleanup+=findDisplayObjects
        return None
        
    def __delete(self, parent, cur, direction):
        #save the deleted key
        deleted = cur.key

        #remove the drawing
        canvas.delete(cur.id)
        canvas.update()
        time.sleep(self.speed(1))
        
        #determine the correct process for removing the node from the tree
        if cur.leftChild:
            if cur.rightChild:                  #case 3: left and right child exist
                self.__promoteSuccessor(parent, cur, direction)
            else:
                if parent is self:              #no right child
                    self.__root = cur.leftChild #root was deleted
                    self.__reDraw(self.__root, None, None, 0)
                elif parent.leftChild is cur:   #parent's left is cur, cur only has a left
                    parent.leftChild = cur.leftChild
                    self.__reDraw(parent.leftChild, parent, Child.LEFT)
                else:                           #parent's right is cur, cur only has a left
                    parent.rightChild = cur.leftChild
                    self.__reDraw(parent.rightChild, parent, Child.RIGHT)
        else:                                   #a right child exists or no children
            if parent is self:                  #deleting the root
                self.__root = cur.rightChild
                self.__reDraw(self.__root, None, None, 0)
            elif parent.leftChild is cur:       #parent's left is cur, cur only has a right child
                parent.leftChild = cur.rightChild
                self.__reDraw(parent.leftChild, parent, Child.LEFT)
            else:                               #parent's right is cur, cur only has a right child
                parent.rightChild = cur.rightChild
                self.__reDraw(parent.rightChild, parent, Child.RIGHT)

        self.nElems -= 1
        return deleted

    #cur is item that is being moved
    #parent is the parent of cur
    #childDirection is the direction that parent should point to cur
    def __reDraw(self, cur, parent, childDirection, level="begin"):
        if cur == None: return

        # if the level of cur is unknown, find the level
        if level == "begin": node, level = self.find(cur.key, flag="level")
        #clean up the find arrow
        cleanUp()

        #remove the current node's representation from the canvas
        canvas.delete(cur.id)
        canvas.update()

        #reDraw the item in the correct position
        x,y = self.calculateCoordinates(parent, level, childDirection)
        canvas.create_circle(x, y, CIRCLE_SIZE, tag = cur.id)
        canvas.create_text(x,y, text=cur.key, font=VALUE_FONT, tag = cur.id)
        if level !=0:
            x1 = parent.coords[0]
            y1 = parent.coords[1] +CIRCLE_SIZE
            x2 = x
            y2 = y-CIRCLE_SIZE
            canvas.create_line(x1, y1, x2, y2, tag = cur.id)
        cur.coords = (x,y)

        #reDraw any of cur's children
        self.__reDraw(cur.leftChild, cur, Child.LEFT, level+1)
        self.__reDraw(cur.rightChild, cur, Child.RIGHT, level+1)

    #description: method used when deleting a node with two children, locates the node to take the place of the deleted node and calls the appropiate methods
    #             the node we want to "promote" is the key that is after the deleted key when all the keys are arranged in ascending order- this is the deleted node's right child's most left child
    #parameters: parent is the parent of the node to be deleted, node is the node being deleted, direction indicates if node is the right or left child of its parent
    def __promoteSuccessor(self, parent, node, direction):
        global cleanup
        findDisplayObjects = []

        successor = node.rightChild
        newParent = node

        arrow = canvas.create_line(successor.coords[0], successor.coords[1] - CIRCLE_SIZE - ARROW_HEIGHT,
                                       successor.coords[0], successor.coords[1] - CIRCLE_SIZE, arrow="last", fill='red')
        findDisplayObjects.append(arrow)
        canvas.update()
        time.sleep(self.speed(1))
                
        #hunt for the right child's most left child
        while successor.leftChild:
            newParent = successor
            successor = successor.leftChild

            canvas.delete(arrow)
            arrow = canvas.create_line(successor.coords[0], successor.coords[1] - CIRCLE_SIZE - ARROW_HEIGHT,
                                       successor.coords[0], successor.coords[1] - CIRCLE_SIZE, arrow="last", fill='red')
            findDisplayObjects.append(arrow)
            canvas.update()
            time.sleep(self.speed(1))

        #move the correct key to the deleted node's slot
        node.key = successor.key

        cleanup += findDisplayObjects

        self.__reDraw(node, parent, direction)
        self.__delete(newParent, successor, direction)

    # ANIMATION METHODS
    def speed(self, sleepTime):
        return (sleepTime * (scaleDefault + 50)) / (scale.get() + 50)

    ######For testing purposes
    def printTree(self):
        self.pTree(self.__root, "ROOT:  ", "")
        print()

    def pTree(self, n, kind, indent):
        print("\n" + indent + kind, end="")
        if n:
            print(n, end="")
            if n.leftChild:
                self.pTree(n.leftChild, "LEFT:  ", indent + "    ")
            if n.rightChild:
                self.pTree(n.rightChild, "RIGHT:  ", indent + "    ")

def clickInsert():
    entered_text = textBox.get()
    if entered_text:
        val = int(entered_text)
        if val < 100:
            tree.insertElem(int(entered_text))
        else:
            outputText.set("Input value must be an integer from 0 to 99.")
    textBox.delete(0, END)

def clickFind():
    entered_text = textBox.get()
    if entered_text:
        val = int(entered_text)
        if val < 100:
            found = tree.find(int(entered_text))
            outputText.set("Found!" if found else "Value not found")
        else:
            outputText.set("Input value must be an integer from 0 to 99.")
    textBox.delete(0, END)

def clickFill():
    entered_text = textBox.get()
    if entered_text:
        val = int(entered_text)
        if val < 32:
            tree.fill(val)
        else:
            outputText.set("Input value must be an integer from 0 to 31.")
    textBox.delete(0, END)

def clickDelete():
    entered_text = textBox.get()
    if entered_text:
        val = int(entered_text)
        if val < 100:
            deleted = tree.delete(int(entered_text))
            outputText.set("Deleted!" if deleted else "Value not found")
        else:
            outputText.set("Input value must be an integer from 0 to 99.")
    textBox.delete(0, END)

#What can be inserted in the textbox
def validate(action, index, value_if_allowed,
             prior_value, text, validation_type, trigger_type, widget_name):
    if text in '0123456789':
        return True
    else:
        return False

def makeButtons():
    fillButton = Button(bottomframe, text="Fill", command= lambda: onClick(clickFill))
    fillButton.grid(row=1, column=0, padx=8, sticky=(E, W))
    findButton = Button(bottomframe, text="Find", command= lambda: onClick(clickFind))
    findButton.grid(row=1, column=1, padx=8, sticky=(E, W))
    insertButton = Button(bottomframe, text="Insert", command= lambda: onClick(clickInsert))
    insertButton.grid(row=1, column=2, padx=8, sticky=(E, W))
    deleteValueButton = Button(bottomframe, text="Delete", command= lambda: onClick(clickDelete))
    deleteValueButton.grid(row=1, column=3, padx=8, sticky=(E, W))

    buttons = [findButton, insertButton, deleteValueButton]
    return buttons


def stop(pauseButton):
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

def close_window():
    window.destroy()
    exit()

def disableButtons():
    for button in buttons:
        button.config(state = DISABLED)

def enableButtons():
    for button in buttons:
        button.config(state = NORMAL)

def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
Canvas.create_circle = _create_circle

window = Tk()
frame = Frame(window)
frame.pack()

waitVar = BooleanVar()

canvas = Canvas(frame, width=WIDTH, height=HEIGHT)
window.title("Tree")
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

outputText = StringVar()
outputText.set('')
output = Label(bottomframe, textvariable=outputText, font=CONTROLS_FONT + ('italic',), fg="blue")
output.grid(row=0, column=3, sticky=(E, W))
bottomframe.grid_columnconfigure(4, minsize=160)

# exit button
Button(bottomframe, text="EXIT", width=4, command=close_window).grid(row=6, column=3, sticky=W)

cleanup = []
buttons = makeButtons()

tree = Tree()
import random
nums = list(range(1, 99))
random.shuffle(nums)
while tree.nElems < 20 and nums:
    tree.insertElem(nums.pop(), False)
window.mainloop()
