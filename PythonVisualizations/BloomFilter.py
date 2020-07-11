from tkinter import *
import re
try:
    from BitHash import BitHash
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .BitHash import BitHash
    from .drawable import *
    from .VisualizationApp import *

# Regular expression for false positive fraction
fraction = re.compile(r'0?.\d+')

class BloomFilter(VisualizationApp):
    CANVAS_WIDTH=800
    CANVAS_HEIGHT=400
    CELL_SIZE = 14
    CELL_BORDER = 1
    BORDER_COLOR = 'black'
    ON_COLOR = 'blue'
    OFF_COLOR = 'white'
    PROBE_COLOR = 'red'
    PROBE_FAILED = 'gray60'
    INSERTED_FONT = (VisualizationApp.CONTROLS_FONT[0], 14)
    INSERTED_COLOR = 'darkblue'
    INSERTED_BG = 'wheat'
    BV_X0 = CELL_SIZE
    BV_Y0 = CELL_SIZE
    BV_ROW_HEIGHT = 5 * CELL_SIZE
    MAX_HASHES = 5
    
    def __init__(self, maxArgWidth=10, title="Bloom Filter", **kwargs):
        kwargs['maxArgWidth'] = maxArgWidth
        super().__init__(title=title, **kwargs)
        self.title = title
        self.buttons = self.makeButtons()
        self.determine_max_bits()
        self.newBloomFilter(5, 3, 0.05)

    # Get bounding coordinates of a cell in the bit vector
    # These are the coordinates within the border
    def bitCellCoords(self, i):
        row = i // self.bits_per_row
        col = i % self.bits_per_row
        upperLeft = (self.BV_X0 + col * self.CELL_SIZE + self.CELL_BORDER,
                     self.BV_Y0 + row * self.BV_ROW_HEIGHT + self.CELL_BORDER)
        return upperLeft + add_vector(upperLeft, (self.CELL_SIZE - 1, ) * 2)

    # Get point in center of a cell in the bit vector
    def bitCellCenter(self, i):
        upperLeft = self.bitCellCoords(i)
        return add_vector(upperLeft[:2], (self.CELL_SIZE // 2, ) * 2)

    # Create an arrow pointing to a cell in the bit vector starting
    # from an origin determined by the hash key
    def cellArrow(self, bit, hashKey, nHashes, color=PROBE_COLOR):
        tip = add_vector(self.bitCellCenter(bit), (0, self.CELL_SIZE))
        origin = ((hashKey + 1) / (nHashes + 1) * self.insertedBoxPos[0] / 5 +
                  self.insertedBoxPos[0] * 3 / 4,
                  self.insertedBoxPos[1] + self.CELL_SIZE)
        offset = (0, min(self.CELL_SIZE * 2, (origin[1] - tip[1]) / 4))
        p1 = subtract_vector(origin, offset)
        p4 = add_vector(tip, offset)
        delta = rotate_vector(
            multiply_vector(subtract_vector(p4, p1), 1/3),
            20 * max(-1, min(1, (p4[0] - p1[0]) / (p1[1] - p4[1]))))
        return self.canvas.create_line(
            *origin, *p1, *add_vector(p1, delta),
            *subtract_vector(p4, delta), *p4, *tip,
            smooth=True, splinesteps=20, arrow="last", width=2, fill=color)
    
    def __bitsNeeded(self, numKeys, numHashes, maxFalsePositive):
        # uses max false positive rate and # of hash functions to compute phi
        phi = (1.0 - (maxFalsePositive ** (1.0 / numHashes)))

        # uses phi, # of hash functions and number of keys to compute
        # the size of the bit vector needed to initialize the bloom filter
        nBits = float(numHashes) / (1.0 - (phi ** (1.0 / numKeys)))
        return int(nBits)  # make sure # of bits is a whole number

    # Create a Bloom filter that will store numKeys keys, using
    # numHashes hash functions, and that will have a false positive
    # rate of maxFalsePositive.
    # All attributes must be private.
    def newBloomFilter(self, numKeys, numHashes, maxFalsePositive):

        # of bits needed is the size to make the bit vector
        needed = self.__bitsNeeded(numKeys, numHashes, maxFalsePositive)
        if needed > self.max_bits:
            return 'Too many bits, {}, needed.  Can display only {}.'.format(
                needed, self.max_bits)
        self.__size = needed
        self.__bv = [0] * self.__size

        # parameters become attributes of the visualized Bloom fitler
        self.__numKeys = numKeys
        self.__numHashes = numHashes
        self.__maxFalsePositive = maxFalsePositive

        # attribute counter for each bit set to 1
        self.__numBitsSet = 0
        #parallel list that displays the contents of the bit vector
        self.__displayList = [0] * self.__size
        self.__inserted = set([])
        self.display()
        return ''
        
    # ANIMATION METHODS

    def setBit(self, bit, callEnviron):
        self.__bv[bit] = 1
        self.canvas.itemconfigure(
            self.__displayList[bit].display_shape, fill=self.ON_COLOR)
        self.__displayList[bit].color = self.ON_COLOR
        self.window.update()
        
    def insert(self, key):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        findDisplayObjects = []
        # before the 1st hash value there is no seed
        seed = 0

        # create number of hash values passed into the bloom filter
        for i in range(self.__numHashes):
            h = BitHash(key, seed)
            hv = h % self.__size

            callEnviron.add(self.cellArrow(hv, i, self.__numHashes))
            self.wait(0.05)
            
            # if location wasn't set, change the bit and increment bit counter
            if self.__bv[hv] == 0:
                self.setBit(hv, callEnviron)
                self.wait(0.05)
                self.__numBitsSet += 1

            # make old hash value new seed
            seed = h

        self.__inserted.add(key)
        self.updateInserted()
        self.cleanUp(callEnviron)

    # Returns True if key MAY have been inserted into the Bloom filter.
    # Returns False if key definitely hasn't been inserted into the BF.
    def find(self, key):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        # before the 1st hash value there is no seed
        seed = 0

        # Probe the Bloom filter for each hash value
        bits = 0
        for i in range(self.__numHashes):
            h = BitHash(key, seed)
            hv = h % self.__size

            probe = self.cellArrow(hv, i, self.__numHashes)
            callEnviron.add(probe)
            self.wait(0.05)
            
            # if location wasn't set, change the arrow highlight
            if self.__bv[hv] == 0:
                self.canvas.itemconfigure(probe, fill=self.PROBE_FAILED)
            else:
                self.canvas.itemconfigure(probe, fill=self.ON_COLOR)
                bits += 1
            self.wait(0.05)
            
            # make old hash value new seed
            seed = h

        self.cleanUp(callEnviron)
        return bits == self.__numHashes

    def determine_max_bits(self):
        canvasDimensions = self.widgetDimensions(self.canvas)
        self.bits_per_row = canvasDimensions[0] // self.CELL_SIZE - 2
        self.max_bits = max(
            (canvasDimensions[1] // self.BV_ROW_HEIGHT - 1) * self.bits_per_row,
            1)

    def display(self):
        self.canvas.delete("all")
        canvasDimensions = self.widgetDimensions(self.canvas)
        for n, bit in enumerate(self.__bv):
            cellCoords = self.bitCellCoords(n)
            border = self.canvas.create_rectangle(
                *add_vector(cellCoords, 
                            multiply_vector((-1, -1, 0, 0), self.CELL_BORDER)),
                outline=self.BORDER_COLOR, width=self.CELL_BORDER, fill='')
            # create display objects for the associated drawables
            color = self.ON_COLOR if bit else self.OFF_COLOR
            cell = self.canvas.create_rectangle(
                *cellCoords, fill=color, outline='')
            self.__displayList[n] = drawable(bit, color, cell, None)
        self.insertedBoxPos = self.bitCellCoords(
            self.max_bits + self.bits_per_row // 2)[:2] + subtract_vector(
                canvasDimensions, (self.CELL_SIZE, ) * 2)
        self.insertedBox = self.canvas.create_rectangle(
            *self.insertedBoxPos, fill=self.INSERTED_BG)
        self.insertedKeys = self.canvas.create_text(
            *add_vector(self.insertedBoxPos, (self.CONTROLS_FONT[1], ) * 2),
            anchor=NW, font=self.INSERTED_FONT, fill=self.INSERTED_COLOR,
            state=DISABLED)
        self.updateInserted()

        self.window.update()

    def updateInserted(self):
        text = 'Inserted: {}'.format(
            '<none>' if len(self.__inserted) == 0 else
            ', '.join(self.__inserted))
        
        # Break text into lines at whitespace
        lines = text.split('\n')
        max_chars = (self.insertedBoxPos[2] - self.insertedBoxPos[0]) // (
            int(self.INSERTED_FONT[1] / 2))
        while len(lines[-1]) > max_chars:
            words = lines[-1].split()
            line = ''
            while words and len(line) + len(words[0]) + 1 < max_chars:
                line += words.pop(0) + ' '
            lines[-1:] = [line, ' '.join(words)]
        self.canvas.itemconfigure(self.insertedKeys, text = '\n'.join(lines))

    # Button functions
    def clickFind(self):
        entered_text = self.getArgument(0)
        if not entered_text:
            self.setMessage("No text entered")
            return
        
        self.setMessage("{} {} in filter".format(
            entered_text, "may be" if self.find(str(entered_text)) else "not"))
        for i in [1, 2]:
            self.clearArgument(i)

    def clickInsert(self):
        entered_text = self.getArgument(0)
        if entered_text:
            self.insert(str(entered_text))
        self.setMessage('{} inserted'.format(entered_text))
        for i in [1, 2]:
            self.clearArgument(i)

    def clickNew(self):
        self.determine_max_bits()
        nKeys, nHashes, probability = self.getArguments()
        msg = ''
        if nKeys.isdigit() and int(nKeys) > 0:
            nKeys = int(nKeys)
        else:
            msg += 'Must provide positive number of keys. '
        if nHashes.isdigit():
            if 0 < int(nHashes) and int(nHashes) < self.MAX_HASHES:
                nHashes = int(nHashes)
            else:
                msg += '#Hashes must be between 0 and {}. '.format(
                    self.MAX_HASHES)
        else:
            msg += 'Must provide number of hashes. '
        if fraction.match(probability):
            probability = float(probability)
        else:
            msg += 'False positive must be fraction like .05'
        if msg:
            self.setMessage(msg)
            return
        self.setMessage(self.newBloomFilter(nKeys, nHashes, probability))
        
    def makeButtons(self):
        vcmd = (self.window.register(makeWidthValidate(self.maxArgWidth)), 
                '%P')
        insertButton = self.addOperation(
            "Insert", self.clickInsert, numArguments=1, validationCmd=vcmd)
        findButton = self.addOperation(
            "Search", self.clickFind, numArguments=1, validationCmd=vcmd)
        newButton = self.addOperation(
            "New", self.clickNew, numArguments=3, validationCmd=vcmd,
            helpText='Enter string or #keys, #hashes, & false positive%')
        self.addAnimationButtons()
        return [findButton, insertButton]

if __name__ == '__main__':
    bloomFilter = BloomFilter()

    bloomFilter.runVisualization()
