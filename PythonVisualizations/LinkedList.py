import time
from tkinter import *
import math

WIDTH = 800
HEIGHT = 400

CELL_SIZE = 50
CELL_BORDER = 2
OPERATIONS_BG = 'beige'
OPERATIONS_BORDER = 'black'
FONT_SIZE = '20'
VALUE_FONT = ('Helvetica', FONT_SIZE)
VALUE_COLOR = 'black'
FOUND_FONT = ('Helvetica', FONT_SIZE)
FOUND_COLOR = 'green2'
CONTROLS_FONT = ('none', '14')
FONT_SIZE = '20'

CELL_WIDTH = 70
CELL_HEIGHT = 50
CELL_GAP = 20
DOT_SIZE = 10
LL_X0 = 100
LL_Y0 = 70
MAX_SIZE=20
LEN_ROW = 5
ROW_GAP = 40

class Node(object):
    # create a linked list node
    #id is used to link the different parts of each node visualization
    def __init__(self, k, n=None, id=None):
        self.key = k
        self.id = id
        self.next = n  # reference to next item in list

    def __str__(self):
        return "{" + str(self.key) + "}"

class LinkedList(object):
    def __init__(self):
        self.first = None
        self.prev_id = -1

    def __len__(self):
        cur = self.first
        ans = 0

        while cur:
            ans += 1
            cur = cur.next

        return ans

    def isEmpty(self):
        return not self.first

    # attempt to insert a new Node containing newKey
    # into the linked list immediately after the first node
    # containing key. Return True on success, False otherwise.
    def insertAfter(self, key, newKey):
        # find the first Node that contains key
        cur = self.first
        while cur and cur.key != key: cur = cur.next

        # if such a node is there, patch in a new Node
        if cur:
            newNode = Node(newKey, cur.next)
            cur.next = newNode
            if not newNode.next: self.__last = newNode

        return cur != None  # return True on success

    # return a tuple containing the key/data pair
    # associated with key. return None if key
    # couldn't be found in the list.
    def find(self, key):
        # loop until we hit the end, or find the key
        cur = self.first
        while cur and cur.key != key: cur = cur.next

        # return the key/data pair if found
        return (cur.key, cur.data) if cur else None

    # delete a node from the linked list, returning the key
    # pair of the deleted node. If key == None, then just delete
    # the first node. Otherwise, attempt to find and delete
    # the first node containing key
    def delete(self, key=None):
        # delete the first node?
        if (not key) or (self.first and key == self.first.key):
            ans = self.first
            if not ans: return None
            self.first = ans.next
            return ans.key, ans.data

        # loop until we hit end, or find key,
        # keeping track of previously visited node
        cur = prev = self.first
        while cur and cur.key != key:
            prev = cur
            cur = cur.next

        # A node with this key isn't on list
        if not cur: return None

        # otherwise remove the node from the list and
        # return the key/data pair of the found node
        prev.next = cur.next

        return cur.key

    # insert a key/data pair at the start of the list
    def insert(self, key):
        newNode = Node(key, self.first)
        self.first = newNode

    def generateId(self):
        return "item" + str(self.prev_id + 1)

    # ANIMATION METHODS
    def speed(self, sleepTime):
        return (sleepTime * (scaleDefault + 50)) / (scale.get() + 50)

    #id is used to link the different parts of each node visualization
    def insertElem(self, newNode,pos=0, id=-1):
        # create new cell and cell value display objects
        val = newNode.key
        x_offset = pos%LEN_ROW * (CELL_WIDTH + CELL_GAP)
        y_offset = pos//LEN_ROW*(CELL_HEIGHT+ROW_GAP)
        if pos == -1:
            x_offset= -LL_X0+10
            y_offset=0
        if id==-1:
            id = self.generateId()
            newNode.id = id
        canvas.create_rectangle(LL_X0 + x_offset,
                                       LL_Y0+y_offset,
                                       LL_X0 + CELL_WIDTH + x_offset,
                                       LL_Y0 + CELL_HEIGHT+y_offset, fill="WHITE", tag=id)
        canvas.create_text(LL_X0 + CELL_HEIGHT // 2 + x_offset,
                                      LL_Y0 + CELL_HEIGHT // 2+y_offset,
                                      text=val, font=('Helvetica', '20'),tag = id)
        canvas.create_oval(LL_X0 + CELL_HEIGHT - DOT_SIZE // 2 + x_offset,
                           LL_Y0 + CELL_HEIGHT // 2 - DOT_SIZE // 2 + y_offset,
                           LL_X0 + CELL_HEIGHT + DOT_SIZE // 2 + x_offset,
                           LL_Y0 + CELL_HEIGHT // 2 + DOT_SIZE // 2+ y_offset,
                           fill="RED", outline="RED", tag = id)
        if pos%LEN_ROW == LEN_ROW-1 and pos!=-1:
            canvas.create_line(LL_X0 + CELL_HEIGHT + x_offset,
                               LL_Y0 + CELL_HEIGHT // 2 + y_offset,
                               LL_X0 + CELL_HEIGHT + x_offset,
                               LL_Y0 + CELL_HEIGHT // 2 + y_offset+ROW_GAP/2 + CELL_HEIGHT/2,
                                tag=id)
            canvas.create_line(LL_X0 + CELL_HEIGHT + x_offset,
                               LL_Y0 + CELL_HEIGHT // 2 + y_offset + ROW_GAP / 2 + CELL_HEIGHT / 2,
                               LL_X0 + CELL_HEIGHT,
                               LL_Y0 + CELL_HEIGHT // 2 + y_offset+ROW_GAP/2 + CELL_HEIGHT/2,
                               tag=id)
            canvas.create_line(LL_X0 + CELL_HEIGHT,
                               LL_Y0 + CELL_HEIGHT // 2 + y_offset + ROW_GAP / 2 + CELL_HEIGHT / 2,
                               LL_X0 + CELL_HEIGHT,
                               LL_Y0 + CELL_HEIGHT // 2 + y_offset + ROW_GAP + CELL_HEIGHT/2,
                               arrow=LAST, tag=id)
        else:
            canvas.create_line(LL_X0 + CELL_HEIGHT + x_offset,
                                    LL_Y0 + CELL_HEIGHT // 2 + y_offset,
                                    LL_X0 + x_offset + CELL_WIDTH + CELL_GAP,
                                    LL_Y0 + CELL_HEIGHT // 2 + y_offset,
                                     arrow = LAST,tag = id)
        # update window
        window.update()

    def clickFind(self, key):
        global cleanup, running
        running = True
        findDisplayObjects = []

        cur = self.first
        pos = 0
        x = pos % LEN_ROW * (CELL_WIDTH + CELL_GAP) + LL_X0 + CELL_WIDTH / 2
        y = pos // LEN_ROW * (CELL_HEIGHT + ROW_GAP) + LL_Y0
        arrow = canvas.create_line(x, y - 40, x, y, arrow="last", fill='red')
        findDisplayObjects.append(arrow)

        # go through each Element in the linked list
        while cur:
            window.update()

            # if the value is found
            if cur.key == key:
                # get the position of the text of the elements
                posVal = (x-10, y+CELL_HEIGHT // 2)

                # cover the current display value with the updated value in green
                cell_val = canvas.create_text(*posVal, text=str(cur.key), font=FOUND_FONT, fill=FOUND_COLOR)

                # add the green value to findDisplayObjects for cleanup later
                findDisplayObjects.append(cell_val)

                # update the display
                window.update()

                cleanup += findDisplayObjects
                return pos

            # if the value hasn't been found, wait 1 second, and then move the arrow over one cell
            time.sleep(self.speed(1))
            cur=cur.next
            pos+=1
            x = pos % LEN_ROW * (CELL_WIDTH + CELL_GAP) + LL_X0 + CELL_WIDTH / 2
            y = pos // LEN_ROW * (CELL_HEIGHT + ROW_GAP) + LL_Y0
            canvas.delete(arrow)
            arrow = canvas.create_line(x, y - 40, x, y, arrow="last", fill='red')
            findDisplayObjects.append(arrow)

            if not running:
                break

        cleanup += findDisplayObjects
        return None

    def display_neatly(self):
        canvas.delete("all")
        n = self.first
        pos=0
        while n:
            ll.insertElem(n, pos)
            n= n.next
            pos+=1


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
    if entered_text:
        val = int(entered_text)
        result = ll.clickFind(val)
        if result != None:
            txt = "Found!"
        else:
            txt = "Value not found"
        outputText.set(txt)

def clickInsert():
    if window.insert_button_counter == 0:
        outputText.set("Enter item of key to insert and click insert")
        window.insert_button_counter+=1
    elif window.insert_button_counter == 1:
        entered_text = textBox.get()
        if entered_text:
            val = int(entered_text)
            if len(ll) >= MAX_SIZE:
                outputText.set("Error! Linked List is already full.")
                window.insert_button_counter=0
            elif val < 100:
                ll.insert(int(entered_text))
                ll.insertElem(ll.first, pos =-1)
                outputText.set("Click insert again to redraw list neatly")
                window.insert_button_counter +=1
            else:
                outputText.set("Input value must be an integer from 0 to 99.")
                window.insert_button_counter=0
        textBox.delete(0, END)
    else:
        ll.display_neatly()
        window.insert_button_counter=0


def clickDelete():
    pass

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
    findButton = Button(operations, text="Find", command= lambda: onClick(clickFind))
    findButton.grid(row=1, column=0, padx=8, sticky=(E, W))
    insertButton = Button(operations, text="Insert", command= lambda: onClick(clickInsert))
    insertButton.grid(row=2, column=0, padx=8, sticky=(E, W))
    deleteValueButton = Button(operations, text="Delete", command= lambda: onClick(clickDelete))
    deleteValueButton.grid(row=3, column=0, padx=8, sticky=(E, W))
    separator = Frame(operations, width=2, bg=OPERATIONS_BORDER)
    separator.grid(row=1, column=3, rowspan=3, sticky=(N, E, W, S))
    buttons = [findButton, insertButton, deleteValueButton]
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
window.title("Linked List")
canvas.pack()

bottomframe = Frame(window)
bottomframe.pack(side=BOTTOM)
operationsUpper = LabelFrame(bottomframe, text="Operations")
operationsUpper.pack(side=TOP)
operationsBorder = Frame(operationsUpper, padx=2, pady=2, bg=OPERATIONS_BORDER)
operationsBorder.pack(side=TOP)
operations = Frame(operationsBorder, bg=OPERATIONS_BG)
operations.pack(side=LEFT)
operationsLower = Frame(bottomframe)
operationsLower.pack(side=BOTTOM)

#Label(bottomframe, text="Find:", font=CONTROLS_FONT + ('bold',)).grid(row=0, column=0, sticky=W)
vcmd = (window.register(validate),
        '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
textBox = Entry(operations, width=20, bg="white", validate='key', validatecommand=vcmd)
textBox.grid(row=2, column=2, padx=8, sticky=E)
scaleDefault = 100
scale = Scale(operationsLower, from_=1, to=200, orient=HORIZONTAL, sliderlength=15)
scale.grid(row=0, column=1, sticky=W)
scale.set(scaleDefault)
scaleLabel = Label(operationsLower, text="Speed:", font=CONTROLS_FONT)
scaleLabel.grid(row=0, column=0, sticky=W)

outputText = StringVar()
outputText.set('')
output = Label(operationsLower, textvariable=outputText, font=CONTROLS_FONT + ('italic',), fg="blue")
output.grid(row=0, column=3, sticky=(E, W))
operationsLower.grid_columnconfigure(3, minsize=160)

# exit button
Button(operationsLower, text="EXIT", width=0, command=close_window)\
    .grid(row=0, column=4, sticky=E)

window.insert_button_counter = 0

cleanup = []
ll = LinkedList()
buttons = makeButtons()
for i in range(13,0,-1):
    ll.insert(i)
ll.display_neatly()
window.mainloop()

'''
Useful Links:
http://effbot.org/zone/tkinter-complex-canvas.htm
https://mail.python.org/pipermail/python-list/2000-December/022013.html
'''

# TODO:
# Find is working, insert and delete are not