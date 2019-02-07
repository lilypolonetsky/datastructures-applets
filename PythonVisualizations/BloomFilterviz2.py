from tkinter import *
from BitHash import BitHash
from BitVector import BitVector
from recordclass import recordclass

WIDTH = 850
HEIGHT = 250

CELL_SIZE = 25
BF_X0 = 100
BF_Y0 = 100

class BloomFilter(object):
    Element = recordclass('Element', ['val','display_shape', 'display_val'])
    Element.__new__.__defaults__ = (None,) * len(Element._fields)

    # See Slide 12 for the math needed to do this.
    def __bitsNeeded(self, numKeys, numHashes, maxFalsePositive):
        # uses max false positive rate and # of hash functions to compute phi
        phi = (1.0 - (maxFalsePositive ** (1.0 / numHashes)))

        # uses phi, # of hash functions and number of keys to compute
        # the size of the bit vector needed to initialize the bloom filter
        nBits = float(numHashes) / (1.0 - (phi ** (1.0 / numKeys)))
        return int(nBits)  # make sure # of bits is a whole number

    # Create a Bloom Filter that will store numKeys keys, using
    # numHashes hash functions, and that will have a false positive
    # rate of maxFalsePositive.
    # All attributes must be private.
    def __init__(self, numKeys, numHashes, maxFalsePositive):

        # of bits needed is the size to make the bit vector
        self.__size = self.__bitsNeeded(numKeys, numHashes, maxFalsePositive)
        self.__bv = BitVector(size=self.__size)

        # parameters passed into the constructor become attributes
        self.__numKeys = numKeys
        self.__numHashes = numHashes
        self.__maxFalsePositive = maxFalsePositive

        # attribute counter for each bit set to 1
        self.__numBitsSet = 0
        #parallel list that displays the contents of the bit vector
        self.__displayList = [0] * self.__size

    # ANIMATION METHODS

    def insert(self, key):
        global cleanup
        findDisplayObjects = []
        # before the 1st hash value there is no seed
        seed = 0

        # create number of hash values passed into the bloom filter
        for i in range(self.__numHashes):
            h = BitHash(key, seed)
            hv = h % self.__size

            # if location wasn't set, change the bit and increment bit counter
            if self.__bv[hv] == 0:
                self.__bv[hv] = 1
                xpos = CELL_SIZE * hv + 10

                self.__displayList[hv].val = 1
                # deletes value from the list and display's the new one
                canvas.delete(self.__displayList[hv].display_val)
                self.__displayList[hv].display_val = canvas.create_text(xpos + (CELL_SIZE / 2), BF_Y0 + (CELL_SIZE / 2), text='1',
                                   font=('Helvetica', '20'))
                self.__displayList[hv].display_val = canvas.create_text(xpos + (CELL_SIZE / 2),
                                                                        BF_Y0 + (CELL_SIZE / 2),
                                                                        text='1',
                                                                        font=('Helvetica', '20'), fill='blue')
                findDisplayObjects.append(self.__displayList[hv].display_val)
                window.update()
                cleanup += findDisplayObjects
                self.__numBitsSet += 1



            # make old hash value new seed
            seed = h
        window.update()

    # Returns True if key MAY have been inserted into the Bloom filter.
    # Returns False if key definitely hasn't been inserted into the BF.
    def find(self, key):
        global cleanup
        findDisplayObjects = []
        self.display()
        # draw an arrow over the first cell
        x = (CELL_SIZE / 2)
        y0 = BF_Y0 - 40
        y1 = BF_Y0 - 15
        # before the 1st hash value there is no seed
        seed = 0

        # create number of hash values passed into the bloom filter
        for i in range(self.__numHashes):
            window.update()
            h = BitHash(key, seed)
            hv = h % self.__size
            xpos = CELL_SIZE * hv + 20
            # check for the key not inserted, return false
            if self.__bv[hv] == 0:
                return False
            else:
                arrow = canvas.create_line(xpos, y0, xpos, y1, arrow="last", fill='red')
                findDisplayObjects.append(arrow)
                self.__displayList[hv].display_val = canvas.create_text(xpos + (CELL_SIZE / 2)-10, BF_Y0 + (CELL_SIZE / 2),
                                                                        text='1',
                                                                        font=('Helvetica', '20'),fill='green2')
                findDisplayObjects.append(self.__displayList[hv].display_val)
                window.update()
                cleanup += findDisplayObjects
            # make old hash value new seed
            seed = h
        cleanup += findDisplayObjects
        # all bits were set
        return True

    def display(self):
        canvas.delete("all")
        xpos = 10
        ypos = BF_Y0

        for n in range(len(self.__displayList)):

            # create display objects for the associated Elements
            cell = canvas.create_rectangle(xpos, ypos, xpos + CELL_SIZE, ypos + CELL_SIZE)
            cell_val = canvas.create_text(xpos + (CELL_SIZE / 2), ypos + (CELL_SIZE / 2), text=self.__bv[n],
                                          font=('Helvetica', '20'))

            self.__displayList[n] = BloomFilter.Element(self.__bv[n], cell, cell_val)

            # increment xpos
            xpos += CELL_SIZE

        window.update()


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
        result = bf.find(str(entered_text))
        if result:
            txt = "Found!"
        else:
            txt = "Value not found"
        outputText.set(txt)

def clickInsert():
    entered_text = textBox.get()
    if entered_text:
        bf.insert(str(entered_text))
        textBox.setvar('')

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
    findButton = Button(bottomframe, text="Find", width=7, command= lambda: onClick(clickFind))
    findButton.grid(row=3, column=1)
    insertButton = Button(bottomframe, text="Insert", width=7, command= lambda: onClick(clickInsert))
    insertButton.grid(row=3, column=2)
    buttons = [findButton, insertButton]
    return buttons

window = Tk()
frame = Frame(window)
frame.pack()

waitVar = BooleanVar()

canvas = Canvas(frame, width=WIDTH, height=HEIGHT,bg="white")
window.title("Bloom Filter")
canvas.pack()

bottomframe = Frame(window)
bottomframe.pack(side=BOTTOM)

textBox = Entry(bottomframe, width=20, bg="white")
textBox.grid(row=3, column=0, sticky=W)

outputText = StringVar()
outputText.set('')
output = Label(bottomframe, textvariable=outputText, font="none 12 bold")
output.grid(row=4, column=1, sticky=E)

# exit button
Button(bottomframe, text="EXIT", width=4, command=close_window).grid(row=3, column=3, sticky=W)

cleanup = []
numKeys = 5 #this effects the length of the bitvector displayed
numHashes = 4
maxFalse = 0.05
bf = BloomFilter(numKeys, numHashes, maxFalse)
buttons = makeButtons()

### PUT BLOOM FILTER MAIN CODE HERE !!!!!!!!
bf.display()

window.mainloop()

#To Do:
# make arrows point to the most recent bits flipped in bv
#make it so that user can insert keys and see them hash instead of reading text file