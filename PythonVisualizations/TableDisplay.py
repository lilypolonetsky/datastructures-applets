__doc__ = """
Helper class for Python visualization applications to display an array (table)
on the canvas.  Multiple Table objects can be created to animate arrays, 
stacks, queues, etc.
"""

from tkinter import *

try:
    from Visualization import *
    from coordinates import *
except ModuleNotFoundError:
    from .Visualization import *
    from .coordinates import *

V = vector

def updateCells(func):  # Decorator to update cells after changes to Table array
    def fWrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self.drawCells()
        return result
    return fWrapper

class Table(list):     # Display a table (array/list) in a visualization app

    def __init__(  # Constructor
            self,
            visualizationApp: 'Visualization app for displaying table',
            origin: 'Upper left corner point of cell 0',
            *args: 'Initial elements in table (not used by Table)',
            cellWidth: 'Table cell width' =50,
            cellHeight: 'Table cell height' =50,
            vertical: 'Use vertical orientation' =False,
            direction: '+1 means higher indices to right/down, -1 otherwise' =1,
            segmentLength: 'Max number of consecutive cells in one row' =None,
            segmentGap: 'Row/column segments are separated by gap' =100,
            label: 'Label (title) of table' ='',
            labelOffset: 'Spacing of label from cell 0' =10,
            labelPosition: 'Label position relative to bbox' =None,
            labelAnchor: 'Label anchor, N/S for vertical else E/W' =None,
            labelFont: 'Label font (default to variable font)' =None,
            labelColor: 'Label color (default to variable color)' =None,
            cellBorderWidth: 'Thickness of cell border lines' =2,
            cellBorderColor: 'Cell border color' ='black',
            cellBorderTags: 'Tags for cell border line items' =('cell',),
            indicesFont: 'If provided, draw numeric cell indices' =None,
            indicesColor: 'Color of indices if font provided' ='gray60',
            indicesAnchor: 'Position indices to the relative to cells' =None,
            indicesOffset: 'Offset of indices from cells' =4,
            indicesTags: 'Tags for index text items' =('cell', 'cellIndex'),
            eventHandlerPairs: '(event, handler) pairs for indices' =(),
            labeledArrowFont: 'Labeled arrow font (default: app variable)' =None,
            labeledArrowColor: 'Labeled arrow color (default: app variable)' =None,
            labeledArrowOffset: 'Offset of arrow tip from cell' =4,
            see: 'Scroll to see table + any see items' =() ):
        if not isinstance(visualizationApp, Visualization):
            raise ValueError('Table only works with Visualization objects')
        super().__init__(args)
        self.app = visualizationApp
        app = visualizationApp
        self.x0, self.y0 = origin
        self.VOrigin = V(origin)
        self.cellWidth, self.cellHeight = cellWidth, cellHeight
        self.VBox = V(cellWidth, cellHeight)
        self.vertical = vertical
        if direction not in (-1, 1):
            raise ValueError('Table direction must be -1 or +1')
        self.direction = direction
        self.segmentLength = segmentLength
        self.segmentGap = segmentGap
        self.label = label
        if labelAnchor is None:
            labelAnchor = (
                ((N if direction < 0 else S) if vertical else
                 (W if direction < 0 else E))
                if labelPosition is None else
                (S if labelPosition is N else N if labelPosition is S else
                 W if labelPosition is E else E))
        if labelPosition is None:
            labelPosition = (S if direction < 0 else N) if vertical else (
                E if direction < 0 else W)
        self.labelAnchor = labelAnchor
        self.labelPosition = labelPosition
        self.labelOffset = labelOffset
        self.labelFont = app.VARIABLE_FONT if labelFont is None else labelFont
        self.labelColor = (
            app.VARIABLE_COLOR if labelColor is None else labelColor)
        self.cellBorderWidth = cellBorderWidth
        self.cellBorderColor = cellBorderColor
        self.cellBorderTags = cellBorderTags
        self.indicesFont = indicesFont
        self.indicesColor = indicesColor
        self.indicesAnchor = indicesAnchor or (E if vertical else S)
        self.indicesOffset = indicesOffset
        self.indicesTags = indicesTags
        self.eventHandlers = eventHandlerPairs
        self.labeledArrowFont = (
            app.VARIABLE_FONT if labeledArrowFont is None else 
            labeledArrowFont)
        self.labeledArrowColor = (
            app.VARIABLE_COLOR if labeledArrowColor is None else
            labeledArrowColor)
        self.labeledArrowOffset = labeledArrowOffset
        self.cells, self.indices = [], []
        
        self.drawLabel()
        self.drawCells(see)

    def drawCells(self, see=(), scale=None):
        while len(self.cells) > len(self):  # Remove any excess cells/indices
            self.app.canvas.delete(self.cells.pop())
            if len(self.indices) > len(self.cells):
                self.app.canvas.delete(self.indices.pop())
        self.cells = [                      # Create any needed new cells
            self.cells[j] if (
                j < len(self.cells) and
                self.app.canvas.type(self.cells[j]) == 'rectangle') else
            self.app.canvas.create_rectangle(
                *self.arrayCellCoords(j, scale=scale), fill='',
                outline=self.cellBorderColor, width=self.cellBorderWidth,
                tags=self.cellBorderTags)
            for j in range(len(self))]
        if self.indicesFont and self.indicesColor: # Create any needed indices
            self.indices = [
                self.indices[j] if (
                    j < len(self.indices) and
                    self.app.canvas.type(self.indices[j]) == 'text') else
                self.app.canvas.create_text(
                    *self.arrayCellIndexCoords(j, scale=scale), text=str(j),
                    anchor=self.indicesAnchor, font=self.indicesFont,
                    fill=self.indicesColor, tags=self.indicesTags)
                for j in range(len(self))]
            for index in self.indices:
                self.app.scaleTextItem(index, scale)
        for textItem in self.indices:
            for event, handler in self.eventHandlers:
                if (callable(handler) and hasattr(Table, handler.__name__) and
                    callable(getattr(self, handler.__name__)())):
                    handler = getattr(self, handler.__name__)()
                self.app.canvas.tag_bind(textItem, event, handler)
        if see:
            self.app.scrollToSee(
                self.items() +
                (tuple(see) if isinstance(see, (list, tuple, set)) else ()))

    def drawLabel(self, scale=None):
        self.labelItem = self.app.canvas.create_text(
            *self.labelCoords(scale=scale), anchor=self.labelAnchor,
            text=self.label, fill=self.labelColor, font=self.labelFont)
        self.app.scaleTextItem(self.labelItem, scale)
        return self.labelItem

    def items(self):       # Tuple of all canvas items being used
        return (self.labelItem, *self.cells, *self.indices)
    
    def cellCoords(self, indexOrCoords, scale=None):
        if scale is None: scale = getattr(self.app, 'scale', 1)
        coordsGiven = isinstance(indexOrCoords, (list, tuple))
        if not coordsGiven:
            if self.segmentLength:
                row = (indexOrCoords // self.segmentLength) * self.direction
                col = (indexOrCoords % self.segmentLength) * self.direction
            else:
                row, col = 0, indexOrCoords * self.direction
        upperLeft = (
            tuple(indexOrCoords) if coordsGiven else
            V(self.VOrigin + V(V((1, 0) if self.vertical else (0, 1)) * 
                               (row * self.segmentGap))) +
            V(self.VBox * V(0 if self.vertical else col,
                            col if self.vertical else 0)))
        return V(upperLeft +
                 (V(V(upperLeft) + self.VBox) - V((self.cellBorderWidth,) * 2))
        ) * scale

    def cellCenter(self, indexOrCoords, scale=None):
        return BBoxCenter(self.cellCoords(indexOrCoords, scale=scale))

    def cellAndCenters(self, indexOrCoords, rows=1, scale=None):
        'Return the cell and center coords for a cell with N rows of text '
        if scale is None: scale = getattr(self.app, 'scale', 1)
        Vy = V(0, self.cellHeight * scale // max(1, rows))
        Vcenter = V(self.cellCenter(indexOrCoords, scale=scale))
        textCenters = tuple(Vcenter + V(Vy * (j - rows / 2 + 1/2))
                            for j in range(max(1, rows)))
        return (self.cellCoords(indexOrCoords), *textCenters)
    
    def arrayCellCoords(self, indexOrCoords, scale=None):
        if scale is None: scale = getattr(self.app, 'scale', 1)
        borderWidth = int(self.cellBorderWidth * scale)
        half = borderWidth // 2
        shift = (borderWidth - half,) * 2 + (-half, ) * 2
        return V(self.cellCoords(indexOrCoords, scale=scale)) - V(shift)

    def arrayCellIndexCoords(self, indexOrCoords, scale=None):
        if scale is None: scale = getattr(self.app, 'scale', 1)
        cell = self.cellCoords(indexOrCoords, scale=scale)
        center = BBoxCenter(cell)
        gap = (self.indicesOffset + self.cellBorderWidth) * scale
        if self.vertical:
            x = cell[0] - gap if E in self.indicesAnchor else cell[2] + gap
            y = center[1]
        else:
            x = center[0]
            y = cell[1] - gap if S in self.indicesAnchor else cell[3] + gap
        return (x, y)

    def labeledArrowCoords(
            self, indexOrCoords, level=1, orientation=0, scale=None, **kwargs):
        if scale is None: scale = getattr(self.app, 'scale', 1)
        cell = self.cellCoords(indexOrCoords, scale=scale)
        center = BBoxCenter(cell)
        gap = (-scale if level < 0 else scale) * (
            self.cellBorderWidth + self.labeledArrowOffset +
            (abs(self.indicesFont[1]) if self.indicesFont and level > 0 else 0))
        side = 2 if level < 0 else 0
        tip = (cell[side] - gap, center[1]) if self.vertical else (
            center[0], cell[side + 1] - gap)
        Vdelta = V(
            V(V((-1, 0) if self.vertical else (0, -1)).rotate(orientation)) *
            abs(scale * self.labeledArrowFont[1]))
        base = V(tip) + V(Vdelta * level)
        return base + tip, base
        
    def labelCoords(self, scale=None):
        if scale is None: scale = getattr(self.app, 'scale', 1)
        cell0 = self.cellCoords(0, scale=scale)
        center = BBoxCenter(cell0)
        side = 0 if self.labelPosition in (N, W) else 2
        gap = self.labelOffset * (scale if self.labelPosition in (N, W)
                                  else -scale)
        vertical = self.labelPosition in (N, S)
        return (center[0] if vertical else cell0[side] - gap,
                cell0[side + 1] - gap if vertical else center[1])

    arrayCellCenter = cellCenter

    pop = updateCells(list.pop)
    insert = updateCells(list.insert)
    append = updateCells(list.append)
    extend = updateCells(list.extend)
    remove = updateCells(list.remove)
    __setitem__ = updateCells(list.__setitem__)

    def __delitem__(self, key):
        result = super().__delitem__(key)
        while len(self.cells) > len(self):
            self.app.canvas.delete(self.cells.pop())
            if len(self.indices) > len(self.cells):
                self.app.canvas.delete(self.indices.pop())
        return result

    def createLabeledArrow(
            self, labeledArrowIndexOrCoords, label='', color=None, font=None,
            width=1, anchor=None, tags=('arrow',), see=(), scale=None,
            **kwargs):
        if color is None: color = self.labeledArrowColor
        if font is None: font = self.labeledArrowFont
        coords = (self.labeledArrowCoords(labeledArrowIndexOrCoords,
                                          scale=scale, **kwargs)
                  if isinstance(labeledArrowIndexOrCoords, (int, float)) else
                  labeledArrowIndexOrCoords)
        if anchor is None: 
            anchor = self.labeledArrowAnchor(coords[0])
        arrow = self.app.canvas.create_line(
            *coords[0], arrow=LAST, fill=color, width=width, tags=tags)
        text = self.app.canvas.create_text(
            *coords[1], anchor=anchor, text=label, font=font, fill=color,
            tags=tags)
        self.app.scaleTextItem(text, scale)
        if see:
            self.app.scrollToSee(
                (arrow, text) +
                (tuple(see) if isinstance(see, (tuple, list, set)) else ()))
        return arrow, text

    def labeledArrowAnchor(self, arrowCoords):
        dx, dy = V(arrowCoords[2:]) - V(arrowCoords[:2])
        return (W if dx < 0 else E) if abs(dx) > abs(dy) else (
            N if dy < 0 else S)
        
    def populateArgWithCellIndexHandler(self, argIdx=0):
        def cellIndexHandler(event):
            can = self.app.canvas
            if event.widget is can:
                for item in can.find_closest(can.canvasx(event.x),
                                             can.canvasy(event.y)):
                    if item in self.indices:
                        self.app.setArgument(
                            self.app.canvas_itemConfig(item, 'text'), argIdx)
        return cellIndexHandler
        
if __name__ == '__main__':
    from drawnValue import *
    app = Visualization(title='Table test', canvasBounds=(0, 0, 800, 400))

    app.setArgument = lambda arg, argIndex: print( # For clicks on indices
        'Set argument', argIndex, 'to {!r}'.format(arg))

    app.startAnimations()
    table1 = Table(app, (100, 50), 'foo', 'bar', label='Foo bar',
                   vertical=True, indicesFont=('Courier', -14), see=True,
                   cellHeight=30, cellBorderWidth=4, indicesAnchor=W,
                   indicesOffset=10,
                   eventHandlerPairs=(('<Button-1>', 
                                       Table.populateArgWithCellIndexHandler),))
    print('table1 contains:', table1)

    table2 = Table(app, (100, 300),
                   'lime\n4', 'apple\n10', 'fig\n8\n??', 'pear\n7',
                   label='Stack', vertical=True, direction=-1, see=True,
                   indicesFont=('Courier', -14), cellWidth=60, cellHeight=50,
                   eventHandlerPairs=(('<Button-1>', 
                                       Table.populateArgWithCellIndexHandler),))
    print('table2 contains:', table2)
    l1arrow = table2.createLabeledArrow(1, 'level -1', level=-1, see=True)
    l2arrow = table2.createLabeledArrow(
        table2.labeledArrowCoords(2, level=2), 'level 2', see=True)


    table3 = Table(app, (300, 70), *tuple(range(17, -1, -1)), label='Numbers+',
                   vertical=False, segmentLength=7, cellHeight=40, see=True,
                   segmentGap=90, cellBorderWidth=1)  #,
                   # indicesFont=('Courier', -14), indicesAnchor=NE)
    print('table3 contains:', table3)
    extras = (True, False, True)
    app.wait(0.5)
    
    table3.extend(extras)
    print('After extending with', extras, 'table3 contains:', table3)

    count = 0
    for tbl in (table1, table2, table3):
        for i in range(len(tbl)):
            val = tbl[i].split('\n') if isinstance(tbl[i], str) else [tbl[i]]
            coords = tbl.cellAndCenters(i, rows=len(val))
            tbl[i] = drawnValue(
                tbl[i],
                app.canvas.create_rectangle(
                    *coords[0],
                    fill=drawnValue.palette[count % len(drawnValue.palette)],
                    outline='', width=0),
                *(app.canvas.create_text(*coords[j + 1], text=str(v))
                  for j, v in enumerate(val)))
            count += 1
    print('Filled in', count, 'table cells')
    app.wait(1)

    interval = (-2, len(table2))
    print('Walking labeled arrow from', interval[0], 'to', interval[1],
          'of', table2.label)
    j = interval[0]
    jArrowConfig = {'level': 1, 'orientation': -40}
    jArrow = table2.createLabeledArrow(j, str(j), **jArrowConfig)
    for j in range(j + 1, interval[1] + 1):
        app.wait(0.1)
        app.moveItemsTo(
            jArrow, table2.labeledArrowCoords(j, **jArrowConfig),
            sleepTime=0.02, see=True, expand=True)
        app.canvas.itemConfig(jArrow[1], text=str(j))

    while table3[0].val > 15:
        print('Popping first cell,', table3[0].val, ', off', table3.label,
              'and moving remaining cells')
        app.moveItemsBy(table3[0].items, (-3 * len(table3), -table3.y0),
                        sleepTime=0.02)
        app.moveItemsTo(
            flat(*(dv.items for dv in table3[1:])),
            flat(*((table3.cellCoords(j), table3.cellCenter(j))
                   for j in range(len(table3) - 1))), sleepTime=0.02,
            see=True, expand=True)
        table3.pop(0)

    table4 = Table(app, (600, 300), label='Booleans', labelPosition=E,
                   vertical=True, cellHeight=25, cellWidth=70, see=True,
                   cellBorderWidth=0)
    print('Table for Boolean values "{}"'.format(table4.label),
          'with label position', table4.labelPosition.upper(),
          'and label anchor', table4.labelAnchor.upper())
        
    j = -2
    jArrow = table3.createLabeledArrow(j, 'j', **jArrowConfig)

    print('Removing booleans from', table3.label)
    while j < len(table3):
        if 0 <= j and isinstance(table3[j].val, bool):
            boolToMove = table3[j]
            print('Deleting cell', j, 'of table', table3.label, 'item',
                  boolToMove.val)
            app.moveItemsBy(boolToMove.items,
                            (table3.cellWidth, table3.cellHeight),
                            sleepTime=0.02, see=True, expand=True)
            del table3[j]
            print('Adding deleeted cell to table', table4.label,
                  'at position', len(table4))
            app.moveItemsLinearly(
                boolToMove.items, table4.cellAndCenters(len(table4)),
                sleepTime=0.02, see=True, expand=True)
            table4.append(boolToMove)
        else:
            j += 1
            app.moveItemsTo(
                jArrow, table3.labeledArrowCoords(j, **jArrowConfig),
                sleepTime=0.02, see=True, expand=True)

    print('Contents of table3, ', table3.label, ':')
    for j in range(len(table3)):
        print('{:3d}: {}'.format(j, table3[j]))
    for tbl in (table2, table3):
        print('The', len(tbl.items()), 
              'canvas items used to draw the cells and label of the',
              tbl.label, 'table are:', tbl.items())
        
    app.runVisualization()
