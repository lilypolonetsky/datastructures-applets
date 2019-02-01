
from tkinter import *
from BitHash import BitHash
from BitVector import BitVector
from recordclass import recordclass

WIDTH = 1500
HEIGHT = 400

CELL_SIZE = 25
BF_X0 = 100
BF_Y0 = 100

class BloomFilter(object):
    Element = recordclass('Element', ['val', 'display_shape', 'display_val'])
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

    # ANIMATION METHODS

    def insert(self, key):
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

                canvas.create_text(xpos + (CELL_SIZE / 2), BF_Y0 + (CELL_SIZE / 2), text='1',
                                   font=('Helvetica', '20')) #need to figure out how to remove the 0 - might have to redraw the bitvector
                self.__numBitsSet += 1


            # make old hash value new seed
            seed = h
        window.update()
    def display(self):
        canvas.delete("all")
        xpos = 10 #trying to make is so that it isn't shifted to the right
        ypos = BF_Y0

        # go through each Element in the list
        # for n in bitVector ????
        for n in self.__bv: #how do I make it have element attributes like in the Array?

            # create display objects for the associated Elements
            cell = canvas.create_rectangle(xpos, ypos, xpos + CELL_SIZE, ypos + CELL_SIZE)
            cell_val = canvas.create_text(xpos + (CELL_SIZE / 2), ypos + (CELL_SIZE / 2), text=n,
                                          font=('Helvetica', '20'))

            # save the display objects to the appropriate attributes of the Element object
            #n.display_shape = cell
            #n.display_val = cell_val

            # increment xpos
            xpos += CELL_SIZE

        window.update()

#CHANGE TO STOP HASHING????
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
    findButton.grid(row=2, column=1)
    insertButton = Button(bottomframe, text="Insert", width=7, command= lambda: onClick(clickInsert))
    insertButton.grid(row=2, column=2)
    buttons = [findButton, insertButton]
    return buttons

window = Tk()
frame = Frame(window)
frame.pack()

waitVar = BooleanVar()

canvas = Canvas(frame, width=WIDTH, height=HEIGHT)
window.title("Bloom Filter")
canvas.pack()

bottomframe = Frame(window)
bottomframe.pack(side=BOTTOM)

textBox = Entry(bottomframe, width=20, bg="white")
textBox.grid(row=4, column=0, sticky=W)

outputText = StringVar()
outputText.set('')
output = Label(bottomframe, textvariable=outputText, font="none 12 bold")
output.grid(row=4, column=1, sticky=E)

# exit button
Button(bottomframe, text="EXIT", width=4, command=close_window).grid(row=6, column=3, sticky=W)

cleanup = []
numKeys = 5 #this effects the length of the bitvector displayed
numHashes = 4
maxFalse = 0.05
bf = BloomFilter(numKeys, numHashes, maxFalse)
buttons = makeButtons()



### PUT BLOOM FILTER MAIN CODE HERE !!!!!!!!
# fin = open("wordlist.txt")
#
# for i in range(numKeys):
#     line = fin.readline()
#     bf.insert(line)
#bf.insert("hello world it's me Sarah")
#fin.close()
bf.display()

window.mainloop()

#To Do:
# make arrows point to the most recent bits flipped in bv
#make it so that user can insert keys and see them hash instead of reading text file