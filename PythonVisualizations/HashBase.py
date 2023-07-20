from tkinter import *
from math import *

try:
    from coordinates import *
    from tkUtilities import *
    from drawnValue import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .coordinates import *
    from .tkUtilities import *
    from .drawnValue import *
    from .VisualizationApp import *

V = vector

class HashBase(VisualizationApp):
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    MAX_CELLS = 61
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def createHasher(
            self, x0=100, y0=314, x1=160, y1=386,
            fill='saddle brown', sections=7, label='HASH', amplitude=0.1,
            font=VisualizationApp.VALUE_FONT, foreground='white'):
        """Create canvas items depicting a hash 'engine' that converts
        strings to numbers.  The hasher will fit within the bounding
        box reaching the maximal vertical dimensions when grinding.
        """
        sections = max(2, sections)
        self.hasher = {
            'Blocks': [None] * sections,
            'BBox': (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)),
            'SectionHeight': abs(y1 - y0) * (1 - 2 * amplitude),
            'SectionOffset': abs(y1 - y0) * amplitude,
            'SectionWidth': abs(x1 - x0) / max(2, sections),
            'Phase': 0,
            }
        self.hasher['Blocks'] = [
            self.canvas.create_rectangle(
                *self.hashBlockCoords(b), fill=fill, outline=None, width=0)
            for b in range(sections)]
        self.hasher['Label'] = self.canvas.create_text(
            (x0 + x1) / 2, (y0 + y1) / 2, text=label, font=font,
            fill=foreground, state=DISABLED)
        
    def hashBlockCoords(self, blockIndex, phase=None):
        h = self.hasher
        if phase is not None:
            h['Phase'] = phase
        fromEnd = min(blockIndex, len(h['Blocks']) - 1 - blockIndex)
        p = h['Phase'] * (1 + fromEnd) + (blockIndex % 2) * pi
        x0 = h['BBox'][0] + h['SectionWidth'] * blockIndex
        x1 = h['BBox'][0] + h['SectionWidth'] * (blockIndex + 1)
        y0 = h['BBox'][1] + h['SectionOffset'] * (sin(p) + 0.5)
        y1 = y0 + h['SectionHeight']
        return (x0, y0, x1, y1)
            
    def hashInputCoords(self, nInputs=2):
        h = self.hasher
        return (h['BBox'][0],
                (h['BBox'][1] * nInputs + h['BBox'][3]) / (nInputs + 1))

    def hashSeedCoords(self):
        h = self.hasher
        return (h['BBox'][0], (h['BBox'][1] + h['BBox'][3] * 2) / 3)

    def hashOutputCoords(self):
        h = self.hasher
        return (h['BBox'][2], (h['BBox'][1] + h['BBox'][3]) / 2)

    def incrementHasherPhase(self, increment=0.2):
        self.hasher['Phase'] += increment
        for bIndex, block in enumerate(self.hasher['Blocks']):
            self.canvas.coords(block, *self.hashBlockCoords(bIndex))

    def positionHashBlocks(self, phase=None):
        for bIndex, block in enumerate(self.hasher['Blocks']):
            self.canvas.coords(block, *self.hashBlockCoords(bIndex, phase))
        
    def animateStringHashing(
            self, text, seed, hashed, sleepTime=0.01,
            callEnviron=None, dx=2, font=VisualizationApp.VARIABLE_FONT, 
            color=VisualizationApp.VARIABLE_COLOR):
        """Animate text and seed flowing into left of hasher and producing
        hashed output string while hasher churns.  Move characters by dx
        on each animation step. Returns list of canvas items for output
        characters"""
        
        if not self.hasher:
            return
        h = self.hasher

        # Create individual character text items to feed into hasher
        text, seed, hashed = str(text), str(seed), str(hashed)
        inputCoords = self.hashInputCoords()
        seedCoords = self.hashSeedCoords()
        outputCoords = self.hashOutputCoords()
        charWidth = textWidth(font, 'W')
        characters = set([
            self.canvas.create_text(
                inputCoords[0] - ((len(text) - i) * charWidth),
                inputCoords[1], text=c, font=font, fill=color, state=DISABLED)
            for i, c in enumerate(text)] + [
                    self.canvas.create_text(
                        seedCoords[0] - ((len(seed) - i) * charWidth),
                        seedCoords[1], text=c, font=font, fill=color,
                        state=DISABLED)
                    for i, c in enumerate(seed)])
        for c in characters:
            self.canvas.lower(c)
        if callEnviron:
            callEnviron |= characters

        output = []        # Characters of hashed output
        pad = abs(font[1])
        rightEdge = h['BBox'][2] + pad
        leftmostOutput = rightEdge

        # While there are input characters or characters yet to output or
        # characters to move out of hasher
        while (characters or len(output) < len(hashed) or
               leftmostOutput < rightEdge):
            self.moveItemsBy(    # Move all characters
                characters.union(output), (dx, 0), sleepTime=sleepTime, steps=1)
            self.incrementHasherPhase()
            deletion = False
            for char in list(characters): # For all input characters
                coords = self.canvas.coords(char)  # See if they entered the
                if coords[0] - pad >= h['BBox'][0]: # hasher bounding box and
                    deletion = True       # delete them if they did
                    if callEnviron:
                        callEnviron.discard(char)
                    self.canvas.delete(char)
                    characters.discard(char)
                    
            if output:
                leftmostOutput = self.canvas.coords(output[-1])[0]

            # When there are characters to ouput and we've either already
            # output a character or deleted an input character and there
            # is room for the next output character, create it
            if (len(output) < len(hashed) and (output or deletion) and
                leftmostOutput >= rightEdge):
                output.append(
                    self.canvas.create_text(
                        max(leftmostOutput - charWidth, outputCoords[0]),
                        outputCoords[1], text=hashed[-(len(output) + 1)], 
                        font=font, fill=color, state=DISABLED))
                self.canvas.lower(output[-1])
                if callEnviron:
                    callEnviron.add(output[-1])
        return output

    def setupDisplay(self, nColumns=3, hasherHeight=70):
        'Define dimensions and coordinates for display items'
        canvasDimensions = (self.targetCanvasWidth, self.targetCanvasHeight)
        self.hasherHeight = hasherHeight
        self.nColumns = nColumns
        self.cellsPerColumn = math.ceil(self.MAX_CELLS / self.nColumns)
        self.columnWidth = self.targetCanvasWidth // self.nColumns
        self.column_x0 = min(self.columnWidth // 4, 60)
        self.cellHeight = (
            (canvasDimensions[1] - hasherHeight) // (self.cellsPerColumn + 2))
        self.outputFont = (self.VALUE_FONT[0],
                           max(self.VALUE_FONT[1], - self.cellHeight * 8 // 10))
        self.VALUE_FONT = (self.VALUE_FONT[0],
                           max(self.VALUE_FONT[1], - self.cellHeight * 7 // 10))
        self.cellIndexFont = (self.VARIABLE_FONT[0],
                              max(self.VALUE_FONT[1], -10))
        self.cellWidth = textWidth(self.VALUE_FONT,
                                   'W' * (self.maxArgWidth + 2))

    def cellColumn(self, index):
        return (index % len(self.table)) // self.cellsPerColumn
    
    def cellCoords(self, index):
        column = self.cellColumn(index)
        row = (index % len(self.table)) % self.cellsPerColumn
        x0 = self.columnWidth * column + self.column_x0
        y0 = (row + 1) * self.cellHeight
        return (x0, y0, 
                x0 + self.cellWidth - self.CELL_BORDER,
                y0 + self.cellHeight - self.CELL_BORDER)

    def cellCenter(self, index):
        return BBoxCenter(self.cellCoords(index))

    def cellArrowCoords(self, index):
        cellCoords = self.cellCoords(index)
        y = (cellCoords[1] + cellCoords[3]) / 2
        return cellCoords[0] - 50, y, cellCoords[0] - 18, y
        
    def newItemCoords(self, offCanvas=False):
        cell0 = self.cellCoords(0)   # Shift cell 0 coords off canvans
        delta = V(self.newValueCoords(offCanvas=offCanvas)) - V(BBoxCenter(cell0))
        return V(cell0) + V(delta * 2)

    def arrayCellDelta(self):
        half_border = self.CELL_BORDER // 2
        return (-half_border, -half_border,
                self.CELL_BORDER - half_border, self.CELL_BORDER - half_border)
    
    def arrayCellCoords(self, index):
        cell_coords = self.cellCoords(index)
        return V(cell_coords) + V(self.arrayCellDelta())
    
    def arrayIndexCoords(self, indexOrCoords, level=1):
        'Coordinates of an index arrow and anchor of its text label'
        cell_coords = (
            self.cellCoords(indexOrCoords) if isinstance(indexOrCoords, int)
            else indexOrCoords)
        tip = (cell_coords[0] - 18, (cell_coords[1] + cell_coords[3]) // 2)
        base = V(tip) - V((level * 12 + 6, 0))
        return (base + tip, base)
    
    def outputBoxCoords(
            self: 'Return the bounding box coordinates for an output box',
            font: 'Font to use in output box, default: outputFont' =None,
            pad: 'Padding from canvas edge' =4,
            nLines: 'Number of text lines in output box' =4):
        if font is None:
            font = getattr(self, 'outputFont', self.VALUE_FONT)
        lineHeight = textHeight(font, ' ')
        left = self.targetCanvasWidth * 4 // 10
        top = self.targetCanvasHeight - pad * 3 - lineHeight * nLines
        return (left, top,
                self.targetCanvasWidth - pad, self.targetCanvasHeight - pad)

    def attributeCoords(
            self: 'Return the text anchor coords for 2 hash table attributes',
            font: 'Font to use for attributes, default: VARIABLE_FONT' =None,
            pad: 'Padding from canvas edge' =4):
        if font is None:
            font = self.VARIABLE_FONT
        left = self.column_x0 + self.columnWidth
        right = self.targetCanvasWidth - pad
        top = self.cellHeight * (self.cellsPerColumn + 1)
        bottom = top + textHeight(font, ' ')
        return left, bottom, right, bottom
        
    def updateNItems(self, nItems=None):
        if nItems is None:
            nItems = self.nItems
        nItemsX, nItemsY, _, _ = self.attributeCoords()
        if self.nItemsText is None or self.canvas.type(self.nItemsText) != 'text':
            self.nItemsText = self.canvas.create_text(
                nItemsX, nItemsY, anchor=SW, text='', font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
        self.scrollToSee((self.nItemsText,))
        self.canvas_itemConfig(self.nItemsText,
                               text='nItems = {}'.format(nItems))
        
    def updateMaxLoadFactor(self, maxLoadFactor=None):
        if maxLoadFactor is None:
            maxLoadFactor = self.maxLoadFactor
        _, _, maxLoadX, maxLoadY = self.attributeCoords()
        if (self.maxLoadFactorText is None or
            self.canvas.type(self.maxLoadFactorText) != 'text'):
            self.maxLoadFactorText = self.canvas.create_text(
                maxLoadX, maxLoadY, anchor=SE, text='', font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
        self.scrollToSee((self.maxLoadFactorText,))
        self.canvas_itemConfig(
            self.maxLoadFactorText, text='maxLoadFactor = {}%'.format(
                int(100 * maxLoadFactor)))
    
    def createArrayCell(     # Create a box representing an array cell
            self, index, tags=["arrayBox"], color=None, width=None):
        if color is None: color = self.CELL_BORDER_COLOR
        if width is None: width = self.CELL_BORDER
        rect = self.canvas.create_rectangle(
            *self.arrayCellCoords(index), fill=None, outline=color, width=width,
            tags=tags)
        self.canvas.lower(rect)
        return rect

    def createArrayIndexLabel(self, index, tags='cellIndex'):
        coords = self.cellArrowCoords(index)
        text = self.canvas.create_text(
            *coords[2:], anchor=W, text='{:2d}'.format(index), tags=tags,
            font=self.cellIndexFont, fill=self.CELL_INDEX_COLOR)
        self.canvas.tag_bind(text, '<Button>', 
                             lambda e: self.setArgument(str(index)))
        return text

    def createArraySizeLabel(self, tags='sizeLabel'):
        coords = V(self.cellCenter(len(self.table) - 1)) + V(0, self.cellHeight)
        return self.canvas.create_text(
            *coords, text='{} cells'.format(len(self.table)), tags=tags,
            font=self.VALUE_FONT, fill=self.VARIABLE_COLOR)

    nextColor = 0
    
    def createCellValue(self, indexOrCoords, key, color=None):
        """Create new canvas items to represent a cell value.  A rectangle is
        created filled with a particular color behind an optional text key.
        The position of the cell can either be an integer index in the Array or
        the bounding box coordinates of the rectangle.  If color is not
        supplied, the next color in the palette is used.  An event handler is
        set up to update the VisualizationApp argument with the cell's value
        if clicked with any button.  Returns a tuple, (rectangle, text), of
        canvas items, which may be 1-tuple if self.showValues is False.
        """
        # Determine position and color of cell
        if isinstance(indexOrCoords, int):
            rectPos = self.cellCoords(indexOrCoords)
            valPos = self.cellCenter(indexOrCoords)
        else:
            rectPos = indexOrCoords
            valPos = BBoxCenter(rectPos)
            
        if color is None:
            # Take the next color from the palette
            color = drawnValue.palette[self.nextColor]
            self.nextColor = (self.nextColor + 1) % len(drawnValue.palette)
    
        cell = (self.canvas.create_rectangle(*rectPos, fill=color, outline='',
                                             width=0, tags='cellShape'),
                self.canvas.create_text(
                    *valPos, text=str(key), font=self.VALUE_FONT,
                    fill=self.VALUE_COLOR, tags="cellVal"))
        handler = lambda e: self.setArgument(
            self.canvas.itemConfig(cell[1], 'text') if
            self.canvas.type(cell[1]) == 'text' else '')
        for item in cell:
            self.canvas.tag_bind(item, '<Button>', handler)

        return cell

    def createArrayIndex(
            self, indexOrCoords, name=None, level=1, color=None, font=None):
        if color is None: color = self.VARIABLE_COLOR
        if font is None: font = self.cellIndexFont
        coords = self.arrayIndexCoords(indexOrCoords, level=level)
        items = (
            self.canvas.create_line(*coords[0], arrow=LAST, fill=color),
            self.canvas.create_text(
                *coords[1], text=name or '', anchor=SE if level > 0 else SW,
                font=font, fill=color))
        return items
