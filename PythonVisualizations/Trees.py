from tkinter import *
from AnimationMethods import *
WIDTH = 800
HEIGHT = 400

CELL_SIZE = 50
CELL_BORDER = 2
ARRAY_X0 = 100
ARRAY_Y0 = 100
OPERATIONS_BG = 'beige'
OPERATIONS_BORDER = 'black'
FONT_SIZE = '20'
VALUE_FONT = ('Helvetica', FONT_SIZE)
VALUE_COLOR = 'black'
FOUND_FONT = ('Helvetica', FONT_SIZE)
FOUND_COLOR = 'green2'
CONTROLS_FONT = ('none', '14')

class Node(object):
    # create a tree node consisting of a key/data pair
    def __init__(self, k, d):
        self.key = k
        self.data = d
        self.leftChild = None
        self.rightChild = None

    def __str__(self):
        return "{" + self.key + " , " + self.data + "}"


class Tree(object):
    def __init__(self, size=0):
        self.__root = None
        self.__nElems = 0
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


    def insert(self, k, d):
        # if tree is empty, then initialize root to the new node
        if not self.__root:
            self.__root = Node(k, d)
            return True

        cur = self.__root  # start at the root

        while k != cur.key:
            # if the key is to the left of current node, follow to the left
            if k < cur.key:
                # if no left child, insert on left
                if not cur.leftChild:
                    cur.leftChild = Node(k, d)
                    self.__nElems += 1
                    return True
                cur = cur.leftChild

            else:  # otherwise, key must be to right of current node
                if not cur.rightChild:
                    cur.rightChild = Node(k, d)
                    self.__nElems += 1
                    return True
                cur = cur.rightChild

        return False  # the key is already there, so fail

    def inOrderTraversal(self, cur):
        if cur:
            self.inOrderTraversal(cur.leftChild)
            print(" " + str(cur), end="")
            self.inOrderTraversal(cur.rightChild)

    def delete(self, key):
        pass

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


#What can be inserted in the textbox
def validate():
    pass

def makeButtons():
    fillButton = Button(bottomframe, text="Fill", command= lambda: onClick(Tree.fill))
    fillButton.grid(row=1, column=0, padx=8, sticky=(E, W))
    findButton = Button(bottomframe, text="Find", command= lambda: onClick(Tree.find))
    findButton.grid(row=1, column=1, padx=8, sticky=(E, W))
    insertButton = Button(bottomframe, text="Insert", command= lambda: onClick(Tree.insert))
    insertButton.grid(row=1, column=2, padx=8, sticky=(E, W))
    deleteValueButton = Button(bottomframe, text="Delete", command= lambda: onClick(Tree.delete))
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

window.mainloop()
