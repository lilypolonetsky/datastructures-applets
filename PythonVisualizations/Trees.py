from tkinter import *
import time

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

    #Fill the tree with n nodes
    def fill(self, n):
        pass

    # find node with given key k
    # return the associated data or None
    def find(self, k):
        # start at the root
        current = self.__root

        # while we haven't found the key
        while current and k != current.key:
            # go left ?
            if k < current.key:
                current = current.leftChild
            # go right
            else:
                current = current.rightChild

        return current.data if current else None

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
                                       ROOT_X0, ROOT_Y0-CIRCLE_SIZE, arrow=LAST, fill='red', tag=id)
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
                return False

            if not running:
                break

        self.nElems += 1
        cleanup += findDisplayObjects
        outputText.set("Inserted") if animation else None
        return True

    def insertChildNode(self, k, parent, level, childDirection):
        x,y = self.calculateCoordinates(parent, level, childDirection)
        canvas.create_circle(x, y, CIRCLE_SIZE)
        canvas.create_text(x,y, text=k, font=VALUE_FONT)
        if level !=0:
            x1 = parent.coords[0]
            y1 = parent.coords[1] +CIRCLE_SIZE
            x2 = x
            y2 = y-CIRCLE_SIZE
            canvas.create_line(x1, y1, x2, y2)
        return Node(k, coords=(x,y))

    def calculateCoordinates(self, parent, level, childDirection):
        if level == 0:
            return ROOT_X0, ROOT_Y0
        elif childDirection == Child.LEFT:
            return parent.coords[0] - 1/2**level* (NODE_X_GAP-CIRCLE_SIZE), ROOT_Y0+level* NODE_Y_GAP
        else:
            return parent.coords[0] + 1/2**level* (NODE_X_GAP-CIRCLE_SIZE), ROOT_Y0+level* NODE_Y_GAP

    def inOrderTraversal(self, cur):
        if cur:
            self.inOrderTraversal(cur.leftChild)
            print(" " + str(cur), end="")
            self.inOrderTraversal(cur.rightChild)

    def delete(self, key):
        pass

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
    pass

def clickFill():
    pass

def clickDelete():
    pass

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
