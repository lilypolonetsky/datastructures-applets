from tkinter import *
import re
try:
    from coordinates import *
    from Hashing import *
    from VisualizationApp import *
    from HashBase import *
except ModuleNotFoundError:
    from .coordinates import *
    from .Hashing import *
    from .VisualizationApp import *
    from .HashBase import *

V = vector

# Regular expression for false positive fraction
fraction = re.compile(r'0*\.\d+')

class BloomFilter(HashBase):
    CANVAS_WIDTH=800
    CANVAS_HEIGHT=400
    CELL_SIZE = 14
    CELL_BORDER = 1
    BORDER_COLOR = 'black'
    ON_COLOR = 'blue'
    OFF_COLOR = 'white'
    REINSERT_COLOR = 'sky blue'
    PROBE_COLOR = 'red'
    PROBE_FAILED = 'gray60'
    INSERTED_FONT = (VisualizationApp.CONTROLS_FONT[0], -14)
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
        return upperLeft + (V(upperLeft) + V((self.CELL_SIZE - 1, ) * 2))

    # Get point in center of a cell in the bit vector
    def bitCellCenter(self, i):
        upperLeft = self.bitCellCoords(i)
        return V(upperLeft[:2]) + V((self.CELL_SIZE // 2, ) * 2)

    # Create an arrow pointing to a cell in the bit vector starting
    # from an origin determined by the hash key
    def cellArrow(self, bit, hashKey, nHashes, color=PROBE_COLOR):
        tip = V(self.bitCellCenter(bit)) + V(0, self.CELL_SIZE * 5 / 8)
        hashOutputCoords = self.hashOutputCoords()
        sep = 10
        origin = (hashOutputCoords[0] +
                  (hashKey + 1) / (nHashes + 3) * 
                  (self.insertedBoxPos[0] - hashOutputCoords[0]),
                  hashOutputCoords[1] - sep)
        offset = (0, min(self.CELL_SIZE * 2, (origin[1] - tip[1]) / 4))
        p1 = V(origin) - V(offset)
        p4 = V(tip) + V(offset)
        delta = V(V(V(p4) - V(p1)) / 3).rotate(
            -20 * max(-1, min(1, (p4[0] - p1[0]) / (p1[1] - p4[1]))))
        steps = int(max(abs(tip[0] - origin[0]), abs(tip[1] - origin[1])))
        return self.canvas.create_line(
            *origin, *p1, *(V(p1) + V(delta)), *(V(p4) - V(delta)), *p4, *tip,
            smooth=True, splinesteps=steps, arrow=LAST, width=2, fill=color)
    
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
        
        # list of canvas rectangles for each bit of the vector
        self.__displayList = [0] * self.__size
        self.__inserted = set([])
        self.display()
        return 'New Bloom filter using {} bits'.format(self.__size)
        
    # ANIMATION METHODS

    def setBit(self, bit, callEnviron):
        self.__bv[bit] = 1
        if self.__displayList[bit]:
            self.canvas.itemconfigure(self.__displayList[bit],
                                      fill=self.ON_COLOR)
        
    def insert(self, key):
        callEnviron = self.createCallEnvironment()

        findDisplayObjects = []
        # before the 1st hash value there is no seed
        seed = 0

        # create number of hash values passed into the bloom filter
        outputChars = []
        for i in range(self.__numHashes):
            h = bitHash(key, seed)
            hv = h % self.__size

            if self.showHashing.get():
                if outputChars:  # Move last output, if any, to seed input
                    rightmost = self.canvas.coords(outputChars[0])
                    seedCoords = self.hashSeedCoords()
                    sep = 10
                    up = seedCoords[1] - (self.hasher['BBox'][3] + sep)
                    down = self.hasher['BBox'][3] + sep - rightmost[1]
                    self.moveItemsBy(
                        outputChars, (0, down), steps=5, sleepTime=.01)
                    self.moveItemsBy(
                        outputChars, (seedCoords[0] - rightmost[0], 0),
                        steps=10, sleepTime=.01)
                    self.moveItemsBy(
                        outputChars, (0, up), steps=5, sleepTime=.01)
                    for char in outputChars:
                        self.canvas.delete(char)
                        callEnviron.discard(char)
                outputChars = self.animateStringHashing(
                    key, seed, h, callEnviron=callEnviron)
            
            callEnviron.add(self.cellArrow(hv, i, self.__numHashes))
            self.wait(0.05)
            
            # if location wasn't set, change the bit and increment bit counter
            if self.__bv[hv] == 0:
                self.setBit(hv, callEnviron)
                self.wait(0.05)
                self.__numBitsSet += 1
            else: # If location was set, mark with a temporary mark
                callEnviron.add(self.canvas.create_rectangle(
                    *self.bitCellCoords(hv), fill=self.REINSERT_COLOR,
                    outline=''))

            # make old hash value new seed
            seed = h

        self.__inserted.add(key)
        self.updateInserted()
        self.cleanUp(callEnviron)

    # Returns True if key MAY have been inserted into the Bloom filter.
    # Returns False if key definitely hasn't been inserted into the BF.
    def find(self, key):
        callEnviron = self.createCallEnvironment()

        # before the 1st hash value there is no seed
        seed = 0

        # Probe the Bloom filter for each hash value
        outputChars = []
        bits = 0
        for i in range(self.__numHashes):
            h = bitHash(key, seed)
            hv = h % self.__size
            
            if self.showHashing.get():
                if outputChars:  # Move last output, if any, to seed input
                    rightmost = self.canvas.coords(outputChars[0])
                    seedCoords = self.hashSeedCoords()
                    sep = 10
                    up = seedCoords[1] - (self.hasher['BBox'][3] + sep)
                    down = self.hasher['BBox'][3] + sep - rightmost[1]
                    self.moveItemsBy(
                        outputChars, (0, down), steps=5, sleepTime=.01)
                    self.moveItemsBy(
                        outputChars, (seedCoords[0] - rightmost[0], 0),
                        steps=10, sleepTime=.01)
                    self.moveItemsBy(
                        outputChars, (0, up), steps=5, sleepTime=.01)
                    for char in outputChars:
                        self.canvas.delete(char)
                        callEnviron.discard(char)
                outputChars = self.animateStringHashing(
                    key, seed, h, callEnviron=callEnviron)

            probe = self.cellArrow(hv, i, self.__numHashes)
            callEnviron.add(probe)
            self.wait(0.05)
            
            # if location wasn't set, change the arrow highlight
            if self.__bv[hv] == 0:
                self.canvas.itemconfigure(probe, fill=self.PROBE_FAILED)
                break
            else:
                self.canvas.itemconfigure(probe, fill=self.ON_COLOR)
                bits += 1
            self.wait(0.05)
            
            # make old hash value new seed
            seed = h

        self.cleanUp(callEnviron)
        return bits == self.__numHashes

    def determine_max_bits(self):
        canvasDimensions = widgetDimensions(self.canvas)
        self.bits_per_row = canvasDimensions[0] // self.CELL_SIZE - 2
        self.max_bits = max(
            (canvasDimensions[1] // self.BV_ROW_HEIGHT - 1) * self.bits_per_row,
            1)

    def display(self):
        self.canvas.delete("all")
        canvasDimensions = widgetDimensions(self.canvas)
        for n, bit in enumerate(self.__bv):
            cellCoords = self.bitCellCoords(n)
            border = self.canvas.create_rectangle(
                *(V(cellCoords) + V(V(-1, -1, 0, 0) * self.CELL_BORDER)),
                outline=self.BORDER_COLOR, width=self.CELL_BORDER, fill='')
            # create display objects for the associated bit on the canvas
            self.__displayList[n] = self.canvas.create_rectangle(
                *cellCoords, fill=self.ON_COLOR if bit else self.OFF_COLOR,
                outline='')
        self.createHasher()
        self.insertedBoxPos = self.bitCellCoords(
            self.max_bits + self.bits_per_row // 2)[:2] + (
                V(canvasDimensions) - V((self.CELL_SIZE, ) * 2))
        self.insertedBox = self.canvas.create_rectangle(
            *self.insertedBoxPos, fill=self.INSERTED_BG)
        self.insertedKeys = self.canvas.create_text(
            *(V(self.insertedBoxPos) + V((abs(self.CONTROLS_FONT[1]), ) * 2)),
            anchor=NW, font=self.INSERTED_FONT, fill=self.INSERTED_COLOR)
        self.updateInserted()

        self.window.update()

    def updateInserted(self):
        text = 'Inserted: {}'.format(
            '<none>' if len(self.__inserted) == 0 else
            ', '.join(self.__inserted))
        
        # Break text into lines at whitespace
        lines = text.split('\n')
        txtWidth = lambda txt: textWidth(self.INSERTED_FONT, txt)
        pad = abs(self.INSERTED_FONT[1])
        maxWidth = self.insertedBoxPos[2] - self.insertedBoxPos[0] - pad
        while txtWidth(lines[-1]) > maxWidth:
            words = lines[-1].split()
            line = ''
            while words and txtWidth(line + words[0] + ' ') < maxWidth:
                line += words.pop(0) + ' '
            lines[-1:] = [line, ' '.join(words)]
        self.canvas.itemconfigure(self.insertedKeys, text = '\n'.join(lines))
        self.clickShowInserts()
        
    # Button functions
    def clickFind(self):
        entered_text = self.getArgument(0)
        if not entered_text:
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
            self.setMessage("No text entered")
            return
        
        if entered_text.isspace():
            self.setMessage("Key contains only whitespace")
        
        self.setMessage("{} {} in filter".format(
            repr(entered_text),
            "may be" if self.find(str(entered_text)) else "not"))
        for i in [1, 2]:
            self.clearArgument(i)

    def clickInsert(self):
        entered_text = self.getArgument(0)

        if entered_text.isspace():
            self.setMessage("Key contains only whitespace")
            return
        
        if entered_text:
            for i in [1, 2]:
                self.clearArgument(i)
            self.insert(str(entered_text))
            self.setMessage('{} inserted'.format(repr(entered_text)))

    def clickNew(self):
        self.determine_max_bits()
        nKeys, nHashes, probability = self.getArguments()
        msg = ''
        if nKeys.isdigit() and int(nKeys) > 0:
            nKeys = int(nKeys)
        else:
            msg += 'Must provide positive number of keys. '
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
        if nHashes.isdigit():
            if 0 < int(nHashes) and int(nHashes) < self.MAX_HASHES:
                nHashes = int(nHashes)
            else:
                msg += '#Hashes must be between 0 and {}. '.format(
                    self.MAX_HASHES)
                self.setArgumentHighlight(1, self.ERROR_HIGHLIGHT)
        else:
            msg += 'Must provide number of hashes. '
            self.setArgumentHighlight(1, self.ERROR_HIGHLIGHT)
        if fraction.match(probability):
            probability = float(probability)
        if not isinstance(probability, float) or (
                probability <= 0 or 1 <= probability):
            msg += 'False positive rate must be a fraction like .05'
            self.setArgumentHighlight(2, self.ERROR_HIGHLIGHT)
        if msg:
            self.setMessage(msg)
            return
        self.setMessage(self.newBloomFilter(nKeys, nHashes, probability))

    def clickShowHashing(self):
        if not self.showHashing.get():
            self.positionHashBlocks(0)

    def clickShowInserts(self):
        self.canvas.itemconfigure(
            self.insertedKeys,
            state=NORMAL if self.showInserts.get() else HIDDEN)
        
    def makeButtons(self):
        vcmd = (self.window.register(
            makeFilterValidate(self.maxArgWidth, ',')), '%P')
        insertButton = self.addOperation(
            "Insert", self.clickInsert, numArguments=1, validationCmd=vcmd,
            helpText='Insert a key into the Bloom filter',
            argHelpText=['key'])
        findButton = self.addOperation(
            "Search", self.clickFind, numArguments=1, validationCmd=vcmd,
            helpText='Search for a key in the Bloom filter',
            argHelpText=['key'])
        newButton = self.addOperation(
            "New", self.clickNew, numArguments=3, validationCmd=vcmd,
            helpText='Create new filter for #keys, #hashes, & false positive%',
            argHelpText=['number of keys', 'number of hashes',
                         'false positive probability'])
        self.showHashing = IntVar()
        self.showHashing.set(1)
        showHashingButton = self.addOperation(
            "Animate hashing", self.clickShowHashing, buttonType=Checkbutton,
            variable=self.showHashing, cleanUpBefore=False,
            helpText='Show/hide animation during hashing')
        self.showInserts = IntVar()
        self.showInserts.set(1)
        self.showInsertsButton = self.addOperation(
            "Show inserted", self.clickShowInserts, buttonType=Checkbutton,
            variable=self.showInserts, cleanUpBefore=False, mutex=False,
            helpText='Show/hide list of inserted keys')
        self.addAnimationButtons()
        return [findButton, insertButton, newButton, self.showInsertsButton]

    def enableButtons(self, enable=True):
        super().enableButtons(enable=enable)
        widgetState(self.showInsertsButton, NORMAL)
    
def makeFilterValidate(maxWidth, exclude=''):
    "Register this with one parameter: %P"
    return lambda value_if_allowed: (
        len(value_if_allowed) <= maxWidth and
        all(c not in exclude for c in value_if_allowed))

if __name__ == '__main__':
    nonneg, negative, options, otherArgs = categorizeArguments(sys.argv[1:])
    bloomFilter = BloomFilter()
    showHashing = not '-S' in options and (
        '-s' in options or bloomFilter.showHashing.get())
    showInserts = not '-I' in options and (
        '-i' in options or bloomFilter.showInserts.get())
    bloomFilter.showInserts.set(showInserts)
    bloomFilter.clickShowInserts()
    if nonneg + negative + otherArgs:
        bloomFilter.showHashing.set(0)
        try:
            for arg in sys.argv[1:]:
                if arg not in options:
                    bloomFilter.insert(arg)
                    bloomFilter.cleanUp()
        except UserStop:
            bloomFilter.cleanUp()
        
    bloomFilter.showHashing.set(showHashing)
    bloomFilter.runVisualization()
